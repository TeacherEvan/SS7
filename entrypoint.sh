#!/bin/bash
    if [ -z "$DISPLAY" ] || ! xset q &>/dev/null; then
    export DISPLAY=:99
    Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &
    sleep 2
    fi

    pulseaudio --start --exit-idle-time=-1 &

    exec "$@"
