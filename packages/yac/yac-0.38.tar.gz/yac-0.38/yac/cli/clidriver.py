import argparse,sys,os
import yac.cli.stack
import yac.cli.vpc
import yac.cli.app
import yac.cli.db
import yac.cli.naming
import yac.cli.security

from yac.cli.primer import show_primer

def main():

    # first argument is help
    if (len(sys.argv)==1 or sys.argv[1] == '-h'):

        show_primer(['primer'])

    # last argument is primer
    elif sys.argv[len(sys.argv)-1] == 'primer':

        # show primer instructions
        show_primer(sys.argv[1:])

    else:

        # strip command from args list
        command = sys.argv[1]
        sys.argv = sys.argv[1:]

        if command == 'stack':

            return yac.cli.stack.main()

        if command == 'app':

            return yac.cli.app.main()

        elif command == 'vpc':

            return yac.cli.vpc.main()

        elif command == 'db':

            return yac.cli.db.main()

        elif command == 'naming':

            return yac.cli.naming.main()

        elif command == 'security':

            return yac.cli.security.main()            

        else:

            return "command not supported, or not yet implemented"
        