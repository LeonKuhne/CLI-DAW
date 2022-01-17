#!/bin/python
from instrument import Instrument
from daw import Daw
from controls import Controls

if __name__ == '__main__':
    # create instruments with rhythms
    kick = Instrument('samples/kick.wav')
    kick.set_rhythm("𝅘𝅥     𝅘𝅥     𝅘𝅥     𝅘𝅥")

    snare = Instrument('samples/snare.wav')
    snare.set_rhythm("        𝅘𝅥       "*2)

    hat = Instrument('samples/hat.wav')
    hat.set_rhythm("𝅘𝅥 "*16)

    ohat = Instrument('samples/oh.wav')
    ohat.set_rhythm("    𝅘𝅥   "*4)

    # create the daw
    daw = Daw()
    daw.add_instrument(kick)
    daw.add_instrument(snare)
    daw.add_instrument(hat)
    daw.add_instrument(ohat)

    # listen to controls
    controls = Controls(daw)
    controls.listen()
