Timetrack (v1.0.2)
=======================

Track the time you spend on activities easily with simple commands.
Also includes pretty exports to JSON and TXT formats.

From the command line output of `./track -h`:

::

    usage: track [-h] [--start NAME] [--stop] [--export FORMAT] [--pretty]
                 [--backup] [--restore] [--clear] [--clear-backup] [-v]

    Current version: v1.0.2

    optional arguments:
      -h, --help       show this help message and exit
      --start NAME     stop the current activity (if any) and start a new one
      --stop           start the previously started activity (if any)
      --export FORMAT  export the database as a JSON or a TXT;
                       you may use '>' to write to a file
      --pretty         displays the output in a pretty format:
                        - JSON: Formats to a readable format
                        - TXT: Creates an aggregate table sorted by activity name
      --backup         make a copy of the database as a backup
      --restore        make a copy of the database as a backup
      --clear          clear the database
      --clear-backup   clear the backup database
      -v, --version    print time-track version and exit
