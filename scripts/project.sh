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
#   ./dev build [firmware|docs|tools|cad|pcb|all]
#   ./dev test                       host pytest, py_compile, link check, shellcheck
#   ./dev preflight                  test + build all (what CI runs)
#   ./dev deploy [firmware|<tool>]   copy the UF2 to RPI-RP2, or a tool to CIRCUITPY
#   ./dev devices                    show RPI-RP2 / CIRCUITPY mounts and serial ports
#   ./dev logs                       qmk console (firmware debug output)
#   ./dev clean | update
#
# Shims: ./build ./test ./flash ./probe <tool> ./site

shlib_import file

# Pinned images and the qmk_firmware commit: scripts/toolchain.env (pull_toolchain.sh).
# shellcheck source=/dev/null
source "$DEV_SCRIPT_DIR/toolchain.env"

X240_KB_DIR="$DEV_REPO_ROOT/firmware/qmk/keyboards/x240_pico"
X240_KB="x240_pico"
X240_KM="default"
X240_QMK_HOME="${QMK_HOME:-$DEV_REPO_ROOT/qmk_firmware}"
X240_QMK_IMAGE="${QMK_DOCKER_IMAGE:-$QMK_IMAGE}"
X240_JEKYLL_IMAGE="${JEKYLL_DOCKER_IMAGE:-$JEKYLL_IMAGE}"
X240_OPENSCAD_IMAGE="${OPENSCAD_DOCKER_IMAGE:-$OPENSCAD_IMAGE}"
X240_KICAD_IMAGE="${KICAD_DOCKER_IMAGE:-$KICAD_IMAGE}"
X240_FREEROUTING_IMAGE="${FREEROUTING_DOCKER_IMAGE:-$FREEROUTING_IMAGE}"
X240_PCB_DIR="$DEV_REPO_ROOT/hardware/pcb"
X240_PCB="x240_pico_rev_b"
X240_OUT="$DEV_REPO_ROOT/out"   # not build/: ./build is the shim
X240_UF2="$X240_QMK_HOME/.build/${X240_KB}_${X240_KM}.uf2"
X240_TOOLS=(matrix_probe ps2_sniffer shift_register_test)

# --- helpers ---------------------------------------------------------------

x240_require_docker() {
  command -v docker >/dev/null 2>&1 || { log_error "docker is required (all toolchains run in containers)"; exit 1; }
  docker info >/dev/null 2>&1 || { log_error "docker daemon is not reachable"; exit 1; }
}

x240_docker_tty() { [[ -t 0 && -t 1 ]] && printf -- '-it' || printf -- '-i'; }

# Shallow clone of qmk_firmware at exactly QMK_FIRMWARE_REF, submodules included.
x240_clone_qmk() {
  mkdir -p "$X240_QMK_HOME"
  git -C "$X240_QMK_HOME" init -q
  git -C "$X240_QMK_HOME" remote add origin "$QMK_FIRMWARE_REPO" 2>/dev/null || true
  git -C "$X240_QMK_HOME" fetch -q --depth 1 origin "$QMK_FIRMWARE_REF"
  git -C "$X240_QMK_HOME" checkout -q FETCH_HEAD
  git -C "$X240_QMK_HOME" submodule update -q --init --recursive --depth 1 --jobs 8
}

# Run a shell command inside the QMK image with the checkout and this keyboard mounted.
# The bind-mounted checkout is owned by the host user, so git inside the container needs
# it marked safe; only the checkout and its lib/* submodules are whitelisted, not '*'.
x240_qmk() {
  x240_require_docker
  [[ -f "$X240_QMK_HOME/Makefile" ]] || { log_error "no qmk_firmware checkout at $X240_QMK_HOME — run ./dev install"; exit 1; }
  docker run --rm "$(x240_docker_tty)" \
    -v "$X240_QMK_HOME":/qmk_firmware \
    -v "$X240_KB_DIR":/qmk_firmware/keyboards/$X240_KB \
    -w /qmk_firmware "$X240_QMK_IMAGE" sh -c \
    "for d in /qmk_firmware /qmk_firmware/lib/*; do git config --global --add safe.directory \"\$d\" >/dev/null 2>&1; done; qmk config user.qmk_home=/qmk_firmware >/dev/null 2>&1; $*"
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
  log_info "install: pinned docker images (scripts/toolchain.env)"
  bash "$DEV_SCRIPT_DIR/pull_toolchain.sh"
  if [[ -f "$X240_QMK_HOME/Makefile" ]]; then
    local have; have="$(git -C "$X240_QMK_HOME" rev-parse HEAD 2>/dev/null || echo unknown)"
    if [[ "$have" == "$QMK_FIRMWARE_REF" ]]; then
      log_info "install: qmk_firmware already at $X240_QMK_HOME @ ${have:0:12}"
    else
      log_warn "install: qmk_firmware at $X240_QMK_HOME is ${have:0:12}, pinned ref is ${QMK_FIRMWARE_REF:0:12} — run ./dev update"
    fi
  else
    log_info "install: cloning qmk_firmware @ ${QMK_FIRMWARE_REF:0:12} (shallow, with submodules) into $X240_QMK_HOME"
    x240_clone_qmk
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
  # The output dir is emptied inside the container (its files are container-owned), so a
  # stale index.html from an earlier run cannot pass for a fresh build. pipefail keeps
  # jekyll's exit status through the grep that trims Sass deprecation noise; grep's own
  # status is ignored since "nothing to print" is the good case.
  x240_jekyll "$X240_OUT/site" "set -o pipefail; rm -rf /out/* /out/.[!.]* 2>/dev/null; bundle install --quiet >/dev/null 2>&1 && { bundle exec jekyll build -d /out 2>&1 | { grep -vE 'DEPRECATION|sass-lang|^\s*[╷╵│]|^\s*[0-9]+ │|\^\^|repetitive|verbose|color-functions|^\s*$' || true; }; }" \
    || { log_error "docs build failed (jekyll exit status above)"; return 1; }
  if [[ -f "$X240_OUT/site/index.html" ]]; then print_success "build: $X240_OUT/site"; else log_error "docs build produced no index.html"; return 1; fi
}

x240_build_tools() {
  log_info "build: byte-compile CircuitPython tools"
  local t
  for t in "${X240_TOOLS[@]}"; do python3 -m py_compile "$DEV_REPO_ROOT/tools/$t/$t.py"; done
  print_success "build: tools compile"
}

# Render every printed part to STL (and a PNG preview) in the OpenSCAD image.
# Parts with variants are rendered once per variant via -D.
x240_build_cad() {
  x240_require_docker
  local out="$X240_OUT/cad" rc=0
  mkdir -p "$out"
  local jobs=(
    "bottom_case_left:bottom_case.scad:half=\"left\""
    "bottom_case_right:bottom_case.scad:half=\"right\""
    "perfboard_sled:perfboard_sled.scad:"
    "usb_strain_relief:usb_strain_relief.scad:"
    "tilt_feet:tilt_feet.scad:"
    "zif_support_block_keyboard:zif_support_block.scad:variant=\"keyboard\""
    "zif_support_block_clickpad:zif_support_block.scad:variant=\"clickpad\""
    "led_light_pipe:led_light_pipe.scad:"
    "pico_mount_bracket:pico_mount_bracket.scad:"
    "fpc_cable_guide_keyboard:fpc_cable_guide.scad:cable=\"keyboard\""
    "fpc_cable_guide_clickpad:fpc_cable_guide.scad:cable=\"clickpad\""
  )
  # 2D plates for the laser-cut route and the box insert, exported as DXF
  local dxf_jobs=(
    "plate_bottom:export_plates.scad:plate=\"bottom\""
    "plate_spacer:export_plates.scad:plate=\"spacer\""
    "box_insert:export_plates.scad:plate=\"insert\""
    "plates_sheet:export_plates.scad:plate=\"sheet\""
  )
  local job name src def
  for job in "${jobs[@]}"; do
    IFS=: read -r name src def <<<"$job"
    log_info "build: cad $name"
    local dargs=()
    [[ -n "$def" ]] && dargs=(-D "$def")
    if ! docker run --rm -v "$DEV_REPO_ROOT/cad":/cad:ro -v "$out":/out -w /cad "$X240_OPENSCAD_IMAGE" \
        openscad -q "${dargs[@]}" -o "/out/$name.stl" "$src" 2>&1 | grep -vE '^\s*$' | sed 's/^/   /'; then
      :
    fi
    [[ -s "$out/$name.stl" ]] || { log_error "build: cad $name produced no STL"; rc=1; }
  done
  for job in "${dxf_jobs[@]}"; do
    IFS=: read -r name src def <<<"$job"
    log_info "build: cad $name (dxf)"
    docker run --rm -v "$DEV_REPO_ROOT/cad":/cad:ro -v "$out":/out -w /cad "$X240_OPENSCAD_IMAGE" \
        openscad -q -D "$def" -o "/out/$name.dxf" "$src" 2>&1 | grep -vE '^\s*$' | sed 's/^/   /' || true
    [[ -s "$out/$name.dxf" ]] || { log_error "build: cad $name produced no DXF"; rc=1; }
  done
  if (( rc == 0 )); then print_success "build: $out ($(find "$out" -name "*.stl" | wc -l) STL, $(find "$out" -name "*.dxf" | wc -l) DXF)"; fi
  return $rc
}

# Generate, route, check and export the Rev B board. Every KiCad step runs in the kicad
# image; routing runs in the freerouting image. Outputs land in out/pcb; the generated
# .kicad_sch/.kicad_pcb are written back into hardware/pcb (they are committed).
# Runs as the invoking user: the image's own uid (1000) only matches by luck, and in CI the
# checkout belongs to uid 1001, so the generated files could not be written there.
x240_kicad() {
  docker run --rm "$(x240_docker_tty)" --user "$(id -u):$(id -g)" -e HOME=/tmp -e XDG_CONFIG_HOME=/tmp/.config \
    -v "$X240_PCB_DIR":/pcb -v "$X240_OUT/pcb":/out -w /pcb "$X240_KICAD_IMAGE" sh -c "$*"
}

x240_build_pcb() {
  x240_require_docker
  local out="$X240_OUT/pcb" passes="${X240_ROUTE_PASSES:-100}"
  mkdir -p "$out"
  log_info "build: pcb — schematic from netlist_model.py, ERC"
  x240_kicad "python3 gen_schematic.py /pcb && kicad-cli sch erc --severity-error --exit-code-violations -o /out/erc.rpt $X240_PCB.kicad_sch" \
    || { log_error "build: pcb ERC has errors (out/pcb/erc.rpt)"; return 1; }
  x240_kicad "kicad-cli sch export pdf -o /out/schematic.pdf $X240_PCB.kicad_sch >/dev/null && kicad-cli sch export netlist -o /out/$X240_PCB.net $X240_PCB.kicad_sch >/dev/null && kicad-cli sch export bom -o /out/bom.csv --fields 'Reference,Value,Footprint,\${QUANTITY}' --group-by Value,Footprint $X240_PCB.kicad_sch >/dev/null"
  log_info "build: pcb — board from netlist_model.py, placement DRC"
  x240_kicad "python3 gen_pcb.py /pcb 2>/dev/null && kicad-cli pcb drc --severity-error --exit-code-violations -o /out/drc-placement.rpt $X240_PCB.kicad_pcb >/dev/null 2>&1 || { kicad-cli pcb drc --severity-error -o /out/drc-placement.rpt $X240_PCB.kicad_pcb >/dev/null 2>&1; grep -c '^\[' /out/drc-placement.rpt; }"
  if [[ "${X240_SKIP_ROUTE:-}" != "1" ]]; then
    log_info "build: pcb — autoroute (freerouting, $passes passes; X240_SKIP_ROUTE=1 to skip)"
    x240_kicad "python3 route_pcb.py export $X240_PCB.kicad_pcb /out/$X240_PCB.dsn 2>/dev/null"
    docker run --rm "$(x240_docker_tty)" -v "$out":/w --entrypoint java "$X240_FREEROUTING_IMAGE" \
      -jar /app/freerouting-executable.jar -de "/w/$X240_PCB.dsn" -do "/w/$X240_PCB.ses" -mp "$passes" -oit 0.5 2>&1 | grep -E 'passes|unrouted|routed|incomplete|Routing' | tail -3 || true
    [[ -s "$out/$X240_PCB.ses" ]] || { log_error "build: pcb — freerouting produced no session file"; return 1; }
    x240_kicad "python3 route_pcb.py import $X240_PCB.kicad_pcb /out/$X240_PCB.ses 2>/dev/null"
  fi
  if [[ "${X240_SKIP_ROUTE:-}" == "1" ]]; then
    log_warn "build: pcb — route skipped; DRC reported, not enforced (board is unrouted)"
    x240_kicad "kicad-cli pcb drc --severity-error -o /out/drc.rpt $X240_PCB.kicad_pcb >/dev/null 2>&1"; grep -E 'unconnected' "$out/drc.rpt" | head -2
  else
    log_info "build: pcb — DRC on the routed board"
    x240_kicad "kicad-cli pcb drc --severity-error --exit-code-violations -o /out/drc.rpt $X240_PCB.kicad_pcb >/dev/null 2>&1" \
      || { log_error "build: pcb DRC has errors (out/pcb/drc.rpt)"; grep -E '^\[|unconnected' "$out/drc.rpt" | head -8; return 1; }
  fi
  log_info "build: pcb — fab outputs"
  x240_kicad "mkdir -p /out/gerbers && kicad-cli pcb export gerbers -o /out/gerbers/ $X240_PCB.kicad_pcb >/dev/null && kicad-cli pcb export drill -o /out/gerbers/ $X240_PCB.kicad_pcb >/dev/null && kicad-cli pcb export pos -o /out/$X240_PCB-pos.csv --format csv --units mm $X240_PCB.kicad_pcb >/dev/null && kicad-cli pcb export pdf -o /out/board.pdf --layers F.Cu,B.Cu,F.Silkscreen,Edge.Cuts $X240_PCB.kicad_pcb >/dev/null && cd /out/gerbers && zip -q -r ../gerbers.zip ."
  print_success "build: $out (schematic.pdf, board.pdf, gerbers.zip, bom.csv, $X240_PCB-pos.csv)"
}

project_build() {
  local what="${DEV_ARGS[0]:-firmware}"
  case "$what" in
    firmware) x240_build_firmware ;;
    docs)     x240_build_docs ;;
    tools)    x240_build_tools ;;
    cad)      x240_build_cad ;;
    pcb)      x240_build_pcb ;;
    all)      x240_build_tools && x240_build_firmware && x240_build_docs && x240_build_cad && x240_build_pcb ;;
    *) log_error "build: unknown target '$what' (firmware|docs|tools|cad|pcb|all)"; exit 2 ;;
  esac
}

# The two case halves must not share any volume: render their intersection and
# require its X extent to be ~0 (touching faces on the seam plane are expected).
x240_test_cad_joint() {
  command -v docker >/dev/null 2>&1 || { log_warn "test: no docker, skipping the CAD joint test"; return 0; }
  log_info "test: CAD split-joint interference"
  local out="$X240_OUT/cad-test"; mkdir -p "$out"
  docker run --rm -v "$DEV_REPO_ROOT/cad":/cad:ro -v "$out":/out -w /cad/tests "$X240_OPENSCAD_IMAGE" \
    openscad -q -o /out/joint_intersection.stl joint_intersection.scad 2>&1 | grep -vE '^\s*$' | sed 's/^/   /' || true
  python3 "$DEV_REPO_ROOT/scripts/check_cad_joint.py" "$out/joint_intersection.stl"
}

project_test() {
  local rc=0
  log_info "test: tools (pytest)"
  if ! python3 -c 'import pytest' 2>/dev/null; then python3 -m pip install --user -q pytest || true; fi
  ( cd "$DEV_REPO_ROOT/tools/tests" && python3 -m pytest -q ) || rc=1
  x240_build_tools || rc=1
  log_info "test: markdown relative links"
  python3 "$DEV_REPO_ROOT/scripts/check_links.py" "$DEV_REPO_ROOT" || rc=1
  x240_test_cad_joint || rc=1
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
    log_info "update: qmk_firmware -> pinned ${QMK_FIRMWARE_REF:0:12}"
    git -C "$X240_QMK_HOME" fetch -q --depth 1 origin "$QMK_FIRMWARE_REF" \
      && git -C "$X240_QMK_HOME" checkout -q FETCH_HEAD \
      && git -C "$X240_QMK_HOME" submodule update -q --init --recursive --depth 1 --jobs 8
  fi
  command -v docker >/dev/null 2>&1 && bash "$DEV_SCRIPT_DIR/pull_toolchain.sh"
  print_success "update: done"
}

project_release()    { not_applicable release "releases are tagged by hand after M8 validation; see CHANGELOG.md"; }
project_screenshot() { not_applicable screenshot "no screen on a keyboard"; }
project_record()     { not_applicable record "no screen on a keyboard"; }
