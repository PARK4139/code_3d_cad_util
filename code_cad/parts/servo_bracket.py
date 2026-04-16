from build123d import BuildPart, BuildSketch, Circle, Rectangle, Locations, extrude, export_step, export_stl


def build_servo_bracket( 
    bracket_width=40.0,
    # bracket_depth=20.0,
    bracket_depth=22.0,
    bracket_thickness=3.0,
    hole_radius=2.0,
    hole_offset_x=14.0,
):
    with BuildPart() as part:
        with BuildSketch():
            Rectangle(bracket_width, bracket_depth)
        extrude(amount=bracket_thickness)

        top_face = part.faces().sort_by()[-1]

        with BuildSketch(top_face):
            with Locations(( -hole_offset_x / 2.0, 0 ), ( hole_offset_x / 2.0, 0 )):
                Circle(radius=hole_radius)
        extrude(amount=-bracket_thickness)

    return part.part


def export_servo_bracket(
    output_step_path="artifacts/servo_bracket.step",
    output_stl_path="artifacts/servo_bracket.stl",
):
    part = build_servo_bracket()
    export_step(to_export=part, file_path=output_step_path)
    export_stl(to_export=part, file_path=output_stl_path)
    return part
