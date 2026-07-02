#!/bin/bash
# Stops the Woodshed local server (port 8420).
lsof -ti :8420 | xargs kill 2>/dev/null
echo "Woodshed server stopped."
exit 0
