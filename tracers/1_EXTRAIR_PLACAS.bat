@echo off
title Automacao Tracers

echo ========================================
echo        AUTOMACAO TRACERS
echo ========================================

cd /d "%~dp0"

echo.
echo [1/3] Verificando ADB...
platform-tools\adb.exe devices > temp_adb.txt

type temp_adb.txt

findstr /R "device$" temp_adb.txt > nul
if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Nenhum dispositivo conectado!
    echo Verifique:
    echo - Cabo USB
    echo - Depuracao USB ativada
    echo - Emulador aberto
    pause
    del temp_adb.txt
    exit
)

del temp_adb.txt

echo.
echo [OK] Dispositivo conectado!

echo.
echo ========================================
echo Escolha o modo de execucao:
echo ========================================
echo 1 - Rodar automacao modo antigo
echo 2 - Abrir interface recomendada
echo.

set /p opcao=Digite 1 ou 2: 

if "%opcao%"=="1" goto modo_console
if "%opcao%"=="2" goto modo_interface

echo Opcao invalida!
pause
exit

:modo_console
echo.
echo [2/3] Iniciando automacao...
pause

py extrair_tracers.py

echo.
echo [3/3] FINALIZADO!
echo Verifique a pasta "saida"
pause
exit

:modo_interface
echo.
echo [2/3] Abrindo interface...
echo Aguarde abrir no navegador...

py -m streamlit run app.py

echo.
echo [3/3] Interface encerrada.
pause
exit