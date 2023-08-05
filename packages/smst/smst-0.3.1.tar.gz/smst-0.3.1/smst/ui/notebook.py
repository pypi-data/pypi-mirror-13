from Tkinter import *


class Notebook(object):
    def __init__(self, master, side=LEFT):
        self.active_fr = None
        self.count = 0
        self.choice = IntVar(0)
        if side in (TOP, BOTTOM):
            self.side = LEFT
        else:
            self.side = TOP
        self.rb_fr = Frame(master, borderwidth=2, relief=GROOVE)
        self.rb_fr.pack(side=side, fill=BOTH)
        self.screen_fr = Frame(master, borderwidth=2, relief=FLAT)
        self.screen_fr.pack(fill=BOTH)

    def __call__(self):
        return self.screen_fr

    def add_screen(self, fr, title):
        b = Radiobutton(self.rb_fr, text=title, indicatoron=0, variable=self.choice, value=self.count,
                        command=lambda: self.display(fr))
        b.pack(fill=BOTH, side=self.side)
        if not self.active_fr:
            fr.pack(fill=BOTH, expand=1)
        self.active_fr = fr
        self.count += 1

    def display(self, fr):
        self.active_fr.forget()
        fr.pack(fill=BOTH, expand=1)
        self.active_fr = fr


def create_notebook(root, frame_classes):
    # make a few diverse frames (panels), each using the NB as 'master':
    nb = Notebook(root, TOP)

    frames = []
    for title, frame_class in frame_classes:
        frame = Frame(nb())
        controller_frame = frame_class(frame)
        frames.append(frame)
        nb.add_screen(frame, title)

    nb.display(frames[0])

    return nb
