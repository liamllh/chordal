texture_name_to_gif = {'Black Gradient': './textures/shitty_matte_black.gif'
               }

# todo import fret marker styles somehow
# todo change to hex codes
# fret color, string color, text color, bg color, fret marker color, note marker color
guitar_styles = {'Neon green': ['green', 'green', 'white', 'black', 'white', 'white'],
                 'Plain white': ['black', 'black', 'black', 'white', 'black', 'grey'],
                 'Blackout': ['white', 'white', 'white', 'black', 'white', 'white'],
                 'Valentine': ['white', 'white', 'red', 'pink', 'red', 'purple']
                 }

instrument_presets = {'Standard guitar': (22, 'E-A-D-G-B-E',),
                      'Open D': (22, 'D-A-D-F#-A-D'),
                      'Drop D': (22, 'D-A-D-G-B-E'),
                      'Standard bass': (22, 'E-A-D-G',),
                      '6-string bass': (22, 'B-E-A-D-G-E',),
                      'Nick Drake': (22, 'C-G-C-F-C-E',),
                      'Midwest emo 1': (22, 'F-A-C-G-C-E'),
                      'Midwest emo 2': (22, 'D-A-E-A-C#-E'),
                      'Midwest emo 3': (22, 'D-A-D-G-A-D'),
                      '7-string guitar': (24, 'B-E-A-D-G-B-E',),
                      '8-string guitar': (24, 'F#-B-E-A-D-G-B-E'),
                      '9-string guitar': (24, 'B-F#-B-E-A-D-G-B-E'),
                      'Baritone': (22, 'B-E-A-D-G-B',),
                      }

color_tuples = {'red': (1, 0, 0),
                'green': (0, 1, 0),
                'blue': (0, 0, 1),
                'orange': (1, 0.5, 0),
                'yellow': (1, 1, 0),
                'lime green': (0.5, 1, 0),
                'turquoise': (0, 0.4, 0.4),
                'teal': (0, 1, 1),
                'white': (1, 1, 1),
                'black': (0, 0, 0),
                'grey': (0.4, 0.4, 0.4),
                'pink': (1, 0.6, 0.9),
                'purple': (0.6, 0.2, 0.8),
                'lavender': (0.9, 0.7, 0.9),
                }

hex_colors: dict[str: str] = {
    'pastel pink': '#f3c2c2',
    'bright lavender': '#d7c6cf',
    'dark lavender': '#aa98a9',
    'red': '#cc2a36',
    'orange': '#eb6841',
    'yellow': '#edc951',
    'teal': '#00a0b0',
    'scarlet': '#b90000',
    'forest green': '#38761d',
    'pink': '#ea9999',
    'deep purple': '#4c1130',
    'neon green': '#04ff00',
    'bright neon green': '#84ff82',
    'aqua': '#00ffd2',
    'deep blue': '#0400ff',
    'neon yellow': '#fbff00',
    'olive greeen': '#52a743',
    'black': '#000000',
    'white': '#ffffff',
    'sunset orange': '#ffc450',
    'light grey': '#c1c1c1',
    'mid grey': '#737373',
    'dark grey': '#2d2d2d',
    'sand': '#ffe9a9',
}

# colors: fretboard, background, fret markers, chord fretting markers, labels
hex_style_dict: dict[str: tuple[str, str, str, str, str]] = {
    'Neon green': ('white', 'black', 'neon green', 'forest green', 'white'),
    'Sunset': ('scarlet', 'sunset orange', 'neon yellow', 'yellow', 'scarlet'),
    'Plain white': ('black', 'white', 'light grey', 'mid grey', 'black'),
    'Dark mode': ('light grey', 'black', 'mid grey', 'dark grey', 'white'),
    'Ocean': ('sand', 'deep blue', 'forest green', 'teal', 'sand'),
}
