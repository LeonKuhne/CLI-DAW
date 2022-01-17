#!/bin/python
import subprocess
from sequencer import Sequencer
from color import Colors

INSTRUMENT_COUNT = 0

class Instrument:
    def __init__(self, sample):
        global INSTRUMENT_COUNT
        INSTRUMENT_COUNT += 1

        self.id = INSTRUMENT_COUNT
        self.seq = Sequencer()
        self.sample = sample
        self.muted = True

        self.border_height = 1
        self.border_width = 2

    def play(self):
        if self.seq.on_note() and not self.muted:
            subprocess.Popen(f"aplay {self.sample} >/dev/null 2>&1", shell=True)

    def set_rhythm(self, pattern):
        self.seq.set_pattern(pattern)

    def toggle_mute(self):
        self.muted = not self.muted

    def width(self):
        return self.seq.width() + self.border_width * 2

    def height(self):
        return self.seq.height() + self.border_height * 2

    def draw_to_screen(self, screen):
        self.screen = screen     
        self.seq.draw_to_screen(screen)

    def draw(self, x, y, selected_note):
        if not self.screen:
            return

        # draw border
        border_color = Colors['border'].inverse() if selected_note == None else Colors['highlight'].inverse()
        for border_idx in range(self.border_height):
            self.screen.addstr(y + border_idx, x, ' ' * self.width(), border_color)
        for line_idx in range(self.seq.height()):
            line_y = 1 + y + line_idx
            self.screen.addstr(line_y, 0, ' ' * self.border_width, border_color)
            self.screen.addstr(line_y, self.width() - self.border_width, ' ' * self.border_width, border_color)
        for border_idx in range(self.border_height):
            self.screen.addstr(y + self.height() - 1+ border_idx, x, ' ' * self.width(), border_color)
        
        # draw instrument name
        header = f"[ {self.id}. {self.sample} ]"
        header_color = Colors['muted'] if self.muted else Colors['default']
        self.screen.addstr(y, x+3, header, header_color.color() if selected_note == None else header_color.inverse())

        # draw sequencer
        self.seq.draw(x + self.border_width, y + self.border_height, selected_note, self.muted)
    
    # for pickling
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['screen']
        return state
    
    def __setstate__(self, state):
        self.__dict__.update(state)
