@echo off
setlocal ENABLEDELAYEDEXPANSION

set "D_ROOT=%~dp0"
if "%D_ROOT:~-1%"=="\" set "D_ROOT=%D_ROOT:~0,-1%"

set "D_BLENDER_API=%D_ROOT%\blender_control_via_python_api"
set "F_RELOAD=%D_BLENDER_API%\reload_servo_bracket.py"

if not exist "%D_BLENDER_API%" (
    mkdir "%D_BLENDER_API%"
)

(
    echo import sys
    echo from pathlib import Path
    echo.
    echo.
    echo def get_argument_value^(flag_name^):
    echo     argv = sys.argv
    echo     if "--" not in argv:
    echo         return None
    echo.
    echo     user_argv = argv[argv.index^("--"^) + 1 :]
    echo.
    echo     for index, token in enumerate^(user_argv^):
    echo         if token == flag_name and index + 1 ^< len^(user_argv^):
    echo             return user_argv[index + 1]
    echo.
    echo     return None
    echo.
    echo.
    echo def delete_object_if_exists^(object_name^):
    echo     import bpy
    echo.
    echo     existing_object = bpy.data.objects.get^(object_name^)
    echo     if existing_object is None:
    echo         return
    echo.
    echo     mesh_data = existing_object.data if hasattr^(existing_object, "data"^) else None
    echo.
    echo     bpy.data.objects.remove^(existing_object, do_unlink=True^)
    echo.
    echo     if mesh_data is not None and mesh_data.users == 0:
    echo         bpy.data.meshes.remove^(mesh_data, do_unlink=True^)
    echo.
    echo.
    echo def import_stl^(stl_path^):
    echo     import bpy
    echo.
    echo     bpy.ops.import_mesh.stl^(filepath=str^(stl_path^)^)
    echo.
    echo     selected_objects = list^(bpy.context.selected_objects^)
    echo     if not selected_objects:
    echo         raise RuntimeError^(f"failed to import STL: {stl_path}"^)
    echo.
    echo     imported_object = selected_objects[0]
    echo     return imported_object
    echo.
    echo.
    echo def rename_object^(imported_object, object_name^):
    echo     if imported_object.data is not None:
    echo         imported_object.data.name = f"{object_name}_mesh"
    echo     imported_object.name = object_name
    echo.
    echo.
    echo def ensure_object_origin^(imported_object^):
    echo     import bpy
    echo.
    echo     bpy.context.view_layer.objects.active = imported_object
    echo     imported_object.select_set^(state=True^)
    echo     bpy.ops.object.origin_set^(type="ORIGIN_GEOMETRY", center="BOUNDS"^)
    echo.
    echo.
    echo def parse_inputs^(^):
    echo     stl_path_raw = get_argument_value^(flag_name="--stl-path"^)
    echo     object_name = get_argument_value^(flag_name="--object-name"^)
    echo.
    echo     if not stl_path_raw:
    echo         raise ValueError^("--stl-path is required"^)
    echo.
    echo     stl_path = Path^(stl_path_raw^)
    echo     if not stl_path.exists^(^):
    echo         raise FileNotFoundError^(f"STL file not found: {stl_path}"^)
    echo.
    echo     if not object_name:
    echo         object_name = "servo_bracket_preview"
    echo.
    echo     return {
    echo         "stl_path": stl_path,
    echo         "object_name": object_name,
    echo     }
    echo.
    echo.
    echo def main^(^):
    echo     import bpy
    echo.
    echo     parsed = parse_inputs^(^)
    echo     stl_path = parsed["stl_path"]
    echo     object_name = parsed["object_name"]
    echo.
    echo     print^(f"reload start: {stl_path}"^)
    echo     print^(f"object name: {object_name}"^)
    echo.
    echo     if bpy.context.object is not None:
    echo         bpy.ops.object.select_all^(action="DESELECT"^)
    echo.
    echo     delete_object_if_exists^(object_name=object_name^)
    echo.
    echo     imported_object = import_stl^(stl_path=stl_path^)
    echo     rename_object^(
    echo         imported_object=imported_object,
    echo         object_name=object_name,
    echo     ^)
    echo     ensure_object_origin^(imported_object=imported_object^)
    echo.
    echo     bpy.context.view_layer.objects.active = imported_object
    echo     imported_object.select_set^(state=True^)
    echo.
    echo     print^("reload done"^)
    echo.
    echo.
    echo if __name__ == "__main__":
    echo     main^(^)
) > "%F_RELOAD%"

if errorlevel 1 (
    echo [ERROR] failed to write: %F_RELOAD%
    exit /b 1
)

echo [INFO] wrote: %F_RELOAD%
endlocal
exit /b 0