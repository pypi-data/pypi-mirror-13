#!/usr/bin/env python3

"""\
Format and print wetlab protocols stored as text files in git repositories.

Usage:
    wet_copy [options] <protocols>...

Arguments:
    <protocols>...
        The path to one or more protocols to print.  You can specify python 
        scripts (with arguments) as protocols by providing a space-separated 
        command line like so: wet_copy 'pcr.py 59 35'

Options:
    -d, --dry-run
        Print the formatted protocol, but don't send it to the printer.

Printed out protocols are nice because they can be easily carried around lab 
during an experiment, annotated in real time, and ultimately taped into a lab 
notebook.  Digital protocols stored as text files in git repositories are nice 
as well, because they can be updated and modified without losing any 
information.  This script helps manage the process of printing out and keeping 
track of digital protocols.

To use this program, start by the adding protocols you use to a git repository.  
Then use the wet_copy command to print out copies of your protocols formatted 
with all the information needed to recover the original digital protocol (e.g. 
a repository URL and a commit hash), enough space to make annotations in the 
margins, and lines showing where to cut so the protocol can be taped into a lab 
notebook.  The wet_copy command won't let you print protocols that have any 
lines wider than 53 characters (otherwise the margin will be too small) or that 
have any uncommitted changes (otherwise the original protocol won't be 
recoverable.)
"""

import os
import subprocess
import shlex
import datetime

__version__ = '1.3.1'
__author__ = 'Kale Kundert'
__email__ = 'kale.kundert@ucsf.edu'

page_width = 68
page_height = 60
content_width = 53
content_height = page_height - 4
margin_width = 78 - page_width

def main():
    import docopt
    args = docopt.docopt(__doc__)
    protocols = [format_protocol(x) for x in args['<protocols>']]
    print_protocols(protocols, dry_run=args['--dry-run'])

def run_command(command, cwd=None, error=None):
    if isinstance(command, str):
        command = shlex.split(command)
    try:
        return subprocess.check_output(command, cwd=cwd).strip().decode()
    except subprocess.CalledProcessError:
        if error is None:
            raise
        elif error == 'ok':
            pass
        else:
            print('Error: ' + error)

def format_protocol(protocol_path):
    """
    Read the given file and convert it into a nicely formatted protocol by 
    adding margins and a header.
    """

    protocol_path, *arguments = protocol_path.split()

    if not os.path.exists(protocol_path):
        print("Error: Protocol '{}' doesn't exist.".format(protocol_path))
        raise SystemExit

    # Figure out what commit is currently checked out and add that information 
    # to the top of the protocol.  Complain if there are any uncommitted 
    # changes.

    git_dir = run_command(
            'git rev-parse --show-toplevel',
            cwd=os.path.dirname(os.path.abspath(protocol_path)),
            error="'{}' not in a git repository.".format(protocol_path))

    protocol_relpath = os.path.relpath(protocol_path, git_dir)

    git_commit = run_command(
            'git log -n 1 --pretty=format:%H -- \'{}\''.format(protocol_relpath),
            cwd=git_dir,
            error="No commits found.")
    git_stale = protocol_relpath in run_command(
            'git ls-files --modified --deleted --others',
            cwd=git_dir)
    git_repo = run_command(
            'git config --get remote.origin.url',
            cwd=git_dir,
            error='ok') or git_dir

    if git_stale:
        print("Error: '{}' has uncommitted changes.".format(protocol_path))
        print()
        subprocess.call(shlex.split('git status'), cwd=git_dir)
        raise SystemExit

    # Create a header containing information about where the digital form of 
    # this protocol can be found.
    
    protocol = [ # (no fold)
            'file: {} {}'.format(protocol_relpath, ' '.join(arguments))[:page_width],
            'repo: {}'.format(git_repo)[:page_width],
            'commit: {}'.format(git_commit),
            'date: {0:%B} {0.day}, {0.year}'.format(datetime.date.today()),
    ]

    # If the given path refers to a python script, run that script to get the 
    # protocol.  Otherwise just read the file.

    if protocol_path.endswith('.py'):
        stdout = subprocess.check_output([protocol_path] + arguments)
        lines = stdout.decode().split('\n')
    else:
        if arguments:
            print("Error: Specified arguments to non-script protocol '{}'.".format(protocol_path))
            raise SystemExit
        with open(protocol_path) as file:
            lines = file.readlines()

    # Add the actual protocol to the list of lines.  Make sure none of the 
    # lines are too long to fit in the notebook.

    protocol.append('')

    for lineno, line in enumerate(lines, 1):
        line = line.rstrip()
        if line.startswith('vim:'):
            continue
        if len(line) > content_width:
            print("Warning: line {} is more than {} characters long.".format(
                lineno, content_width))
            if input("Continue anyways? [y/N] ").lower() != 'y':
                raise SystemExit
        protocol.append(line)

    # Remove trailing blank lines.

    while not protocol[-1].strip():
        protocol.pop()

    # Split the protocol into pages, if necessary.

    pages = []
    current_page = []

    for i, line_i in enumerate(protocol):
        # If the line isn't blank, add it to the current page like usual.

        if line_i.strip():
            current_page.append(line_i)

        # If the line is blank, find the next blank line and see if it fits on 
        # the same page.  If it does, add the blank line to the page and don't 
        # do anything special.  If it doesn't, make a new page.

        else:
            for j, line_j in enumerate(protocol[i+1:], i+1):
                if not line_j.strip():
                    break

            if i // page_height != j // page_height:
                pages.append(current_page)
                current_page = []
            else:
                current_page.append(line_i)

    pages.append(current_page)

    # Add a margin on the left, so that the pages can be stapled together 
    # naturally.

    left_margin = ' ' * margin_width + '│ '
    return ['\n'.join(left_margin + line for line in page) for page in pages]

def print_protocols(protocols, dry_run=False):
    """
    Print out the given protocols.

    If more than one protocol is sent to the printer, each protocol will be 
    printed on its own page.  It's also possible for a single protocol to span 
    multiple pages.  If dry_run=True, the protocols will be simply printed to 
    the terminal instead of being sent to the printer.
    """

    pages = sum(protocols, [])

    if dry_run:
        if len(pages) > 1:
            for page in pages:
                print(' ' * margin_width + '┌' + '─' * (page_width + 1))
                print(page)
                print(' ' * margin_width + '└' + '─' * (page_width + 1))
        else:
            print(pages[0])
    else:
        from subprocess import Popen, PIPE
        form_feed = ''
        print_cmd = (
                'paps --font "FreeMono 12" --left-margin 0 --right-margin 0 | '
                'lpr -o sides=one-sided'
        )
        lpr = Popen(print_cmd, shell=True, stdin=PIPE)
        lpr.communicate(input=form_feed.join(pages).encode())


if __name__ == '__main__':
    main()



