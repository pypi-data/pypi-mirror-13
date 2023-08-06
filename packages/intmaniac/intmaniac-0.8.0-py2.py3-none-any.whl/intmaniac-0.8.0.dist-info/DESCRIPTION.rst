INTManiac
=========

A docker-compose based integration / user acceptance test / whatever test tool. For more information please `see the GitHub page`_.

.. _`see the GitHub page`: https://github.com/flypenguin/python-intmaniac

CHANGELOG
=========

0.8.0
-----

- TeamCity outputs pretty sensbile now


0.7.0
-----

- added configuration fields ``test_before`` and ``test_after``
- won't mention "cleanup and bugfixes" any more


0.6.0
-----

- changed test directory logic, is now ``$pwd/intmaniac_$PID`` by default
- command line settings override everything now
- fixed a couple of bugs
- internal restructuring


0.5.2
-----

- fixed bug in cleanup command execution
- fixed bug in exception logging (yeah)
- fixed logging output diarrhoe


0.5.1
-----

- fixed string handling bug


0.5.0
-----

- Switched to ``popen()`` for command execution because of thread-safety (setting of current working directory)
- Create a log file with all output by default now in ``base_dir``
- Fixed a couple of python 3 string / bytes handling issues
- Internal refactoring and restructuring


0.4.1
-----

- Documentation update (added CHANGES.rst, README.rst for pypi)
- Unit testing available in python 2.x now with external mock module
- Internal changes


