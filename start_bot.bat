@echo off
cd /d D:\MrBot_v2
:loop
python bot.py
timeout /t 5
goto loop
