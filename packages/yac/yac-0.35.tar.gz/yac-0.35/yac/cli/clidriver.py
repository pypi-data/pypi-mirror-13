import argparse,sys,os
import yac.cli.stack
import yac.cli.vpc
from yac.lib.config import get_config_path

def show_yac_usage():

    with open(os.path.join( get_config_path(),'primer','yac-usage')) as usage_file:
        yac_usage = usage_file.read()

    print yac_usage

def main():

    if sys.argv[1] == '-h':

        # show usage instructions
        show_yac_usage()

    else:

        # strip command from args list
        command = sys.argv[1]
        sys.argv = sys.argv[1:]

        if command == 'stack':

            return yac.cli.stack.main()

        elif command == 'vpc':

            return yac.cli.vpc.main()

        else:

            return "command not yet implemented"
        