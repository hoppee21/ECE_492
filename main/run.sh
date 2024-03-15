#!/bin/bash

cleanup(){
	echo "caught SIGINT signal"
	kill $MAINHUB_PID $DISPLAY_PID
	exit
}

python Mainhub.py &
MAINHUB_PID=$!

python display.py &
DISPLAY_PID=$!

trap 'cleanup' SIGINT

wait $MAINHUB_PID
wait $DISPLAY_PID