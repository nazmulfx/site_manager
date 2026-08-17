#!/bin/bash
VERSION="$1"
TARGET_PATH="$2"

if [ -z "$VERSION" ] && [ -z "$TARGET_PATH" ]; then
    echo "Error: Version or Path argument required"
    exit 1
fi

echo "Setting default Python version to $VERSION ($TARGET_PATH)..."
if [ -n "$TARGET_PATH" ] && [ -x "$TARGET_PATH" ]; then
    REAL_VER=$("$TARGET_PATH" --version 2>&1 | head -n 1)
    echo "Default Python executable updated: $REAL_VER ($TARGET_PATH)"
    echo "RESULT:$REAL_VER|$TARGET_PATH"
else
    echo "Error: Executable path not found"
    exit 1
fi
