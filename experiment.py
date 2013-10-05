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


class Experiment:
    def __init__(self, steps=[]):
        self.steps = steps
        self.current_step = 0

    def __getitem__(self, item):
        return self.steps[item]

    # Returns true if their is no more steps to do
    def do_next_step(self, display):
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]

            if step.type == "text":
                display.display_text(step.value, step.length)
            elif step.type == "image":
                display.display_image(step.value, step.length)
            elif step.type == "click":
                if step.action == "display_text":
                    display.display_text(step.value, clickable=True)
                elif step.action == "display_image":
                    display.display_image(step.value, clickable=True)

            self.current_step += 1
            return False
        else:
            return True


class Step:
    def __init__(self, step_type, value, length=0, action=""):
        self.type = step_type
        self.value = value
        self.length = length
        self.action = action