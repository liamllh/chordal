"""from tkinter import Tk, Frame, Label, font, Button, Entry, OptionMenu, Canvas
from tkinter import NORMAL, DISABLED
from tkinter import IntVar, StringVar"""
from tkinter.ttk import *  # todo if i import all the tk button class gets overridden, but if i don't styles aren't recognized
from tkinter import Tk, Frame, Label, Button, Entry, OptionMenu, Canvas, NORMAL, DISABLED, IntVar, StringVar
from tkinter.font import Font
from typing import Literal

from chord_dicts import note_to_index, chords_to_intervals, intervals_in_scales
from style_dicts import hex_style_dict, instrument_presets
from instruments import Instrument
from math import ceil


# still todo
# switch dropdown menu icons to something better
# general style stuff (background color, frame outlines, widget shapes, etc)
# set the chord/arp/scale bg to the instrument bg to avoid flashing on changing pages
# set button/label styles for viewing based on instrument style
# adjust page next/back region for chord viewing
# implement fret marker shapes
# allow scrolling on chord view pages
# save button

def split_columns_evenly(frame: Frame | Tk, n: int, max_columns: int = 5):

    for i in range(max_columns):
        if i < n:
            frame.columnconfigure(i, weight=1)
        # reset all columns past the ones we want to reconfigure
        else:
            frame.columnconfigure(i, weight=0)

    return


class InstrumentPreviewImage:

    def __init__(
            self,
            style: str,
            num_frets: int,
            tuning: str,
            instrument_preview_frame: Frame,
    ):
        self.style = style
        self.num_frets = num_frets
        self.tuning = tuning
        self.instrument_preview_frame = instrument_preview_frame
        self.curr_instrument = Instrument(
            num_frets,
            tuning,
            instrument_preview_frame,
            style=self.style,
        )

    def update(
            self,
            style: str,
            num_frets: int,
            tuning: str,
    ):
        # ungrid last canvas preview, update parameters, grid
        self.curr_instrument.template_canvas.grid_forget()
        self.style = style
        self.num_frets = num_frets
        self.tuning = tuning
        self.curr_instrument = Instrument(
            self.num_frets,
            self.tuning,
            self.instrument_preview_frame,
            style=self.style,
        )
        self.curr_instrument.template_canvas.grid(row=2, column=0, columnspan=2)


class EveryChord:

    def __init__(
            self,
            default_tuning: str = "E-A-D-G-B-E",
            default_fret_number: int = 22,
            default_preset: str = "Standard guitar",
            default_style: str = "Neon green",
            default_chord_root: str = "C",
            default_chord_type: str = " major",
            default_scale_root: str = "C",
            default_scale_type: str = "major",
            default_arp_root: str = "C",
            default_arp_type: str = "M7",
            default_pagination: int = 3,
    ):
        # project assets
        self.master = Tk()
        split_columns_evenly(self.master, 3)
        # project styles
        self.header_font = Font(
                size=24,
                family="Quicksand",
                weight="bold",)
        self.project_font = Font(
                size=12,
                family="Quicksand",)
        self.app_width = 960
        self.app_height = 1080
        self.app_geometry = f"{self.app_width}x{self.app_height}"
        self.app_style = Style()
        # button styles
        self.app_style.configure(
            'EC.TButton',
            font=self.project_font,
            width=14,
        )

        self.button_width = 14

        # we must initialize all frames independently first, because the classes depend circularly on each other
        self.main_menu_frame = Frame(master=self.master)
        self.instrument_preset_frame = Frame(master=self.master)
        self.instrument_creation_frame = Frame(master=self.master)
        self.instrument_preview_window_frame = Frame(master=self.master)
        self.chart_type_selection_frame = Frame(master=self.master)
        self.chord_selection_frame = Frame(master=self.master)
        # because chords are paginated, we have to initialize these pages as null
        self.pages: list[Frame] = list()
        self.fretboard_storage_frame = Frame(master=self.master)
        self.scale_selection_frame = Frame(master=self.master)
        self.scale_viewer_frame = Frame(master=self.master)
        self.arpeggio_selection_frame = Frame(master=self.master)
        self.arpeggio_viewer_frame = Frame(master=self.master)

        # initialize other circular variables
        self.tuning_entry_var = StringVar()
        self.tuning_entry_var.set(default_tuning)
        self.tuning_entry_is_valid = True
        self.fret_num_var = IntVar()
        self.fret_num_var.set(default_fret_number)
        self.fret_num_is_valid = True

        self.instrument_preview = InstrumentPreviewImage(
            default_style, default_fret_number, default_tuning, self.instrument_preview_window_frame)

        self.preset_var = StringVar()
        self.preset_var.set(default_preset)
        self.style_var = StringVar()
        self.style_var.set(default_style)
        self.choice_var = StringVar()
        self.choice_var.set("Chord")

        self.chord_root_var = StringVar()
        self.chord_root_var.set(default_chord_root)
        self.chord_type_var = StringVar()
        self.chord_type_var.set(default_chord_type)
        self.scale_root_var = StringVar()
        self.scale_root_var.set(default_scale_root)
        self.scale_type_var = StringVar()
        self.scale_type_var.set(default_scale_type)
        self.arp_root_var = StringVar()
        self.arp_root_var.set(default_arp_root)
        self.arp_type_var = StringVar()
        self.arp_type_var.set(default_arp_type)
        self.default_pagination = default_pagination
        self.previous_frame = self.instrument_preset_frame

        self.main_menu = MainMenu(self)
        self.main_menu_frame.grid(column=1)
        self.instrument_creation = InstrumentCreation(self)
        self.instrument_preset = InstrumentPreset(self)
        self.instrument_preview_window = InstrumentPreview(self)
        self.chart_type_selection = ChartSelection(self)
        self.chord_selection = ChordSelection(self)
        self.chord_viewer = ChordViewer(self)
        self.scale_selection = ScaleSelection(self)
        self.scale_viewer = ScaleViewer(self)
        self.arpeggio_selection = ArpeggioSelection(self)
        self.arpeggio_viewer = ArpeggioViewer(self)

        # initialize start screen
        self.master.title("Everychord")
        self.master.geometry(self.app_geometry)
        self.master.resizable(True, True)
        self.master.mainloop()


class MainMenu:

    def __init__(self, app: EveryChord):

        self.app = app

        self.working_logo = Label(
            master=self.app.main_menu_frame,
            text="Everychord",
            font=self.app.header_font,
        )
        self.create_instrument_button = Button(
            master=self.app.main_menu_frame,
            text="New instrument",
            command=lambda: self.to_new_instrument(),
        )
        # self.create_instrument_button.config(style='EC.TButton')
        self.create_instrument_button.config()

        self.load_preset_button = Button(
            master=self.app.main_menu_frame,
            text="Load preset",
            font=self.app.project_font,
            command=lambda: self.to_instrument_presets(),
            width=self.app.button_width
        )

        self.close_program_button = Button(
            master=self.app.main_menu_frame,
            text="Exit",
            font=self.app.project_font,
            command=lambda: self.exit(),
            width=self.app.button_width
        )

        self.working_logo.grid(row=0, column=0, columnspan=2)
        self.create_instrument_button.grid(row=1, column=1)
        self.load_preset_button.grid(row=2, column=1)
        self.close_program_button.grid(row=3, column=1)

    def to_new_instrument(self):
        self.app.main_menu_frame.grid_forget()
        self.app.instrument_creation_frame.grid(column=1)
        return

    def to_instrument_presets(self):
        self.app.main_menu_frame.grid_forget()
        self.app.instrument_preset_frame.grid(column=1)
        return

    def exit(self):
        self.app.master.destroy()
        return


class InstrumentPreset:

    def __init__(self, app: EveryChord):

        self.app = app
        split_columns_evenly(self.app.instrument_preset_frame, 2)

        self.available_presets = list(instrument_presets.keys())
        self.available_presets.remove(self.app.preset_var.get())
        self.app.preset_var.trace_add("write", self.preset_callback)

        self.presets = OptionMenu(
            self.app.instrument_preset_frame,
            self.app.preset_var,
            self.app.preset_var.get(),
            *self.available_presets
        )
        self.presets.config(font=self.app.project_font)
        self.presets.config(width=self.app.button_width)

        self.tuning_feedback_label = Label(
            master=self.app.instrument_preset_frame,
            text="Tuning: ",
            font=self.app.project_font,
        )
        self.tuning_feedback = Label(
            master=self.app.instrument_preset_frame,
            text=str(instrument_presets.get(app.preset_var.get())[1]),  # default tuning to instantiate
            font=self.app.project_font,
        )
        self.fret_num_feedback_label = Label(
            master=self.app.instrument_preset_frame,
            text="Frets: ",
            font=self.app.project_font,
        )
        self.fret_num_feedback = Label(
            master=self.app.instrument_preset_frame,
            text=str(instrument_presets.get(app.preset_var.get())[0]),
            font=self.app.project_font,
        )

        self.next_button = Button(
            master=self.app.instrument_preset_frame,
            font=self.app.project_font,
            text="Next",
            command=lambda: self.next(),
            width=self.app.button_width,
        )

        self.back_button = Button(
            text="Back",
            master=self.app.instrument_preset_frame,
            command=lambda: self.back(),
            font=self.app.project_font,
            width=self.app.button_width,
        )

        self.presets.grid(row=1, column=0, columnspan=2)
        self.back_button.grid(row=0, column=0, sticky="E")
        self.next_button.grid(row=0, column=1, sticky="W")
        self.fret_num_feedback.grid(row=2, column=1, sticky="W")
        self.tuning_feedback.grid(row=3, column=1, sticky="W")
        self.fret_num_feedback_label.grid(row=2, column=0, sticky="E")
        self.tuning_feedback_label.grid(row=3, column=0, sticky="E")


    def preset_callback(self, var, mode, index):

        curr_preset = self.app.preset_var.get()
        curr_frets, curr_tuning = instrument_presets.get(curr_preset)
        self.app.fret_num_var.set(curr_frets)
        self.app.tuning_entry_var.set(curr_tuning)
        self.tuning_feedback.config(text=curr_tuning)
        self.fret_num_feedback.config(text=curr_frets)

        return

    def next(self):
        # record which frame to return to upon instrument preview back button press
        self.app.previous_frame = self.app.instrument_preset_frame
        self.app.instrument_preset_frame.grid_forget()
        self.app.instrument_preview_window_frame.grid(column=1)
        return

    def back(self):
        self.app.instrument_preset_frame.grid_forget()
        self.app.main_menu_frame.grid(column=1)
        return


class InstrumentCreation:

    def __init__(self, app: EveryChord):

        self.app = app
        split_columns_evenly(self.app.instrument_creation_frame, 2)

        self.tuning_error_label = Label(
            master=self.app.instrument_creation_frame,
            text="",
            font=self.app.project_font,
        )

        self.fret_num_error_label = Label(
            master=self.app.instrument_creation_frame,
            text="",
            font=self.app.project_font,
        )

        self.app.fret_num_var.trace_add("write", self.fret_num_entry_callback)
        self.fret_num_entry = Entry(
            master=self.app.instrument_creation_frame,
            textvariable=self.app.fret_num_var,
        )

        self.app.tuning_entry_var.trace_add('write', self.tuning_entry_callback)
        self.tuning_entry = Entry(
            master=self.app.instrument_creation_frame,
            textvariable=self.app.tuning_entry_var,
        )

        self.fret_num_entry_label = Label(
            text="Number of frets",
            master=self.app.instrument_creation_frame,
            font=self.app.project_font,
        )

        self.tuning_label = Label(
            text="Tuning",
            master=self.app.instrument_creation_frame,
            font=self.app.project_font,
        )

        self.next_button = Button(
            master=self.app.instrument_creation_frame,
            font=self.app.project_font,
            text="Next",
            command=lambda: self.next(),
            state=DISABLED,
            width=self.app.button_width,
        )

        self.back_button = Button(
            text="Back",
            master=self.app.instrument_creation_frame,
            command=lambda: self.back(),
            font=self.app.project_font,
            width=self.app.button_width,
        )

        self.fret_num_entry_label.grid(row=1, column=0)
        self.fret_num_entry.grid(row=1, column=1)
        self.fret_num_error_label.grid(row=2, column=0, columnspan=2)
        self.tuning_label.grid(row=3, column=0)
        self.tuning_entry.grid(row=3, column=1)
        self.tuning_error_label.grid(row=4, column=0, columnspan=2)

        self.back_button.grid(row=0, column=0)
        self.next_button.grid(row=0, column=1)
        # perform initial validation (default variables should be valid)
        self.tuning_entry_callback(None, None, None)


    def fret_num_entry_validate(self) -> tuple[bool, str]:
        try:
            fret_num = int(self.app.fret_num_var.get())
        except Exception as e:
            print(e)
            return False, "Fret number must be an integer"
        if not (2 < fret_num <= 36):
            return False, "Frets must be between 3 and 36"
        return True, "validated"

    def tuning_entry_validate(self) -> tuple[bool, str]:
        # avoid giving an error msg for empty entry, but still prevent next button from activating
        entry = self.app.tuning_entry_var.get()
        if entry is None:
            return False, ""
        # sanitize input; delete all entries past the max valid entry length
        if len(entry) > 35:  # at most 12-string instrument; worst case, "C#-C#-C#-..." = 35 chars (11 * 3 + 2)
            self.app.tuning_entry_var.set(entry[:35])
            entry = entry[:35]

        note_list = entry.split("-")
        num_strings = len(note_list)
        if num_strings > 12:
            return False, f"Instrument must have 12 or fewer strings (current: {num_strings})"
        for note in note_list:
            # validate each note
            if note == "":
                return False, "Invalid final character"
            if note not in note_to_index.keys():
                return False, f"Note {note} not recognized"

        return True, "validated"


    def fret_num_entry_callback(self, var, index, mode):

        self.app.fret_num_is_valid, message = self.fret_num_entry_validate()
        if self.app.fret_num_is_valid:
            self.fret_num_error_label.config(text="")
            self.fret_num_error_label.grid(row=2, column=0, columnspan=2)

            # release next button if both valid
            if self.app.tuning_entry_is_valid:
                self.app.instrument_preview.update(
                    self.app.style_var.get(),
                    self.app.fret_num_var.get(),
                    self.app.tuning_entry_var.get())
                self.next_button.config(state=NORMAL)

        else:
            self.fret_num_error_label.config(text=message)
            self.fret_num_error_label.grid(row=2, column=0, columnspan=2)
            self.next_button.config(state=DISABLED)

    def tuning_entry_callback(self, var, index, mode, ):

        self.app.tuning_entry_is_valid, message = self.tuning_entry_validate()

        if self.app.tuning_entry_is_valid:
            self.tuning_error_label.config(text="")
            self.tuning_error_label.grid(row=4, column=0, columnspan=2)

            # release next button and update preview in the background if both valid
            if self.app.fret_num_is_valid:
                self.app.instrument_preview.update(
                    self.app.style_var.get(),
                    self.app.fret_num_var.get(),
                    self.app.tuning_entry_var.get())
                self.next_button.config(state=NORMAL)

        else:
            self.tuning_error_label.config(text=message)
            self.tuning_error_label.grid(row=4, column=0, columnspan=2)
            self.next_button.config(state=DISABLED)

    def next(self):
        # record which frame to return to upon instrument preview back button press
        self.app.previous_frame = self.app.instrument_creation_frame
        self.app.instrument_creation_frame.grid_forget()
        self.app.instrument_preview_window_frame.grid(column=1)

    def back(self):
        self.app.instrument_creation_frame.grid_forget()
        self.app.main_menu_frame.grid(column=1)


class InstrumentPreview:

    def __init__(self, app: EveryChord):

        self.app = app
        split_columns_evenly(self.app.instrument_preview_window_frame, 2)

        self.available_style_options = list(hex_style_dict.keys())
        self.available_style_options.remove(self.app.style_var.get())

        self.app.style_var.trace_add("write", self.preview_instrument_callback)

        self.style_selection = OptionMenu(
            self.app.instrument_preview_window_frame,
            self.app.style_var,
            self.app.style_var.get(),  # this will be the default style on intitialization
            *self.available_style_options,
        )
        self.style_selection.config(font=self.app.project_font)
        self.style_selection.config(width=self.app.button_width)

        self.style_label = Label(
            text="Fretboard style:",
            master=self.app.instrument_preview_window_frame,
            font=self.app.project_font,
        )

        self.back_button = Button(
            text="Back",
            master=self.app.instrument_preview_window_frame,
            command=lambda: self.back(),
            font=self.app.project_font,
            width=self.app.button_width,
        )

        self.next_button = Button(
            text="Next",
            master=self.app.instrument_preview_window_frame,
            command=lambda: self.next(),
            font=self.app.project_font,
            width=self.app.button_width,
        )

        self.style_label.grid(row=1, column=0, sticky="E")
        self.style_selection.grid(row=1, column=1, sticky="W")
        self.back_button.grid(row=0, column=0, sticky="E")
        self.next_button.grid(row=0, column=1, sticky="W")
        # initialize default preview
        self.preview_instrument_callback(None, None, None)

        return

    def preview_instrument_callback(self, var, index, mode):
        self.app.instrument_preview.update(
            self.app.style_var.get(),
            self.app.fret_num_var.get(),
            self.app.tuning_entry_var.get())

        """new_bg_color: str = self.app.instrument_preview.curr_instrument.background_color
        self.app.chord_selection_frame.config(bg=new_bg_color)
        self.app.scale_selection_frame.config(bg=new_bg_color)
        self.app.scale_viewer_frame.config(bg=new_bg_color)
        self.app.arpeggio_selection_frame.config(bg=new_bg_color)
        self.app.arpeggio_viewer_frame.config(bg=new_bg_color)
        self.app.master.config(bg=new_bg_color)"""

        return

    def next(self):
        self.app.instrument_preview_window_frame.grid_forget()
        self.app.chart_type_selection_frame.grid(column=1)

    def back(self):
        self.app.instrument_preview_window_frame.grid_forget()
        self.app.previous_frame.grid(column=1)


class ChartSelection:

    def __init__(self, app: EveryChord):

        self.app = app
        split_columns_evenly(self.app.chart_type_selection_frame, 2)

        self.choice_label = Label(
            master=self.app.chart_type_selection_frame,
            text="Choose chart type:",
            font=self.app.project_font,
        )

        self.choices = OptionMenu(
            self.app.chart_type_selection_frame,
            self.app.choice_var,
            "Chord", "Scale", "Arpeggio",
        )
        self.choices.config(font=self.app.project_font)
        self.choices.config(width=self.app.button_width)

        self.back_button = Button(
            master=self.app.chart_type_selection_frame,
            text="Back",
            command=lambda: self.back(),
            font=self.app.project_font,
            width=self.app.button_width,
        )

        self.next_button = Button(
            master=self.app.chart_type_selection_frame,
            text="Next",
            font=self.app.project_font,
            command=lambda: self.next(),
            width = self.app.button_width,
        )

        self.choice_label.grid(row=1, column=0, sticky="E")
        self.choices.grid(row=1, column=1, sticky="W")
        self.next_button.grid(row=0, column=1, sticky="W")
        self.back_button.grid(row=0, column=0, sticky="E")

        return

    def next(self):

        self.app.chart_type_selection_frame.grid_forget()

        if self.app.choice_var.get() == "Chord":
            self.app.chord_selection_frame.grid(column=1)
        elif self.app.choice_var.get() == "Scale":
            self.app.scale_selection_frame.grid(column=1)
        elif self.app.choice_var.get() == "Arpeggio":
            self.app.arpeggio_selection_frame.grid(column=1)

    def back(self):
        self.app.chart_type_selection_frame.grid_forget()
        self.app.instrument_preview_window_frame.grid(column=1)


class ChordSelection:

    def __init__(self, app: EveryChord):

        self.app = app
        split_columns_evenly(self.app.chord_selection_frame, 2)

        self.root_choice_label = Label(
            master=self.app.chord_selection_frame,
            text="Choose chord root:",
            font=self.app.project_font,
        )

        self.root_choice = OptionMenu(
            self.app.chord_selection_frame,
            self.app.chord_root_var,
            *note_to_index.keys()
        )
        self.root_choice.config(font=self.app.project_font)

        self.type_choice_label = Label(
            master=self.app.chord_selection_frame,
            text="Choose chord type:",
            font=self.app.project_font,
        )

        self.type_choice = OptionMenu(
            self.app.chord_selection_frame,
            self.app.chord_type_var,
            *chords_to_intervals.keys()
        )
        self.type_choice.config(font=self.app.project_font)

        self.next_button = Button(
            master=self.app.chord_selection_frame,
            text="Next",
            font=self.app.project_font,
            command=lambda: self.next(),
            width=self.app.button_width,
        )

        self.back_button = Button(
            master=self.app.chord_selection_frame,
            text="Back",
            font=self.app.project_font,
            command=lambda: self.back(),
            width=self.app.button_width,
        )

        self.root_choice_label.grid(row=1, column=0)
        self.root_choice.grid(row=1, column=1, sticky="W")
        self.type_choice_label.grid(row=2, column=0)
        self.type_choice.grid(row=2, column=1, sticky="W")
        self.next_button.grid(row=0, column=1, sticky="W")
        self.back_button.grid(row=0, column=0, sticky="E")

        return

    def next(self):
        self.app.chord_selection_frame.grid_forget()
        self.app.chord_viewer = ChordViewer(self.app)
        self.app.chord_viewer.update_chord()
        self.app.pages[0].grid(column=1)
        return

    def back(self):
        self.app.chord_selection_frame.grid_forget()
        self.app.chart_type_selection_frame.grid(column=1)


class ChordViewer:

    def __init__(self, app: EveryChord):

        self.app = app
        self.num_chords_to_display = 0
        self.curr_page_idx = 0
        self.num_pages = 0

        return

    def paginate(self) -> list[Frame]:

        self.num_pages = ceil(self.num_chords_to_display / self.app.default_pagination)
        pages: list[Frame] = list()
        bg_color: str = self.app.instrument_preview.curr_instrument.background_color

        for i in range(self.num_pages):

            this_page = Frame(
                self.app.master,
                bg=bg_color,
            )
            split_columns_evenly(this_page, 3)

            next_page_button = Button(
                master=this_page,
                text=" > ",
                font=self.app.project_font,
                command=lambda:  self.goto_next_page(),
                width=round(self.app.button_width / 2),
            )

            prev_page_button = Button(
                master=this_page,
                text=" < ",
                font=self.app.project_font,
                command=lambda: self.goto_last_page(),
                width=round(self.app.button_width / 2),
            )

            prev_page_button.grid(row=1, column=0, sticky="E")
            next_page_button.grid(row=1, column=2, sticky="W")

            pages.append(this_page)

        return pages

    def update_chord(self):

        # we need to reinitialize the instrument with the current frame to display voicings
        self.app.instrument = Instrument(
            num_frets=self.app.instrument_preview.curr_instrument.num_frets,
            tuning=self.app.instrument_preview.curr_instrument.tuning,
            style=self.app.instrument_preview.curr_instrument.style,
            display_frame=self.app.fretboard_storage_frame
        )

        # now compute chords and show
        title: str = self.app.chord_root_var.get() + self.app.chord_type_var.get()
        fretted_chords, barred_chords = self.app.instrument.get_chord_fret_pairs(
            self.app.chord_root_var.get(),
            self.app.chord_type_var.get())
        self.num_chords_to_display = len(fretted_chords) + len(barred_chords)

        # initializes pages
        self.app.pages = self.paginate()
        # populates pages
        self.app.instrument.display_chord_voicings(
            fretted_chords, barred_chords,
            title, self.app.pages, self.app.default_pagination)

        for page_idx, page in enumerate(self.app.pages):
            # we need to do this after instantiating instrument
            page.config(bg=self.app.instrument.background_color)

            current_page_label = Label(
                text=f"{page_idx + 1} / {self.num_pages}",
                font=self.app.project_font,
                master=page,
            )

            back_button = Button(
                master=page,
                text="Back",
                font=self.app.project_font,
                command=lambda: self.back(),
                width=self.app.button_width,
            )

            current_page_label.grid(row=1, column=1)
            back_button.grid(row=0, column=0, columnspan=3)

        self.app.pages[self.curr_page_idx].grid()
        return

    def goto_next_page(self):
        curr_page = self.app.pages[self.curr_page_idx]
        curr_page.grid_forget()
        self.increment_page_idx("next")
        next_page = self.app.pages[self.curr_page_idx]
        next_page.grid()

    def goto_last_page(self):
        curr_page = self.app.pages[self.curr_page_idx]
        curr_page.grid_forget()
        self.increment_page_idx("prev")
        last_page = self.app.pages[self.curr_page_idx]
        last_page.grid()

    def increment_page_idx(self, mode: Literal["next","prev"]):

        if mode == "next":
            self.curr_page_idx = (self.curr_page_idx + 1) % self.num_pages
        if mode == "prev":
            self.curr_page_idx = (self.curr_page_idx - 1) % self.num_pages

    def back(self):
        self.app.pages[self.curr_page_idx].grid_forget()
        self.app.chord_selection_frame.grid(column=1)
        return


class ScaleSelection:

    def __init__(self, app: EveryChord):
        self.app = app
        split_columns_evenly(self.app.scale_selection_frame, 2)

        self.root_choice_label = Label(
            master=self.app.scale_selection_frame,
            text="Choose scale root",
            font=self.app.project_font,
        )

        self.root_choice = OptionMenu(
            self.app.scale_selection_frame,
            self.app.scale_root_var,
            *note_to_index.keys(),
        )
        self.root_choice.config(font=self.app.project_font)
        self.root_choice.config(width=self.app.button_width)

        self.type_choice_label = Label(
            master=self.app.scale_selection_frame,
            text="Choose scale type",
            font=self.app.project_font,
        )

        self.type_choice = OptionMenu(
            self.app.scale_selection_frame,
            self.app.scale_type_var,
            *intervals_in_scales.keys()
        )
        self.type_choice.config(font=self.app.project_font)
        self.type_choice.config(width=self.app.button_width)

        self.next_button = Button(
            master=self.app.scale_selection_frame,
            text="Next",
            font=self.app.project_font,
            command=lambda: self.next(),
            width=self.app.button_width,
        )

        self.back_button = Button(
            master=self.app.scale_selection_frame,
            text="Back",
            font=self.app.project_font,
            command=lambda: self.back(),
            width=self.app.button_width,
        )

        self.root_choice_label.grid(row=1, column=0)
        self.root_choice.grid(row=1, column=1, sticky="W")
        self.type_choice_label.grid(row=2, column=0)
        self.type_choice.grid(row=2, column=1, sticky="W")
        self.next_button.grid(row=0, column=1, sticky="W")
        self.back_button.grid(row=0, column=0, sticky="E")

        return

    def next(self):
        self.app.scale_selection_frame.grid_forget()
        self.app.scale_viewer.update_scale()
        self.app.scale_viewer_frame.grid(column=1)
        return

    def back(self):
        self.app.scale_selection_frame.grid_forget()
        self.app.chart_type_selection_frame.grid(column=1)


class ScaleViewer:

    def __init__(self, app: EveryChord):

        self.app = app

        self.back_button = Button(
            text="Back",
            font=self.app.project_font,
            command=lambda: self.back(),
            master=self.app.scale_viewer_frame,
            width=self.app.button_width,
        )
        self.back_button.pack()
        self.fretted_notes = list()
        self.title: str = ""
        self.scale_canvas: Canvas = Canvas(master=self.app.arpeggio_viewer_frame)

        return

    def update_scale(self):
        # clear last chart
        self.scale_canvas.pack_forget()
        # update parameters to current user input values
        self.app.instrument = Instrument(
            num_frets=self.app.instrument_preview.curr_instrument.num_frets,
            tuning=self.app.instrument_preview.curr_instrument.tuning,
            style=self.app.instrument_preview.curr_instrument.style,
            display_frame=self.app.scale_viewer_frame
        )

        self.fretted_notes = self.app.instrument.get_scale(
            self.app.scale_root_var.get(),
            self.app.scale_type_var.get())
        self.title = self.app.scale_root_var.get() + " " + self.app.scale_type_var.get() + " scale"
        self.scale_canvas = self.app.instrument.display_voicing(self.fretted_notes, self.title)
        # display the new canvas
        self.scale_canvas.pack()
        return

    def back(self):
        self.app.scale_viewer_frame.grid_forget()
        self.app.scale_selection_frame.grid(column=1)
        return


class ArpeggioSelection:

    def __init__(self, app: EveryChord):
        self.app = app
        split_columns_evenly(self.app.arpeggio_selection_frame, 2)

        self.root_choice_label = Label(
            master=self.app.arpeggio_selection_frame,
            text="Choose arpeggio root",
            font=self.app.project_font,
        )

        self.root_choice = OptionMenu(
            self.app.arpeggio_selection_frame,
            self.app.arp_root_var,
            *note_to_index.keys()
        )
        self.root_choice.config(font=self.app.project_font)
        self.root_choice.config(width=self.app.button_width)

        self.type_choice_label = Label(
            master=self.app.arpeggio_selection_frame,
            text="Choose arpeggio type",
            font=self.app.project_font,
        )

        self.type_choice = OptionMenu(
            self.app.arpeggio_selection_frame,
            self.app.arp_type_var,
            *chords_to_intervals.keys()
        )
        self.type_choice.config(font=self.app.project_font)
        self.type_choice.config(width=self.app.button_width)

        self.next_button = Button(
            master=self.app.arpeggio_selection_frame,
            text="Next",
            font=self.app.project_font,
            command=lambda: self.next(),
            width=self.app.button_width,
        )

        self.back_button = Button(
            master=self.app.arpeggio_selection_frame,
            text="Back",
            font=self.app.project_font,
            command=lambda: self.back(),
            width = self.app.button_width,
        )

        self.root_choice_label.grid(row=1, column=0)
        self.root_choice.grid(row=1, column=1, sticky="W")
        self.type_choice_label.grid(row=2, column=0)
        self.type_choice.grid(row=2, column=1, sticky="W")
        self.next_button.grid(row=0, column=1, sticky="W")
        self.back_button.grid(row=0, column=0, sticky="E")

        return

    def next(self):
        self.app.arpeggio_selection_frame.grid_forget()
        self.app.arpeggio_viewer.update_arpeggio()
        self.app.arpeggio_viewer_frame.grid(column=1)
        return

    def back(self):
        self.app.arpeggio_selection_frame.grid_forget()
        self.app.chart_type_selection_frame.grid(column=1)
        return


class ArpeggioViewer:

    def __init__(self, app: EveryChord):

        self.app = app

        self.back_button = Button(
            text="Back",
            font=self.app.project_font,
            command=lambda: self.back(),
            master=self.app.arpeggio_viewer_frame,
            width=self.app.button_width,
        )
        self.back_button.pack()
        self.fretted_notes = list()
        self.title: str = ""
        self.arp_canvas: Canvas = Canvas(master=self.app.arpeggio_viewer_frame)

        return

    def update_arpeggio(self):
        # clear last chart
        self.arp_canvas.pack_forget()
        # update parameters to current user input values
        self.app.instrument = Instrument(
            num_frets=self.app.instrument_preview.curr_instrument.num_frets,
            tuning=self.app.instrument_preview.curr_instrument.tuning,
            style=self.app.instrument_preview.curr_instrument.style,
            display_frame=self.app.arpeggio_viewer_frame
        )

        self.fretted_notes = self.app.instrument.get_arp(
            self.app.arp_root_var.get(),
            self.app.arp_type_var.get())
        self.title = self.app.arp_root_var.get() + self.app.arp_type_var.get() + " arpeggio"
        self.arp_canvas = self.app.instrument.display_voicing(self.fretted_notes, self.title)
        # display the new canvas
        self.arp_canvas.pack()

    def back(self):
        self.app.arpeggio_viewer_frame.grid_forget()
        self.app.arpeggio_selection_frame.grid(column=1)
        return



if __name__ == '__main__':
    EveryChord()
