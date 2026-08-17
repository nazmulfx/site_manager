#!/bin/bash
BENCH_NAME="$1"
FRAPPE_BRANCH="${2:-version-16}"
PYTHON_PATH="$3"
NODE_VERSION="$4"
PARENT_DIR="${5:-$HOME}"


if [ -z "$BENCH_NAME" ]; then
    echo "Error: Bench name is required"
    exit 1
fi

TARGET_PATH="$PARENT_DIR/$BENCH_NAME"

if [ -d "$TARGET_PATH" ]; then
    echo "Bench folder already exists at $TARGET_PATH"
else
    echo "Initializing new bench: $BENCH_NAME in $PARENT_DIR..."
    echo "Frappe Branch: $FRAPPE_BRANCH"

    # Handle NVM Node version if specified
    if [ -n "$NODE_VERSION" ] && [ -s "$HOME/.nvm/nvm.sh" ]; then
        source "$HOME/.nvm/nvm.sh"
        nvm use "$NODE_VERSION" 2>/dev/null || nvm install "$NODE_VERSION" 2>/dev/null || true
    fi

    PY_ARG=""
    if [ -n "$PYTHON_PATH" ] && [ -x "$PYTHON_PATH" ]; then
        PY_ARG="--python $PYTHON_PATH"
    fi

    cd "$PARENT_DIR" || exit 1
    bench init "$BENCH_NAME" --frappe-branch "$FRAPPE_BRANCH" $PY_ARG
fi

# Inspect created bench
ver_file="$TARGET_PATH/apps/frappe/frappe/__init__.py"
f_ver="Unknown"
if [ -f "$ver_file" ]; then
    f_ver=$(grep -oE "__version__ = [\"'\"][^\"'\"]+" "$ver_file" | cut -d"\"" -f2 | cut -d"'" -f2)
    [ -z "$f_ver" ] && f_ver="v16.x"
fi

py_bin="$TARGET_PATH/env/bin/python"
py_ver="Unknown"
if [ -x "$py_bin" ]; then
    py_ver=$("$py_bin" --version 2>&1 | head -n 1)
fi

n_ver=$(node -v 2>/dev/null || echo "Unknown")

status="Stopped"
if pgrep -f "$TARGET_PATH" >/dev/null 2>&1 || pgrep -f "$BENCH_NAME" >/dev/null 2>&1; then
    status="Running"
fi


BENCH_CLI_VER=$(bench --version 2>/dev/null || echo "Unknown")

echo "Bench ready: $BENCH_NAME ($TARGET_PATH)"
echo "RESULT:$BENCH_NAME|$TARGET_PATH|$f_ver|$py_ver|$n_ver|$status|$BENCH_CLI_VER"

