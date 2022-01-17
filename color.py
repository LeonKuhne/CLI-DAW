#!/bin/python
import curses

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
