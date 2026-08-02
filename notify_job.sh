#!/data/data/com.termux/files/usr/bin/bash
cd /data/data/com.termux/files/home/jobscout
python -u main.py notify --category all --min-score 8 --jobs-only >> notify_job.log 2>&1
