#!/usr/bin/env bash
# SCRIPT: pull_toolchain.sh
# DESCRIPTION: Pull the pinned Docker images in scripts/toolchain.env; optionally save
#              them as tarballs for offline use, or re-resolve the pins from the tags.
# USAGE: scripts/pull_toolchain.sh [--save <dir>] [--load <dir>] [--refresh] [--verify]
#
# PARAMETERS:
#   --save <dir>    After pulling, `docker save` each image to <dir>/<name>.tar (GBs; not committed).
#   --load <dir>    `docker load` tarballs from <dir> instead of pulling (offline machine).
#   --refresh       Pull the floating tags, resolve their current digests, rewrite toolchain.env.
#   --verify        Print the tool versions inside each image.
# EXIT_CODES:
#   0 success, 1 a pull/load/verify failed, 2 bad arguments
# ----------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/_bootstrap.sh"
shlib_import logging
ENV_FILE="$SCRIPT_DIR/toolchain.env"
# shellcheck source=/dev/null
source "$ENV_FILE"

save_dir="" load_dir="" refresh=false verify=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --save) save_dir="${2:?--save needs a directory}"; shift 2 ;;
    --load) load_dir="${2:?--load needs a directory}"; shift 2 ;;
    --refresh) refresh=true; shift ;;
    --verify) verify=true; shift ;;
    -h|--help) sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) log_error "unknown argument: $1"; exit 2 ;;
  esac
done

command -v docker >/dev/null 2>&1 || { log_error "docker is required"; exit 1; }

images=(QMK JEKYLL OPENSCAD)

if [[ -n "$load_dir" ]]; then
  for n in "${images[@]}"; do
    tar="$load_dir/$(echo "$n" | tr '[:upper:]' '[:lower:]').tar"
    [[ -f "$tar" ]] || { log_error "missing $tar"; exit 1; }
    log_info "load: $tar"; docker load -q -i "$tar" >/dev/null
  done
elif $refresh; then
  for n in "${images[@]}"; do
    tag_var="${n}_IMAGE_TAG"; tag="${!tag_var}"
    log_info "refresh: pulling $tag"; docker pull -q "$tag" >/dev/null
    digest="$(docker inspect --format '{{index .RepoDigests 0}}' "$tag")"
    sed -i -E "s|^${n}_IMAGE=.*|${n}_IMAGE=\"$digest\"|" "$ENV_FILE"
    log_info "refresh: ${n}_IMAGE=$digest"
  done
  sed -i -E "s|^# Digests and the QMK commit were last resolved on .*|# Digests and the QMK commit were last resolved on $(date +%F).|" "$ENV_FILE"
  print_success "refresh: $ENV_FILE rewritten (QMK_FIRMWARE_REF is left for you to bump deliberately)"
else
  for n in "${images[@]}"; do
    var="${n}_IMAGE"; ref="${!var}"
    log_info "pull: $ref"; docker pull -q "$ref" >/dev/null
    # give the digest-pinned image its friendly tag too, so `docker images` reads sanely
    tag_var="${n}_IMAGE_TAG"; docker tag "$ref" "${!tag_var}" 2>/dev/null || true
  done
fi

if [[ -n "$save_dir" ]]; then
  mkdir -p "$save_dir"
  for n in "${images[@]}"; do
    var="${n}_IMAGE"; tar="$save_dir/$(echo "$n" | tr '[:upper:]' '[:lower:]').tar"
    log_info "save: ${!var} -> $tar"; docker save -o "$tar" "${!var}"
  done
  print_success "save: $(du -sh "$save_dir" | cut -f1) in $save_dir (keep it out of git)"
fi

if $verify; then
  echo "qmk:      $(docker run --rm "$QMK_IMAGE" sh -c 'qmk --version; arm-none-eabi-gcc --version | head -1' | paste -sd' ')"
  echo "jekyll:   $(docker run --rm "$JEKYLL_IMAGE" jekyll --version 2>/dev/null)"
  echo "openscad: $(docker run --rm "$OPENSCAD_IMAGE" openscad --version 2>&1 | head -1)"
  echo "qmk_firmware ref: $QMK_FIRMWARE_REF"
fi
print_success "toolchain ready"
