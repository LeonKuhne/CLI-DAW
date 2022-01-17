class Controls:
    def __init__(self, daw):
        self.daw = daw
        self.listening = False

        self.bindings = {
            # basic controls
            ' ': self.daw.toggle_play, # play/pause
            'm': lambda: self.daw.selected_instrument().toggle_mute(), # toggle mute
            't': self.daw.tempo.tap, # tempo
            'T': self.daw.tempo.reset, # reset tempo
            'r': self.daw.reset_playhead, # reset playhead
            'c': self.daw.screen.clear, # clean screen
            
            # manage projects
            'f': self.daw.load, # open project file
            'q': lambda: self.quit(True), # save and quit
            'Q': self.quit, # quit
            
            # select instrument
            'j': self.daw.next_instrument,
            'k': self.daw.prev_instrument,
            
            # select note
            'l': lambda: self.daw.move_note(1),
            'h': lambda: self.daw.move_note(-1),
            'w': lambda: self.daw.move_note(4),
            'b': lambda: self.daw.move_note(-4),

            # toggle note
            'i': lambda: self.daw.selected_instrument().seq.toggle_note(self.daw.selected_note_idx),
            
            # edit pattern
            'd': lambda: self.daw.selected_instrument().seq.duplicate(), # duplicate
            'e': lambda: self.daw.selected_instrument().seq.extend(), # extend
            's': lambda: self.daw.selected_instrument().seq.shorten(), # shorten
            'R': lambda: self.daw.selected_instrument().seq.reset(), # reset
        }
    
    # listen for keyboard input
    def listen(self):
        self.listening = True
         
        while self.listening:
            self.daw.draw_state()
            key = self.daw.screen.getkey()

            if key in self.bindings:
                self.bindings[key]()
            else:
                self.daw.info(f"Unknown binding: {key}")

    def quit(self, save=False):
       self.daw.playing = False
       self.listening = False

       if save:
           self.daw.save()
