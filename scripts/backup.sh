#!/bin/bash

DATE=$(date +%F_%H-%M)

pg_dump \
-U mrbot \
-h postgres \
mrbot > /backups/mrbot_$DATE.sql