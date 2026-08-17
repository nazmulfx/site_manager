#!/bin/bash

ACTIVE_PATH=$(which python3 2>/dev/null || which python 2>/dev/null || echo "")
ACTIVE_REAL_PATH=""
if [ -n "$ACTIVE_PATH" ]; then
    ACTIVE_REAL_PATH=$(realpath "$ACTIVE_PATH" 2>/dev/null || echo "$ACTIVE_PATH")
fi

ACTIVE_VER=""
if [ -n "$ACTIVE_PATH" ]; then
    ACTIVE_VER=$("$ACTIVE_PATH" --version 2>&1 | head -n 1)
fi

echo "Active Python executable: ${ACTIVE_REAL_PATH:-None} ($ACTIVE_VER)"
echo "Scanning installed Python versions..."

declare -A SEEN

POSSIBLE_PATTERNS=(
    "/usr/bin/python3*"
    "/usr/local/bin/python3*"
    "/bin/python3*"
    "$HOME/.pyenv/shims/python3*"
    "$HOME/.local/bin/python3*"
)

# Expand uv python pattern
UV_PYTHONS=("$HOME"/.local/share/uv/python/*/bin/python3*)

ALL_PATTERNS=("${POSSIBLE_PATTERNS[@]}" "${UV_PYTHONS[@]}")

for p in "${ALL_PATTERNS[@]}"; do
    for bin_path in $p; do
        if [ -f "$bin_path" ] && [ -x "$bin_path" ]; then
            case "$bin_path" in
                *-config|*-m) continue ;;
            esac

            real_p=$(realpath "$bin_path" 2>/dev/null || echo "$bin_path")
            if [ -z "${SEEN["$real_p"]}" ]; then
                SEEN["$real_p"]=1
                ver_str=$("$bin_path" --version 2>&1 | head -n 1)
                if [[ "$ver_str" == Python* ]]; then
                    is_def=0
                    if [ "$real_p" = "$ACTIVE_REAL_PATH" ] || [ "$bin_path" = "$ACTIVE_PATH" ]; then
                        is_def=1
                    fi
                    echo "Found Python version: $ver_str ($real_p)"
                    echo "RESULT:$ver_str|$real_p|$is_def"
                fi
            fi
        fi
    done
done

echo "Python version discovery complete."
