from pathlib import Path
import json
import time
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
F_HEARTBEAT = (
    D_PROJECT
    / "blender_control_via_python_api"
    / "runtime"
    / "blend_session_reloader_heartbeat.json"
)

DEFAULT_OBJECT_NAME = "servo_bracket_preview"
PREVIEW_COLLECTION_NAME = "preview_runtime"

POLL_INTERVAL_SECONDS = 0.5

LAST_SIGNATURE = None
TIMER_REGISTERED = False


# TODO : _________________________________________________ 1. HELPERS

def load_command():
    if not F_COMMAND.exists():
        return None

    try:
        return json.loads(F_COMMAND.read_text(encoding="utf-8"))
    except Exception as e:
        print("command read failed:", e)
        return None


def update_heartbeat():
    F_HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "epoch_seconds": time.time(),
        "command_file": str(F_COMMAND.resolve()),
    }
    try:
        F_HEARTBEAT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception as e:
        print("heartbeat write failed:", e)


def build_signature(payload):
    return (
        payload.get("command_type"),
        payload.get("stl_path"),
        payload.get("object_name"),
        payload.get("stl_sha256"),
        payload.get("stl_mtime_ns"),
    )


def ensure_preview_collection():
    col = bpy.data.collections.get(PREVIEW_COLLECTION_NAME)
    if col:
        return col

    col = bpy.data.collections.new(PREVIEW_COLLECTION_NAME)
    bpy.context.scene.collection.children.link(col)
    return col


def delete_object(name):
    obj = bpy.data.objects.get(name)
    if not obj:
        return None

    matrix = obj.matrix_world.copy()
    mesh = obj.data if obj.type == "MESH" else None

    bpy.data.objects.remove(obj, do_unlink=True)

    if mesh and mesh.users == 0:
        bpy.data.meshes.remove(mesh, do_unlink=True)

    return matrix


def import_stl(path):
    bpy.ops.object.select_all(action="DESELECT")

    before = {o.name for o in bpy.data.objects}

    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(filepath=str(path))
    elif hasattr(bpy.ops.import_mesh, "stl"):
        bpy.ops.import_mesh.stl(filepath=str(path))
    else:
        raise RuntimeError("STL import operator missing")

    after = [o for o in bpy.data.objects if o.name not in before and o.type == "MESH"]
    if after:
        return after[0]

    sel = [o for o in bpy.context.selected_objects if o.type == "MESH"]
    if sel:
        return sel[0]

    raise RuntimeError("STL import failed")


def move_to_collection(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)

    if obj.name not in col.objects:
        col.objects.link(obj)


def rename(obj, name):
    obj.name = name
    if obj.data:
        obj.data.name = f"{name}_mesh"


def select(obj):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)


# TODO : _________________________________________________ 2. CORE

def reload_stl(stl_path_str, object_name):
    stl_path = Path(stl_path_str)
    if not stl_path.exists():
        print("stl not found:", stl_path)
        return

    old_matrix = delete_object(object_name)
    new_obj = import_stl(stl_path)
    rename(new_obj, object_name)
    col = ensure_preview_collection()
    move_to_collection(new_obj, col)
    if old_matrix is not None:
        new_obj.matrix_world = old_matrix
    select(new_obj)


def reload_if_needed():
    global LAST_SIGNATURE

    payload = load_command()
    if not payload:
        return

    if payload.get("command_type") != "reload_stl":
        return

    sig = build_signature(payload)
    if sig == LAST_SIGNATURE:
        return

    stl_path = Path(payload["stl_path"])
    name = payload.get("object_name", DEFAULT_OBJECT_NAME)

    print("reload start:", stl_path)
    try:
        reload_stl(stl_path, name)
    except Exception as e:
        print("reload failed:", e)
        traceback.print_exc()
        return

    LAST_SIGNATURE = sig

    print("reload done:", name)


# TODO : _________________________________________________ 3. TIMER

def timer():
    try:
        update_heartbeat()
    except Exception as e:
        print("timer error:", e)
        print(traceback.format_exc())

    return POLL_INTERVAL_SECONDS


def start():
    global TIMER_REGISTERED

    if TIMER_REGISTERED:
        print("timer already running")
        return

    try:
        from . import blend_socket_server
        blend_socket_server.start_server(reload_stl)
    except Exception as e:
        print("failed to start socket server:", e)

    update_heartbeat()
    bpy.app.timers.register(
        timer,
        first_interval=0.1,
        persistent=True,
    )
    TIMER_REGISTERED = True

    print("reloader started")
    print("watching:", F_COMMAND)

    reload_if_needed()


# TODO : _________________________________________________ 4. ENTRY

start()