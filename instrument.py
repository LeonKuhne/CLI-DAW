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

    def play(self):
        if self.seq.on_note() and not self.muted:
            subprocess.Popen(f"aplay {self.sample} >/dev/null 2>&1", shell=True)

    def set_rhythm(self, pattern):
        self.seq.set_sequence(pattern)

    def toggle_mute(self):
        self.muted = not self.muted

    def draw_to_screen(self, screen):
        self.screen = screen        
        self.seq.draw_to_screen(screen)

    def draw(self, x, y, selected_note, Colors):
        if not self.screen:
            return

        # draw instrument name
        header = f"[ {self.id}. {self.sample} ]"
        header_color = Colors['muted'] if self.muted else Colors['default']
        self.screen.addstr(y, 3, header, header_color.color() if selected_note == None else header_color.inverse())

        # draw sequencer
        self.seq.draw(x+1, y, selected_note, self.muted, Colors)

class Sequencer:
    def __init__(self):
        self.time_indicators = "|   -   ǂ   -   ǁ   -   ǂ   -   "
        self.height = 6 # the number of lines tall when drawn
        self.draw_line = 1 # the line index with drawable notes
        self.note_width = 3 # the width of each note

        self.position = 0
        self.reset()

    def draw_to_screen(self, screen):
        self.screen = screen        

    def draw(self, x, y, selected_note, is_muted, Colors):
        if not self.screen:
            return
        
        # draw everything
        color = curses.A_DIM if is_muted else Colors['default'].color()
        self.screen.addstr(y, x, str(self), color)
        
        # draw highlighted
        if selected_note != None:
            select_x = selected_note % self.get_notes()
            select_char = self.sequence[select_x]
            self.screen.addstr(y + self.draw_line, select_x*self.note_width, select_char * self.note_width, Colors['highlight'].inverse())        
    
    def __str__(self):
        measures = self.get_measures()
        notes = self.get_notes()
        scaled_sequence = ''.join([(' ' if note == ' ' else '█') * self.note_width for note in list(self.sequence.ljust(notes))])
        tick_mark = ((' ' * (self.note_width//2) + '*').ljust(self.note_width) * self.position).ljust(notes*self.note_width, ' ')
        time_indicators = (' ' * (self.note_width-1)).join(list(self.time_indicators)) + ' ' * (self.note_width-1)
        time_markers = ''.join([str(n).ljust(int(DIVISIONS/4 * self.note_width), ' ') for n in range(1, measures*4+1)])

        return f"""\
{tick_mark}
{scaled_sequence}
{time_indicators * measures}
{time_markers}\
"""
    
    def set_pos(self, pos):
        self.position = pos % self.get_notes()

    def set_sequence(self, sequence):
        self.sequence = sequence
        # fix the length
        self.sequence = sequence.ljust(DIVISIONS * self.get_measures(), ' ')

    def get_measures(self):
        return (len(self.sequence) - 1) // DIVISIONS + 1
   
    def get_notes(self):
        return self.get_measures() * DIVISIONS 

    def on_note(self):
        return self.sequence[self.position] != ' '

    def toggle_note(self, idx):
        idx = idx % self.get_notes()
        if self.sequence[idx] == ' ':
            self.sequence = self.sequence[:idx] + '𝅘𝅥' + self.sequence[idx+1:]
        else:
            self.sequence = self.sequence[:idx] + ' ' + self.sequence[idx+1:]

    def duplicate(self):
        self.sequence *= 2
    
    def extend(self):
        self.sequence +=  ' ' * DIVISIONS

    def shorten(self):
        if len(self.sequence) > DIVISIONS:
            self.sequence = self.sequence[:len(self.sequence)-DIVISIONS]

    def reset(self):
        self.sequence = " " * DIVISIONS

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, state):
        self.__dict__.update(state)

if __name__ == '__main__':
    kick = Instrument('samples/kick.wav')
    kick.set_rhythm("𝅘𝅥     𝅘𝅥     𝅘𝅥     𝅘𝅥               𝅘𝅥     𝅘𝅥   𝅘𝅥   𝅘𝅥 𝅘𝅥            ")
