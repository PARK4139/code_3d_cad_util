import bpy


# TODO : _________________________________________________ 0. SAFETY FIRST
def ensure_collection_created(collection_name):
    collection = bpy.data.collections.get(collection_name)
    if collection is None:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def ensure_collection_cleared(collection):
    object_names = [obj.name for obj in collection.objects]
    for object_name in object_names:
        obj = bpy.data.objects.get(object_name)
        if obj is not None:
            bpy.data.objects.remove(obj, do_unlink=True)


def ensure_box_created(name, size_xyz, location_xyz, collection):
    bpy.ops.mesh.primitive_cube_add(
        size=2.0,
        location=location_xyz,
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (
        size_xyz[0] / 2.0,
        size_xyz[1] / 2.0,
        size_xyz[2] / 2.0,
    )

    for linked_collection in obj.users_collection:
        linked_collection.objects.unlink(obj)

    collection.objects.link(obj)
    return obj


def ensure_cylinder_created(name, radius, depth, location_xyz, rotation_xyz, collection):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=depth,
        location=location_xyz,
        rotation=rotation_xyz,
    )
    obj = bpy.context.active_object
    obj.name = name

    for linked_collection in obj.users_collection:
        linked_collection.objects.unlink(obj)

    collection.objects.link(obj)
    return obj


def ensure_wall_built(collection):
    return ensure_box_created(
        name="wall",
        size_xyz=(300.0, 10.0, 300.0),
        location_xyz=(0.0, -5.0, 150.0),
        collection=collection,
    )


def ensure_switch_mock_built(collection):
    plate = ensure_box_created(
        name="switch_plate",
        size_xyz=(120.0, 8.0, 70.0),
        location_xyz=(0.0, 4.0, 120.0),
        collection=collection,
    )

    rocker = ensure_box_created(
        name="switch_rocker",
        size_xyz=(55.0, 6.0, 55.0),
        location_xyz=(0.0, 11.0, 120.0),
        collection=collection,
    )

    return plate, rocker


def ensure_servo_mock_built(collection):
    body = ensure_box_created(
        name="servo_body_top",
        size_xyz=(23.0, 12.0, 29.0),
        location_xyz=(0.0, 18.0, 170.0),
        collection=collection,
    )

    horn = ensure_cylinder_created(
        name="servo_horn_top",
        radius=6.0,
        depth=2.0,
        location_xyz=(0.0, 25.0, 170.0),
        rotation_xyz=(1.5708, 0.0, 0.0),
        collection=collection,
    )

    return body, horn


def ensure_cover_mock_built(collection):
    return ensure_box_created(
        name="cover_top_variant_a",
        size_xyz=(140.0, 32.0, 120.0),
        location_xyz=(0.0, 16.0, 130.0),
        collection=collection,
    )


def main():
    collection = ensure_collection_created(
        collection_name="POC_SWITCHBOT",
    )
    ensure_collection_cleared(
        collection=collection,
    )

    ensure_wall_built(
        collection=collection,
    )
    ensure_switch_mock_built(
        collection=collection,
    )
    ensure_servo_mock_built(
        collection=collection,
    )
    ensure_cover_mock_built(
        collection=collection,
    )

    print("PoC scene generated.")


if __name__ == "__main__":
    main()