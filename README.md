virtualenv-command-dispatcher
====
I wanted to be able to use tools installed in virtualenvs without going through
the trouble of explicitly activating, or even moving to a directory
that auto-activates them, while remaining relatively friendly to most shells.

My solution is to inject the necessary info directly into the env of a python
subprocess call, thereby auto activating and deactivating the correct env
for the correct tool, as dictated by a user-maintained mapping file
(a list of aliases for the tools you want to use). Currently, this is
achieved by sourcing the activate script in the subprocess call before running
the command.

Usage
-----
There are two entry point scripts: vcd and vcdc

    vcd
        Runs all registered commands from the command line

    vcd-conifg
        Registers new virtualenvs ('venvs') and commands ('cmds') for use with vcd


Examples
--------
Install different versions of tools into their own virtualenvs, but execute them from the main system

    $ virtualenv old_pep8
    $ virtualenv new_pep8
    $ source old_pep8/bin/activate; pip install 'pep8==1.5.7'; deactivate
    $ source new_pep8/bin/activate; pip install pep8>1.5.7; deactivate

    $ vcd-config add venv old_pep8 ./old_pep8
    $ vcd-config add venv new_pep8 ./new_pep8
    $ vcd-config add cmd old_pep8 old-pep8
    $ vcd-config add cmd new_pep8 new-pep8
    $ vcd old-pep8 --verison
    1.5.7
    $ vcd new-pep8 --verison
    1.6.2
