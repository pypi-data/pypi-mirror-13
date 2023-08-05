import argparse,sys,os
from yac.lib.config import get_root_path
from sets import Set

yac_commands = ['stack', 'app', 'db', 'vpc', 'naming', 'security', 'primer', 'setup', 'restore']

def show_primer(command_array):

    path_elements = [get_root_path(),'primer']

    path_elements = path_elements + command_array

    # make sure no options are mixed in
    if len(Set(command_array) & Set(yac_commands)) != len(command_array):

        print ("Options cannot be used with the primer command. usage: yac <command> <subcommand> primer")

    else:
        with open(os.path.join( *path_elements)) as primer_file:
            primer_file_content = primer_file.read()

        print primer_file_content
