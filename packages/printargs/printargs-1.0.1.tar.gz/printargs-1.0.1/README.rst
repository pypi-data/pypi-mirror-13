README
======

Printargs - A debugging helper for argparse
-------------------------------------------

Print a nicely formatted view of an `argparse.Namespace` object
for debugging purposes:

::

    import sys
    import argparse    
    import printargs

    def main(args):
        printargs.show(args)
        # do somthing with args

    def get_argument_parser():
        p = argparse.ArgumentParser()
        p.add_argument('-f', '--foo', action='store')
        p.add_argument('-b', '--bar', action='store', type=int)
        p.add_argument('-o', '--output', action='store', default=sys.stdout)
        return p

    if __name__ == "__main__":
        argument_parser = get_argument_parser()
        args = argument_parser.parse_args()
        main(args)

To use the output for logging or to edit it use the `printargs.formatted`
function, which returns the string instead of printing it:

::

    import sys
    import argparse    
    import printargs

    def main(args):
        t = printargs.formatted(args)
        with open('log', 'a') as logfile:
            logfile.write("Test program called with parameters:")
            logfile.write(t)
            logfile.write("\n\n")
        

    def get_argument_parser():
        p = argparse.ArgumentParser()
        p.add_argument('-f', '--foo', action='store')
        p.add_argument('-b', '--bar', action='store', type=int)
        p.add_argument('-o', '--output', action='store', default=sys.stdout)
        return p

    if __name__ == "__main__":
        argument_parser = get_argument_parser()
        args = argument_parser.parse_args()
        main(args)

Installation
~~~~~~~~~~~~

Printargs can be installed with pip:

::

   me@machine:~$ pip install printargs

or from the sources:

::

   me@machine:~$ git clone https://HenningTimm@bitbucket.org/HenningTimm/printargs.git
   me@machine:~$ cd printargs
   me@machine:~/printargs$ python setup.py install


Planned features
~~~~~~~~~~~~~~~~

- curses based output with colors


License
~~~~~~~

Printargs is Open Source and licensed under the `MIT
License <http://opensource.org/licenses/MIT>`__.
