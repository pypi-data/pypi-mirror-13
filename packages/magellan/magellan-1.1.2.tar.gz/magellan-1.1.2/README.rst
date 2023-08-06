========
Magellan
========
*Explore Python Package Dependencies like your name is Fernando!*

**Mission / Goals:**

The overall aim is to do with package exploration for conflict detection.

E.g. Going from one version of a library to another (i.e. upgrading Django)
can cause conflicts when some dependencies need to be upgraded, but others
depend on the earlier versions. It may be necessary to upgrade due to
important security updates no longer being maintained on a platform, thus
this requires a solution.

**Installation:**

NB: Best to install Magellan into its own dedicated environment so as not to pollute the results you are interrogating.

python setup.py install


**Command line interfaces:**

magellan <options>


**Options:**

*Positional Arguments*

``<packages>`` e.g. ``Package1 Package2 etc..``
    Packages to explore.

*Optional Arguments*

``-h, --help``
    Show this help message and exit

``-f <package_file>, --package-file <package_file>``
    File with list of packages

``-r <requirements_file>, --install-requirements <requirements_file>``
                        Requirements file (e.g. requirements.txt) to install.

``-n <venv_name>, --venv-name <venv_name>``
    Specify name for virtual environment, default isMagEnv0, MagEnv1 etc

*Functional with output*

``-A <package-name>, --get-ancestors <package-name>``
     Show which packages in environment depend on <package-name>

``-Z <package-name>, --get-descendants <package-name>``
     Show which packages in environment <package-name> depends on; can be useful if package not on PyP.

``-D <package-name> <version>, --get-dependencies <package-name> <version>``
    Get dependencies of package, version combo, from PyPI. NB Can be used multiple times but must always specify desired version. Usage -D <package-name> <version>.

``-C, --detect-env-conflicts``
    Runs through installed packages in specified environment to detect if there are any conflicts between dependencies and versions.

``-P <package> <version>, --package-conflicts <package> <version>``
    Check whether a package will conflict with the current environment, either through addition or change. NB Can be used multiple times but must always specify desired version.

``-O, --outdated``
    Checks whether the major/minor versions of a package are outdated.

``-R, --compare-env-to-req-file``
    Compare a requirements file to an environment.

``-l <package>, --list-all-versions <package>``
    List all versions of package on PyPI and exit. NB Can be used multiple times; supersedes -s/-p.

``-s, --show-all-packages``
    Show all packages by name and exit.

``-p, --show-all-packages-and-versions``
    Show all packages with versions and exit.

*Configuration Arguments*

``-v, --verbose``
    Verbose mode

``--super-verbose``
    Super verbose mode

``--path-to-env-bin <path-to-env-bin>``
    Path to virtual env bin

``--cache-dir <cache-dir>``
    Cache directory - used for pip installs.

``--keep-env-files``
    Don't delete the nodes, edges, package_requirements env files.

``--no-pip-update``
    If invoked will not update to latest version of pip when creating new virtual env.

``--logfile``
    Set this flag to enable output to magellan.log.

``--colour  |  --color``
    Prints output to console with pretty colours.


**Example Usage:**

- ``magellan  |  magellan -h``
        Prints out help file.
- ``magellan -R -r requirements.txt -n MyEnv``
        Compares requirements file to environment for differences.
- ``magellan <packages> -O  |  magellan -O  |  magellan -O -f myPackageFile.txt``
        Checks packages to see if they are outdated on major/minor versions. If no packages or files are specified it checks all within the environment.
- ``magellan -r requirements.txt -O``
        Checks outdated major/minor versions in requirements file.
- ``magellan -n MyEnv -P PackageToCheck Version``
        Highlight conflicts with current environment when upgrading or adding a new package.
        Note this argument can be called multiple times, e.g., "magellan -n MyEnv -P Django 1.8.1 -P pbr 1.0.1"
- ``magellan -n MyEnv -C``
        Detect conflicts in environment "MyEnv"
- ``magellan -n MyEnv --package-file myPackageFile.txt --super-verbose``
        Analyse packages in myPackageFile.txt, using "super verbose" (i.e. debug) mode.
- ``magellan -l <package>``
        List all versions of <package> available on PyPI.
- ``magellan -s / magellan -p``
        Shows all packages in current environment (-p with versions). Performs no further analysis.
- ``magellan -s -n MyEnv``
        Shows all packages in MyEnv environment.
- ``magellan -s > myPackageFile.txt``
        Output all packages in current environment and direct into myPackageFile.txt.


**Known Issues:**
- finding requirements of scipy falls over as it has some prerequisites on system packages (BLAS etc).
Have fixed it so magellan doesn't crash on the failed install/pip crash.