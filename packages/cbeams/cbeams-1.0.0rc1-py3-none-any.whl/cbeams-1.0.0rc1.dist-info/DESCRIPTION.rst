in the terminal.
Home-page: http://pypi.python.org/pypi/cbeams/
Author: Jonathan Hartley
Author-email: tartley@tartley.com
License: UNKNOWN
Description: Dependencies
        ------------
        
        Developed on on Ubuntu 14.04.
        
        Likely runs on other Linux.
        
        Might work on OSX.
        
        Will not work on Windows. The 'cmd' terminal does not accept ANSI terminal
        codes. Could probably be made to work on Windows using 'colorama', or ansi.sys.
        
        Requires Python 3.4. Probably also runs on other 3.x, but I haven't tried it.
        
        Python dependencies are specified in setup.py.
        
        Install
        -------
        
        ::
        
            pip install cbeams
        
        Usage
        -----
        
        See `cbeams -h`.
        
        Immediate Future Plans
        ----------------------
        * Upload to PyPI
            Using setup.cfg instead of setup.py?
        * Create a wheel
            Using 'twine'? See https://packaging.python.org
            Backport this into python-app template
        * Create a redistributable binary for Linux
            Backport this into python-app template
        * Switch to python3.5.1
        * Create a redistributable binary for OSX
            Backport this into python-app template
        * Run on Windows, using colorama
        * Create a redistributable binary for Windows
        
        Hacking
        -------
        
        To populate a virtualenv, run tests, etc, see the commands in the Makefile.
        These can often work in Windows too, under Bash shells like Cygwin, Msys.
        
        Populating the virtualenv in the manner shown in the Makefile will also
        add "-e ." to the virtualenv, which adds this project in 'develop mode',
        meaning both that source edits are immediately visible within the virtualenv,
        and that the application entry points listed in setup.py are converted into
        executable scripts on the PATH.
        
        Thanks
        ------
        
        To the processes or influences that resulted in the creation of our universe
        and the emergence within it of complexity, life, and intelligence.
        
        Contact
        -------
        
        :For users: Downloads & documentation:
            http://pypi.python.org/pypi/cbeams/
        
        :For developers: Souce code & issues:
            https://github.com/tartley/cbeams/
        
        :Contact the author:
            Jonathan Hartley, email: tartley at domain tartley.com, Twitter: @tartley.
        
        
Keywords: console blessings ansi terminal animation
Platform: UNKNOWN
Classifier: Development Status :: 4 - Beta
Classifier: Environment :: Console
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: BSD License
Classifier: Natural Language :: English
Classifier: Operating System :: MacOS :: MacOS X
Classifier: Operating System :: POSIX :: Linux
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.4
Classifier: Programming Language :: Python :: Implementation :: CPython
Classifier: Topic :: Games/Entertainment
