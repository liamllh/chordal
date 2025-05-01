from itertools import (combinations,  # for getting all possible subsets of strings to use in voicing a chord
                       compress)  # for indexing a list using bool array


def filter_instrument_range(
        semitones_in_instrument: list[list[int]],
        range_above_below: int,
        starting_string_idx: int,
        num_frets: int) -> list[list[int]]:
    # chords built from above the maximum range below the octave are redundant and can be constructed from lower frets
    max_non_redundant_fret = min(11 + 2 * range_above_below, num_frets)
    semitones_in_instrument_fret_filter = semitones_in_instrument[:][:max_non_redundant_fret]
    semitones_in_instrument_filtered = semitones_in_instrument_fret_filter[starting_string_idx:]
    return semitones_in_instrument_filtered


def get_allowed_fret_ranges(
        required_first_string_fret: int,
        range_above_below: int,
        num_frets: int,
) -> tuple[list[list[int]], list[bool]]:

    allowed_fret_range = 2 * range_above_below
    if required_first_string_fret <= range_above_below:
        # first case: required first voicing fret is close to the open string -
        # we need to account for fret ranges that might reach the 10th and 11th frets
        possible_ranges_lo: list[list[int]] = [
            list(range(i, min(i + allowed_fret_range, num_frets + 1)))
            for i in range(0, required_first_string_fret + 1)
        ]
        # second case: required first voicing fret is at the octave above the open string
        # (allows for fretting above the octave but reaching below it on higher strings)
        possible_ranges_hi: list[list[int]] = [
            [0] + list(range(i, min(i + allowed_fret_range, num_frets + 1)))
            # the starting range index may go up to 11; 12 or above is reducible to a lower octabe
            for i in range(required_first_string_fret - allowed_fret_range + 13, 12)
        ]
        possible_ranges = possible_ranges_lo + possible_ranges_hi
        range_is_hi_arr: list[bool] = [False for _ in range(len(possible_ranges_lo))] + [True for _ in range(len(possible_ranges_hi))]

    else:
        possible_ranges: list[list[int]] = [
            [0] + list(range(i, min(allowed_fret_range + i, num_frets)))
            for i in range(max(1, required_first_string_fret - allowed_fret_range), required_first_string_fret + 1)]
        range_is_hi_arr: list[bool] = [False for _ in range(len(possible_ranges))]

    return possible_ranges, range_is_hi_arr


def build_chord_better(
        semitones_in_instrument: list[list[int]],
        semitones_in_chord: list[int],
        range_above_below = 2,
        starting_string_idx = 0,
#    ------ fretted chord part -------  ------------------- barred chord part --------------------
) -> tuple[list[list[tuple[int, int]]], list[tuple[list[tuple[int, int]], list[tuple[int, int]]]]]:

    num_frets, num_strings = len(semitones_in_instrument[0]), len(semitones_in_instrument)
    num_strings = num_strings - starting_string_idx
    semitones_in_instrument = filter_instrument_range(semitones_in_instrument, range_above_below, starting_string_idx, num_frets)
    first_string_semitones = semitones_in_instrument[0]
    root_note = semitones_in_chord[0]
    required_first_string_fret = first_string_semitones.index(root_note, 0, 12)

    # apply condition 1: the root note must be in the allowed range of the first string
    possible_fret_ranges, root_is_hi_bool_arr = get_allowed_fret_ranges(required_first_string_fret, range_above_below, num_frets)

    semitones_in_possible_fret_ranges = [[[
        string_semitones[fret]
        for fret in possible_frets]
        for string_semitones in semitones_in_instrument[1:]]  # ignore the first string; this voicing is already fixed
        for possible_frets in possible_fret_ranges]

    # apply condition 2: ensure that each note of the chord is present at least once in the allowed range across all strings
    remaining_notes = semitones_in_chord[1:]
    for fret_range_idx, strings_semitones in enumerate(semitones_in_possible_fret_ranges):

        for remaining_note in remaining_notes:
            note_is_in_string = [remaining_note in string_semitones for string_semitones in strings_semitones]
            if not any(note_is_in_string):
                # we know that at least one of the notes in the chord we want to form is not present across any of these
                # strings at this fret range; remove this range from consideration
                semitones_in_possible_fret_ranges.remove(strings_semitones)
                possible_fret_ranges.pop(fret_range_idx)
                break

    # now we know the ranges may all potentially give valid chords:
    # we must find the indices on each string which have a note in the chord
    any_chord_note_is_on_fret: list[list[list[bool]]] = list()
    for strings_semitones in semitones_in_possible_fret_ranges:
        possible_fret_range_note_idx_array: list[list[bool]] = list()

        for string_semitones in strings_semitones:
            fret_is_in_chord: list[bool] = [
                fret_semitone in semitones_in_chord
                for fret_semitone in string_semitones]
            possible_fret_range_note_idx_array.append(fret_is_in_chord)

        any_chord_note_is_on_fret.append(possible_fret_range_note_idx_array)

    # semitones which are both in each prospeective fret ranges and the chord
    chord_semitones_in_fret_ranges: list[list[list[int]]] = list()
    # frets containing semitones in prospective fret ranges and chord
    chord_frets_in_fret_ranges: list[list[list[int]]] = list()

    for idx, strings_semitones in enumerate(semitones_in_possible_fret_ranges):

        chord_semitones_in_this_fret_range: list[list[int]] = list()
        chord_frets_in_this_fret_range: list[list[int]] = list()

        for jdx, string_semitones in enumerate(strings_semitones):
            # boolean filter
            semitones_on_this_string_in_chord = list(compress(string_semitones, any_chord_note_is_on_fret[idx][jdx]))
            frets_on_this_string_in_chord = list(compress(possible_fret_ranges[idx], any_chord_note_is_on_fret[idx][jdx]))

            chord_semitones_in_this_fret_range.append(semitones_on_this_string_in_chord)
            chord_frets_in_this_fret_range.append(frets_on_this_string_in_chord)

        chord_semitones_in_fret_ranges.append(chord_semitones_in_this_fret_range)
        chord_frets_in_fret_ranges.append(chord_frets_in_this_fret_range)

    # we need to get allowed subsets of strings to use to form chords;
    # the minimum number of strings needed is len(remaining_notes);
    # the maximum number of strings allowed is num_strings
    # we must get all possible string subsets for each allowed number of strings
    allowed_strings = range(len(remaining_notes), num_strings)
    all_string_subsets: list[tuple[int, ...]] = list()
    # dim 1: fret range subset
    # dim 2: string subset
    # dim 3: all combinations of frets/semitones comprising potential chord
    # dim 4: frets/semitones comprising potential chord
    all_subsets_string_fret_combinations: list[list[list[list[int]]]] = list()
    all_subsets_string_semitone_combinations: list[list[list[list[int]]]] = list()
    subset_chord_candidate_string_correspondence: list[list[list[tuple[int, ...]]]] = list()
    # do subdivisions
    for strings_to_use in allowed_strings:
        string_subsets: list[tuple[int, ...]] = list(combinations(range(num_strings - 1), strings_to_use))

        for subset in string_subsets:
            all_string_subsets.append(subset)

    # repeat chord procedure across all subsets
    for string_subset in all_string_subsets:

        # all possible combinations of in-chord fret indices over the current string subset
        this_subset_string_fret_combinations: list[list[list[int]]] = list()
        # semitones corresponding to the fret combination chosen above
        this_subset_string_semitone_combinations: list[list[list[int]]] = list()
        # a record of the string subset used to create string-fret tuples later
        this_subset_chord_candidate_string_correspondence: list[list[tuple[int, ...]]] = list()

        for idx, chord_semitones_in_this_fret_range in enumerate(chord_semitones_in_fret_ranges):
            # filter fret range to string subset and extract frets and notes
            chord_semitones_in_this_fret_range_subset = [chord_semitones_in_this_fret_range[string] for string in string_subset]
            chord_frets_in_this_fret_range = chord_frets_in_fret_ranges[idx]
            chord_frets_in_this_fret_range_subset = [chord_frets_in_this_fret_range[string] for string in string_subset]

            # generate all combinations of frets and their corresponding semitones in this string subset
            num_combinations = 1
            for string_frets_in_this_fret_range_subset in chord_frets_in_this_fret_range_subset:
                num_combinations *= len(string_frets_in_this_fret_range_subset)

            # initialize empty vector of size num_combinations
            string_fret_combinations: list[list[int]] = [[] for _ in range(num_combinations)]
            string_semitone_combinations: list[list[int]] = [[] for _ in range(num_combinations)]

            # for indexing s.t. every unique combination is generated - defines the repeat length of individual
            # frets within the allowed frets
            current_stride = 1
            this_string_subset: list[tuple[int, ...]] = list()  # initialize to avoid error

            for jdx, string_frets_in_this_fret_range_subset in enumerate(chord_frets_in_this_fret_range_subset):
                string_semitones_in_this_fret_range_subset = chord_semitones_in_this_fret_range_subset[jdx]
                possible_frets = len(string_frets_in_this_fret_range_subset)
                this_string_subset: list[tuple[int, ...]] = list()

                # we modulate the pattern multiplicity inversely to the stride multiplicity to ensure that each
                # appending pattern is the same length
                appending_pattern_semitones = [
                    string_semitone
                    for _ in range(current_stride)  # multiplicity of each note in pattern
                    for string_semitone in string_semitones_in_this_fret_range_subset
                    for __ in range(num_combinations // (current_stride * possible_frets))  # multiplicity of whole pattern
                ]

                appending_pattern_frets = [
                    string_fret
                    for _ in range(current_stride)  # multiplicity of each note in pattern
                    for string_fret in string_frets_in_this_fret_range_subset
                    for __ in range(num_combinations // (current_stride * possible_frets))  # multiplicity of whole pattern
                ]

                for kdx, semitone_entry in enumerate(appending_pattern_semitones):
                    string_semitone_combinations[kdx].append(semitone_entry)
                for kdx, fret_entry in enumerate(appending_pattern_frets):
                    string_fret_combinations[kdx].append(fret_entry)
                # need the right multiplicity so ssc, sfc, and ss arrays are indexed equivalently
                for _ in range(len(string_fret_combinations)):
                    this_string_subset.append(string_subset)

                current_stride *= possible_frets

            this_subset_string_fret_combinations.append(string_fret_combinations)
            this_subset_string_semitone_combinations.append(string_semitone_combinations)
            this_subset_chord_candidate_string_correspondence.append(this_string_subset)

        all_subsets_string_fret_combinations.append(this_subset_string_fret_combinations)
        all_subsets_string_semitone_combinations.append(this_subset_string_semitone_combinations)
        subset_chord_candidate_string_correspondence.append(this_subset_chord_candidate_string_correspondence)

    master_combination_string_fret_tuples: list[list[tuple[int, int]]] = list()
    master_combination_string_semitone_tuples: list[list[tuple[int, int]]] = list()

    # all combinations are formed; now we need to pack into fret-string tuples for checking playability:
    for fret_range_idx, fret_range_semitone_split in enumerate(all_subsets_string_semitone_combinations):
        for string_subset_idx, string_subset_fret_range_semitone_split in enumerate(fret_range_semitone_split):

            # ex. if the root is F and the first open string is E, there are different chords available with the root
            # voiced on the 1st vs. the 13th fret; here we keep track of which root gave rise to which range
            range_uses_hi_root = root_is_hi_bool_arr[string_subset_idx]
            root_fret: int = required_first_string_fret + 12 * int(range_uses_hi_root)

            for combination_idx, semitone_combination_split in enumerate(string_subset_fret_range_semitone_split):

                fret_combination_split = all_subsets_string_fret_combinations[fret_range_idx][string_subset_idx][combination_idx]
                string_idxs = subset_chord_candidate_string_correspondence[fret_range_idx][string_subset_idx][combination_idx]
                this_combination_string_fret_tuples: list[tuple[int, int]] = list()
                this_combination_string_semitone_tuples: list[tuple[int, int]] = list()

                # add root note
                this_combination_string_fret_tuples.append((starting_string_idx, root_fret))
                this_combination_string_semitone_tuples.append((starting_string_idx, semitones_in_chord[0]))

                # add found notes
                for fret_idx, fret in enumerate(fret_combination_split):
                    this_combination_string_fret_tuples.append(
                        # add 1 for indexing (we ignore starting string for finding additional notes)
                        (string_idxs[fret_idx] + starting_string_idx + 1, fret))

                for semitone_idx, semitone in enumerate(semitone_combination_split):
                    this_combination_string_semitone_tuples.append(
                        (string_idxs[semitone_idx] + starting_string_idx + 1, semitone))

                master_combination_string_fret_tuples.append(this_combination_string_fret_tuples)
                master_combination_string_semitone_tuples.append(this_combination_string_semitone_tuples)

    validated_chord_string_fret_tuples: list[list[tuple[int, int]]] = list()
    validated_barre_string_fret_tuples: list[list[tuple[int, int]]] = list()
    for combination_idx, string_semitone_tuples in enumerate(master_combination_string_semitone_tuples):

        strings_in_chord = [string_semitone_tuple[0] for string_semitone_tuple in string_semitone_tuples]
        string_fret_tuples = master_combination_string_fret_tuples[combination_idx]
        num_voicing_notes = len(string_semitone_tuples)

        # apply rule 1: each semitone in the chord must be represented in the combination
        semitones_in_combination = [string_semitone_tuple[1] for string_semitone_tuple in string_semitone_tuples]
        frets_in_combination = [string_fret_tuple[1] for string_fret_tuple in string_fret_tuples]
        if not all([chord_semitone in semitones_in_combination for chord_semitone in semitones_in_chord]):
            continue

        # apply rule 2: notes on consecutive strings may not be identical
        for semitone_idx, semitone in enumerate(semitones_in_combination[:-1]):
            next_semitone = semitones_in_combination[semitone_idx + 1]
            if semitone == next_semitone:
                continue

        # apply rule 3:
        # check if valid barre:
        # if there are no open notes
        if not 0 in frets_in_combination:
            min_fret = min(frets_in_combination)
            # if all the notes in the chord are consecutive
            if strings_in_chord == list(range(strings_in_chord[0], strings_in_chord[-1] + 1)):
                # if there are multiple notes at the lowest fret
                num_barre_notes = frets_in_combination.count(min_fret)
                if num_barre_notes > 1:
                    # if there are no more than 3 non-barre notes
                    num_non_barre_notes = num_voicing_notes - num_barre_notes
                    if num_non_barre_notes <= 3:
                        validated_barre_string_fret_tuples.append(string_fret_tuples)
                        continue

        num_fretted_voicing_notes = num_voicing_notes - frets_in_combination.count(0)
        # if not valid barre, remove all entries with more than 4 fretted notes
        if num_fretted_voicing_notes > 4:
            continue

        validated_chord_string_fret_tuples.append(string_fret_tuples)

    validated_chord_string_fret_tuples = list(
        list(x)
        for x in set(frozenset(x)
        for x in validated_chord_string_fret_tuples))
    validated_barre_string_fret_tuples = list(
        list(x)
        for x in set(frozenset(x)
        for x in validated_barre_string_fret_tuples))

    handled_validated_barre_string_fret_tuples: list[tuple[list[tuple[int, int]], list[tuple[int, int]]]] = [
        handle_barre_chord(barre_chord) for barre_chord in validated_barre_string_fret_tuples
    ]

    return validated_chord_string_fret_tuples, handled_validated_barre_string_fret_tuples


def handle_barre_chord(
        barre_chord: list[tuple[int, int]]
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:

    frets_in_chord: list[int] = [string_fret_pair[1] for string_fret_pair in barre_chord]

    barre_fret: int = min(frets_in_chord)
    barred_strings: list[int] = list()
    barre_chord_fretted: list[tuple[int, int]] = list()
    barre_chord_barred: list[tuple[int, int]] = list()

    for string_fret_pair in barre_chord:
        if string_fret_pair[1] == barre_fret:
            barred_strings.append(string_fret_pair[0])
            barre_chord_barred.append(string_fret_pair)
        else:
            barre_chord_fretted.append(string_fret_pair)

    first_barre_string: int = min(barred_strings)
    last_barre_string: int = max(barred_strings)
    first_barre_pair: tuple[int, int] = barre_chord_barred[barred_strings.index(first_barre_string)]
    last_barre_pair: tuple[int, int] = barre_chord_barred[barred_strings.index(last_barre_string)]

    return barre_chord_fretted, [first_barre_pair, last_barre_pair]


if __name__ == '__main__':
    pass
