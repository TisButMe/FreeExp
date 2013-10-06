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
        var_lines = [x for x in lines if x.count("=") == 1]
        for line in var_lines:
            var_name = line.split("=")[0].strip(" ")

            if line.split("=")[1].count(",") >= 1:
                value = [x.strip(" ") for x in line.split("=")[1].split(
                    ",")] # Splits the part of the line after the "=" by "," and removes extra spaces
                value[-1] = value[-1][:-1] # Removes the extra \n at the end of the var value
            else:
                value = line.split("=")[1].strip(" ")[:-1] # Same idea

            vars[var_name] = value
        return vars

    @staticmethod
    def clean_vars(lines):
        return [x for x in lines if x.count("=") == 0][1:]

    def find_exps(self, lines):
        #First we remove the extra blank lines separating the experiments
        raw_exps = [lines[0].lower()] + [lines[i].lower() for i in range(1, len(lines)) if
                                         not (lines[i] == '\n' and lines[i - 1] == '\n')]

        exps = [Experiment() for i in range(raw_exps.count('\n') + 1)]

        #We remove the \n terminating the line if there are any
        for i in range(len(raw_exps)):
            if raw_exps[i][-1] == '\n':
                raw_exps[i] = raw_exps[i][:-1]

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
                        line.split(".")[1:]] #We don't want the first part, whihc isn't a command.
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
                if command.count("with speed") == 0:
                    to_add = [Step("text", "", 1000) for i in range(len(parts))]
                    parts = self.mix_parts([parts, to_add])
                else:
                    to_add = [Step("text", "", command.split(" ")[-1]) for i in range(len(parts))]
                    parts = self.mix_parts([parts, to_add])

        return Experiment(parts)

    def gen_part_array(self, raw_part, mult=1):
        words = raw_part.strip(" ").split(" ")
        steps = []
        step_type = self.find_var_type(words[1])

        if len(words) == 2:
            for i in range(int(words[0]) * mult):
                #Looks for the i-nth element of the variable called (mod that var size to prevent errors)
                step_val = self.vars[words[1]][i % len(self.vars[words[1]])]
                steps.append(Step(step_type, step_val, 1000))
        elif len(words) == 5:
            speed = int(words[4])
            for i in range(int(words[0]) * mult):
                #Looks for the i-nth element of the variable called (mod that var size to prevent errors)
                step_val = self.vars[words[1]][i % len(self.vars[words[1]])]
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