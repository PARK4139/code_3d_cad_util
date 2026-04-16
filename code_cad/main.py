from __future__ import annotations

import hashlib
import json
import os
import socket
import subprocess
import time
from pathlib import Path


# TODO : _________________________________________________ 0. PATHS / CONFIG

D_PROJECT = Path(__file__).resolve().parent.parent
D_ARTIFACTS = D_PROJECT / "artifacts"
D_RUNTIME = D_PROJECT / "blender_control_via_python_api" / "runtime"

F_SERVO_BRACKET_STL = D_ARTIFACTS / "servo_bracket.stl"
F_SERVO_BRACKET_STEP = D_ARTIFACTS / "servo_bracket.step"
F_RELOAD_COMMAND = D_RUNTIME / "reload_command.json"
F_RELOADER_HEARTBEAT = D_RUNTIME / "blend_session_reloader_heartbeat.json"
F_BLEND_SESSION_RELOADER = D_PROJECT / "blender_control_via_python_api" / "blend_session_reloader.py"

# Change this if your Blender executable path is different.
F_BLENDER_EXE = Path(r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe")

# Socket configuration
SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 65432

# Optional: if you want Blender to open a specific .blend file on first launch.
F_STARTUP_BLEND = D_PROJECT / "blender_control_via_python_api" / "startup_scene.blend"

PREVIEW_OBJECT_NAME = "servo_bracket_preview"


# TODO : _________________________________________________ 1. HELPERS

def ensure_directory_created(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def trigger_socket_reload(stl_path: Path, object_name: str) -> bool:
    """Attempts to send a reload command over TCP. Returns True if successful."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            s.connect((SOCKET_HOST, SOCKET_PORT))
            payload = {
                "command": "reload_stl",
                "stl_path": str(stl_path.resolve()),
                "object_name": object_name
            }
            s.sendall(json.dumps(payload).encode('utf-8'))
        return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False


def is_reloader_heartbeat_alive() -> bool:
    if not F_RELOADER_HEARTBEAT.exists():
        print("reloader alive: False")
        return False
    try:
        data = json.loads(F_RELOADER_HEARTBEAT.read_text(encoding="utf-8"))
        epoch = data.get("epoch_seconds", 0)
        age = time.time() - epoch
        alive = age <= 3.0
        print("reloader heartbeat age:", age)
        print("reloader alive:", alive)
        return alive
    except Exception:
        print("reloader alive: False")
        return False


def get_file_sha256(file_path: Path) -> str:
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file_obj:
        while True:
            chunk = file_obj.read(1024 * 1024)
            if not chunk:
                break
            sha256.update(chunk)

    return sha256.hexdigest()


def write_reload_command(
    stl_path: Path,
    object_name: str,
) -> None:
    ensure_directory_created(path=D_RUNTIME)

    payload = {
        "command_type": "reload_stl",
        "stl_path": str(stl_path.resolve()),
        "object_name": object_name,
        "stl_sha256": get_file_sha256(file_path=stl_path),
        "stl_mtime_ns": stl_path.stat().st_mtime_ns,
    }

    F_RELOAD_COMMAND.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"reload command written: {F_RELOAD_COMMAND}")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def is_windows() -> bool:
    return os.name == "nt"


def is_blender_running() -> bool:
    if is_windows():
        result = subprocess.run(
            args=["tasklist", "/FI", "IMAGENAME eq blender.exe"],
            capture_output=True,
            text=True,
            check=False,
        )
        stdout_lower = result.stdout.lower()
        return "blender.exe" in stdout_lower

    result = subprocess.run(
        args=["pgrep", "-f", "blender"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and bool(result.stdout.strip())


def build_blender_launch_command() -> list[str]:
    if not F_BLENDER_EXE.exists():
        raise FileNotFoundError(f"Blender executable not found: {F_BLENDER_EXE}")

    if not F_BLEND_SESSION_RELOADER.exists():
        raise FileNotFoundError(f"Reloader script not found: {F_BLEND_SESSION_RELOADER}")

    command = [str(F_BLENDER_EXE)]

    if F_STARTUP_BLEND.exists():
        command.append(str(F_STARTUP_BLEND))

    command.extend(
        [
            "--python",
            str(F_BLEND_SESSION_RELOADER),
        ]
    )

    return command


def ensure_blender_started_if_needed() -> None:
    if is_blender_running():
        print("blender already running: skip auto launch")
    blender_running = is_blender_running()
    heartbeat_alive = is_reloader_heartbeat_alive()

    print("blender_running:", blender_running)
    print("heartbeat_alive:", heartbeat_alive)

    if blender_running and heartbeat_alive:
        print("blender running with active reloader: skip auto launch")
        return

    print("launching blender (no active reloader detected)")
    command = build_blender_launch_command()

    subprocess.Popen(
        args=command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(D_PROJECT),
    )

    print("blender auto launch requested")
    print(f"blender exe: {F_BLENDER_EXE}")
    print(f"reloader script: {F_BLEND_SESSION_RELOADER}")

    # Small delay so the first session can start before the next manual run.
    time.sleep(1.0)


# TODO : _________________________________________________ 2. CAD EXPORT

def export_servo_bracket() -> None:
    ensure_directory_created(path=D_ARTIFACTS)

    from build123d import export_step, export_stl
    from parts.servo_bracket import build_servo_bracket

    part = build_servo_bracket()

    export_stl(
        to_export=part,
        file_path=str(F_SERVO_BRACKET_STL),
    )
    export_step(
        to_export=part,
        file_path=str(F_SERVO_BRACKET_STEP),
    )

    print(f"stl exported:  {F_SERVO_BRACKET_STL}")
    print(f"step exported: {F_SERVO_BRACKET_STEP}")


# TODO : _________________________________________________ 3. MAIN

def main() -> None:
    export_servo_bracket()

    if trigger_socket_reload(F_SERVO_BRACKET_STL, PREVIEW_OBJECT_NAME):
        print("instant reload triggered via socket")
    else:
        print("socket server not reached; falling back to file + auto-launch")
        write_reload_command(F_SERVO_BRACKET_STL, PREVIEW_OBJECT_NAME)
        ensure_blender_started_if_needed()

    print("done: CAD process completed")


if __name__ == "__main__":
    main()