from typing import Literal
from graphics_tk import (make_fretboard, mark_fret, title_chart, mark_barre, notate_fretted_chord_near_nut,
                         notate_barred_chord_near_nut)
from charting import (get_instrument_semitones_from_c, convert_chord_to_semitones,
                      convert_scale_to_semitones, build_scale, build_arpeggio)
from charting_better import build_chord_better
from tkinter import Frame, Canvas, font
from style_dicts import hex_style_dict, hex_colors


class Instrument:

    def __init__(
            self,
            num_frets: int,
            tuning: list[str] | str,
            display_frame: Frame,
            neck_scale_constant: float = 700,
            string_spacing: float = 25,
            init_x_coord: float = 100.0,
            init_y_coord: float = 100.0,
            padding: float = 50.0,
            single_marker_pos: Literal["middle", "top", "bottom", "none"] = "middle",
            double_marker_pos: Literal["middle", "top", "bottom", "none"] = "middle",
            right_handed: bool = True,
            canvas_grid: bool = False,
            marker_radius: float = 4,
            style: str = 'Dark mode',
    ):
        """
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
        :param marker_radius: radius (px) of fretted notes
        :return: list of fret x-coordinate midpoints, list of string y coordinates, canvas object, root object.
        """
        self.num_frets = num_frets
        self.tuning = tuning
        self.tuning_list = self.tuning.split("-")
        self.num_strings = len(self.tuning_list)
        self.semitones_from_c: list[list[int]] = get_instrument_semitones_from_c(
            self.num_frets,
            self.tuning_list,
        )

        self.style = style
        color_keys = hex_style_dict.get(self.style)
        self.fretboard_color, self.background_color, self.fret_marker_color, self.note_marker_color, self.label_color = \
            [hex_colors.get(color) for color in color_keys]
        self.display_frame = display_frame
        self.fret_x_coord_midpoints, self.string_y_coords, self.template_canvas, self.display_frame = make_fretboard(
            self.num_frets,
            self.tuning,
            self.display_frame,
            fretboard_color=self.fretboard_color,
            background_color=self.background_color,
            marker_color=self.fret_marker_color,
            label_color=self.label_color,
            neck_scale_constant=neck_scale_constant,
            string_spacing=string_spacing,
            init_x_coord=init_x_coord,
            init_y_coord=init_y_coord,
            padding=padding,
            single_marker_pos=single_marker_pos,
            double_marker_pos=double_marker_pos,
            right_handed=right_handed,
            canvas_grid=canvas_grid,
        )

        # set title location to top left
        self.title_location: tuple[float, float] = self.fret_x_coord_midpoints[0], self.string_y_coords[0]
        self.right_handed = right_handed
        if self.right_handed:
            self.string_y_coords.reverse()

        self.marker_radius = marker_radius


    def copy_fretboard_to(self, destination_canvas: Canvas) -> None:

        for item_id in self.template_canvas.find_all():
            item_coords = self.template_canvas.coords(item_id)
            item_type = self.template_canvas.type(item_id)
            item_options = self.template_canvas.itemconfigure(item_id)
            item_options_processed: dict[str: any] = {}

            # have to exclude irrelevant options, which are of the form {'key': ('key', '', '', '', '')}
            # relevant options will have the form {'key': ('key', '', '', true_val, true_val)};
            #   true vals are duplicated for some reason
            for key, vals in item_options.items():
                if all([val == '' for val in vals[1:]]):
                    pass
                else:
                    true_val = vals[-1]
                    item_options_processed.update({key: true_val})

            if item_type == "line":
                destination_canvas.create_line(*item_coords, **item_options_processed,)
            elif item_type == "rectangle":
                destination_canvas.create_rectangle(*item_coords, **item_options_processed,)
            elif item_type == "text":
                destination_canvas.create_text(*item_coords, **item_options_processed,)
            elif item_type == "oval":
                destination_canvas.create_oval(*item_coords, **item_options_processed,)

        return

    def display_chord_voicings(
            self,
            fretted_pairs,
            barred_pairs,
            title: str,
            pages: list[Frame],
            canvases_per_page: int,
    ) -> list[Canvas]:

        chords_canvases: list[Canvas] = list()
        current_canvas_idx = 0

        for barred_chord in barred_pairs:
            current_page = pages[current_canvas_idx // canvases_per_page]
            this_chord_chart = Canvas(
                master=current_page,
                bg=self.background_color,
                width=self.template_canvas.winfo_reqwidth(),
                height=self.template_canvas.winfo_reqheight(),
            )
            # add fretboard to this canvas
            self.copy_fretboard_to(this_chord_chart)

            this_chord_fretted_pairs, this_chord_barre_bounds = barred_chord
            for string_idx, fret_idx in this_chord_fretted_pairs:
                mark_fret(
                    this_chord_chart,
                    self.fret_x_coord_midpoints[fret_idx],
                    self.string_y_coords[string_idx],
                    self.note_marker_color,
                )

            lo_pair, hi_pair = this_chord_barre_bounds
            fret_x_coord = self.fret_x_coord_midpoints[lo_pair[1]]
            lo_y_coord = self.string_y_coords[lo_pair[0]]
            hi_y_coord = self.string_y_coords[hi_pair[0]]
            mark_barre(
                this_chord_chart,
                fret_x_coord,
                lo_y_coord,
                hi_y_coord,
                marker_color=self.note_marker_color,
            )

            notate_barred_chord_near_nut(
                barred_chord,
                self.string_y_coords,
                self.fret_x_coord_midpoints[0],
                this_chord_chart,
                self.label_color,
            )

            title_chart(this_chord_chart, title, self.title_location, self.label_color)
            chords_canvases.append(this_chord_chart)
            current_canvas_idx += 1

        for fretted_chord in fretted_pairs:

            current_page = pages[current_canvas_idx // canvases_per_page]
            this_chord_chart = Canvas(
                master=current_page,
                bg=self.background_color,
                width=self.template_canvas.winfo_reqwidth(),
                height=self.template_canvas.winfo_reqheight(),
            )
            # add fretboard to this canvas
            self.copy_fretboard_to(this_chord_chart)

            for string_idx, fret_idx in fretted_chord:
                mark_fret(
                    this_chord_chart,
                    self.fret_x_coord_midpoints[fret_idx],
                    self.string_y_coords[string_idx],
                    self.note_marker_color,
                )

            notate_fretted_chord_near_nut(
                fretted_chord,
                self.string_y_coords,
                self.fret_x_coord_midpoints[0],
                this_chord_chart,
                self.label_color,
            )

            title_chart(this_chord_chart, title, self.title_location, self.label_color)
            chords_canvases.append(this_chord_chart)
            current_canvas_idx += 1

        for i, canvas in enumerate(chords_canvases):
            # put canvases below all menu items
            canvas.grid(row=2 + i, column=0, columnspan=3)

        return chords_canvases


    def display_voicing(
            self,
            fretted_pairs: list[list[int, int]],
            title: str,
    ):
        # no scrolling so no need to nest in a window in a canvas; pack in display frame
        chart_canvas = Canvas(
                master=self.display_frame,
                bg=self.background_color,
                width=self.template_canvas.winfo_reqwidth(),
                height=self.template_canvas.winfo_reqheight(),
            )
        self.copy_fretboard_to(chart_canvas)

        for fret_idx, string_idx in fretted_pairs:
            fret_x_coord = self.fret_x_coord_midpoints[fret_idx]
            string_y_coord = self.string_y_coords[string_idx]
            mark_fret(chart_canvas, fret_x_coord, string_y_coord, self.note_marker_color)

        title_chart(chart_canvas, title, self.title_location, self.label_color)
        return chart_canvas


    def get_chord_fret_pairs(
            self,
            chord_root: str,
            chord_type: str,
            ) -> tuple[list[list[tuple[int, int]]], list[tuple[list[tuple[int, int]], list[tuple[int, int]]]]]:

        intervals_in_chord = convert_chord_to_semitones(chord_type, chord_root)
        minimum_strings_needed = len(intervals_in_chord)
        all_fretted_chords, all_barred_chords = list(), list()
        # repeat the procedure until we use the very least number of strings needed to form the chord
        for starting_idx in range(self.num_strings - minimum_strings_needed + 1):
            fretted_chords, barred_chords = build_chord_better(
                self.semitones_from_c,
                intervals_in_chord,
                starting_string_idx=starting_idx,
            )

            for chord in fretted_chords:
                all_fretted_chords.append(chord)
            for chord in barred_chords:
                all_barred_chords.append(chord)

        return all_fretted_chords, all_barred_chords


    def get_scale(
            self,
            scale_root: str,
            scale_type: str,
    ) -> list[list[int, int]]:

        intervals_in_scale = convert_scale_to_semitones(scale_type, scale_root)
        fret_string_pairs = build_scale(intervals_in_scale, self.semitones_from_c)

        return fret_string_pairs


    def get_arp(
            self,
            arp_root: str,
            arp_type: str,
    ) -> list[list[int, int]]:

        intervals_in_arp = convert_chord_to_semitones(arp_type, arp_root)
        fret_string_pairs = build_arpeggio(self.semitones_from_c, intervals_in_arp)

        return fret_string_pairs


if __name__ == '__main__':
    # todo fix scrollbar using https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter
    pass
