__author__ = 'Thomas Poinsot'
# Copyright (c) 2013 Thomas Poinsot

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import Image
import ImageTk
import tkFont
import Tkinter as tk
from parser import Parser


class App:
    def __init__(self, exp_list, pause_message, end_message):
        self.exp_list = exp_list
        self.pause_mess = pause_message
        self.end_mess = end_message
        self.currentexp = 0

        self.root = tk.Tk()
        self.root.title("FreeExp 0.1")
        self.customfont = tkFont.Font(family="Helvetica", size=50)
        self.label = tk.Label(self.root)
        self.label.pack()

        self.display_text(self.pause_mess)
        self.root.bind_all("<Button-1>", lambda event: self.continue_exec())

        self.root.mainloop()

    def continue_exec(self):
        self.root.unbind_all("<Button-1>")
        last = self.exp_list[self.currentexp].do_next_step(self)

        if last and self.currentexp < len(self.exp_list) - 1:
            self.currentexp += 1
            self.display_text(self.pause_mess, clickable=True)
        elif last and self.currentexp == len(self.exp_list) - 1:
            self.display_text(self.end_mess)
            self.root.bind_all("<Button-1>", lambda event: self.root.quit())

    def display_image(self, filename, for_time=0, clickable=False):
        image = Image.open(filename)
        image.thumbnail((800, 600), Image.ANTIALIAS)
        tkimage = ImageTk.PhotoImage(image)
        self.label.configure(image=tkimage, width=800, height=600)
        self.label.image = tkimage

        if clickable:
            self.root.bind_all("<Button-1>", lambda event: self.continue_exec())

        if for_time != 0:
            self.root.after(for_time, self.continue_exec)

    def display_text(self, text, for_time=0, clickable=False):
        self.label.configure(text=text, image="", width=19, height=7,
                             font=self.customfont)
        if clickable:
            self.root.bind_all("<Button-1>", lambda event: self.continue_exec())

        if for_time != 0:
            self.root.after(for_time, self.continue_exec)


p = Parser("config.txt")
app = App(p.exp_list, p.pause_message, p.end_message)
