@echo off
rem Gera o executavel (dist\ConversorHEIC) e, se o Inno Setup estiver
rem instalado, o instalador (dist\ConversorHEIC-Setup-<versao>.exe).
rem Uso: build_windows.bat [versao]     ex.: build_windows.bat 1.2.0
setlocal
set VERSAO=%~1
if "%VERSAO%"=="" set VERSAO=1.0.0

python -m pip install --upgrade pip || goto :erro
python -m pip install -r requirements.txt pyinstaller || goto :erro

python -m PyInstaller --noconfirm --clean --windowed ^
  --name ConversorHEIC --icon assets\icon.ico ^
  --add-data "assets;assets" ^
  --collect-all pillow_heif --collect-all customtkinter --collect-all av ^
  --hidden-import PIL._tkinter_finder ^
  app.py || goto :erro

set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
  echo.
  echo Inno Setup 6 nao encontrado: gerado apenas dist\ConversorHEIC\ConversorHEIC.exe
  echo Para gerar o instalador, instale em https://jrsoftware.org/isdl.php
  goto :fim
)
%ISCC% /DMyAppVersion=%VERSAO% installer\ConversorHEIC.iss || goto :erro
echo.
echo Instalador gerado em dist\ConversorHEIC-Setup-%VERSAO%.exe
goto :fim

:erro
echo.
echo *** Falha na geracao. Veja as mensagens acima. ***
exit /b 1

:fim
endlocal
