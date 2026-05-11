@echo off
setlocal

cd /d "%~dp0.."

start "" http://localhost:8501

python -m streamlit run app.py ^
  --server.port 8501 ^
  --server.address localhost ^
  --server.headless true ^
  --server.fileWatcherType none ^
  --browser.gatherUsageStats false ^
  --global.developmentMode false