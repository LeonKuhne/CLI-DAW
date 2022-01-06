#!/bin/python

import time
import curses
import subprocess
from threading import Thread
from colorama import Fore, Back, Style

# mash together curses with audio player using a sequencer

instruments = []
class Instrument:
    def __init__(self, sample):
        self.seq = Sequencer()
        self.sample = sample
        instruments.append(self)
        self.name = f"{len(instruments)}. {sample}"
        self.muted = True

    def play(self):
        if self.seq.on_note() and not self.muted:
            subprocess.Popen(f"aplay {self.sample} >/dev/null 2>&1", shell=True)

    def set_rhythm(self, pattern):
        self.seq.set_sequence(pattern)

    def toggle_mute(self):
        self.muted = not self.muted

divisions = 32
class Sequencer:
    def __init__(self):
        self.time_indicators = "|   -   ǂ   -   ǁ   -   ǂ   -   "
        self.height = 6 # the number of lines tall when drawn
        self.draw_line = 2 # the line number index with drawable notes
        
        self.position = 0
        self.reset()
        
    def __str__(self):
        measures = self.get_measures()
        notes = self.get_notes()
        time_markers = ''.join([str(n).ljust(int(divisions/4), ' ') for n in range(1, measures*4+1)])
        tick_mark = (' ' * self.position + '*').ljust(notes, ' ')
        return f"""\
⌟{'—' * notes}⌞
|{tick_mark}|
|{self.sequence.ljust(notes, ' ')}|
|{self.time_indicators * measures}|
|{time_markers}|
⌝{'—' * notes}⌜\
"""
    
    def set_pos(self, pos):
        self.position = pos % (self.get_measures() * divisions)

    def set_sequence(self, sequence):
        self.sequence = sequence
        # fix the length
        self.sequence = sequence.ljust(divisions * self.get_measures(), ' ')

    def get_measures(self):
        return (len(self.sequence) - 1) // divisions + 1
   
    def get_notes(self):
        return self.get_measures() * divisions 

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
        self.sequence +=  ' ' * divisions

    def shorten(self):
        if len(self.sequence) > divisions:
            self.sequence = self.sequence[:len(self.sequence)-divisions]

    def reset(self):
        self.sequence = " " * divisions

MIN_BPM = 30
MAX_BPM = 420
MIN_TEMPO_TAPS = 8
class Daw:
    def __init__(self):
        self.tick = 0
        self.tempo = 120
        
        self.playing = False
        self.listening = False

        self.selected_instrument_idx = 0
        self.selected_note_idx = 0
        self.tempo_tap_times = []
        self.info = ""
        
        self.screen = curses.initscr()
        self.screen.clear()
        self.draw_state()

    def next_state(self):
        self.tick += 1
        for i in instruments:
            i.seq.set_pos(self.tick)

    def draw_state(self):
        # draw instruments
        for idx in range(0, len(instruments)):
            instrument = instruments[idx] 
            sequencer = instrument.seq
            spacing = sequencer.height

            if not instrument.muted:
                self.screen.addstr(idx * spacing+1, 0, str(sequencer))
            else:
                # indicate muted
                self.screen.addstr(idx * spacing+1, 0, str(sequencer), curses.A_DIM)
            
            if not idx == self.selected_instrument_idx:
                self.screen.addstr(idx * spacing+1, 3, f"[ {instruments[idx].name} ]")
            else:
                sequence = sequencer.sequence
                note_spacing = sequencer.draw_line
                note_idx = self.selected_note_idx % len(sequence)
                selected_note = sequence[note_idx]
                
                # highlight navigation
                self.screen.addstr(idx * spacing+1, 3, f"[ {instruments[idx].name} ]", curses.A_REVERSE)
                self.screen.addstr(idx * spacing+1 + note_spacing, note_idx+1, selected_note, curses.A_REVERSE)
        
        self.screen.addstr(0, 0, self.info, curses.A_REVERSE)
        
        self.screen.refresh()
        
    def play_state(self):
        for i in instruments:
            i.play()
    
    def play(self):
        Thread(target = self.play_loop).start()

    def play_loop(self):
        self.playing = True
        last = time.time()
        while self.playing:
            self.next_state()
            self.draw_state()
            self.play_state()

            delta = 60/self.tempo * 4/divisions
            now = time.time()
            since_last = (now - last) / 1000
            last = now
            time.sleep(delta - since_last)

    # listen for keyboard input
    def listen(self):
        self.listening = True
        while self.listening:
            self.draw_state()
            key = self.screen.getkey()

            #
            # CONTROL

            # play/pause
            if key == ' ':
                if self.playing:
                    self.playing = False
                else:
                    self.play()
            # toggle mute
            if key == 'm':
                self.selected_instrument().toggle_mute()
            # tempo
            if key == 't':
                # mark the time
                self.tempo_tap_times.append(time.time())
                
                if len(self.tempo_tap_times) > 2:
                    tempo_tap_diffs = [stop-start for start, stop in zip(self.tempo_tap_times[:-1], self.tempo_tap_times[1:])]
                    avg_tempo = sum(tempo_tap_diffs) / len(tempo_tap_diffs)

                    # update the tempo
                    if len(self.tempo_tap_times) >= MIN_TEMPO_TAPS:
                        if avg_tempo < 60 / MIN_BPM:
                            self.tempo = int(60 / avg_tempo * 100) / 100
                            self.info = f"tempo set to {self.tempo}"
            # reset tempo
            if key == 'T':
                self.tempo_tap_times = []
                self.info = f"tempo taps cleared"
            # reset playhead
            if key == 'r':
                self.tick = 0
                for i in instruments:
                    i.seq.set_pos(0)
                self.screen.clear()
            # clean screen
            if key == 'c':
                self.screen.clear()
            # quit
            if key == 'q':
                self.playing = False 
                self.listening = False
            
            #
            # NAVIGATE

            # select instrument
            if key == 'j':
                self.selected_instrument_idx = (self.selected_instrument_idx + 1) % len(instruments)
            if key == 'k':
                self.selected_instrument_idx = (self.selected_instrument_idx - 1) % len(instruments)
            # select note
            if key == 'h':
                self.selected_note_idx -= 1
            if key == 'l':
                self.selected_note_idx += 1
            if key == 'b':
                self.selected_note_idx -= 4
            if key == 'w':
                self.selected_note_idx += 4

            # 
            # COMPOSE

            # toggle note
            if key == 'i':
                self.selected_instrument().seq.toggle_note(self.selected_note_idx)
            # duplicate
            if key == 'd':
                self.selected_instrument().seq.duplicate()
            # extend
            if key == 'e':
                self.selected_instrument().seq.extend()
            # shorten
            if key == 's':
                self.selected_instrument().seq.shorten()
                self.screen.clear()
            # reset
            if key == 'R':
                self.selected_instrument().seq.reset()
                self.screen.clear()
   
    def selected_instrument(self):
        return instruments[self.selected_instrument_idx]


if __name__ == '__main__':
    kick = Instrument('kick.wav')
    kick.set_rhythm("𝅘𝅥     𝅘𝅥     𝅘𝅥     𝅘𝅥               𝅘𝅥     𝅘𝅥   𝅘𝅥   𝅘𝅥 𝅘𝅥            ")

    snare = Instrument('snare.wav')
    snare.set_rhythm("        𝅘𝅥       "*2)

    hat = Instrument('hat.wav')
    hat.set_rhythm("𝅘𝅥 "*16)
    
    ohat = Instrument('oh.wav')
    ohat.set_rhythm("    𝅘𝅥   "*4)
   
    daw = Daw()
    daw.listen()

