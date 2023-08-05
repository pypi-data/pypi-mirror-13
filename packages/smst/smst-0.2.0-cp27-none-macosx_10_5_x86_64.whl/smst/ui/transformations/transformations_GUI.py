from Tkinter import *
from ..notebook import notebook   # window with tabs

from .stftMorph_GUI_frame import StftMorph_frame
from .sineTransformations_GUI_frame import SineTransformations_frame
from .harmonicTransformations_GUI_frame import HarmonicTransformations_frame
from .stochasticTransformations_GUI_frame import StochasticTransformations_frame
from .hpsTransformations_GUI_frame import HpsTransformations_frame
from .hpsMorph_GUI_frame import HpsMorph_frame

def main():
    root = Tk( )
    root.title('sms-tools transformations GUI')
    nb = notebook(root, TOP) # make a few diverse frames (panels), each using the NB as 'master':

    # uses the notebook's frame
    f1 = Frame(nb( ))
    stft = StftMorph_frame(f1)

    f2 = Frame(nb( ))
    sine = SineTransformations_frame(f2)

    f3 = Frame(nb( ))
    harmonic = HarmonicTransformations_frame(f3)

    f4 = Frame(nb( ))
    stochastic = StochasticTransformations_frame(f4)

    f5 = Frame(nb( ))
    hps = HpsTransformations_frame(f5)

    f6 = Frame(nb( ))
    hpsmorph = HpsMorph_frame(f6)

    nb.add_screen(f1, "STFT Morph")
    nb.add_screen(f2, "Sine")
    nb.add_screen(f3, "Harmonic")
    nb.add_screen(f4, "Stochastic")
    nb.add_screen(f5, "HPS")
    nb.add_screen(f6, "HPS Morph")


    nb.display(f1)

    root.geometry('+0+0')
    root.mainloop( )

if __name__ == '__main__':
    main()
