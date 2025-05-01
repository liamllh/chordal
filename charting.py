from chord_dicts import note_to_index, interval_to_integer, chords_to_intervals, sharp_to_flat, intervals_in_scales
from typing import Literal


def convert_chord_to_semitones(
        chord_type: str,
        chord_root: str,
) -> list[int]:
    """
    Gets semitones from C for each interval in a chord, given the chord root and chord type
    :param chord_type: Type of chord (see chord_dicts.chords_to_intervals)
    :param chord_root: Root note
    :return:
    """
    chord_intervals: list[str] = chords_to_intervals.get(chord_type)
    assert chord_intervals is not None, f"Chord type {chord_type} not recognized!"
    root_semitones = note_to_index.get(chord_root)
    interval_semitones: list[int] = [
        (root_semitones + interval_to_integer.get(interval)) % 12
        for interval in chord_intervals]

    return interval_semitones


def convert_scale_to_semitones(
        scale_type: str,
        scale_root: str,
) -> list[int]:

    scale_intervals: list[str] = intervals_in_scales.get(scale_type)
    assert scale_intervals is not None, f"Scale type {scale_type} not recognized!"
    root_semitones = note_to_index.get(scale_root)
    interval_semitones: list[int] = [
        (root_semitones + interval_to_integer.get(sharp_to_flat.get(interval))) % 12
        for interval in scale_intervals
    ]

    return interval_semitones


def get_instrument_semitones_from_c(
        num_frets: int,
        tuning: list[str],
) -> list[list[int]]:
    """
    Gets the semitones from C for each playable note in the instrument. Ordered higher-level by string and lower-level
        by fret.
    :param num_frets: Number of frets in the instrument
    :param tuning: Tuning of the instrument
    :return: Nested list of semitones from C
    """

    strings_semitones_from_c: list[list[int]] = list()
    for note in tuning:
        note_semitones_from_c = note_to_index.get(note)
        string_semitones_from_c: list[int] = [(note_semitones_from_c + i) % 12 for i in range(num_frets)]
        strings_semitones_from_c.append(string_semitones_from_c)\

    return strings_semitones_from_c


# gets human-playable range of frets given a list of frets already included in a chord
def update_allowed_fret_range(
        current_frets: list[int],
        total_frets: int,
        allowed_range: int = 4) -> list[int]:
    """
    Gets playable range of frets given current list of fretted notes
    :param current_frets: Currently fretted frets
    :param total_frets: Length of fretboard in frets
    :param allowed_range: Span of frets allowed
    :return:
    """
    # if we have not found any fretted notes or the fretted note is on an open string
    if not current_frets or current_frets == [0]:
        return [i for i in range(0, total_frets)]

    # ignore open strings; always allowed
    if 0 in current_frets:
        current_frets.remove(0)

    current_frets.sort()

    lower_bound = max(current_frets[-1] - allowed_range, 1)
    # we use a max of total_frets - 1 because they are used for indexing
    upper_bound = min(current_frets[0] + allowed_range, total_frets - 1)
    allowable_range = list(range(lower_bound, upper_bound))

    # open string always allowed
    allowable_range.insert(0, 0)

    return allowable_range


def permute_chord(
        chord_root: str,
        chord_type: str,
):
    full_output: list[list[int, int]] = list()

    return

def build_chord(
        string_interval_lists: list[list[int]],
        intervals_in_chord: list[int],
        mode: Literal["td", "bu", "mo"] = False,
        any_order_after_root: bool = False,
        first_string: int = 0,
) -> list[tuple[int, int]]:
    """
    Gets fret, string pairs playable on the instrument satisfying intervals_in_chord
    :param string_interval_lists: Lists of semitones from C for each fret for each string, ordered with strings
        top-level and frets bottom-level
    :param intervals_in_chord: (ordered) semitones from C in the chord
    :param mode: whether to search for valid notes starting at the lowest allowed fret ("bu"; bottom up), the highest
        allowed fret ("td"; top down) or fan out from the middle of the allowed range ("mo"; middle out)
    :param any_order_after_root: whether to preserve note order after finding root note
    :param first_string: First string to begin searching
    :return:
    """
    print(mode)
    chord_fretboard_indices = list()
    chord_fret_indices = list()
    string_index, chord_note_index = first_string, 0
    num_string_candidates: int = len(string_interval_lists)
    num_frets: int = len(string_interval_lists[0])
    allowed_frets = update_allowed_fret_range([], num_frets)
    print(f"{allowed_frets = }")

    # return when outside the range of strings
    while string_index < num_string_candidates:
        # todo allow for chord shapes out of order relative to the input intervals_in_chord
        current_interval = intervals_in_chord[chord_note_index]
        current_string_intervals = string_interval_lists[string_index]
        print(f"{current_string_intervals = }")
        allowed_string_intervals = [current_string_intervals[x] for x in allowed_frets]
        print(f"{allowed_string_intervals = }")
        fret_index = 0

        # top down mode
        if mode == "td" and len(chord_fretboard_indices) > 0:
            # reverse
            allowed_string_intervals: list[int] = allowed_string_intervals[::-1]
            allowed_frets_indexer: list[int] = list(range(len(allowed_string_intervals)))[::-1]

        elif mode == "mo" and len(chord_fretboard_indices) > 0:
            middle_fret: int = len(allowed_string_intervals) // 2
            current_fret = middle_fret
            allowed_frets_indexer: list[int] = [current_fret]
            # allowed fret indices oscillate around the middle fret
            for n in range(1, len(allowed_string_intervals)):
                current_fret += n * (-1) ** n
                allowed_frets_indexer.append(current_fret)

            print(f"{allowed_frets_indexer = }")
            # get allowed string intervals using this indexer
            allowed_string_intervals = [allowed_string_intervals[idx] for idx in allowed_frets_indexer]

        # default initial behavior is bottom up; we do not want to return repeats varying by octaves so we force the
        # root note to be the lowest possible
        else:  # mode == "bu"; no input sanitization because this is an intermediate in an internal function
            allowed_frets_indexer: list[int] = list(range(len(allowed_string_intervals)))

        print(f"{allowed_string_intervals = }\n{allowed_frets_indexer = }")
        # loop over all note intervals in the current string
        for string_interval in allowed_string_intervals:

            found_note = False  # indicate whether we have found a note on this string
            candidate_interval = string_interval

            if candidate_interval == current_interval:
                found_note = True
                chord_fretboard_indices.append((allowed_frets[allowed_frets_indexer[fret_index]], string_index))
                chord_fret_indices.append(allowed_frets[allowed_frets_indexer[fret_index]])

                # if we have as many notes in the constructed chord as in the chord intervals list, we have built the chord
                if len(chord_fretboard_indices) == len(intervals_in_chord):
                    return chord_fretboard_indices

                allowed_frets = update_allowed_fret_range(chord_fret_indices, num_frets)
                print(f"{allowed_frets = }")
                fret_index += 1
                chord_note_index += 1
                # now move to the next string

            if found_note:
                break

            fret_index += 1

        string_index += 1
        if string_index == len(string_interval_lists):
            break

    # avoid returning incomplete chord
    return chord_fretboard_indices if len(chord_fretboard_indices) == len(intervals_in_chord) else None


def build_chords(intervals_in_chord: list[int],
                 all_string_intervals: list[list[int]],
                 starting_string_index: int = 0,
                 inversion: int = 0,
                 ) -> list[tuple[int, int]] or None:
    """
    Searches for valid chords beginning at each string in the instrument
    :param intervals_in_chord: Semitones from C (ordered) for each interval in the chord
    :param all_string_intervals: Semitones from C for each fret for each string in the instrument
    :param starting_string_index: Initial string to begin search
    :param inversion: Chord inversion.
    :return:
    """

    # reorder intervals
    if inversion:
        assert inversion <= len(intervals_in_chord) - 1, f"This inversion cannot be constructed for this chord"
        inverted_interval = intervals_in_chord[inversion]
        intervals_in_chord.remove(inverted_interval)
        intervals_in_chord.insert(0, inverted_interval)

    # todo develop method to repeat semitones, ex the G major barre [(3, 0), (5, 1), (5, 2), (4, 3), (3, 4), (3, 5)]
    # comprised of semitones (relative to C): [7, 2, 7, 11, 2, 7]

    # restrictions:
    #   each semitone in the chord must be present in the reordered / possibly repeated chord
    #   the first semitone must be the root
    #   consecutive semitones must not be the same
    # starting from G major: [7, 11, 2]
    # first, permute the notes past the root, appending each of these permutations to the root note
    # [7, 11, 2] -> [7, 11, 2] & [7, 2, 11]
    # then,

    chord_list = []
    first_string_index = starting_string_index
    num_strings: int = len(all_string_intervals)
    # starting on each string with enough higher strings to allow chord to be built
    while first_string_index < num_strings - len(intervals_in_chord) + 1:
        chord_fretboard_indices_bu = build_chord(all_string_intervals, intervals_in_chord, first_string=first_string_index, mode="bu")
        chord_fretboard_indices_mo = build_chord(all_string_intervals, intervals_in_chord, first_string=first_string_index, mode="mo")
        chord_fretboard_indices_td = build_chord(all_string_intervals, intervals_in_chord, first_string=first_string_index, mode="td")

        if chord_fretboard_indices_bu:
            print(f"bu found {chord_fretboard_indices_bu}")
            chord_list.append(chord_fretboard_indices_bu)
        if chord_fretboard_indices_bu:
            print(f"mo found {chord_fretboard_indices_mo}")
            chord_list.append(chord_fretboard_indices_mo)
        if chord_fretboard_indices_td:
            print(f"td found {chord_fretboard_indices_td}")
            chord_list.append(chord_fretboard_indices_td)

        first_string_index += 1

    # remove potential duplicates from different chord id methods
    # need to turn each entry to tuple to avoid TypeError unhashable type 'list'
    chord_list = list(set([tuple(voicing) for voicing in chord_list]))
    print(chord_list)
    return chord_list


# returns pairs of [fret, string] for notes belonging to a given scale on the fretboard
def build_scale(
        scale_intervals: list[int],
        all_string_intervals: list[list[int]]
    ) -> list[list[int, int]]:

    string_fret_pairs = list()

    string_index: int = 0
    for single_string_intervals in all_string_intervals:

        fret_index: int = 0
        for interval in single_string_intervals:

            if interval in scale_intervals:
                pair: list[int, int] = [fret_index, string_index]
                string_fret_pairs.append(pair)

            fret_index += 1

        string_index += 1

    return string_fret_pairs


# similar to build scale, but limited to notes on frets +- some range from the fret index of the first note in the arpeggio
# search range for the first interval will be the same as the search range for the last string
def build_arpeggio(string_semitone_lists: list[list[int]], semitones_in_arpeggio: list[int], retry=False):

    arpeggio_fret_string_pairs = list()
    string_index, arpeggio_note_index = 0, 0
    num_string_candidates = len(string_semitone_lists)
    num_frets = len(string_semitone_lists[0])

    # first note of interval list on first string defines initial allowed fret range
    root_fret = string_semitone_lists[0].index(semitones_in_arpeggio[0])
    allowed_frets = update_allowed_fret_range_arpeggio(root_fret, num_frets)

    while string_index < num_string_candidates:

        frets_on_string = list()
        arpeggio_notes_on_string = 0
        current_string_intervals = string_semitone_lists[string_index]
        current_string_intervals = [current_string_intervals[x] for x in allowed_frets]
        fret_index = 0

        # loop over all note intervals in the current string
        for current_string_interval in current_string_intervals:

            search_interval = semitones_in_arpeggio[arpeggio_note_index % len(semitones_in_arpeggio)]
            # print(f"string {string_index + 1} allowed frets in range [{allowed_frets[0]}, {allowed_frets[-1]}]")
            if current_string_interval == search_interval:

                current_fret_index = allowed_frets[fret_index]
                arpeggio_fret_string_pairs.append([current_fret_index, string_index])
                frets_on_string.append(current_fret_index)
                allowed_frets = update_allowed_fret_range_arpeggio(frets_on_string[0], num_frets)

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


def update_allowed_fret_range_arpeggio(root_fret, total_frets, allowed_range=3) -> list[int]:

    if root_fret - allowed_range < 0:
        lower_bound = 0
        upper_bound = 2 * allowed_range + 1

    else:
        lower_bound = root_fret - allowed_range
        upper_bound = min(root_fret + allowed_range + 2, total_frets - 1)

    return list(range(lower_bound, upper_bound + 1))


# todo detect barre
# if none of the strings in the voicing are open
    # if the lowest fretted string is repeated
        # remove barred points from draw markers and draw a barre across these strings,
        # returning the two exterior fret string pairs which define the bar

if __name__ == '__main__':
    from graphics_tk import make_fretboard
    tuning = "D-A-F#-A-C#-E"
    make_fretboard(
        30,
        tuning,
    )
    chord = convert_chord_to_semitones("M7", "C")
    instrument_semitones = get_instrument_semitones_from_c(30, tuning.split("-"))
    i = build_chords(
            chord,
            instrument_semitones,
    )

    print(i)