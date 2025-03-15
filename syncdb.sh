#!/bin/bash

REMOTE_HOST="192.168.0.139"
REMOTE_DB_PATH="/home/stu/tacoma_data_logger/battery.db"
LOCAL_DB_PATH="/home/stu/battery.db"
LOG_FILE="battery.log"

ping -c 1 "$REMOTE_HOST" &>/dev/null

if [ $? -eq 0 ]; then
  echo "$(date): tacoma detected, syncing db" >> $LOG_FILE
  
  rsync -avz --delete "$REMOTE_HOST:$REMOTE_DB_PATH" "$LOCAL_DB_PATH" >> "$LOG_FILE" 2>&1
  
  if [ $? -eq 0 ]; then
    echo "$(date): Database sync successful." >> "$LOG_FILE"
  else
    echo "$(date): Database sync failed." >> "$LOG_FILE"
  fi

else
  echo "$(date): Remote device $REMOTE_HOST is not reachable." >> "$LOG_FILE"
fi
    

