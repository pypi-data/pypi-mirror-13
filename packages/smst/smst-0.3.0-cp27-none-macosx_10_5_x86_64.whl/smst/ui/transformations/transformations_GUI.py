from Tkinter import *

from ..notebook import create_notebook
from .stftMorph_GUI_frame import StftMorphFrame
from .sineTransformations_GUI_frame import SineTransformationsFrame
from .harmonicTransformations_GUI_frame import HarmonicTransformationsFrame
from .stochasticTransformations_GUI_frame import StochasticTransformationsFrame
from .hpsTransformations_GUI_frame import HpsTransformationsFrame
from .hpsMorph_GUI_frame import HpsMorphFrame


def main():
    root = Tk()
    root.title('sms-tools transformations GUI')

    create_notebook(root, [
        ("STFT Morph", StftMorphFrame),
        ("Sine", SineTransformationsFrame),
        ("Harmonic", HarmonicTransformationsFrame),
        ("Stochastic", StochasticTransformationsFrame),
        ("HPS", HpsTransformationsFrame),
        ("HPS Morph", HpsMorphFrame)
    ])

    root.geometry('+0+0')
    root.mainloop()


if __name__ == '__main__':
    main()
