#!/data/data/com.termux/files/usr/bin/bash
cd /data/data/com.termux/files/home/jobscout
python main.py notify --category all --min-score 8 >> notify_job.log 2>&1
