Release History
===============

**1.0.19 - 2015-02-11**

    *   Changed distribution model to **pip**, only - shipment of pre-built
        Windows executables has been discarded.
    *   Set context to NOVERIFY in **retention** and **unload** to work around
        a restriction for HTTPS connections invented with Python 3.5

**1.0.18 - 2015-05-20**

    *   Fixed hcplist: re-queue an URL if an HcpsdkTimeoutError is raised
        during read()

**1.0.17 - 2015-05-13**

    *   Added more debugging output for *list* when using -vvv

**1.0.16 - 2015-04-07**

    *   Fixed hcplist: fixed a bug when discovering the default namespace

**1.0.15 - 2015-03-29**

    *   Now build with hcpsdk 0.9.2.21
    *   Fixed hcplist: improved error handling for http requests

**1.0.14 - 2015-03-16**

    *   Now build with hcpsdk 0.9.2.13
    *   Added in hcplist: --pause_after and --pause_minute to allow hcplist to
        stop discovery after a number of found folders and objects for some
        minutes. This is due to some older HCP systems having problems to keep
        pace with the tool
    *   Fixed hcplist: better error handling for http requests

**1.0.13 - 2015-03-08**

    *   Now build with hcpsdk 0.9.0.6

**1.0.12 - 2015-03-01**

    *   Fixed a situation where in 'list'a persistent connection was left in an
        unusable state due to not reading all received data from the response

**1.0.11 - 2015-02-27**

    *   Fixed a bug in 'unload' that lead to an exception being raised when
        unloading the default namespace
    *   Merged the 1.0.8 and 1.0.10 branches

**1.0.9 - 2015-02-20**

    *   'list', 'load': now using hcpsdk to connect HCP
    *   'list': now db, csv or both are written during the run, no more db dump at the end

**1.0.8 - 2012-03-06**

    *   Changed  the licensing model to the MTI License,
        the documentation to the open office format,
        the setup scripts to allow for installation into Python's
        site-packages folder

**1.0.7 - 2012-02-29**

    *   Fixed a bug in 'unload' that prevented deletion of objects when --purge
        wasn't given.

**1.0.6 - 2012-02-29**

    *   Fixed a bug in dbwriter, crashing thread due to eroneous SQL command
        when doing a 'unload' with --fatDB enabled

**1.0.5 - 2012-02-15**

    *   For 'unload', a switch '--versionedNS' to be set when the target
        namespace allows versioning.

**1.0.4 - 2011-12-01**

    *   Changed in 'list': the behaviour when thread end, to assure that
        dbWriter can execute all its requests.

**1.0.3 - 2011-11-30**

    *   Changed in 'list': csvWriter now used 'UTF-8' encoding

**1.0.2 - 2011-08-05**

    *   Fixed another bug keeping the dbWriter from doing the last commit

**1.0.1 - 2011-08-05**

    *   Changed in 'list': fixed another bug keeping the program from ending if
        dbWriter thread dies

**1.0.0 - 2011-08-04**

    *   Changed in 'list': stop program when dbWriter thread fails

**0.9.9 - 2011-07-07**

    *   Added version of all subCmds are listet when calling 'hcpt --version'
    *   Minor changes in 'hcptest'

**0.9.8 - 2011-07-06**

    *   Fixed a false argument setting for 'unload' in hcpt.py

**0.9.7 - 2011-07-05**

    *   Fixed bug in subCmd 'test' - transfer of 'loginterval' to the subCmds
    *   Epilog of subCmd 'retention's help message
    *   Added a User Manual ;-)

**0.9.6 - 2011-07-04**

    *   Added hcpretention as subcommand into hcpt
    *   Fixed a bug in _unload.hcpunload.py

**0.9.5 - 2011-07-01**

    *   Added a test suite, available as subcommand 'test'

**0.9.4 - 2011-07-01**

    *   Added added hcpunload as subCmd 'unload' into hcp

**0.9.3 - 2011-06-30**

    *   Minor bug fixes in hcpargs.py and _cookie/hcpcookie.py
    *   Moved hcpArgs() into hcp.py, skipping hcpargs.py

**0.9.2 - 2011-06-29**

    *   Added hcpload as subCmd 'load' into hcpt

**0.9.0 - 2011-06-29**

    *   Initial Release - merging most of the HCP tools into one. 1st step is
        hcpcookie and hcplist
