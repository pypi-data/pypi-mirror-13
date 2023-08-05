from Tkinter import *

from ..notebook import create_notebook
from .dftModel_GUI_frame import DftModelFrame
from .stftModel_GUI_frame import StftModelFrame
from .sineModel_GUI_frame import SineModelFrame
from .harmonicModel_GUI_frame import HarmonicModelFrame
from .stochasticModel_GUI_frame import StochasticModelFrame
from .sprModel_GUI_frame import SprModelFrame
from .spsModel_GUI_frame import SpsModelFrame
from .hprModel_GUI_frame import HprModelFrame
from .hpsModel_GUI_frame import HpsModelFrame

def main():
    root = Tk()
    root.title('sms-tools models GUI')

    # make a few diverse frames (panels), each using the NB as 'master':
    create_notebook(root, [
        ("DFT", DftModelFrame),
        ("STFT", StftModelFrame),
        ("Sine", SineModelFrame),
        ("Harmonic", HarmonicModelFrame),
        ("Stochastic", StochasticModelFrame),
        ("SPR", SprModelFrame),
        ("SPS", SpsModelFrame),
        ("HPR", HprModelFrame),
        ("HPS", HpsModelFrame)
    ])

    root.geometry('+0+0')
    root.mainloop()


if __name__ == '__main__':
    main()
