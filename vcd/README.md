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
