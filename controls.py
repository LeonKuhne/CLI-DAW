import pickle
import re

class Controls:
    def __init__(self, daw, info=lambda _: None):
        self.daw = daw
        self.info = daw.info # TODO create a display class and pass that instead
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
            'f': self.load_project, # open project file
            'q': lambda: self.quit(True), # save and quit
            'Q': self.quit, # force quit
            
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
                self.info(f"Unknown binding: {key}")

    def prompt(self, text):
        self.info(text)

        response = ""
        key = ""
        while not (key == '\n' and len(response) > 0):
            key = self.daw.screen.getkey()
            
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

    def save_project(self):
        project_name = self.prompt('save as ') 
        if not project_name:
            self.info("project not saved")
            return

        with open(f"{project_name}.proj", 'wb') as f:
            pickle.dump(self.daw, f)
        self.info(f"saved as '{project_name}.proj'")

    def load_project(self):
        project_name = self.prompt('load project ')
        
        if not project_name:
            self.info("no project loaded")
            return
        
        with open(f"{project_name}.proj", 'rb') as f:
            self.daw = pickle.load(f) # TODO navigation doesn't work on load
        self.info(f"loaded '{project_name}.proj'")

    def quit(self, save=False):
       self.daw.playing = False
       self.listening = False

       if save:
           self.save_project()

