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

import re
import copy
import random

from experiment import Experiment, Step


class Parser:
    def __init__(self, config_filename):
        self.lines = []

        with open(config_filename, "r") as f:
            line = f.readline()
            while line:
                self.lines.append(line)
                line = f.readline()

        self.lines = self.remove_comments(self.lines)
        self.lines = self.clean_up(self.lines)
        self.vars = self.find_vars(self.lines)
        self.lines = self.clean_vars(self.lines)
        self.exp_list = self.find_exps(self.lines)

        if "pause_message" in self.vars.keys():
            self.pause_message = self.vars["pause_message"]
        else:
            self.pause_message = "Next experiment"

        if "end_message" in self.vars.keys():
            self.end_message = self.vars["end_message"]
        else:
            self.end_message = "End of the experiments"

    @staticmethod
    def remove_comments(lines):
        return [x for x in lines if not x.startswith("//")]

    @staticmethod
    def clean_up(lines):
        while lines[0] == "\n":
            lines = lines[1:]

        while lines[-1] == "\n":
            lines = lines[:-1]
        return lines

    @staticmethod
    def find_vars(lines):
        vars = {}
        for line in [l for l in lines if re.search(r"=", l)]:
            regexp = re.compile(r"^\s*(\w+)\s*=\s*(.+\n?)").match(line)
            var_name = regexp.group(1)
            var_value = regexp.group(2)

            if re.search(r",", var_value):
                var_value = re.findall(r"\s*(\w+(?:\..{3})?)\s*(?:\n?|,)", var_value)
            else:
                var_value = re.match(r"(.+)\n?", var_value).group(1)

            vars[var_name] = var_value
        return vars

    def clean_vars(self, lines):
        return self.clean_up([x for x in lines if x.count("=") == 0])

    def find_exps(self, lines):
        #First we remove the extra blank lines separating the experiments
        raw_exps = [lines[0].lower()] + [lines[i].lower() for i in range(1, len(lines)) if
                                         not (lines[i] == '\n' and lines[i - 1] == '\n')]

        exps = [Experiment() for i in range(raw_exps.count('\n') + 1)]

        #We remove the \n terminating the line if there are any
        for i in range(len(raw_exps)):
            raw_exps[i] = re.match(r"(.*)\n?", raw_exps[i]).group(1)

        counter = 0
        for exp in raw_exps:
            if exp == '':
                counter += 1
                continue
                #Can't change this line to a +=, it somehow bypasses the [counter] and adds to every exp in exps (WTF ?)
            exps[counter].steps = exps[counter].steps + self.gen_exp_from_line(exp).steps

        return exps

    def gen_exp_from_line(self, line):
        #We first look for commands
        if line.count(".") >= 1:
            commands = [x.lower().strip(" ") for x in
                        line.split(".")[1:]] #We don't want the first part, which isn't a command.
            line = line.split(".")[0]
        else:
            commands = []

        #We look for "separated by", and split the line if there is one
        parts = line.split("separated by")

        #If the line starts with "display" we remove "display" from the line, and use the method to gen a part on the rest.
        if parts[0].startswith("display"):
            parts[0] = self.gen_part_array(parts[0][8:])

        #For the other parts, we directly use the method to gen parts array
        for i in range(1, len(parts)):
            parts[i] = self.gen_part_array(parts[i], len(parts[i - 1]))

        #We then mix the parts together in 1 final experiment.
        parts = self.mix_parts(parts)

        #We then apply the commands:
        for command in commands:
            if command.startswith("use blanks"):
                speed = re.search(r"with speed\s+(\d+)", command)
                if speed:
                    to_add = [Step("text", "", speed.group(1)) for i in range(len(parts))]
                else:
                    to_add = [Step("text", "", 1000) for i in range(len(parts))]

                parts = self.mix_parts([parts, to_add])

        return Experiment(parts)

    def gen_part_array(self, raw_part, mult=1):
        steps = []
        regexp = re.search(r"(\d+)\s+(random\s+)?(\w+)(?:\s+with speed\s+(\d+))?", raw_part)

        nb = int(regexp.group(1))
        random_step = True if regexp.group(2) else False
        var_name = regexp.group(3)
        speed = int(regexp.group(4)) if regexp.group(4) else 1000
        step_type = self.find_var_type(var_name)

        if random_step:
            current_vars = copy.deepcopy(self.vars)
            random.shuffle(current_vars[var_name])
        else:
            current_vars = self.vars

        for i in range(nb * mult):
            #Looks for the i-nth element of the variable called (mod that var size to prevent errors)
            step_val = current_vars[var_name][i % len(current_vars[var_name])]
            steps.append(Step(step_type, step_val, speed))

        return steps

    @staticmethod
    def mix_parts(parts):
        while len(parts) > 1:
            temp = []
            inclu_size = len(parts[-1]) / len(parts[-2])

            for i in range(len(parts[-2])):
                temp += [parts[-2][i]] + parts[-1][i * inclu_size:(i + 1) * inclu_size]

            parts[-2] = temp
            parts = parts[:-1]
        return parts[0]

    def find_var_type(self, var_name):
        if type(self.vars[var_name]) == list and self.vars[var_name][0].endswith(".jpg"):
            return "image"
        elif type(self.vars[var_name]) == list:
            return "text"