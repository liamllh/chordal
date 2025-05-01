from turtle import mainloop, delay
from chord_calc import label_notes, convert_indices_to_intervals, build_chords, build_arpeggio, build_scale
from chord_dicts import chords_to_intervals, index_to_note, interval_to_integer, note_to_index, numeral_to_semitones, \
    intervals_in_scales
from itertools import permutations
from style_dicts import texture_name_to_gif, guitar_styles, color_tuples
from deprecated_graphics import draw_fretboard, title_chart, draw_notes, notate_fret_numbers


class Instrument:

    def __init__(self,
                 frets: int,
                 tuning: str,  # 'E-A-D-G-B-E' -> ('E', 'A', 'D', 'G', 'B', 'E')
                 color_key: str,  # i.e. 'neon green' -> ('green', 'green', 'white', 'white', 'black')
                 fret_marker_style: str = 'Plain white',
                 scale_factor: float = 1.0,
                 texture: str | None = None,
                 animated: bool = False,
                 ):
        """

        :param frets: Number of frets on the instrument
        :param tuning: Instrument tuning, as hyphen-separated string (ex. 'E-A-D-G-B-E')
        :param color_key: Scheme for coloring instrument
        :param fret_marker_style: Scheme for coloring fret markers
        :param scale_factor: Scale of drawing
        :param texture: !!! Not yet implemented !!! Texture of fretboard
        :param animated: Bool determining whether the turtle is animated or shapes are drawn instantly
        """
        color_list = guitar_styles.get(color_key)
        color_list_tuples = [color_tuples.get(color) for color in color_list]

        self.frets = frets
        self.tuning = tuple(tuning.split("-"))
        self.strings = len(self.tuning)
        self.fret_color = color_list_tuples[0]
        self.string_color = color_list_tuples[1]
        self.text_color = color_list_tuples[2]
        self.bg_color = color_list_tuples[3]
        self.fret_marker_color = color_list_tuples[4]
        self.note_marker_color = color_list_tuples[5]
        self.fret_marker_style = fret_marker_style
        self.scale_factor = scale_factor
        self.texture = texture_name_to_gif.get(texture)

        if animated:
            delay(10)
        else:
            delay(0)

        self.warnings_and_assertions()
        self.fret_positions, self.string_positions, self.Screen = self.draw()

    def warnings_and_assertions(self):
        """
        Asserts that user parameters are valid
        """
        assert 3 <= self.strings <= 12, "Instrument must have between 3 and 12 strings"
        assert 7 <= self.frets <= 27, "Instrument must have between 7 and 27 frets"
        assert self.fret_marker_style == "middle" or "left" or "right", "Invalid marker style"
        assert self.fret_color, "Invalid color key"

    def draw(self):
        """
        Draws the fretboard
        """
        fret_positions, string_positions, screen = draw_fretboard(strings=self.strings,
                                                                  tuning=self.tuning,
                                                                  frets=self.frets,
                                                                  fret_marker_style=self.fret_marker_style,
                                                                  scale_factor=self.scale_factor,
                                                                  texture=self.texture,
                                                                  fret_color=self.fret_color,
                                                                  string_color=self.string_color,
                                                                  tuning_label_color=self.text_color,
                                                                  background_color=self.bg_color,
                                                                  fret_marker_color=self.fret_marker_color,
                                                                  )

        return fret_positions, string_positions, screen

    def scale(self, scale_root, scale_type):
        """
        Displays the scale notes on the fretboard
        :param scale_root: Root note of scale as str
        :param scale_type: Scale type as str
        """
        scale_intervals = intervals_in_scales.get(scale_type)
        assert scale_intervals, "Invalid scale"

        standard_string_ints = label_notes(self.strings, self.frets, self.tuning, output_as_integers=True)
        standard_string_intervals = convert_indices_to_intervals(standard_string_ints, scale_root)
        scale_pairs = build_scale(scale_intervals, standard_string_intervals)

        chart_y_max = self.string_positions[-1]
        title_chart(f"{scale_root} {scale_type} scale", chart_y_max, scale_factor=self.scale_factor, text_color=self.text_color)
        draw_notes(self.fret_positions, self.string_positions, scale_pairs, scale_factor=self.scale_factor, color=self.note_marker_color)

        self.Screen.getcanvas().update()
        self.Screen.getcanvas().postscript(file="test image.ps")

        return None

    # todo allow save option
    # todo slash chord functionality
    def chord(
            self,
            chord_root,
            chord_type,
            inversion=0,
            starting_string_index=0,
            debug=False,
            permute=False
    ):
        """
        Displays chord if permute is False, or chords if permute is True, matching chord_root, chord_type, and inversion
        :param chord_root:
        :param chord_type:
        :param inversion:
        :param starting_string_index:
        :param debug:
        :param permute:
        :return:
        """
        chord_intervals = chords_to_intervals.get(chord_type)
        assert chord_intervals, "Invalid chord"

        standard_string_ints = label_notes(self.strings, self.frets, self.tuning, output_as_integers=True)
        standard_string_intervals = convert_indices_to_intervals(standard_string_ints, chord_root)

        if permute:
            permuted_intervals = set(permutations(chord_intervals))
            chord_variations = list()
            for chord_intervals in permuted_intervals:

                single_chord_variations = build_chords(chord_intervals, standard_string_intervals, inversion=inversion,
                                                       starting_string_index=starting_string_index, debug=debug)
                for chord in single_chord_variations:
                    chord_variations.append(chord)

        else:
            chord_variations = build_chords(chord_intervals, standard_string_intervals, inversion=inversion,
                                            starting_string_index=starting_string_index, debug=debug)

        # print(f"{chord_root}{chord_type}: {len(chord_variations)} variations")
        if len(chord_variations) > 0:

            if inversion:
                inverted_note_interval_relative_to_root = chord_intervals[inversion]

                inverted_note_integer = (interval_to_integer.get(inverted_note_interval_relative_to_root) +
                                         note_to_index.get(chord_root)) % 12

                inverted_note = index_to_note.get(inverted_note_integer)
                chord_chart_title = f"{chord_root}{chord_type}/{inverted_note}"

            else:
                chord_chart_title = f"{chord_root}{chord_type}"

            title_turtle = title_chart(chord_chart_title, self.string_positions[-1], scale_factor=self.scale_factor,
                                       text_color=self.text_color)

            for chord_variation in chord_variations:
                note_turtle = draw_notes(self.fret_positions, self.string_positions, chord_variation, scale_factor=self.scale_factor,
                                         color=self.note_marker_color)
                fret_number_turtle = notate_fret_numbers(self.string_positions, chord_variation, scale_factor=self.scale_factor,
                                                         fret_number_color=self.text_color)

                note_turtle.clear()
                fret_number_turtle.clear()

            # input("Press enter to close")
            # time.sleep(0.1)
            # time.sleep(1)
            title_turtle.clear()
            # note_turtle.clear()
            # fret_number_turtle.clear()

        else:
            if inversion:
                print(f"Shape for {chord_root}{chord_type} (inversion {inversion}) not found in this tuning")
            else:
                print(f"Shape for {chord_root}{chord_type} not found in this tuning")

        return None

    def arpeggio(self,
                 arpeggio_root,
                 arpeggio_type,
                 ) -> None:
        """
        Displays fretboard with arpeggio_type starting on note arpeggio_root annotated
        :param arpeggio_root: Root of arpeggio
        :param arpeggio_type: Type of arpeggio, determining intervals from root
        """

        standard_string_integers = label_notes(self.strings, self.frets, self.tuning, output_as_integers=True)
        standard_string_intervals = convert_indices_to_intervals(standard_string_integers, arpeggio_root)
        chord_intervals = chords_to_intervals.get(arpeggio_type)
        fret_string_pairs = build_arpeggio(standard_string_intervals, chord_intervals)

        chart_y_max = self.string_positions[-1]
        title_turtle = title_chart(f"{arpeggio_root}{arpeggio_type} arpeggio", chart_y_max, scale_factor=self.scale_factor,
                                   text_color=self.text_color)
        note_turtle = draw_notes(self.fret_positions, self.string_positions, fret_string_pairs, scale_factor=self.scale_factor,
                                 color=self.note_marker_color)

        mainloop()
        note_turtle.clear()
        title_turtle.clear()

        return None

    def all_chords(self, permute=False) -> None:
        """
        Sequentially displays all possible ways to fret every chord for every root note on the instrument
        :param permute: Whether to give all possible chords or first found chord
        """

        chord_list = chords_to_intervals.keys()
        root_list = note_to_index.keys()

        for root_note in root_list:
            for chord_type in chord_list:

                self.chord(root_note, chord_type, permute=permute)

        return None

    def progression(
            self,
            root_note: str,
            root_numeral_list: list[str],
            chord_type_list: list[str],
            permute=False) -> None:
        """
        Displays chords in a progression
        :param root_note: Root note
        :param root_numeral_list: Numerals of progression, i.e. ["I", "IV", "V", "I"]
        :param chord_type_list: Names of chords in progression, i.e. ["M7", "6", "b7", "M"]
        :param permute: Whether to give all possible chords or first found chord
        """

        assert len(root_numeral_list) == len(chord_type_list), f"The lengths of the chord roots ({len(root_numeral_list)}) and chord types ({len(chord_type_list)}) must match"

        root_note_integer = note_to_index.get(root_note)
        root_notes_integers = [(numeral_to_semitones.get(root_numeral) + root_note_integer) % 12 for root_numeral in root_numeral_list]
        root_notes = [index_to_note.get(note_integer) for note_integer in root_notes_integers]

        # todo add additional title functionality
        i = 0
        for root_note in root_notes:
            chord_type = chord_type_list[i]
            # print(f"{root_note}{chord_type}")
            self.chord(root_note, chord_type, permute=permute)
            i += 1

        return None


def list_chords() -> None:
    """
    Lists encoded chords for the user
    """
    print(chords_to_intervals.keys())
    return None


def list_scales() -> None:
    """
    Lists encoded scales for the user
    """
    print(intervals_in_scales.keys())
    return None


def list_fretboard_themes() -> None:
    """
    Lists fretboard themes for the user
    """
    print(guitar_styles.keys())
    return None


if __name__ == '__main__':

    guitar = Instrument(22, 'C-G-C-F-C-E', 'Neon green', 'left', scale_factor=3, animated=True)
    prog_list = ['VI', 'III', 'V', 'I']
    type_list = ['m7', 'm7b5', '7', 'sus2']
    # list_scales()
    # guitar.all_chords(permute=True)
    # guitar.scale("F", 'iwato')
    guitar.all_chords(permute=True)
