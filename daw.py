#!/bin/python

# mash together curses with audio player using a sequencer

import time
import curses
from threading import Thread
from instrument import Instrument
from sequencer import DIVISIONS
from tempo import Tempo
from controls import Controls
from color import Colors

class Daw:
    def __init__(self):
        self.selected_instrument_idx = 0
        self.selected_note_idx = 0
        self.instruments = []
        self.tick = 0
        self.tempo = Tempo(120, self.info)
        self.playing = False
        self.reset_screen()

    def add_instrument(self, instrument):
        instrument.draw_to_screen(self.screen)
        self.instruments.append(instrument)

    def next_state(self):
        for i in self.instruments:
            i.seq.set_pos(self.tick)
        self.tick += 1

    def draw_state(self):
        # draw instruments
        for idx in range(0, len(self.instruments)):
            instrument = self.instruments[idx] 
            spacing = instrument.height() + 1
            sequencer_line = 1+idx*spacing
            is_selected = idx == self.selected_instrument_idx
            selected_pos = self.selected_note_idx if is_selected else None
            
            instrument.draw(0, sequencer_line, selected_pos)
          
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

            # calculate timing
            delta = 60/self.tempo.bpm * 4/DIVISIONS
            now = time.time()
            since_last = (now - last)
            delay = delta - since_last
            
            # increment timing
            last += delta
            if delay > 0:
                time.sleep(delay)

    def toggle_play(self):
        if self.playing:
            self.playing = False
        else:
            self.play()

    def next_instrument(self):
        self.selected_instrument_idx = (self.selected_instrument_idx + 1) % len(self.instruments)

    def prev_instrument(self):
        self.selected_instrument_idx = (self.selected_instrument_idx - 1) % len(self.instruments)
    
    def move_note(self, delta):
        self.selected_note_idx += delta

    def reset_playhead(self):
        self.tick = 0
        for i in self.instruments:
            i.seq.set_pos(0)
   
    def selected_instrument(self):
        return self.instruments[self.selected_instrument_idx]

    def reset_screen(self):
        self.screen = curses.initscr()
       
        # load colors
        curses.start_color()
        for color in Colors.values():
            curses.init_pair(color.id, color.foreground, color.background)
            curses.init_pair(color.id+1, color.background, color.foreground)

        # load instruments
        for i in self.instruments:
            i.draw_to_screen(self.screen)

        self.screen.clear()
        self.draw_state()

    def info(self, text):
        info_width = 48
        self.screen.addstr(0, 0, ' ' * info_width, Colors['default'].color()) # clear
        self.screen.addstr(0, 0, text, Colors['default'].inverse()) # print

    # for pickling
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['screen']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.reset_screen()
