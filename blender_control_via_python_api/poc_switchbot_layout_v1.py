import bpy


def create_primitive(name, mesh_type, collection, location, scale=None, radius=None, depth=None, rotation=(0, 0, 0)):
    """Helper to create a mesh primitive and ensure it resides in the correct collection."""
    if mesh_type == "cube":
        # Use size=1.0 so that obj.scale corresponds directly to dimensions
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
        if scale:
            bpy.context.active_object.scale = scale
    elif mesh_type == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location, rotation=rotation)

    obj = bpy.context.active_object
    obj.name = name

    # Ensure object is linked to target collection and unlinked from others
    if obj.name not in collection.objects:
        collection.objects.link(obj)
    
    for coll in list(obj.users_collection):
        if coll != collection:
            coll.objects.unlink(obj)
            
    return obj


def main():
    coll_name = "POC_SWITCHBOT"

    # 1. Initialize Collection
    collection = bpy.data.collections.get(coll_name)
    if not collection:
        collection = bpy.data.collections.new(coll_name)
        bpy.context.scene.collection.children.link(collection)

    # 2. Clear only objects inside the specific collection
    print(f"Cleaning collection: {coll_name}")
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # 3. Build Layout
    print("Building switch-bot layout...")

    # Wall (Background/Mount)
    create_primitive("wall", "cube", collection, (0.0, -5.0, 150.0), scale=(300.0, 10.0, 300.0))

    # Switch Components
    create_primitive("switch_plate", "cube", collection, (0.0, 4.0, 120.0), scale=(120.0, 8.0, 70.0))
    create_primitive("switch_rocker", "cube", collection, (0.0, 11.0, 120.0), scale=(55.0, 6.0, 55.0))

    # Servo Components
    create_primitive("servo_body_top", "cube", collection, (0.0, 18.0, 170.0), scale=(23.0, 12.0, 29.0))
    
    # 90 degrees (1.5708 rad) rotation on X to align horn face
    create_primitive(
        "servo_horn_top", 
        "cylinder", 
        collection, 
        (0.0, 25.0, 170.0), 
        radius=6.0, 
        depth=2.0, 
        rotation=(1.5708, 0.0, 0.0)
    )

    # Cover/Housing
    create_primitive(
        "cover_top_variant_a", 
        "cube", 
        collection, 
        (0.0, 16.0, 130.0), 
        scale=(140.0, 32.0, 120.0)
    )

    print("PoC Layout generation complete.")


if __name__ == "__main__":
    main()