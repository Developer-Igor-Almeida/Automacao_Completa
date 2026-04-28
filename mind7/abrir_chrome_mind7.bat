@echo off
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
--remote-debugging-port=9222 ^
--user-data-dir="%~dp0perfil_chrome" ^
--start-maximized ^
https://mind-7.org/painel/consultas/placa/