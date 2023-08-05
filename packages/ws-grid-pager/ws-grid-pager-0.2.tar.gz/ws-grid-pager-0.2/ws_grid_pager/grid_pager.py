#!/usr/bin/env python

import argparse
import os
from subprocess import call, check_output, Popen, PIPE
import sys

"""
This module contains a class, 'GridPager', which acts as a workspace pager
that treats the workspaces as if they actually are layed out as a grid.  It
is designed/tested for Fluxbox, but theoretically could be used by any EMWH-
compatable window manager which allows key-bindings to execute a cmd-line
program.  It's only dependecies are xprop, and wmctrl.
"""

class GridPager(object):
    """
    This class implements a workspace pager which can perform the
    following actions:
    * switch-workspace: switch the user's workspace left/right/up/down
    * send-window: send the current window to workspace left/right/up/down
    * take-window: switch the user's workspace left/right/up/down,
      bringing allong the current window

    It depends on the environment variables WORKSPACE_ROWS and
    WORKSPACE_COLUMNS being defined with integer values and that
    WORKSPACE_ROWS * WORKSPACE_COLUMNS = the number of workspaces

    The action, direction, and whether wrapping should be enabled
    are specified at the command-line
    """
    def __init__(self):
        # NOTE: the following variables are 1-based
        self.num_rows = self.get_int_env_var("WORKSPACE_ROWS")
        self.num_cols = self.get_int_env_var("WORKSPACE_COLUMNS")
        self.num_workspaces = self.get_xprop_value("_NET_NUMBER_OF_DESKTOPS")
        if self.num_rows * self.num_cols != self.num_workspaces:
            # FIXME? report an error somehow?
            sys.exit(1)
        # NOTE: the following variables are 0-based
        self.curr_ws = self.get_xprop_value("_NET_CURRENT_DESKTOP")
        self.curr_row = self.curr_ws // self.num_cols
        self.curr_col = self.curr_ws % self.num_cols
        args = self.parse_cmd_line_args()
        for key, val in args.items():
            setattr(self, key, val)
        if self.debug:
            self.dump_vars()

    def get_int_env_var(self, var_name):
        """Either returns the int value of an env var or raises an exception
        """
        try:
            str_val = os.environ[var_name]
            int_val = int(str_val)
        except KeyError:
            raise Exception("env var %s not defined" % var_name)
        except ValueError:
            raise Exception("env var %s is not an integer" % var_name)
        else:
           return int_val

    def get_xprop_value(self, property_name):
        """Queries xprop for property_name and returns it's value

        Probably should be more pythonic and parse out the value
        rather than piping it through awk
        """
        p1 = Popen(["xprop", "-root", property_name], stdout=PIPE)
        p2 = Popen(["awk", "{print $3}"], stdin=p1.stdout, stdout=PIPE)
        p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
        return int(p2.communicate()[0])

    def parse_cmd_line_args(self):
        """Parses the cmd-line args.  Will exit if required args are missing
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--direction",
                            choices=["left", "right", "up", "down"],
                            required=True)
        parser.add_argument("-a", "--action",
                            choices=["switch-workspace",
                                     "send-window",
                                     "take-window"],
                            required=True)
        parser.add_argument("-w", "--wrap", action="store_true")
        parser.add_argument("--debug", action="store_true")
        args = parser.parse_args()
        return vars(args)

    def dump_vars(self):
        """Prints the values of the variables determined within __init__
        """
        print """num rows: %d
num cols: %d
current workspace: %d
curr row: %d
cur col: %d
action: %s
direction: %s
wrap: %s""" % (self.num_rows, self.num_cols,
               self.curr_ws, self.curr_row, self.curr_col,
               self.action, self.direction, self.wrap)

    def calculate_new_workspace(self):
        """Calculates and returns the new workspace number.

           The calculation is based on the values of self.direction
           and self.wrap.

           The new workspace defaults to the current one, as the current
           workspace may be at either the first/last column/row.  If wrap
           is true, the new workspace will always be different than the
           current workspace
        """
        new_ws = self.curr_ws
        if "left" == self.direction:
            if 0 == self.curr_col:
                if self.wrap:
                    new_ws = (self.curr_row * self.num_cols) + self.num_cols -1
            else:
                new_ws = self.curr_ws - 1
        elif "right" == self.direction:
            if self.curr_col == self.num_cols -1:
                if self.wrap:
                    # first column of current row
                    new_ws = self.curr_row * self.num_cols
            else:
                new_ws = self.curr_ws + 1
        elif "up" == self.direction:
            if self.curr_row == 0:
                if self.wrap:
                    # same column of last row
                    new_ws = (self.num_rows - 1) * self.num_cols
            else:
                new_ws = self.curr_ws - self.num_cols
        elif "down" == self.direction:
            if self.curr_row == self.num_rows - 1:
                if self.wrap:
                    # same column, first row
                    new_ws = self.curr_col
            else:
                new_ws = self.curr_ws + self.num_cols
        return new_ws

    def perform_action(self):
        """Performs action the user requested, provided the new workspace differs
        """
        new_ws = self.calculate_new_workspace()
        if new_ws != self.curr_ws:
            if "switch-workspace" == self.action:
                self.switch_to_workspace(new_ws)
            elif "send-window" == self.action:
                self.send_active_window_to_workspace(new_ws)
            elif "take-window" == self.action:
                # this *could* be a separate function, but hardly worth it
                self.send_active_window_to_workspace(new_ws)
                self.switch_to_workspace(new_ws)

    def switch_to_workspace(self, workspace_num):
        """Switches the user's to workspace identified by workspace_num
        """
        cmd = "wmctrl -s %d" % workspace_num
        if self.debug: print cmd
        call(cmd, shell=True)

    def send_active_window_to_workspace(self, workspace_num):
        """Sends the active window to the workspace specified

           Only the active window is moved to the specified workspace. The
           user's workspace is not switched
        """
        cmd = "wmctrl -r \":ACTIVE:\" -t %d" % workspace_num
        if self.debug: print cmd
        call(cmd, shell=True)


# if __name__ == "__main__":
#     gp = GridPager()
#     gp.perform_action()
