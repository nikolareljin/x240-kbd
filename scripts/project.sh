#!/usr/bin/env bash
# Repo-specific behaviour for ./dev, sourced by scripts/cli.sh before dispatch.
#
# x240-kbd has no app to start: the artifacts are a QMK UF2 for the Pico, three
# CircuitPython probing tools, and the docs site. Every toolchain runs in Docker
# (qmkfm/qmk_cli, jekyll/jekyll) so nothing has to be installed on the host
# beyond docker, git and python3.
#
# scripts/cli.sh itself is refreshed from the script-helpers template and must
# not be edited; this file is where the verbs get their meaning.
#
#   ./dev install                    submodules, docker images, qmk_firmware checkout
#   ./dev build [firmware|docs|tools|all]
#   ./dev test                       host pytest, py_compile, link check, shellcheck
#   ./dev preflight                  test + build all (what CI runs)
#   ./dev deploy [firmware|<tool>]   copy the UF2 to RPI-RP2, or a tool to CIRCUITPY
#   ./dev devices                    show RPI-RP2 / CIRCUITPY mounts and serial ports
#   ./dev logs                       qmk console (firmware debug output)
#   ./dev clean | update
#
# Shims: ./build ./test ./flash ./probe <tool> ./site

shlib_import file

X240_KB_DIR="$DEV_REPO_ROOT/firmware/qmk/keyboards/x240_pico"
X240_KB="x240_pico"
X240_KM="default"
X240_QMK_HOME="${QMK_HOME:-$DEV_REPO_ROOT/qmk_firmware}"
X240_QMK_IMAGE="${QMK_DOCKER_IMAGE:-qmkfm/qmk_cli}"
X240_JEKYLL_IMAGE="${JEKYLL_DOCKER_IMAGE:-jekyll/jekyll:4}"
X240_OUT="$DEV_REPO_ROOT/out"   # not build/: ./build is the shim
X240_UF2="$X240_QMK_HOME/.build/${X240_KB}_${X240_KM}.uf2"
X240_TOOLS=(matrix_probe ps2_sniffer shift_register_test)

# --- helpers ---------------------------------------------------------------

x240_require_docker() {
  command -v docker >/dev/null 2>&1 || { log_error "docker is required (all toolchains run in containers)"; exit 1; }
  docker info >/dev/null 2>&1 || { log_error "docker daemon is not reachable"; exit 1; }
}

x240_docker_tty() { [[ -t 0 && -t 1 ]] && printf -- '-it' || printf -- '-i'; }

# Run a shell command inside the QMK image with the checkout and this keyboard mounted.
x240_qmk() {
  x240_require_docker
  [[ -f "$X240_QMK_HOME/Makefile" ]] || { log_error "no qmk_firmware checkout at $X240_QMK_HOME — run ./dev install"; exit 1; }
  docker run --rm "$(x240_docker_tty)" \
    -v "$X240_QMK_HOME":/qmk_firmware \
    -v "$X240_KB_DIR":/qmk_firmware/keyboards/$X240_KB \
    -w /qmk_firmware "$X240_QMK_IMAGE" sh -c \
    "git config --global --add safe.directory '*' >/dev/null 2>&1; qmk config user.qmk_home=/qmk_firmware >/dev/null 2>&1; $*"
}

# Run a shell command inside the Jekyll image with docs/ mounted; $1 is the output dir.
x240_jekyll() {
  x240_require_docker
  local out="$1"; shift
  mkdir -p "$out" "$X240_OUT/.bundle"
  docker run --rm "$(x240_docker_tty)" -e JEKYLL_ENV=production \
    -v "$DEV_REPO_ROOT/docs":/srv/jekyll -v "$out":/out -v "$X240_OUT/.bundle":/usr/local/bundle \
    -w /srv/jekyll "$X240_JEKYLL_IMAGE" sh -c "$*"
}

# Find a mounted drive by volume label (RPI-RP2, CIRCUITPY) on Linux or macOS.
x240_find_mount() {
  local label="$1" d
  [[ -n "${X240_MOUNT:-}" && -d "$X240_MOUNT" ]] && { printf '%s\n' "$X240_MOUNT"; return 0; }
  for d in "/media/$USER/$label" "/run/media/$USER/$label" "/media/$label" "/mnt/$label" "/Volumes/$label"; do
    [[ -d "$d" ]] && { printf '%s\n' "$d"; return 0; }
  done
  if command -v findmnt >/dev/null 2>&1; then
    d="$(findmnt -rn -o TARGET -S "LABEL=$label" 2>/dev/null | head -1)"
    [[ -n "$d" ]] && { printf '%s\n' "$d"; return 0; }
  fi
  return 1
}

x240_wait_mount() {
  local label="$1" secs="${2:-60}" m i
  for ((i = 0; i < secs; i++)); do
    if m="$(x240_find_mount "$label")"; then printf '%s\n' "$m"; return 0; fi
    (( i == 0 )) && log_info "waiting up to ${secs}s for a drive labelled $label (override with X240_MOUNT=/path)"
    sleep 1
  done
  return 1
}

x240_is_tool() { local t; for t in "${X240_TOOLS[@]}"; do [[ "$t" == "$1" ]] && return 0; done; return 1; }

# --- verbs -----------------------------------------------------------------

project_install() {
  log_info "install: submodules"
  git -C "$DEV_REPO_ROOT" submodule update --init --recursive
  x240_require_docker
  log_info "install: docker images"
  docker pull -q "$X240_QMK_IMAGE" >/dev/null
  docker pull -q "$X240_JEKYLL_IMAGE" >/dev/null
  if [[ -f "$X240_QMK_HOME/Makefile" ]]; then
    log_info "install: qmk_firmware already at $X240_QMK_HOME"
  else
    log_info "install: cloning qmk_firmware (shallow, with submodules) into $X240_QMK_HOME"
    git clone -q --depth 1 --recurse-submodules --shallow-submodules -j8 \
      https://github.com/qmk/qmk_firmware "$X240_QMK_HOME"
  fi
  if command -v python3 >/dev/null 2>&1 && ! python3 -c 'import pytest' 2>/dev/null; then
    log_warn "python3 has no pytest; ./dev test will try 'pip install --user pytest'"
  fi
  print_success "install: done"
}

x240_build_firmware() {
  log_info "build: firmware ($X240_KB:$X240_KM) in $X240_QMK_IMAGE"
  x240_qmk "qmk compile -kb $X240_KB -km $X240_KM -j \$(nproc)"
  mkdir -p "$X240_OUT"
  cp "$X240_UF2" "$X240_OUT/" && print_success "build: $X240_OUT/$(basename "$X240_UF2")"
}

x240_build_docs() {
  log_info "build: docs site in $X240_JEKYLL_IMAGE"
  x240_jekyll "$X240_OUT/site" "bundle install --quiet >/dev/null 2>&1; bundle exec jekyll build -d /out 2>&1 | grep -vE 'DEPRECATION|sass-lang|^\s*[╷╵│]|^\s*[0-9]+ │|\^\^|repetitive|verbose|color-functions|^\s*$'"
  if [[ -f "$X240_OUT/site/index.html" ]]; then print_success "build: $X240_OUT/site"; else log_error "docs build produced no index.html"; return 1; fi
}

x240_build_tools() {
  log_info "build: byte-compile CircuitPython tools"
  local t
  for t in "${X240_TOOLS[@]}"; do python3 -m py_compile "$DEV_REPO_ROOT/tools/$t/$t.py"; done
  print_success "build: tools compile"
}

project_build() {
  local what="${DEV_ARGS[0]:-firmware}"
  case "$what" in
    firmware) x240_build_firmware ;;
    docs)     x240_build_docs ;;
    tools)    x240_build_tools ;;
    all)      x240_build_tools && x240_build_firmware && x240_build_docs ;;
    *) log_error "build: unknown target '$what' (firmware|docs|tools|all)"; exit 2 ;;
  esac
}

project_test() {
  local rc=0
  log_info "test: tools (pytest)"
  if ! python3 -c 'import pytest' 2>/dev/null; then python3 -m pip install --user -q pytest || true; fi
  ( cd "$DEV_REPO_ROOT/tools/tests" && python3 -m pytest -q ) || rc=1
  x240_build_tools || rc=1
  log_info "test: markdown relative links"
  python3 "$DEV_REPO_ROOT/scripts/check_links.py" "$DEV_REPO_ROOT" || rc=1
  if command -v shellcheck >/dev/null 2>&1; then
    log_info "test: shellcheck (repo-owned scripts; cli.sh/_bootstrap.sh are the script-helpers template)"
    ( cd "$DEV_REPO_ROOT" && shellcheck -x dev build test flash probe site scripts/project.sh ) || rc=1
  else
    log_warn "test: shellcheck not installed, skipping"
  fi
  if (( rc == 0 )); then print_success "test: all passed"; else log_error "test: failures above"; fi
  return $rc
}

project_preflight() {
  project_test
  DEV_ARGS=(all)          # an array cannot be set in a command prefix; it would become the string "(all)"
  project_build
  print_success "preflight: green"
}

project_run() {
  not_applicable run "a keyboard is not started; flash it with ./dev deploy and watch ./dev logs"
}

project_logs() {
  x240_require_docker
  log_info "logs: qmk console (needs the firmware built with CONSOLE_ENABLE = yes)"
  docker run --rm "$(x240_docker_tty)" --privileged -v /dev/bus/usb:/dev/bus/usb "$X240_QMK_IMAGE" qmk console
}

project_deploy() {
  local what="${DEV_ARGS[0]:-firmware}" m
  if [[ "$what" == "firmware" ]]; then
    [[ -f "$X240_UF2" ]] || x240_build_firmware
    log_info "deploy: hold BOOTSEL while plugging the Pico in (or use Bootmagic / RUN + BOOTSEL)"
    m="$(x240_wait_mount RPI-RP2 90)" || { log_error "no RPI-RP2 drive appeared"; exit 1; }
    cp "$X240_UF2" "$m/" && sync && print_success "deploy: $(basename "$X240_UF2") -> $m (the Pico reboots into the firmware)"
  elif x240_is_tool "$what"; then
    log_info "deploy: the Pico must be running CircuitPython (CIRCUITPY drive present)"
    m="$(x240_wait_mount CIRCUITPY 90)" || { log_error "no CIRCUITPY drive appeared"; exit 1; }
    cp "$DEV_REPO_ROOT/tools/$what/$what.py" "$m/code.py" && sync
    print_success "deploy: tools/$what/$what.py -> $m/code.py — open a 115200 baud serial terminal"
  else
    log_error "deploy: unknown target '$what' (firmware|${X240_TOOLS[*]})"; exit 2
  fi
}

project_devices() {
  local label m
  for label in RPI-RP2 CIRCUITPY; do
    if m="$(x240_find_mount "$label")"; then echo "$label  $m"; else echo "$label  (not mounted)"; fi
  done
  echo "serial ports:"
  find /dev -maxdepth 1 \( -name 'ttyACM*' -o -name 'tty.usbmodem*' \) 2>/dev/null | sed 's/^/  /' || true
  if command -v lsusb >/dev/null 2>&1; then
    echo "usb (Raspberry Pi 2e8a, Synaptics 06cb, this keyboard 6e6b):"
    lsusb 2>/dev/null | grep -iE '2e8a|06cb|6e6b' | sed 's/^/  /' || echo "  none"
  fi
}

project_clean() {
  rm -rf "$X240_OUT" "$DEV_REPO_ROOT/docs/_site" "$DEV_REPO_ROOT/docs/.jekyll-cache"
  find "$DEV_REPO_ROOT/tools" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true
  rm -rf "$DEV_REPO_ROOT/tools/tests/.pytest_cache"
  if [[ -d "$X240_QMK_HOME/.build" ]] && command -v docker >/dev/null 2>&1; then
    # objects are root-owned from the container; remove them the same way
    docker run --rm -v "$X240_QMK_HOME":/qmk_firmware "$X240_QMK_IMAGE" sh -c "rm -rf /qmk_firmware/.build/obj_${X240_KB}_* /qmk_firmware/.build/${X240_KB}_*" || true
  fi
  log_info "clean: done (the qmk_firmware checkout itself is kept; delete $X240_QMK_HOME by hand)"
}

project_update() {
  git -C "$DEV_REPO_ROOT" submodule update --remote --merge scripts/script-helpers
  if [[ -d "$X240_QMK_HOME/.git" ]]; then
    log_info "update: qmk_firmware"
    git -C "$X240_QMK_HOME" pull -q --ff-only && git -C "$X240_QMK_HOME" submodule update -q --init --recursive
  fi
  command -v docker >/dev/null 2>&1 && { docker pull -q "$X240_QMK_IMAGE" >/dev/null; docker pull -q "$X240_JEKYLL_IMAGE" >/dev/null; }
  print_success "update: done"
}

project_release()    { not_applicable release "releases are tagged by hand after M8 validation; see CHANGELOG.md"; }
project_screenshot() { not_applicable screenshot "no screen on a keyboard"; }
project_record()     { not_applicable record "no screen on a keyboard"; }
