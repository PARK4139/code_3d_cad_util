import bpy


def main():
    print("Blender Python API connected.")

    bpy.ops.mesh.primitive_cube_add(
        size=2.0,
        location=(0.0, 0.0, 0.0),
    )

    obj = bpy.context.active_object
    obj.name = "test_cube"

    print(f"Created object: {obj.name}")


if __name__ == "__main__":
    main()


