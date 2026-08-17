#!/bin/bash

# Source NVM if available
if [ -s "$HOME/.nvm/nvm.sh" ]; then
    source "$HOME/.nvm/nvm.sh"
fi

ACTIVE_VER=$(node -v 2>/dev/null || echo "")
ACTIVE_PATH=$(which node 2>/dev/null || echo "")

echo "Active Node version: ${ACTIVE_VER:-None} (${ACTIVE_PATH:-None})"
echo "Scanning installed Node versions..."

declare -A SEEN

# 1. Scan NVM versions directory
NVM_DIR="$HOME/.nvm/versions/node"
if [ -d "$NVM_DIR" ]; then
    for dir in "$NVM_DIR"/*; do
        if [ -d "$dir" ] && [ -x "$dir/bin/node" ]; then
            ver=$(basename "$dir")
            [[ "$ver" != v* ]] && ver="v$ver"
            bin_path="$dir/bin/node"
            is_def=0
            if [ "$ver" = "$ACTIVE_VER" ] || [ "$bin_path" = "$ACTIVE_PATH" ]; then
                is_def=1
            fi
            SEEN["$ver"]=1
            echo "Found NVM version: $ver ($bin_path)"
            echo "RESULT:$ver|$bin_path|$is_def"
        fi
    done
fi

# 2. Check common system paths
for sys_bin in /usr/bin/node /usr/local/bin/node /bin/node; do
    if [ -x "$sys_bin" ]; then
        real_bin=$(realpath "$sys_bin" 2>/dev/null || echo "$sys_bin")
        ver=$("$sys_bin" -v 2>/dev/null || echo "")
        if [ -n "$ver" ]; then
            [[ "$ver" != v* ]] && ver="v$ver"
            if [ -z "${SEEN["$ver"]}" ]; then
                SEEN["$ver"]=1
                is_def=0
                if [ "$ver" = "$ACTIVE_VER" ] || [ "$real_bin" = "$ACTIVE_PATH" ]; then
                    is_def=1
                fi
                echo "Found system version: $ver ($real_bin)"
                echo "RESULT:$ver|$real_bin|$is_def"
            fi
        fi
    fi
done

echo "Node version discovery complete."

