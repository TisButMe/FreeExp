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
import time
import threading

import mtTkinter as tk


class App:
    def __init__(self, exp_list, pause_message):
        self.exp_list = exp_list
        self.pause_mess = pause_message
        self.end_mess = "End of the experiment !"
        self.currentexp = 0
        self.running_exp_thread = threading.Thread()

        self.root = tk.Tk()
        self.customfont = tkFont.Font(family="Helvetica", size=50)
        self.label = tk.Label(self.root)
        self.label.pack()

        self.display_text(self.pause_mess)
        self.root.bind_all("<Button-1>", lambda event: self.start(self.currentexp))

        self.root.mainloop()

    def start(self, expnb=0):
        if not self.running_exp_thread.isAlive() and expnb < len(self.exp_list):
            if expnb == len(self.exp_list) - 1:
                self.running_exp_thread = threading.Thread(target=self.exp_list[expnb].start, args=[self, True])
            else:
                self.running_exp_thread = threading.Thread(target=self.exp_list[expnb].start, args=[self])

            self.running_exp_thread.daemon = True
            self.running_exp_thread.start()
            self.currentexp += 1

    def display_image(self, filename):
        image = Image.open(filename)
        image.thumbnail((800, 600), Image.ANTIALIAS)
        tkimage = ImageTk.PhotoImage(image)
        self.label.configure(image=tkimage, width=800, height=600)
        self.label.image = tkimage

    def display_text(self, text):
        self.label.configure(text=text, image="", width=19, height=7,
                             font=self.customfont)


class Experiment:
    def __init__(self, img_list, word_list, img_speed, word_speed, img_nb, word_nb):
        self.exp = self.gen_exp(img_list, word_list, img_speed, word_speed, img_nb, word_nb)

    def __getitem__(self, item):
        return self.exp[item]

    def start(self, display, last=False):
        for step in self.exp:
            print(step.value)
            if step.type == "text":
                display.display_text(step.value)
            elif step.type == "image":
                display.display_image(step.value)

            time.sleep(float(step.length) / 1000)

        if last:
            display.display_text(display.end_mess)
        else:
            display.display_text(display.pause_mess)

    @staticmethod
    def gen_exp(img_list, word_list, img_speed, word_speed, img_nb, word_nb):
        exp = []
        compt_words = 0
        compt_img = 0

        if img_nb > len(img_list) or word_nb > len(word_list):
            raise ValueError("The given lists of images or words are not long enough")

        for i in range(img_nb):
            exp.append(Step("image", img_list[compt_img], img_speed))
            compt_img += 1
            for j in range(word_nb):
                exp.append(Step("text", word_list[compt_words], word_speed))
                compt_words += 1

        return exp


class Step:
    def __init__(self, step_type, value, length):
        self.type = step_type
        self.value = value
        self.length = length


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

        return Experiment(img_list, word_list, img_speed, word_speed, img_nb, word_nb)

    except IndexError:
        return ""


def read_config(filename):
    config = {}
    experiment_list = []

    with open(filename, 'r') as f:
        pause_message = f.readline().split(":")[1].strip(" ")[:-1]
        f.readline()

        experiment_list.append(read_exp(f))
        while f.readline() == "\n":
            experiment_list.append(read_exp(f))

    config["p_mess"] = pause_message
    config["list"] = experiment_list

    return config


config = read_config("config.txt")
app = App(config["list"], config["p_mess"])

