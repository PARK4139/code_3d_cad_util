@echo off
setlocal

set "D_ROOT=%~dp0"
if "%D_ROOT:~-1%"=="\" set "D_ROOT=%D_ROOT:~0,-1%"

set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
set "BLEND_FILE_PATH="

cd /d "%D_ROOT%\code_cad"
python main.py

endlocal