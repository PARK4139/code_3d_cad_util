import socket
import threading
import json
import bpy

# Shared state between socket thread and Blender main thread
COMMAND_QUEUE = []
SERVER_PORT = 65432
RELOAD_CALLBACK = None

def socket_listener():
    """Threaded background listener for reload commands."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(('127.0.0.1', SERVER_PORT))
        except OSError as e:
            print(f"Socket server bind failed (port {SERVER_PORT} likely in use): {e}")
            return
            
        s.listen(1)
        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(4096)
                    if not data:
                        continue
                    payload = json.loads(data.decode('utf-8'))
                    if payload.get("command") == "reload_stl":
                        COMMAND_QUEUE.append(payload)
            except Exception as e:
                print(f"Socket server error: {e}")

def process_queue_timer():
    """Blender timer checking the command queue in the main thread."""
    global RELOAD_CALLBACK
    
    while COMMAND_QUEUE:
        cmd = COMMAND_QUEUE.pop(0)
        stl_path = cmd.get("stl_path")
        obj_name = cmd.get("object_name")
        
        if RELOAD_CALLBACK and stl_path:
            try:
                print(f"Socket trigger: reloading {obj_name}")
                RELOAD_CALLBACK(stl_path, obj_name)
            except Exception as e:
                print(f"Socket-triggered reload failed: {e}")
                
    return 0.1  # Check again in 100ms

def start_server(callback):
    """Initializes the server and registers the Blender timer."""
    global RELOAD_CALLBACK
    RELOAD_CALLBACK = callback
    
    # Start socket thread
    t = threading.Thread(target=socket_listener, daemon=True)
    t.start()
    
    # Register Blender main-thread consumer
    bpy.app.timers.register(process_queue_timer)
    print(f"Socket server thread started on port {SERVER_PORT}")