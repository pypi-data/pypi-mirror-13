import sys

from grid_pager import GridPager


def run():
    sys.argv.extend(["--action", "take-window"])
    gp = GridPager()
    gp.perform_action()