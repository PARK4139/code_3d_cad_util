@echo off
setlocal

set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
set "SCRIPT_FILE=%%USERPROFILE%%\Downloads\code_3d_cad_util\blender_control_via_python_api\poc_switchbot_scene.py"

"%BLENDER_EXE%" --python "%SCRIPT_FILE%"

endlocal