#!/bin/python
import curses
from color import Colors

DIVISIONS = 32

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

    def draw(self, x, y, selected_note, is_muted):
        if not self.screen:
            return
        
        # draw info lines in configured order
        for idx, draw_line in enumerate(self.draw_order):
            draw_line(x, y + idx, selected_note, is_muted)
   
    def draw_time_markers(self, x, y, selected_note, is_muted):
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
    

    def draw_pattern(self, x, y, selected_note, is_muted):
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

    # for pickling
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['screen']
        return state
    
    def __setstate__(self, state):
        self.__dict__.update(state)
