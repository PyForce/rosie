#!/bin/bash
# rosie and nginx in one container, under tini (PID 1). A stop signal reaches
# both (rosie stops the motors), and the container ends when either one dies.
set -eu

stopping=false
rosie=""
nginx=""
stop() {
    kill -TERM "$rosie" "$nginx" 2>/dev/null || true
}
trap 'stopping=true; stop' TERM INT

# your configuration if you mounted one, else the image's
config=/config/config.ini
[ -f "$config" ] || config=/etc/rosie/config.ini

rosie --config "$config" start &
rosie=$!
nginx -e stderr -g "daemon off;" &
nginx=$!

# wait returns when either one ends, or on a signal (after the trap ran)
status=0
wait -n "$rosie" "$nginx" || status=$?
stop
wait || true
# asked to stop: a clean exit; one of them died: its error, for --restart on-failure
if $stopping; then exit 0; fi
exit $(( status == 0 ? 1 : status ))
