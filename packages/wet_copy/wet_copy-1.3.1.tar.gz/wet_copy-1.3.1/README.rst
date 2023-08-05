Wet Copy
========
The purpose of this program is to format and print wetlab protocols that are 
stored as text files in git repositories.  Printed out protocols are nice 
because they can be easily carried around lab during an experiment, annotated 
in real time, and ultimately taped into a lab notebook.  Digital protocols 
stored as text files in git repositories are nice as well, because they can be 
updated and modified without losing any information.  This script helps manage 
the process of printing out and keeping track of digital protocols.

To use this program, start by the adding protocols you use to a git repository. 
Then use the wet_copy command to print out copies of your protocols formatted 
with all the information needed to recover the original digital protocol (e.g. 
a repository URL and a commit hash), enough space to make annotations in the 
margins, and lines showing where to cut so the protocol can be taped into a lab 
notebook.  The wet_copy command won't let you print protocols that have any 
lines wider than 53 characters (otherwise the margin will be too small) or that 
have any uncommitted changes (otherwise the original protocol won't be 
recoverable).

Installation
============
The easiest way to install wet_copy is from the PyPI::

    $ pip3 install wet_copy

Alternatively, you can clone this repository and install wet_copy from source::

    $ git clone git@github.com:kalekundert/wet_copy.git
    $ pip3 install ./wet_copy

Note that wet_copy requires python 3.

License
=======
Copyright (C) 2015, Kale Kundert

This program is free software: you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation, either version 3 of the License, or (at your option) any later 
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 
this program.  If not, see <http://www.gnu.org/licenses/>.

