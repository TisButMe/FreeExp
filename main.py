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

import Tkinter as tk
import Image
import ImageTk
import tkFont


class App:
    compt = 0
    exp = []

    def __init__(self, exp):
        self.root = tk.Tk()

        self.label = tk.Label(self.root)
        self.label.pack()

        self.exp = exp
        self.customfont = tkFont.Font(family="Helvetica", size=50)

        self.change()
        self.root.mainloop()

    def change(self, event=""):
        if self.compt < len(self.exp):
            if self.exp[self.compt][0] == "image":
                image = Image.open(self.exp[self.compt][1])
                image.thumbnail((800, 600), Image.ANTIALIAS)
                tkimage = ImageTk.PhotoImage(image)
                self.label.configure(image=tkimage, width=800, height=600)
                self.label.image = tkimage
                self.root.after(self.exp[self.compt][2], self.change)
            elif self.exp[self.compt][0] == "text":
                self.label.configure(text=self.exp[self.compt][1], image="", width=19, height=7,
                                     font=self.customfont)
                self.root.after(self.exp[self.compt][2], self.change)
            elif self.exp[self.compt][0] == "pause":
                self.root.bind("<Button-1>", self.change)
                self.label.configure(text=self.exp[self.compt][1], image="", width=19, height=7,
                                     font=self.customfont)

        self.compt += 1


def gen_exp(img_list, word_list, img_speed, word_speed, img_nb, word_nb):
    exp = []
    compt_words = 0
    compt_img = 0

    if img_nb > len(img_list) or word_nb > len(word_list):
        print(len(img_list))
        raise ValueError("The given lists of images or words are not long enough")

    for i in range(img_nb):
        exp.append(["image", img_list[compt_img], img_speed])
        compt_img += 1
        for j in range(word_nb):
            exp.append(["text", word_list[compt_words], word_speed])
            compt_words += 1

    return exp


def read_exp(f):
    try:
        img_line = f.readline().split(":")
        img_list = [x.strip(" ") for x in img_line[1].split(",")]
        img_list[-1] = img_list[-1][:-1] #Strips the \n char at the end of the last filename

        word_line = f.readline().split(":")
        word_list = [x.strip(" ") for x in word_line[1].split(",")]
        word_list[-1] = word_list[-1][:-1] #Same thing

        speed_line = f.readline().split(":")[1].split(",")
        speed_line = [x.strip(" ") for x in speed_line]
        img_speed = int(speed_line[0])
        word_speed = int(speed_line[1])

        nb_line = f.readline().split(":")[1].split(",")
        nb_line = [x.strip(" ") for x in nb_line]
        img_nb = int(nb_line[0])
        word_nb = int(nb_line[1])

        return gen_exp(img_list, word_list, img_speed, word_speed, img_nb, word_nb)

    except IndexError:
        return ""


def read_config(filename):
    exps = []

    with open(filename, 'r') as f:
        pause_message = f.readline().split(":")[1].strip(" ")[:-1]
        f.readline()

        exps += read_exp(f)
        while f.readline() == "\n":
            exps.append(["pause", pause_message])
            exps += read_exp(f)

    print exps
    return exps


app = App(read_config("config.txt"))
app.mainloop()
