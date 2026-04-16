@echo off
setlocal ENABLEDELAYEDEXPANSION

REM TODO : _________________________________________________ 0. SAFETY FIRST
set "TITLE=ensure_build123d_servo_bracket_scaffolded"
title %TITLE%

echo [INFO] start

REM TODO : _________________________________________________ 1. PATHS
set "D_ROOT=%~dp0"
if "%D_ROOT:~-1%"=="\" set "D_ROOT=%D_ROOT:~0,-1%"

set "D_PARTS=%D_ROOT%\parts"
set "D_ASSEMBLIES=%D_ROOT%\assemblies"
set "D_ARTIFACTS=%D_ROOT%\artifacts"
set "F_MAIN=%D_ROOT%\main.py"
set "F_SERVO_BRACKET=%D_PARTS%\servo_bracket.py"

REM TODO : _________________________________________________ 2. TIMESTAMP
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "TS=%%I"
if not defined TS (
    echo [ERROR] failed to get timestamp
    exit /b 1
)

echo [INFO] TS=%TS%
echo [INFO] D_ROOT=%D_ROOT%
echo [INFO] D_PARTS=%D_PARTS%
echo [INFO] D_ASSEMBLIES=%D_ASSEMBLIES%
echo [INFO] D_ARTIFACTS=%D_ARTIFACTS%
echo [INFO] F_MAIN=%F_MAIN%
echo [INFO] F_SERVO_BRACKET=%F_SERVO_BRACKET%

REM TODO : _________________________________________________ 3. ENSURE DIRECTORIES
if not exist "%D_PARTS%" (
    mkdir "%D_PARTS%"
    echo [INFO] created: %D_PARTS%
) else (
    echo [INFO] already exists: %D_PARTS%
)

if not exist "%D_ASSEMBLIES%" (
    mkdir "%D_ASSEMBLIES%"
    echo [INFO] created: %D_ASSEMBLIES%
) else (
    echo [INFO] already exists: %D_ASSEMBLIES%
)

if not exist "%D_ARTIFACTS%" (
    mkdir "%D_ARTIFACTS%"
    echo [INFO] created: %D_ARTIFACTS%
) else (
    echo [INFO] already exists: %D_ARTIFACTS%
)

REM TODO : _________________________________________________ 4. BACKUP EXISTING FILES
if exist "%F_MAIN%" (
    copy /Y "%F_MAIN%" "%F_MAIN%.backup_%TS%" >nul
    echo [INFO] backup created: %F_MAIN%.backup_%TS%
) else (
    echo [INFO] no existing main.py found
)

if exist "%F_SERVO_BRACKET%" (
    copy /Y "%F_SERVO_BRACKET%" "%F_SERVO_BRACKET%.backup_%TS%" >nul
    echo [INFO] backup created: %F_SERVO_BRACKET%.backup_%TS%
) else (
    echo [INFO] no existing servo_bracket.py found
)

REM TODO : _________________________________________________ 5. WRITE parts\servo_bracket.py
(
    echo from build123d import BuildPart, BuildSketch, Circle, Rectangle, Locations, extrude, export_step, export_stl
    echo.
    echo.
    echo def build_servo_bracket^( 
    echo     bracket_width=40.0,
    echo     bracket_depth=20.0,
    echo     bracket_thickness=3.0,
    echo     hole_radius=2.0,
    echo     hole_offset_x=14.0,
    echo ^):
    echo     with BuildPart^(^) as part:
    echo         with BuildSketch^(^):
    echo             Rectangle^(bracket_width, bracket_depth^)
    echo         extrude^(amount=bracket_thickness^)
    echo.
    echo         top_face = part.faces^(^).sort_by^(^)[-1]
    echo.
    echo         with BuildSketch^(top_face^):
    echo             with Locations^(( -hole_offset_x / 2.0, 0 ^), ^( hole_offset_x / 2.0, 0 ^)^):
    echo                 Circle^(radius=hole_radius^)
    echo         extrude^(amount=-bracket_thickness^)
    echo.
    echo     return part.part
    echo.
    echo.
    echo def export_servo_bracket^(
    echo     output_step_path="artifacts/servo_bracket.step",
    echo     output_stl_path="artifacts/servo_bracket.stl",
    echo ^):
    echo     part = build_servo_bracket^(^)
    echo     export_step^(to_export=part, file_path=output_step_path^)
    echo     export_stl^(to_export=part, file_path=output_stl_path^)
    echo     return part
) > "%F_SERVO_BRACKET%"

if errorlevel 1 (
    echo [ERROR] failed to write: %F_SERVO_BRACKET%
    exit /b 1
) else (
    echo [INFO] wrote: %F_SERVO_BRACKET%
)

REM TODO : _________________________________________________ 6. WRITE main.py
(
    echo from pathlib import Path
    echo.
    echo from parts.servo_bracket import export_servo_bracket
    echo.
    echo.
    echo def main^(^):
    echo     print^("main start"^)
    echo.
    echo     d_artifacts = Path^(__file__^).resolve^(^).parent / "artifacts"
    echo     d_artifacts.mkdir^(parents=True, exist_ok=True^)
    echo.
    echo     export_servo_bracket^(
    echo         output_step_path=str^(d_artifacts / "servo_bracket.step"^),
    echo         output_stl_path=str^(d_artifacts / "servo_bracket.stl"^),
    echo     ^)
    echo.
    echo     print^("export done"^)
    echo     print^("main end"^)
    echo.
    echo.
    echo if __name__ == "__main__":
    echo     main^(^)
) > "%F_MAIN%"

if errorlevel 1 (
    echo [ERROR] failed to write: %F_MAIN%
    exit /b 1
) else (
    echo [INFO] wrote: %F_MAIN%
)

REM TODO : _________________________________________________ 7. ENSURE PACKAGE MARKERS
if not exist "%D_PARTS%\__init__.py" (
    type nul > "%D_PARTS%\__init__.py"
    echo [INFO] created: %D_PARTS%\__init__.py
) else (
    echo [INFO] already exists: %D_PARTS%\__init__.py
)

if not exist "%D_ASSEMBLIES%\__init__.py" (
    type nul > "%D_ASSEMBLIES%\__init__.py"
    echo [INFO] created: %D_ASSEMBLIES%\__init__.py
) else (
    echo [INFO] already exists: %D_ASSEMBLIES%\__init__.py
)

REM TODO : _________________________________________________ 8. RUN
echo [INFO] running python main.py
python "%F_MAIN%"
if errorlevel 1 (
    echo [ERROR] python main.py failed
    exit /b 1
)

echo [INFO] done
echo [INFO] expected outputs:
echo         %D_ARTIFACTS%\servo_bracket.step
echo         %D_ARTIFACTS%\servo_bracket.stl

endlocal
exit /b 0