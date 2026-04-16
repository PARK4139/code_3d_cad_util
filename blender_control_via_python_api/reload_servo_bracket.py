import sys
from pathlib import Path


def get_argument_value(flag_name):
    argv = sys.argv
    if "--" not in argv:
        return None

    user_argv = argv[argv.index("--") + 1 :]

    for index, token in enumerate(user_argv):
        if token == flag_name and index + 1 < len(user_argv):
            return user_argv[index + 1]

    return None


def delete_object_if_exists(object_name):
    import bpy

    existing_object = bpy.data.objects.get(object_name)
    if existing_object is None:
        return

    mesh_data = existing_object.data if hasattr(existing_object, "data") else None

    bpy.data.objects.remove(existing_object, do_unlink=True)

    if mesh_data is not None and mesh_data.users == 0:
        bpy.data.meshes.remove(mesh_data, do_unlink=True)


def import_stl(stl_path):
    import bpy

    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(filepath=str(stl_path))
    elif hasattr(bpy.ops.import_mesh, "stl"):
        bpy.ops.import_mesh.stl(filepath=str(stl_path))
    else:
        raise RuntimeError(
            "No STL import operator found. "
            "Install/enable the 'STL format (legacy)' Blender extension first."
        )

    selected_objects = list(bpy.context.selected_objects)
    if not selected_objects:
        raise RuntimeError(f"failed to import STL: {stl_path}")

    imported_object = selected_objects[0]
    return imported_object


def rename_object(imported_object, object_name):
    if imported_object.data is not None:
        imported_object.data.name = f"{object_name}_mesh"
    imported_object.name = object_name


def ensure_object_origin(imported_object):
    import bpy

    bpy.context.view_layer.objects.active = imported_object
    imported_object.select_set(state=True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")


def parse_inputs():
    stl_path_raw = get_argument_value(flag_name="--stl-path")
    object_name = get_argument_value(flag_name="--object-name")

    if not stl_path_raw:
        raise ValueError("--stl-path is required")

    stl_path = Path(stl_path_raw)
    if not stl_path.exists():
        raise FileNotFoundError(f"STL file not found: {stl_path}")

    if not object_name:
        object_name = "servo_bracket_preview"

    return {
        "stl_path": stl_path,
        "object_name": object_name,
    }


def main():
    import bpy

    parsed = parse_inputs()
    stl_path = parsed["stl_path"]
    object_name = parsed["object_name"]

    print(f"reload start: {stl_path}")
    print(f"object name: {object_name}")

    if bpy.context.object is not None:
        bpy.ops.object.select_all(action="DESELECT")

    delete_object_if_exists(object_name=object_name)

    imported_object = import_stl(stl_path=stl_path)
    rename_object(
        imported_object=imported_object,
        object_name=object_name,
    )
    ensure_object_origin(imported_object=imported_object)

    bpy.context.view_layer.objects.active = imported_object
    imported_object.select_set(state=True)

    print("reload done")


if __name__ == "__main__":
    main()