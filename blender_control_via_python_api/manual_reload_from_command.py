from pathlib import Path
import json
import traceback

import bpy


# TODO : _________________________________________________ 0. PATHS / CONFIG

D_PROJECT = Path(r"C:\Users\USER\Downloads\code_3d_cad_util")
F_COMMAND = (
    D_PROJECT
    / "blender_control_via_python_api"
    / "runtime"
    / "reload_command.json"
)

DEFAULT_OBJECT_NAME = "servo_bracket_preview"
PREVIEW_COLLECTION_NAME = "preview_runtime"


# TODO : _________________________________________________ 1. HELPERS

def ensure_command_payload_loaded():
    if not F_COMMAND.exists():
        raise FileNotFoundError(f"Command file not found: {F_COMMAND}")

    payload = json.loads(F_COMMAND.read_text(encoding="utf-8"))
    return payload


def ensure_preview_collection():
    collection = bpy.data.collections.get(PREVIEW_COLLECTION_NAME)
    if collection is not None:
        return collection

    collection = bpy.data.collections.new(PREVIEW_COLLECTION_NAME)
    bpy.context.scene.collection.children.link(collection)
    return collection


def ensure_object_deleted(object_name):
    old_object = bpy.data.objects.get(object_name)
    old_matrix_world = None
    old_mesh = None

    if old_object is None:
        return old_matrix_world

    old_matrix_world = old_object.matrix_world.copy()
    old_mesh = old_object.data if old_object.type == "MESH" else None

    bpy.data.objects.remove(old_object, do_unlink=True)

    if old_mesh is not None and old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh, do_unlink=True)

    return old_matrix_world


def ensure_stl_imported(stl_path):
    bpy.ops.object.select_all(action="DESELECT")

    before_names = {obj.name for obj in bpy.data.objects}

    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(filepath=str(stl_path))
    elif hasattr(bpy.ops.import_mesh, "stl"):
        bpy.ops.import_mesh.stl(filepath=str(stl_path))
    else:
        raise RuntimeError("No STL import operator found.")

    imported_objects = [
        obj
        for obj in bpy.data.objects
        if obj.name not in before_names and obj.type == "MESH"
    ]

    if imported_objects:
        return imported_objects[0]

    selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
    if selected_objects:
        return selected_objects[0]

    raise RuntimeError(f"Failed to import STL: {stl_path}")


def ensure_object_moved_to_collection(obj, target_collection):
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)

    if obj.name not in target_collection.objects:
        target_collection.objects.link(obj)


def ensure_object_renamed(obj, object_name):
    obj.name = object_name

    if obj.data is not None:
        obj.data.name = f"{object_name}_mesh"


def ensure_object_selected(obj):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)


# TODO : _________________________________________________ 2. CORE

def ensure_preview_reloaded_from_command():
    payload = ensure_command_payload_loaded()

    command_type = payload.get("command_type")
    if command_type != "reload_stl":
        raise RuntimeError(f"Unsupported command_type: {command_type}")

    stl_path = Path(payload["stl_path"])
    object_name = payload.get("object_name", DEFAULT_OBJECT_NAME)

    if not stl_path.exists():
        raise FileNotFoundError(f"STL file not found: {stl_path}")

    print("manual reload start")
    print(f"command_file = {F_COMMAND}")
    print(f"stl_path = {stl_path}")
    print(f"object_name = {object_name}")
    print(f"stl_exists = {stl_path.exists()}")

    old_matrix_world = ensure_object_deleted(object_name=object_name)

    new_object = ensure_stl_imported(stl_path=stl_path)
    ensure_object_renamed(
        obj=new_object,
        object_name=object_name,
    )

    preview_collection = ensure_preview_collection()
    ensure_object_moved_to_collection(
        obj=new_object,
        target_collection=preview_collection,
    )

    if old_matrix_world is not None:
        new_object.matrix_world = old_matrix_world

    ensure_object_selected(obj=new_object)

    print("manual reload done")
    print(f"new_obj = {new_object.name}")
    print(f"verts = {len(new_object.data.vertices) if new_object.type == 'MESH' else None}")
    print(f"loc = {tuple(round(v, 4) for v in new_object.location)}")
    print(f"collections = {[c.name for c in new_object.users_collection]}")


# TODO : _________________________________________________ 3. ENTRYPOINT

def main():
    try:
        ensure_preview_reloaded_from_command()
    except Exception as exc:
        print(f"manual reload failed: {exc}")
        print(traceback.format_exc())
        raise


main()