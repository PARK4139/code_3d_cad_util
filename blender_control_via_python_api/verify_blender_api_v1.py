import bpy


def main():
    print("--- verify_blender_api_v1: START ---")

    collection_name = "VERIFY_BLENDER_API"

    # 1. Ensure collection exists
    collection = bpy.data.collections.get(collection_name)
    if collection is None:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)

    # 2. Clear only objects inside this specific collection
    print(f"Cleaning collection: {collection_name}")
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # 3. Create verification cube
    bpy.ops.mesh.primitive_cube_add(
        size=2.0,
        location=(0.0, 0.0, 0.0),
    )
    
    obj = bpy.context.active_object
    obj.name = "verify_cube"

    # 4. Ensure object is only in the target collection
    for coll in list(obj.users_collection):
        if coll != collection:
            coll.objects.unlink(obj)
            
    if obj.name not in collection.objects:
        collection.objects.link(obj)

    print(f"Successfully created: {obj.name}")
    print("--- verify_blender_api_v1: END ---")

if __name__ == "__main__":
    main()