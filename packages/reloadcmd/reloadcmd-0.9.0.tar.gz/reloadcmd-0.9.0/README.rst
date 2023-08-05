=========
reloadcmd
=========

Re-executes program when files are changed, moved or deleted

Usage
=====
usage: monitor [-h] [-d DEBUG] [-p PATH] [-e [FILE_EXT [FILE_EXT ...]]] -c
               COMMAND

Restarts process when any files / directory changes

optional arguments:
  -h, --help            show this help message and exit
  -d DEBUG, --debug DEBUG
                        Debug mode
  -p PATH, --path PATH  Which directory to watch for changes
  -e [FILE_EXT [FILE_EXT ...]], --extension [FILE_EXT [FILE_EXT ...]]
                        Which file extensions to listen for
  -c COMMAND, --command COMMAND
                        Command to be executed

``$ reloadcmd --command "while [ 1 -eq 1 ]; do echo 2; sleep 1; done"``

Dependencies
============
* `watchdog <https://pypi.python.org/pypi/watchdog>`
* `coloredlogs <https://pypi.python.org/pypi/coloredlogs>`
