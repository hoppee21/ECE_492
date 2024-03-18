#!/bin/bash

cleanup(){
	echo "caught SIGINT signal"
	kill "$MAINHUB_PID" "$DISPLAY_PID" "$RESCHEDULE_PID"
	exit
}

python Mainhub.py &
MAINHUB_PID=$!

python display.py &
DISPLAY_PID=$!

python reschedule.py &
RESCHEDULE_PID=$!

trap 'cleanup' SIGINT

wait $MAINHUB_PID
wait $DISPLAY_PID
wait $RESCHEDULE_PID