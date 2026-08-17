#!/bin/bash

# Default search directory is home directory ($HOME)
SEARCH_DIR="${1:-$HOME}"


echo "Searching for bench directories in: $SEARCH_DIR..."

BENCH_CLI_VER=$(bench --version 2>/dev/null || echo "Unknown")

for dir in "$SEARCH_DIR"/*; do
    if [ -d "$dir" ] && [ -d "$dir/sites" ] && [ -d "$dir/apps/frappe" ]; then
        bench_name=$(basename "$dir")
        
        # Frappe Version
        ver_file="$dir/apps/frappe/frappe/__init__.py"
        f_ver="Unknown"
        if [ -f "$ver_file" ]; then
            f_ver=$(grep -oE "__version__ = [\"'\"][^\"'\"]+" "$ver_file" | cut -d"\"" -f2 | cut -d"'" -f2)
            [ -z "$f_ver" ] && f_ver="v16.x"
        fi
        
        # Python Version
        py_bin="$dir/env/bin/python"
        py_ver="Unknown"
        if [ -x "$py_bin" ]; then
            py_ver=$("$py_bin" --version 2>&1 | head -n 1)
        fi
        
        # Node Version
        n_ver=$(node -v 2>/dev/null || echo "Unknown")
        
        # Status
        status="Stopped"
        if pgrep -f "$dir" >/dev/null 2>&1 || pgrep -f "$bench_name" >/dev/null 2>&1; then
            status="Running"
        fi

        
        echo "Found Bench: $bench_name (Frappe: $f_ver, Python: $py_ver, Status: $status)"
        echo "RESULT:$bench_name|$dir|$f_ver|$py_ver|$n_ver|$status|$BENCH_CLI_VER"
    fi
done

echo "Bench list discovery complete."
