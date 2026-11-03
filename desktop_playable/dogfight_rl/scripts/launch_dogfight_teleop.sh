#!/usr/bin/env bash
# Desktop and CLI wrapper; no conda activation or dependency changes.
set -uo pipefail
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_ROOT="$PROJECT_ROOT/runs/battle/teleop/launcher"
mkdir -p "$LOG_ROOT"
LOG_FILE="$LOG_ROOT/$(date +%Y%m%d_%H%M%S)_$$.log"
fail() {
    local message="$1"
    printf '%s\n日志：%s\n' "$message" "$LOG_FILE" >&2
    if command -v zenity >/dev/null && [[ -n "${DISPLAY:-}" && "${DOGFIGHT_NO_DIALOG:-0}" != 1 ]]; then
        zenity --error --no-markup --title='机器狗对战环境启动失败' --width=640 --text="$message
日志：$LOG_FILE" 2>/dev/null || true
    fi
    exit 1
}
exec 9>"$LOG_ROOT/desktop.lock"
if ! flock -n 9; then fail '机器狗遥控入口已经运行，请先关闭原仿真窗口。'; fi
PYTHON_BIN="${DOGFIGHT_PYTHON:-$HOME/miniconda3/envs/dogfight/bin/python}"
[[ -x "$PYTHON_BIN" ]] || fail "冻结Python不存在：$PYTHON_BIN（可设置DOGFIGHT_PYTHON）"
# The desktop provides these. An SSH/Codex launch may use the sole existing local X11 display.
if [[ -z "${DISPLAY:-}" ]]; then
    shopt -s nullglob
    display_sockets=(/tmp/.X11-unix/X*)
    [[ ${#display_sockets[@]} -eq 1 ]] || fail '无法唯一确定图形桌面DISPLAY，请在Ubuntu桌面启动。'
    export DISPLAY=":${display_sockets[0]##*X}"
fi
if [[ -z "${XAUTHORITY:-}" && -f "/run/user/$(id -u)/gdm/Xauthority" ]]; then
    export XAUTHORITY="/run/user/$(id -u)/gdm/Xauthority"
fi
export PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 OMNI_KIT_ACCEPT_EULA=YES
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
unset LD_LIBRARY_PATH
cd "$PROJECT_ROOT" || fail '无法进入正式项目目录。'
printf 'DOGFIGHT V0.2 TELEOP\nStarted: %s\nProject: %s\nPython: %s\nDISPLAY: %s\n' "$(date -Is)" "$PROJECT_ROOT" "$PYTHON_BIN" "$DISPLAY" > "$LOG_FILE"
child_pid=''
stop_child() {
    if [[ -n "$child_pid" ]]; then kill -TERM "$child_pid" 2>/dev/null || true; wait "$child_pid" 2>/dev/null || true; fi
}
trap stop_child INT TERM HUP
"$PYTHON_BIN" -B "$PROJECT_ROOT/launch.py" teleop "$@" >> "$LOG_FILE" 2>&1 &
child_pid=$!
wait "$child_pid"
result=$?
child_pid=''
if [[ $result -ne 0 && $result -ne 130 && $result -ne 143 ]]; then
    detail="$(tail -n 9 "$LOG_FILE")"
    fail "仿真退出码：$result
$detail"
fi
exit "$result"
