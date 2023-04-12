#!/bin/sh
# Tim H 2023
# Start-up script for launching the Python script
# intentionally not /bin/bash
# This can happen if you're trying to run an x86 built image on an 
# arm64/aarch64 machine.
# https://stackoverflow.com/a/64215125

echo "[$(date)] start_python_script.sh started"

PASSWORD_FILE="/app/password.txt"

# load the environment variables
source "/app/.env"

# DEBUG: display env variables
# printenv

# load the environment variable into a text file
# don't include a new line
# make sure that the current user has write permissions on the directory
echo -n "$VERIZON_PASSWORD" > "$PASSWORD_FILE"

# limit permissions on the file
chmod 600 "$PASSWORD_FILE"

# run the Python script using loaded environment variables
/app/soft_reboot_verizon_4g_repeater.py \
    --url="$VERIZON_URL" \
    --password-file="$PASSWORD_FILE"
    # --dry-run # if testing

echo "[$(date)] start_python_script.sh finished"
