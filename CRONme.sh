#!/bin/bash
cd ~/adx-bot

# Start the script if it had not generated any output for longer then 60 minutes
[[ $(date +%s -r adx_bot_status.txt) -lt $(date +%s --date="60 min ago") ]] && python3 adx_bot.py >> adx_bot.log.txt

# CRON example to run every hour:
# 20 * * * * ~/adx-bot/CRONme.sh
