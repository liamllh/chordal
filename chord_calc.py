from chord_dicts import note_to_index, index_to_note, integer_to_interval, sharp_to_flat, interval_to_integer, numeral_to_semitones


def label_notes(
        strings: int,
        frets: int,
        tuning: tuple,
        output_as_integers: bool = True,
) -> list[list[int | str]]:
    """
    Given a tuning and the instrument parameters, return a nested list containing notes corresponding to each fret
        for each string
    :param strings: Number of strings
    :param frets: Number of frets
    :param tuning: Tuning as hyphen-separated string, ex. 'E-A-D-G-B-E'
    :param output_as_integers: Whether to return output as integer semitones from C or as str notes
    :return: nested list containing notes corresponding to each fret for each string
    """
    assert len(tuning) == strings, f"String-tuning mismatch: this instrument has {strings} strings but the tuning is for {len(tuning)} strings"

    all_string_notes = list()
    all_string_note_indices = list()

    # get the number of semitones up from C for each note on each string
    for open_note in tuning:
        note_index: int = note_to_index.get(open_note)
        string_note_indices = range(note_index, note_index + frets)
        string_note_indices = [note % 12 for note in string_note_indices]
        all_string_note_indices.append(string_note_indices)

    if output_as_integers:
        return all_string_note_indices

    # convert semitones from C to notes (ex. 4 -> 'E', 6 -> 'F#')
    for string_note_indices in all_string_note_indices:
        string_notes = list()

        for string_note_index in string_note_indices:
            string_notes.append(index_to_note.get(string_note_index))

        all_string_notes.append(string_notes)

    return all_string_notes


# note_to_index dict sets C = 0, C# = 1, etc, so the indices must be shifted such that the desired root note has index 0
def convert_relative_to_c(all_string_ints: list[list[int]], root_note: str) -> list[list[int]]:
    """

    :param all_string_ints:
    :param root_note:
    :return:
    """

    interval_shift: int = note_to_index.get(root_note)
    all_string_ints_shifted = list()

    for string_ints in all_string_ints:
        string_ints_shifted = [(string_int - interval_shift) % 12 for string_int in string_ints]
        all_string_ints_shifted.append(string_ints_shifted)

    return all_string_ints_shifted


# convert integer indices to intervals relative to a root note
def convert_indices_to_intervals(all_string_notes: list[list[int]], relative_note: str):

    all_string_notes = convert_relative_to_c(all_string_notes, relative_note)
    all_string_intervals = list()
    for string_notes in all_string_notes:
        string_intervals = [integer_to_interval.get(string_note) for string_note in string_notes]
        all_string_intervals.append(string_intervals)

    return all_string_intervals


# returns pairs of [fret, string] for notes belonging to a given scale on the fretboard
def build_scale(scale_intervals: list, all_string_intervals: list[list[str]]):

    string_fret_pairs = list()
    intervals_in_key = [sharp_to_flat.get(interval) if 's' in interval else interval for interval in scale_intervals]

    string_index = 0
    for string_interval_list in all_string_intervals:

        fret_index = 0
        for interval in string_interval_list:

            if interval in intervals_in_key:
                string_fret_pairs.append([fret_index, string_index])

            fret_index += 1

        string_index += 1

    return string_fret_pairs


# returns the lists of [fret, string] comprising a given chord, starting on all possible strings
# todo maybe: get chords for permutations of chord notes? would make inversions irrelevant
# todo: if I do add permutations, make sure to remove chords w/ repeated notes, i.e. add2 and add9, from the all chords list
# maybe do a separate octave aware dictionary?
def build_chords(intervals_in_chord: list,
                 all_string_intervals: list[list[int]],
                 starting_string_index: int = 0,
                 inversion: int = 0,
                 debug=False) -> list[list[int, int]] or None:

    all_string_fret_pairs = list()
    # intervals_in_chord = chords_to_intervals.get(chord).copy()

    # reorder intervals
    if inversion:
        assert inversion <= len(intervals_in_chord) - 1, f"This inversion cannot be constructed for this chord"
        inverted_interval = intervals_in_chord[inversion]
        intervals_in_chord.remove(inverted_interval)
        intervals_in_chord.insert(0, inverted_interval)

    intervals_in_chord = [sharp_to_flat.get(interval) if 's' in interval else interval for interval in
                          intervals_in_chord]

    chord_list = list()
    first_string_index = starting_string_index
    while first_string_index < len(all_string_intervals) - len(intervals_in_chord) + 1:
        chord_fretboard_indices = build_chord(all_string_intervals, intervals_in_chord, first_string=first_string_index, debug=debug)

        if chord_fretboard_indices:
            chord_list.append(chord_fretboard_indices)

        first_string_index += 1

    return chord_list


# returns pairs of [fret, string] for notes in a chord
# ensure that chords can be formed by a human:
# chords cannot span more than 5 frets (excluding open strings)
def build_chord(string_interval_lists, intervals_in_chord, first_string=0, debug=False):

    chord_fretboard_indices = list()
    chord_fret_indices = list()
    string_index, chord_note_index = first_string, 0
    string_candidates = len(string_interval_lists)
    total_frets = len(string_interval_lists[0])
    allowed_frets = update_allowed_fret_range([], total_frets)

    if debug:
        print(f"{string_interval_lists = }\n"
              f"{intervals_in_chord = }")

    # return when outside of the range of strings
    while string_index < string_candidates:
        current_interval = intervals_in_chord[chord_note_index]
        current_string_intervals = string_interval_lists[string_index]

        if debug:
            print(f"{string_interval_lists[string_index] = }\n"
                  f"searching for interval {current_interval} on string {string_index}")

        if debug:
            print(f"{len(current_string_intervals) = }, {allowed_frets = }")
        current_string_intervals = [current_string_intervals[x] for x in allowed_frets]
        if debug:
            print(f"filtered string = {current_string_intervals}")
        fret_index = 0

        # loop over all note intervals in the current string
        for string_interval in current_string_intervals:

            found_note = False  # indicate whether or not we have found a note on this string
            candidate_interval = string_interval

            if debug:
                print(f"{candidate_interval = }")

            if candidate_interval == current_interval:
                found_note = True
                chord_fretboard_indices.append([allowed_frets[fret_index], string_index])
                chord_fret_indices.append(allowed_frets[fret_index])

                if debug:
                    print(f"appending f,s = {[allowed_frets[fret_index], string_index]}")
                    print(f"current fretted notes: {chord_fretboard_indices}")
                    print(f"current frets: {chord_fret_indices}")
                    print(f"need {len(intervals_in_chord)} notes, have {len(chord_fretboard_indices)}")

                # if we have as many notes in the constructed chord as in the chord intervals list, we have built the chord
                if len(chord_fretboard_indices) == len(intervals_in_chord):

                    if debug:
                        print(f"returning chord: {chord_fretboard_indices}")

                    return chord_fretboard_indices

                allowed_frets = update_allowed_fret_range(chord_fret_indices, total_frets)
                fret_index += 1
                chord_note_index += 1
                # now move to the next string

            if found_note:
                break

            fret_index += 1

        string_index += 1
        if string_index == len(string_interval_lists):
            break

    return chord_fretboard_indices if len(chord_fretboard_indices) == len(intervals_in_chord) else None


# returns the first [fret, string] pair corresponding to search_interval if the fret is in allowed_range
def find_interval_on_string(string_fret_pairs, search_interval, allowed_range) -> list[int, int] or None:

    for string_fret_pair in string_fret_pairs:
        fret, string, interval = string_fret_pair

        if fret in allowed_range and interval == search_interval:
            return [fret, string]

    return None


# gets human-playable range of frets given a list of frets already included in a chord
def update_allowed_fret_range(current_frets: list, total_frets, allowed_range: int=4) -> list:

    if not current_frets or current_frets == [0]:
        return [i for i in range(0, total_frets)]

    if 0 in current_frets:
        current_frets.remove(0)

    current_frets.sort()

    lower_bound = max(current_frets[-1] - allowed_range, 1)
    upper_bound = min(current_frets[0] + allowed_range, total_frets)

    allowable_range = [i for i in range(lower_bound, upper_bound + 1)]

    # open string always allowed
    allowable_range.insert(0, 0)

    return allowable_range


# similar to build scale, but limited to notes on frets +- some range from the fret index of the first note in the arpeggio
# todo: if no notes are found on a string, imcrement to the next note and search again
# search range for the first interval will be the same as the search range for the last string
def build_arpeggio(string_interval_lists, intervals_in_arpeggio, retry=False):

    arpeggio_fret_string_pairs = list()
    string_index, arpeggio_note_index = 0, 0
    string_candidates = len(string_interval_lists)
    total_frets = len(string_interval_lists[0])

    # first note of interval list on first string defines initial allowed fret range
    root_fret = string_interval_lists[0].index(intervals_in_arpeggio[0])
    allowed_frets = update_allowed_fret_range_arpeggio(root_fret, total_frets)

    while string_index < string_candidates:

        frets_on_string = list()
        arpeggio_notes_on_string = 0
        current_string_intervals = string_interval_lists[string_index]
        current_string_intervals = [current_string_intervals[x] for x in allowed_frets]
        fret_index = 0

        # loop over all note intervals in the current string
        for current_string_interval in current_string_intervals:

            search_interval = intervals_in_arpeggio[arpeggio_note_index % len(intervals_in_arpeggio)]
            # print(f"string {string_index + 1} allowed frets in range [{allowed_frets[0]}, {allowed_frets[-1]}]")
            if current_string_interval == search_interval:

                current_fret_index = allowed_frets[fret_index]
                arpeggio_fret_string_pairs.append([current_fret_index, string_index])
                frets_on_string.append(current_fret_index)
                allowed_frets = update_allowed_fret_range_arpeggio(frets_on_string[0], total_frets)

                fret_index += 1
                arpeggio_note_index += 1
                arpeggio_notes_on_string += 1

            else:
                fret_index += 1

        if arpeggio_notes_on_string == 0:
            # if no notes are found on string, increment to the next note and try again on the same string, unless this has already been done
            if retry:
                string_index += 1

            else:
                arpeggio_note_index += 1
                retry = True

        else:
            retry = False
            string_index += 1

    return arpeggio_fret_string_pairs


# todo: edit the first note on 0 fret case, can give some strange shapes
def update_allowed_fret_range_arpeggio(root_fret, total_frets, allowed_range=3) -> list[int]:

    if root_fret - allowed_range < 0:
        lower_bound = 0
        upper_bound = 2 * allowed_range + 1

    else:
        lower_bound = root_fret - allowed_range
        upper_bound = min(root_fret + allowed_range + 2, total_frets - 1)

    return [i for i in range(lower_bound, upper_bound + 1)]


# takes a list of chord numerals and converts to notes in a given key
# ex ['I', 'IV', 'V'] in D -> ['D', 'G', 'A']
# todo not fully implemented
def chord_roots_from_progression(progression_chord_numerals: list, root_note: str) -> list[str]:

    root_note_index = note_to_index.get(root_note)
    semitones_from_C = [(root_note_index + numeral_to_semitones.get(numeral)) % 12 for numeral in progression_chord_numerals]
    root_notes_in_progression = [index_to_note.get(note_index) for note_index in semitones_from_C]

    return root_notes_in_progression


if __name__ == '__main__':
    pass
    # user initial input:
    # strings: int [4, 12]
    # frets: int [12, 24]
    # tuning: str (give user as many options as input strings)

    # build the instrument neck
    # options to customize the colors of: frets, strings, fretboard, fret markers, fretboard material pattern

    # fretboard materials (need pngs): ebony, rosewood, maple, indian laurel, ovangkol, padauk, pau ferro, walnut, richlite, micarta, rocklite

    # user drawing input
    # choose chord(s) or scale
    # for chords, let user choose chord types
    # construct input space for each chord type for each of 12 notes
    # options to customize note marker shapes, colors
