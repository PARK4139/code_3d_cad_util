from pathlib import Path

from build123d import Axis, Box, Cylinder, Mode, export_step, export_stl


def main():
    print("main start")

    part = Box(
        length=40,
        width=20,
        height=10,
    )

    hole = Cylinder(
        radius=3,
        height=20,
        align=None,
        mode=Mode.SUBTRACT,
    )

    hole = hole.rotate(
        axis=Axis.X,
        angle=90,
    ).translate(
        vector=(0, 0, 5),
    )

    result = part + hole

    Path("artifacts").mkdir()

    export_stl(
        to_export=result,
        file_path=str(Path("artifacts") / "sample_part.stl"),
    )

    export_step(
        to_export=result,
        file_path= str(Path("artifacts") / "sample_part.step"),
    )

    print("export done")
    print("main end")


if __name__ == "__main__":
    main()