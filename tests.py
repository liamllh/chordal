def fretboard_drawing_configurations():
    from graphics_tk import make_fretboard
    print("Odd string #, top-top markers")
    a, b, canvas, root = make_fretboard(36, tuning="E-A-D-G-B-E-C",
                                        single_marker_pos="top",
                                        double_marker_pos="top", )
    canvas.pack()
    root.mainloop()
    print("Odd string #, mid-mid markers")
    a, b, canvas, root = make_fretboard(36, tuning="E-A-D-G-B-E-C",
                                        single_marker_pos="middle",
                                        double_marker_pos="middle", )
    canvas.pack()
    root.mainloop()
    print("Odd string #, btm-btm markers")
    a, b, canvas, root = make_fretboard(36, tuning="E-A-D-G-B-E-C",
                                        single_marker_pos="bottom",
                                        double_marker_pos="bottom", )
    canvas.pack()
    root.mainloop()
    print("Even string #, top-top markers")
    a, b, canvas, root = make_fretboard(36, tuning="E-A-D-G-B-E",
                                        single_marker_pos="top",
                                        double_marker_pos="top", )
    canvas.pack()
    root.mainloop()
    print("Even string #, mid-mid markers")
    a, b, canvas, root = make_fretboard(36, tuning="E-A-D-G-B-E",
                                        single_marker_pos="middle",
                                        double_marker_pos="middle", )
    canvas.pack()
    root.mainloop()
    print("Even string #, btm-btm markers")
    a, b, canvas, root = make_fretboard(36, tuning="E-A-D-G-B-E",
                                        single_marker_pos="bottom",
                                        double_marker_pos="bottom", )
    canvas.pack()
    root.mainloop()


def graphics_test():
    from charting import build_chords, get_instrument_semitones_from_c, convert_chord_to_semitones
    from graphics_tk import mark_fret, make_fretboard, title_chart
    tuning = "F-A-C-G-B-E-G#-C#"
    posx, posy, canv, dummy = make_fretboard(
        30,
        tuning,
    )
    chty, chro = "M7", "F#"
    chord = convert_chord_to_semitones(chty, chro)
    instrument_semitones = get_instrument_semitones_from_c(30, tuning.split("-"))
    i = build_chords(
        chord,
        instrument_semitones,
    )
    for voicing in i:
        posx, posy, canv, root = make_fretboard(
            30,
            tuning,
        )
        for fret, string in voicing:
            thisx = posx[fret]
            thisy = posy[string]
            mark_fret(canv, thisx, thisy, 8, "#f4c2c2")
            title_chart(canv, chro + chty, (posx[0], posy[0]), "black")
        canv.pack()
        root.mainloop()


if __name__ == '__main__':
    graphics_test()