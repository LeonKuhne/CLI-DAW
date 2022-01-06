#!/bin/python

# mash together curses with audio player using a sequencer

import time
import curses
from threading import Thread
from colorama import Fore, Back, Style
from instrument import Instrument, Sequencer, DIVISIONS
import pickle
import re

MIN_BPM = 30
MAX_BPM = 420
MIN_TEMPO_TAPS = 8
class Daw:
    def __init__(self):
        self.info = ""
        self.tempo_tap_times = []
        self.selected_instrument_idx = 0
        self.selected_note_idx = 0
        self.instruments = []
        self.tick = 0
        self.tempo = 120
        self.playing = False
        self.listening = False
        self.reset_screen()

    def add_instrument(self, instrument):
        self.instruments.append(instrument)

    def next_state(self):
        self.tick += 1
        for i in self.instruments:
            i.seq.set_pos(self.tick)

    def draw_state(self):
        # draw instruments
        for idx in range(0, len(self.instruments)):
            instrument = self.instruments[idx] 
            sequencer = instrument.seq
            spacing = sequencer.height

            if not instrument.muted:
                self.screen.addstr(idx * spacing+1, 0, str(sequencer))
            else:
                # indicate muted
                self.screen.addstr(idx * spacing+1, 0, str(sequencer), curses.A_DIM)
            
            if not idx == self.selected_instrument_idx:
                self.screen.addstr(idx * spacing+1, 3, f"[ {idx}. {instrument.sample} ]")
            else:
                sequence = sequencer.sequence
                note_spacing = sequencer.draw_line
                note_idx = self.selected_note_idx % len(sequence)
                selected_note = sequence[note_idx]
                
                # highlight navigation
                self.screen.addstr(idx * spacing+1, 3, f"[ {idx}. {instrument.sample} ]", curses.A_REVERSE)
                self.screen.addstr(idx * spacing+1 + note_spacing, note_idx+1, selected_note, curses.A_REVERSE)
        
        self.screen.addstr(0, 0, self.info, curses.A_REVERSE)
        
        self.screen.refresh()
        
    def play_state(self):
        for i in self.instruments:
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

            delta = 60/self.tempo * 4/DIVISIONS
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
                for i in self.instruments:
                    i.seq.set_pos(0)
                self.screen.clear()
            # clean screen
            if key == 'c':
                self.screen.clear()
            # save 
            if key == 'q':
                self.save()
            # save and quit
            if key == 'Q':
                self.save()
                self.playing = False
                self.listening = False
            # open project file
            if key == 'f':
                self.load()
                
            #
            # NAVIGATE

            # select instrument
            if key == 'j':
                self.selected_instrument_idx = (self.selected_instrument_idx + 1) % len(self.instruments)
            if key == 'k':
                self.selected_instrument_idx = (self.selected_instrument_idx - 1) % len(self.instruments)
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
        return self.instruments[self.selected_instrument_idx]

    def reset_screen(self):
        self.screen = curses.initscr()
        self.screen.clear()
        self.draw_state()

    #
    # Project Management

    def prompt(self, text):
        self.screen.addstr(0, 0, text)

        response = ""
        key = self.screen.getkey()
        while not (key == '\n' and len(response) > 0):
            key = self.screen.getkey()
            if re.match(r'[a-zA-Z -_]', key):
                response += key
        
        self.screen.clear()
        return response

    def save(self):
        project_name = self.prompt('save as ') 
        with open(f"{project_name}.proj", 'wb') as f:
            pickle.dump(self, f)

    def load(self):
        project_name = self.prompt('load project ')
        with open(f"{project_name}.proj", 'rb') as f:
            return pickle.load(f)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['screen']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.reset_screen()

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
    daw.add_instrument(kick)
    daw.add_instrument(snare)
    daw.add_instrument(hat)
    daw.add_instrument(ohat)
    daw.listen()

