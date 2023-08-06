Summary
-------
This cube helps to manage and monitor subprocesses.

Description
-----------

This cube provides an easy way to run subprocesses using a dedicated
workflow.

Subprocesses can be configured (command line, environment, working
directory).

To start the subprocess, one just has to fire the 'start' transition.

The standard outputs (stdout and stderr) are stored into the database
as ``File``. The outputs are updated each time the subprocess writes
data into the stream.

The subprocess can update the ``advance_ratio`` to inform the user
about the process advancement.

Once the subprocess finishes, the ``complete`` or ``fail`` transition
is fired automatically.

The subprocess can be killed using the ``kill`` transition.