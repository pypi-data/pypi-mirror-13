import sys

from grid_pager import GridPager

def run():
    sys.argv.extend(["--action", "switch-workspace"])
    gp = GridPager()
    gp.perform_action()
