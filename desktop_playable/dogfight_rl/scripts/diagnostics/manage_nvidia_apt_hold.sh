#!/usr/bin/env bash
set -euo pipefail

mode="${1:-hold}"
if [[ "$mode" != "hold" && "$mode" != "unhold" && "$mode" != "status" ]]; then
  echo "Usage: sudo $0 [hold|unhold|status]" >&2
  exit 2
fi

native_arch="$(dpkg --print-architecture)"
mapfile -t packages < <(
  dpkg-query -W -f='${binary:Package}\t${Status}\n' 2>/dev/null \
    | awk '($2 == "install" || $2 == "hold") && $3 == "ok" && $4 == "installed" {print $1}' \
    | grep -E '^(nvidia|libnvidia|xserver-xorg-video-nvidia|linux-(modules|objects|signatures)-nvidia)' \
    | sed "s/:${native_arch}$//" \
    | sort -u
)

if (( ${#packages[@]} == 0 )); then
  echo "No installed NVIDIA APT packages found." >&2
  exit 1
fi

if [[ "$mode" == "status" ]]; then
  held="$(apt-mark showhold)"
  for package in "${packages[@]}"; do
    if grep -Fxq "$package" <<<"$held"; then
      printf 'HELD     %s\n' "$package"
    else
      printf 'NOT_HELD %s\n' "$package"
    fi
  done
  exit 0
fi

if (( EUID != 0 )); then
  echo "Run with sudo: sudo $0 $mode" >&2
  exit 1
fi

apt-mark "$mode" "${packages[@]}"

echo
echo "NVIDIA APT package status:"
held="$(apt-mark showhold)"
for package in "${packages[@]}"; do
  if grep -Fxq "$package" <<<"$held"; then
    printf 'HELD     %s\n' "$package"
  else
    printf 'NOT_HELD %s\n' "$package"
  fi
done
