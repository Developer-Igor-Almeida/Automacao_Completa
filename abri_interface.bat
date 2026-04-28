@echo off
title Automacao Completa

cd /d "%~dp0"

py -m streamlit run app.py

pause