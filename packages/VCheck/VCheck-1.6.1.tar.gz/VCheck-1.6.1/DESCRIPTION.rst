VCheck
======

This project is designed to make version checking easier in scripts. A 
common development problem of scripts is that they depend on older
versions of packages that have evolved.  These scripts may have
incompatibilities with the newer modules that result in the scripts
breaking. It is then very difficult to track down which version of the
module the script depends on if it was never recorded which version of
the module the script is built against.

Initially, this requires modules to be installed via PIP in
development mode in a git repository. The end-goal is to have version
checking be flexible enough to detect git and work with or without it.
