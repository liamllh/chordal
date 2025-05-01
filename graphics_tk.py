from tkinter import font, Canvas, Frame
from tkinter import SW, RIGHT
from typing import Literal


MARKER_RADIUS = 8


def canvas_debug_grid(
        canvas: Canvas,
        x_range: tuple[float, float] = (-1000, 1000),
        y_range: tuple[float, float] = (-1000, 1000),
        spacing: float = 50
) -> None:
    x_span, y_span = x_range[1] - x_range[0], y_range[1] - y_range[0]
    x_num, y_num = int(x_span // spacing), int(y_span // spacing)

    for x_point in range(x_num):
        for y_point in range(y_num):
            x_point_scaled = x_point * spacing + x_range[0]
            y_point_scaled=  y_point * spacing + y_range[0]
            canvas.create_arc(
                x_point_scaled - 3, y_point_scaled - 3,
                x_point_scaled + 3, y_point_scaled + 3, extent=360, tags="debug")
            if x_point % 5 == 0 and y_point % 5 == 0:
                canvas.create_text(
                    x_point_scaled, y_point_scaled,
                    text=f"{x_point_scaled},{y_point_scaled}", tags="debug")

    return


def title_chart(
        canvas: Canvas,
        desc: str,
        top_left_fretboard_coords: tuple[float, float],
        text_color: str,
) -> None:
    x_coord, y_coord = top_left_fretboard_coords
    title_font = font.Font(
        size=24,
        family='Quicksand',
        # weight="bold"
    )
    canvas.create_text(x_coord, y_coord, text=desc, fill=text_color, tags="title", anchor=SW, font=title_font)


def draw_frets(
        canvas: Canvas,
        num_frets: int,
        neck_length: float,
        neck_width: float,
        init_x: float,
        init_y: float,
        color: str,
) -> list[float]:

    two_1_12_amen: float = 2**(-1/12)
    relative_fret_x_values = [two_1_12_amen**n for n in range(num_frets)]
    scale_constant = sum(relative_fret_x_values)
    fret_x_diffs: list[float] = [
        relative_scale * neck_length / scale_constant
        for relative_scale in relative_fret_x_values] + [init_x + neck_length]

    # cumsum for x positions
    fret_x_values: list[float] = [0] + [sum(fret_x_diffs[:i]) for i in range(num_frets)]

    # draw last fret
    canvas.create_line(
        init_x + neck_length, init_y,
        init_x + neck_length, init_y + neck_width,
        tags="fretboard",
        fill=color,
    )

    for current_fret_x_value in fret_x_values:  # add 1
        # draw each fret
        canvas.create_line(
            current_fret_x_value + init_x, init_y,
            current_fret_x_value + init_x, init_y + neck_width,
            tags="fretboard",
            fill=color,
        )

    # record these for notating fingering positions
    fret_midpoints: list[float] = [
        (fret_x_values[i + 1] + fret_x_values[i]) * 0.5 + init_x
         for i in range(num_frets)
    ]

    return fret_midpoints


def draw_strings(
        canvas: Canvas,
        num_strings: int,
        neck_scale_constant: float,
        string_spacing: float,
        init_x: float,
        init_y: float,
        color:str,
) -> list[float]:

    string_y_values: list[float] = [init_y + i * string_spacing for i in range(num_strings)]

    for y_value in string_y_values:
        canvas.create_line(
            init_x, y_value,
            init_x + neck_scale_constant, y_value,
            tags="fretboard",
            fill=color,
        )

    return string_y_values


def label_tuning(
        canvas: Canvas,
        tuning: list[str],
        string_y_positions: list[float],
        init_x_coord: float,
        color: str,
) -> None:
    tuning_font = font.Font(
        size=12,
        family='Quicksand',
    )

    for i, string_note in enumerate(tuning):
        note_x_position, note_y_position = init_x_coord - 20, string_y_positions[i]

        # todo notes should be aligned even if number of characters varies
        canvas.create_text(
            note_x_position, note_y_position,
            text=string_note, tags="fretboard",
            justify=RIGHT, font=tuning_font,
            fill=color,
        )
    return


def draw_fret_markers(
        canvas: Canvas,
        num_frets: int,
        fret_x_midpoints: list[float],
        string_y_coords: list[float],
        num_strings: int,
        single_marker_position: Literal["middle", "top", "bottom", "none"],
        double_marker_position: Literal["middle", "top", "bottom", "none"],
        color: str,
        # todo all single marker option
        # todo check distance between frets to get max radius of marker
) -> None:

    num_octaves = num_frets // 12
    semitones_beyond_whole_octave = num_frets % 12
    mod_3_markers: list[int] = [3 + 12 * i for i in range(num_octaves + int(semitones_beyond_whole_octave >= 3))]
    mod_5_markers: list[int] = [5 + 12 * i for i in range(num_octaves + int(semitones_beyond_whole_octave >= 5))]
    mod_7_markers: list[int] = [7 + 12 * i for i in range(num_octaves + int(semitones_beyond_whole_octave >= 7))]
    mod_9_markers: list[int] = [9 + 12 * i for i in range(num_octaves + int(semitones_beyond_whole_octave >= 9))]
    octave_fret_markers: list[int] = [i * 12 for i in range(1, int(num_frets // 12) + 1)]
    single_frets_to_mark: list[int] = sorted(
        mod_3_markers + mod_5_markers + mod_7_markers + mod_9_markers
    )

    num_strings_is_odd: bool = num_strings % 2 == 1
    # set single marker y positions
    middle_string: int = num_strings // 2
    if single_marker_position == "middle":
        if num_strings_is_odd:
            single_marker_y_pos = (
                string_y_coords[middle_string]
                + string_y_coords[middle_string + 1]) * 0.5
        else:
            single_marker_y_pos = (
                string_y_coords[middle_string - 1]
                + string_y_coords[middle_string]) * 0.5

    elif single_marker_position == "top":
        single_marker_y_pos = (string_y_coords[0] + string_y_coords[1]) * 0.5
    else:
        single_marker_y_pos = (string_y_coords[-1] + string_y_coords[-2]) * 0.5

    # draw single markers
    if single_marker_position == "none":
        pass
    else:
        for fret in single_frets_to_mark:
            single_marker_x_pos = fret_x_midpoints[fret]
            canvas.create_oval(
                single_marker_x_pos - MARKER_RADIUS, single_marker_y_pos - MARKER_RADIUS,
                single_marker_x_pos + MARKER_RADIUS, single_marker_y_pos + MARKER_RADIUS,
                fill=color, tags="fretboard",
            )

    # set octave marker y positions
    if double_marker_position == "middle":
        # if odd number of strings, doubled markers should be split between the middle string
        if num_strings_is_odd:
            marker_1_y_pos = (string_y_coords[middle_string - 1]
                              + string_y_coords[middle_string]) * 0.5
            marker_2_y_pos = (string_y_coords[middle_string ]
                              + string_y_coords[middle_string + 1]) * 0.5
        # if even number of strings, doubled markers should be split between the strings above and below middle strings
        else:
            marker_1_y_pos = (string_y_coords[middle_string - 2] + string_y_coords[middle_string - 1]) * 0.5
            marker_2_y_pos = (string_y_coords[middle_string] + string_y_coords[middle_string + 1]) * 0.5

    elif double_marker_position == "top":
        marker_1_y_pos = (string_y_coords[0] + string_y_coords[1]) * 0.5
        marker_2_y_pos = (string_y_coords[1] + string_y_coords[2]) * 0.5
    else:
        marker_1_y_pos = (string_y_coords[-1] + string_y_coords[-2]) * 0.5
        marker_2_y_pos = (string_y_coords[-2] + string_y_coords[-3]) * 0.5

    # draw octave markers
    if double_marker_position == "none":
        pass
    else:
        for fret in octave_fret_markers:
            double_marker_x_pos = fret_x_midpoints[fret]
            canvas.create_oval(
                double_marker_x_pos - MARKER_RADIUS, marker_1_y_pos - MARKER_RADIUS,
                double_marker_x_pos + MARKER_RADIUS, marker_1_y_pos + MARKER_RADIUS,
                fill=color, tags="fretboard",
            )
            canvas.create_oval(
                double_marker_x_pos - MARKER_RADIUS, marker_2_y_pos - MARKER_RADIUS,
                double_marker_x_pos + MARKER_RADIUS, marker_2_y_pos + MARKER_RADIUS,
                fill=color, tags="fretboard",
            )

    return


def notate_fretted_chord_near_nut(
        fretted_notes: list[list[int, int]],
        string_y_positions: list[float],
        nut_x_position: float,
        canvas: Canvas,
        annotation_color: str,
) -> None:
    # have to declare in here or we get a 'font declared too early' error
    annotation_font = font.Font(
        size=12,
        family='Quicksand',
    )

    fretted_strings: list[int] = [string_idx for string_idx, fret_idx in fretted_notes]
    fretted_frets: list[int] = [fret_idx for string_idx, fret_idx in fretted_notes]
    first_string, last_string = min(fretted_strings), max(fretted_strings)

    for string_num in range(first_string, last_string + 1):

        if string_num in fretted_strings:
            fret_num = fretted_frets[fretted_strings.index(string_num)]
            canvas.create_text(
                # we use x position - 40 because the tuning is 20 px from the nut
                nut_x_position - 40, string_y_positions[string_num],
                text=fret_num,
                font=annotation_font,
                fill=annotation_color
            )

        else:
            canvas.create_text(
                nut_x_position - 40, string_y_positions[string_num],
                text="x",
                font=annotation_font,
                fill=annotation_color
            )


def notate_barred_chord_near_nut(
        barred_chord: tuple[list[list[int, int]], list[list[int, int]]],
        string_y_positions: list[float],
        nut_x_position: float,
        canvas: Canvas,
        # annotation_font: font.Font,
        annotation_color: str,
) -> None:
    # have to declare in here or we get a 'font declared too early' error
    annotation_font = font.Font(
        size=12,
        family='Quicksand',
    )

    fretted_notes, barred_notes = barred_chord
    fretted_strings: list[int] = [string_idx for string_idx, fret_idx in fretted_notes]
    fretted_frets: list[int] = [fret_idx for string_idx, fret_idx in fretted_notes]
    barre_start_string, barre_end_string = barred_notes[0][0], barred_notes[1][0]

    # create fretted note annotations
    for string_num in fretted_strings:
        fret_num = fretted_frets[fretted_strings.index(string_num)]
        canvas.create_text(
            nut_x_position - 40, string_y_positions[string_num],
            text=fret_num,
            font=annotation_font,
            fill=annotation_color,
        )

    # create barre annotation, offset along x-axis by an additional 20 px
    barre_annotation_y_start: float = string_y_positions[barre_start_string]
    barre_annotation_y_end: float = string_y_positions[barre_end_string]
    # arrow body
    canvas.create_line(
        (nut_x_position - 60, barre_annotation_y_start,
         nut_x_position - 60, barre_annotation_y_end),
        fill=annotation_color,
    )
    # arrowhead
    canvas.create_polygon(
        [nut_x_position - 64, barre_annotation_y_end + 10,
         nut_x_position - 60, barre_annotation_y_end,
         nut_x_position - 56, barre_annotation_y_end + 10,
         nut_x_position - 60, barre_annotation_y_end + 5,
         ],
        fill=annotation_color,
    )

    canvas.create_text(
        (nut_x_position - 72, 0.5 * (barre_annotation_y_start + barre_annotation_y_end)),
        text=barred_notes[0][1],  # barre fret
        fill=annotation_color,
        font=annotation_font,
    )

    return


def mark_fret(
        canvas: Canvas,
        fret_x_coord: float,
        string_y_coord: float,
        marker_color: str,
        radius: float = MARKER_RADIUS,
) -> Canvas:
    canvas.create_oval(
        fret_x_coord - radius, string_y_coord - radius,
        fret_x_coord + radius, string_y_coord + radius,
        fill=marker_color, tags="chord"
    )
    return canvas


def mark_barre(
        canvas: Canvas,
        fret_x_coord: float,
        lo_str_y_coord: float,
        hi_str_y_coord: float,
        radius: float = MARKER_RADIUS,
        marker_color: str = "red"
) -> Canvas:
    # draw rounded barre endpoints
    canvas = mark_fret(canvas, fret_x_coord, lo_str_y_coord, radius=radius, marker_color=marker_color)
    canvas = mark_fret(canvas, fret_x_coord, hi_str_y_coord, radius=radius, marker_color=marker_color)
    canvas.create_rectangle(
        fret_x_coord - radius, lo_str_y_coord,
        fret_x_coord + radius, hi_str_y_coord,
        outline="",
        fill=marker_color,
        tags="chord",
    )
    return canvas


def make_fretboard(
        num_frets: int,
        tuning: list[str] | str,
        root: Frame,
        fretboard_color: str = "black",
        background_color: str = "white",
        marker_color: str = "black",
        label_color: str = "black",
        neck_scale_constant: float = 300,
        string_spacing: float = 11,
        init_x_coord: float = 40,
        init_y_coord: float = 40,
        padding: float = 20.0,
        single_marker_pos: Literal["middle", "top", "bottom", "none"] = "middle",
        double_marker_pos: Literal["middle", "top", "bottom", "none"] = "middle",
        right_handed: bool = True,
        canvas_grid: bool = False,
) -> tuple[list[float], list[float], Canvas, Frame]:
    """

    :param label_color:
    :param marker_color:
    :param background_color:
    :param fretboard_color:
    :param num_frets: Number of frets on instrument. Minimum 3.
    :param tuning: Instrument tuning. Used to infer number of strings. Minimum 3.
        Format: hyphen-separated notes, ex. "E-A-D-G-B-E"
    :param neck_scale_constant: Neck length, px
    :param string_spacing: Px between strings
    :param init_x_coord: Top left corner x-coord. Default 100 px.
    :param init_y_coord: Top left corner y-coord. Default 100 px.
    :param padding: Whitespace between fretboard edges and window edge. Default 50 px.
    :param single_marker_pos: Position of single fret markers on neck. Default middle.
    :param double_marker_pos: Position of octave fret markers on neck. Default middle.
    :param right_handed: If right_handed, notes will be ordered bottom-to-top. Default True.
    :param canvas_grid: Debugging option. Draws point grid at 50x50px intervals, with text coordinate annotations every
        250x250px. Default False.
    :return: list of fret x-coordinate midpoints, list of string y coordinates, canvas object, root object.
    """

    tuning_list: list[str] = tuning.split("-") if type(tuning) is str else tuning
    num_strings: int = len(tuning_list)

    assert len(tuning_list) == num_strings, (
        f"String number and tuning do not match\n"
        f"Expected {len(tuning_list)} strings for tuning {tuning}; got {num_strings}")
    assert 2 < num_frets, "Fret number must be greater than 2"
    assert 2 < num_strings, "String number must be greater than 2"

    fretboard_width = string_spacing * (num_strings - 1)

    # boundaries: (-init_x, fretboard_length + init_x)
    #             (-init_y, string_width + init_y)
    # => width = 2 * init_x + fretboard_length + padding
    # => length = 2 * init_y + fretboard_width + padding
    canvas = Canvas(
        root,
        width=neck_scale_constant + 2 * abs(init_x_coord) + padding,
        height=fretboard_width * 1.2 + abs(init_y_coord) + padding,
        bg=background_color,
    )

    if canvas_grid:
        canvas_debug_grid(canvas)

    fret_x_coord_midpoints: list[float] = draw_frets(
        canvas,
        num_frets,
        neck_scale_constant,
        fretboard_width,
        init_x_coord,
        init_y_coord,
        color=fretboard_color
    )

    string_y_coords: list[float] = draw_strings(
        canvas,
        num_strings,
        neck_scale_constant,
        string_spacing,
        init_x_coord,
        init_y_coord,
        color=fretboard_color,
    )

    # if right-handed, strings will be drawn from lightest to heaviest
    if right_handed:
        tuning_list.reverse()

    label_tuning(
        canvas,
        tuning_list,
        string_y_coords,
        init_x_coord,
        color=label_color
    )

    draw_fret_markers(
        canvas,
        num_frets,
        fret_x_coord_midpoints,
        string_y_coords,
        num_strings,
        single_marker_pos, double_marker_pos,
        color=marker_color,
    )

    return fret_x_coord_midpoints, string_y_coords, canvas, root
