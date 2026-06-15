#!/bin/bash

# --- Configuration ---
URL="http://localhost:5000/apidocs/"
DB_PATHS=(
  "data/test/db_test.json"
  "static/test/product_image/"
  "static/test/product_document/"
)

# --- Pre-run Cleanup ---
# Remove database and static files defined in the array
rm -rf "${DB_PATHS[@]}"


# --- Shutdown handler ---
cleanup () {
  echo -e "\n[system] Termination signal received.Cleaning up..."
  # Kill all child prossees started by this script (inclouding Chrome and Watcher)
  pkill -P $$ 2>/dev/null || true
  # Force release port 5000 if it's still occupied
  fuser -k 5000/tcp 2>/dev/null || true
}


# Execute cleanup function on Exit, Interrupt (Ctrl+C), or Termination
trap cleanup EXIT 
trap "exit 130" INT
trap "exit 143" TERM

# --- Swagger Watcher (Background) ---
(
  # Wait until the server returns a successful response
  until curl -s "$URL" >/dev/null;do
    sleep 0.5
  done 

  echo "[watcher] Server is live. Launching Swagger UI"

  # Launch Chrome in 'app mode' (cleaner UI) with a unique temporary profile
  google-chrome \
    --app="$URL" \
    --user-data-dir="/tmp/chrome_dev_$(date +%s)" \
    --no-first-run \
    >/dev/null 2>&1 &

) &


# --- Main Execution ---
echo "[system] Starting Flask application..."
mkdir -p logs
python3 main.py > "logs/flask.log" 2>&1
