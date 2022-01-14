#!/bin/python

import subprocess

DIVISIONS = 32

class Instrument:
    def __init__(self, sample):
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

class Sequencer:
    def __init__(self):
        self.time_indicators = "|   -   ǂ   -   ǁ   -   ǂ   -   "
        self.height = 6 # the number of lines tall when drawn
        self.draw_line = 2 # the line number index with drawable notes
        self.note_width = 3 # the width of each note

        self.position = 0
        self.reset()
        
    def __str__(self):
        measures = self.get_measures()
        notes = self.get_notes()
        scaled_sequence = ''.join([(' ' if note == ' ' else '█') * self.note_width for note in list(self.sequence.ljust(notes))])
        tick_mark = ((' ' * (self.note_width//2) + '*').ljust(self.note_width) * self.position).ljust(notes*self.note_width, ' ')
        time_indicators = (' ' * (self.note_width-1)).join(list(self.time_indicators)) + ' ' * (self.note_width-1)
        time_markers = ''.join([str(n).ljust(int(DIVISIONS/4 * self.note_width), ' ') for n in range(1, measures*4+1)])

        return f"""\
⌟{'—' * notes * self.note_width}⌞
|{tick_mark}|
|{scaled_sequence}|
|{time_indicators * measures}|
|{time_markers}|
⌝{'—' * notes * self.note_width}⌜\
"""
    
    def set_pos(self, pos):
        self.position = pos % (self.get_measures() * DIVISIONS)

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
