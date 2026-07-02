#!/bin/bash
# THE WOODSHED — double-click to launch.
# Force-restarts the local server so you ALWAYS get the current code (an old or hung
# server left on the port was making reloads crawl). Serves this folder at
# http://localhost:8420 and opens your browser. Requests are logged to the file below.
cd "$(dirname "$0")"
PORT=8420
LOG="/tmp/woodshed-$PORT.log"

# Kill whatever is holding the port (stale / single-threaded / hung server), then start fresh.
lsof -ti tcp:$PORT 2>/dev/null | xargs kill -9 2>/dev/null
sleep 0.5
nohup python3 "$(dirname "$0")/woodshed_server.py" $PORT >"$LOG" 2>&1 &
sleep 1
echo "Woodshed server restarted on http://localhost:$PORT  (log: $LOG)"
open "http://localhost:$PORT"
exit 0
