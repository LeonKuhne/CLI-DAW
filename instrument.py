#!/bin/python

import curses
import subprocess

DIVISIONS = 32

instrument_count = 0
class Instrument:
    def __init__(self, sample):
        global instrument_count
        instrument_count += 1

        self.id = instrument_count
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

    def draw(self, x, y, selected_note, Colors):
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
        self.seq.draw(x + self.border_width, y + self.border_height, selected_note, self.muted, Colors)

class Sequencer:
    def __init__(self):
        self.note_width = 2 # the width of each note
        self.position = 0
        self.draw_order = [
            self.draw_pattern,
            self.draw_time_markers,
        ]
        
        self.reset()

    def width(self):
        return self.get_notes() * self.note_width

    def height(self):
        return len(self.draw_order)

    def draw_to_screen(self, screen):
        self.screen = screen        

    def draw(self, x, y, selected_note, is_muted, Colors):
        if not self.screen:
            return
        
        # draw info lines in configured order
        for idx, draw_line in enumerate(self.draw_order):
            draw_line(x, y + idx, selected_note, is_muted, Colors)
   
    def draw_time_markers(self, x, y, selected_note, is_muted, Colors):
        color = curses.A_DIM if is_muted else Colors['default'].color()
        
        # number indicators
        text = ''
        for measure in range(self.get_measures()*4):
            text += f"{' '*(self.note_width//2)}{measure}".ljust(int(DIVISIONS/8) * self.note_width, ' ')
            text += f"{' '*(self.note_width//2)}-".ljust(int(DIVISIONS/8) * self.note_width, ' ')
        
        # playhead
        playhead_idx = self.position * self.note_width + (self.note_width // 2)
        text = f"{text[:playhead_idx]}*{text[playhead_idx+1:]}"
        self.screen.addstr(y, x, text, color)
    

    def draw_pattern(self, x, y, selected_note, is_muted, Colors):
        text = ''.join([(' ' if note == ' ' else '█') * self.note_width for note in list(self.pattern.ljust(self.get_notes()))])
        color = curses.A_DIM if is_muted else Colors['default'].color()
        self.screen.addstr(y, x, text, color)
    
        # draw highlighted note
        if selected_note != None:
            select_x = selected_note % self.get_notes()
            select_char = self.pattern[select_x]
            self.screen.addstr(y, x+select_x*self.note_width, select_char * self.note_width, Colors['highlight'].inverse())
        
        

    def set_pos(self, pos):
        self.position = pos % self.get_notes()

    def set_pattern(self, pattern):
        # fix the length
        self.pattern = pattern.ljust(DIVISIONS * self.get_measures(), ' ')

    def get_measures(self):
        return (len(self.pattern) - 1) // DIVISIONS + 1
   
    def get_notes(self):
        return self.get_measures() * DIVISIONS 

    def on_note(self):
        return self.pattern[self.position] != ' '

    def toggle_note(self, idx):
        idx = idx % self.get_notes()
        note = self.pattern[idx]
        self.pattern = self.pattern[:idx] + ('𝅘𝅥' if note == ' ' else ' ') + self.pattern[idx+1:]

    def duplicate(self):
        self.pattern *= 2
    
    def extend(self):
        self.pattern +=  ' ' * DIVISIONS

    def shorten(self):
        if len(self.pattern) > DIVISIONS:
            self.pattern = self.pattern[:len(self.pattern) - DIVISIONS]
            self.screen.clear() # WEIRD

    def reset(self):
        self.pattern = " " * DIVISIONS

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, state):
        self.__dict__.update(state)

if __name__ == '__main__':
    kick = Instrument('samples/kick.wav')
    kick.set_rhythm("𝅘𝅥     𝅘𝅥     𝅘𝅥     𝅘𝅥               𝅘𝅥     𝅘𝅥   𝅘𝅥   𝅘𝅥 𝅘𝅥            ")
