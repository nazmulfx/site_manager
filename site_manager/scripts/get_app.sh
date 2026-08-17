#!/bin/bash
BENCH_PATH="$1"
APP_NAME="$2"
BRANCH="$3"

if [ -z "$BENCH_PATH" ] || [ ! -d "$BENCH_PATH" ]; then
    echo "Error: Invalid or missing bench directory path: $BENCH_PATH"
    exit 1
fi

if [ -z "$APP_NAME" ]; then
    echo "Error: App Name or Link is required"
    exit 1
fi

cd "$BENCH_PATH" || exit 1

# Source NVM if present
if [ -s "$HOME/.nvm/nvm.sh" ]; then
    source "$HOME/.nvm/nvm.sh"
fi

echo "Navigated to bench directory: $BENCH_PATH"
if [ -n "$BRANCH" ]; then
    echo "Executing: bench get-app $APP_NAME --branch $BRANCH"
    bench get-app "$APP_NAME" --branch "$BRANCH"
else
    echo "Executing: bench get-app $APP_NAME"
    bench get-app "$APP_NAME"
fi

EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "RESULT:SUCCESS"
else
    echo "RESULT:FAILED"
fi

exit $EXIT_CODE
