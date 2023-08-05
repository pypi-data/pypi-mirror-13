import sys

from grid_pager import GridPager


def run():
    sys.argv.extend(["--action", "send-window"])
    gp = GridPager()
    gp.perform_action()