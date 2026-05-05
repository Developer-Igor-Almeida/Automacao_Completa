@echo off
title Automacao Completa

cd /d "%~dp0"

powershell -WindowStyle Hidden -Command "Start-Process py -ArgumentList '-m streamlit run app.py --server.port 8501 --server.headless true' -WindowStyle Hidden"

timeout /t 4 > nul

start "" http://automacaotracersmind7.local:8501

exit