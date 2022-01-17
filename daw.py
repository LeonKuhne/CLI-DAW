#!/bin/python

# mash together curses with audio player using a sequencer

import time
import curses
from threading import Thread
import pickle
import re
from instrument import Instrument, Sequencer, DIVISIONS
from tempo import Tempo

COLOR_COUNT = 0
class Color:
    def __init__(self, foreground, background):
        global COLOR_COUNT
        COLOR_COUNT += 2
        self.id = COLOR_COUNT
        self.foreground = foreground
        self.background = background

    def color(self):
        return curses.color_pair(self.id)
    
    def inverse(self):
        return curses.color_pair(self.id+1)

Colors = {
    'default': Color(curses.COLOR_WHITE, curses.COLOR_BLACK),
    'muted': Color(curses.COLOR_RED, curses.COLOR_BLACK),
    'highlight': Color(curses.COLOR_GREEN, curses.COLOR_BLACK),
    'border': Color(curses.COLOR_MAGENTA, curses.COLOR_BLACK),
}

class Daw:
    def __init__(self):
        self.selected_instrument_idx = 0
        self.selected_note_idx = 0
        self.instruments = []
        self.tick = 0
        self.tempo = Tempo(120, self.info)
        self.playing = False
        self.listening = False
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
            spacing = instrument.height()
            sequencer_line = 1+idx*spacing
            is_selected = idx == self.selected_instrument_idx
            selected_pos = self.selected_note_idx if is_selected else None
            
            instrument.draw(0, sequencer_line, selected_pos, Colors)
          
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
                self.tempo.tap()
            # reset tempo
            if key == 'T':
                self.tempo.reset()
                self.info(f"tempo taps cleared")
            # reset playhead
            if key == 'r':
                self.tick = 0
                for i in self.instruments:
                    i.seq.set_pos(0)
                self.screen.clear()
            # clean screen
            if key == 'c':
                self.screen.clear()
            # save and quit
            if key == 'q':
                self.save()
                self.playing = False
                self.listening = False
            # quit
            if key == 'Q':
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
       
        # load colors
        curses.start_color()
        for color in Colors.values():
            curses.init_pair(color.id, color.foreground, color.background)
            curses.init_pair(color.id+1, color.background, color.foreground)

        self.screen.clear()
        self.draw_state()

    #
    # Project Management

    def prompt(self, text):
        self.info(text)

        response = ""
        key = ""
        while not (key == '\n' and len(response) > 0):
            key = self.screen.getkey()
            
            if key == '\n': # submit on empty
                break
            if key == '\x7f': # support delete
                response = response[:-1]
            else:
                # sanitize 
                if key == ' ':
                    key = '_'
                # validate 
                if re.match(r'[a-zA-Z-_]', key):
                    response += key
            
            self.info(text + response)
        
        return response

    def save(self):
        project_name = self.prompt('save as ') 
        if not project_name:
            self.info("project not saved")
            return

        with open(f"{project_name}.proj", 'wb') as f:
            pickle.dump(self, f)
        self.info(f"saved as '{project_name}.proj'")

    def load(self):
        project_name = self.prompt('load project ')
        with open(f"{project_name}.proj", 'rb') as f:
            return pickle.load(f)

    def info(self, text):
        info_width = 48
        self.screen.addstr(0, 0, ' ' * info_width) # clear
        self.screen.addstr(0, 0, text, curses.A_REVERSE) # print

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['screen']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.reset_screen()

if __name__ == '__main__':
    kick = Instrument('samples/kick.wav')
    kick.set_rhythm("𝅘𝅥     𝅘𝅥     𝅘𝅥     𝅘𝅥")

    snare = Instrument('samples/snare.wav')
    snare.set_rhythm("        𝅘𝅥       "*2)

    hat = Instrument('samples/hat.wav')
    hat.set_rhythm("𝅘𝅥 "*16)
    
    ohat = Instrument('samples/oh.wav')
    ohat.set_rhythm("    𝅘𝅥   "*4)
   
    daw = Daw()
    daw.add_instrument(kick)
    daw.add_instrument(snare)
    daw.add_instrument(hat)
    daw.add_instrument(ohat)
    daw.listen()

