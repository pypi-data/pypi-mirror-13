# -*- coding: utf-8 -*-
# The MIT License (MIT)
#
# Copyright (c) 2011-2016 Thorsten Simons (sw@snomis.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Sos of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyrighftware without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copiet notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import argparse
import os
import sys


from hcptcmds.hcpinit import gvars
import hcptcmds.hcpf
import hcptcmds.hcpcookie
import hcptcmds.hcpload
import hcptcmds.hcplist
import hcptcmds.hcpretention
import hcptcmds.hcptest
import hcptcmds.hcpunload

def hcpArgs():
    '''
    hcpArgs - build the argument parser, parse the command line and
              run the respective functions.
    '''

    #===========================================================================
    # create the main parser as a central switchboard
    #===========================================================================
    mainDescription = '''%(prog)s serves as a switchboard for the HCP tools.
    Required option is the subcommand to be used. Please note that arguments
    described here are additional to the subcommand\'s arguments.'''

    mainEpilog='''Use it this way:
    %(prog)s [common arguments] subcommand [subcommand arguments]'''

    mainVersions='  %(prog)s: {0}\n'.format(gvars.Version) + \
                 '   cookie: {0}\n'.format(hcptcmds.hcpcookie.Version) + \
                 '     load: {0}\n'.format(hcptcmds.hcpload.Version) + \
                 '     list: {0}\n'.format(hcptcmds.hcplist.Version) + \
                 'retention: {0}\n'.format(hcptcmds.hcpretention.Version) + \
                 '     test: {0}\n'.format(hcptcmds.hcptest.Version) + \
                 '   unload: {0}\n'.format(hcptcmds.hcpunload.Version)

    mainParser = argparse.ArgumentParser(description=mainDescription,
                            formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=mainEpilog)
    mainParser.add_argument('--version', action='version',
                           version=mainVersions)
    mainParser.add_argument('-u', '--user', dest='user', required=True,
                            help='data access acount')
    mainParser.add_argument('-p', '--password', dest='password',
                            help='''password (will require manual input if not
                            given)''')
    mainParser.add_argument('-l', '--logfile', dest='logfile',
                            help='logfile (defaults to \'%(prog)s_subcmd.log\')')
    mainParser.add_argument('-i', '--loginterval', type=int, dest='loginterval',
                            default=10, metavar='seconds',
                            help='logging interval (defaults to 10 sec.)')
    mainParser.add_argument('-t', '--threads', type=int, dest='NoOfThreads',
                            default=30, metavar='\'# of threads\'',
                            help='no. of parallel threads (defaults to 30)')
    mainParser.add_argument('--nossl', dest='nossl', action='store_true',
                            default=False,
                            help='use http instead of https')
    mainParser.add_argument('-v', dest='verbose', action='count', default=0,
                            help='''verbosity (-v = INFO, -vv = DEBUG,
                            -vvv = garbage collection statistics)''')
    mainParser.add_argument('--gc', dest='gc', metavar='t1.t2.t3',
                            help='''garbage collection thresholds (defaults to
                            \'700.10.10\'- see \'http://docs.python.org/py3k/
                            library/gc.html#gc.set_threshold\')''')
    subparsers = mainParser.add_subparsers(dest='subCmdName')

    #===========================================================================
    # create the parser for 'cookie'
    #===========================================================================
    cookieDescription = '''Calculate the HCP access token to be used in
    http-requests.'''
    cookieParser = subparsers.add_parser('cookie',
                                         help='calculate HCP access token',
                                         description=cookieDescription)
    cookieParser.add_argument('--version', action='version',
                              version='%(prog)s {0}'.format(hcptcmds.hcpcookie.Version),
                              help='show subfunctions version and exit')
    cookieParser.add_argument("acctype", choices=["daac", "mapi"],
                              help="account type (DataAccessAccount or MAPI)")
    cookieParser.set_defaults(func=hcptcmds.hcpcookie.hcpCookie)

    #===========================================================================
    # create the parser for 'load'
    #===========================================================================
    loadDescription='''\'%(prog)s\' performs bulk data ingestion into HCP for
    testing purposes. It always uses https (or http if \'--nossl\' is given) and
    allows for multi-threaded ingestion.'''

    loadEpilog='''Controlled by \'--structure [#_of_dirs
    [#_of_dirs [...]]] #_of_files\', a directory structure is build and
    \'#_of_files\' copies of \'ingestfile\' will be ingested into each lowest
    level directory. Example: \'3 3 3\' causes three directories to be created
    below \'targetdir\' (0000, 0001, 0002), with another three subdirectories
    (0000, 0001, 0002) in each of them and three copies of \'ingestfile\' to be
    written into each of these subdirectories. Be cautious, you could use up a
    lot of capacity in HCP and generate a lot of network trafic while using
    it...'''

    loadParser = subparsers.add_parser('load',description=loadDescription,
                                       epilog=loadEpilog,
                                       help='load bulk testdata into HCP')
    loadParser.add_argument('--version', action='version',
                           version='%(prog)s {0}'.format(hcptcmds.hcpload.Version),
                           help='show subfunctions version and exit')
    loadParser.add_argument('-c', '--cluster', required=True,
                            help='target namespace (full qualified DNS-name)')
    loadParser.add_argument('-d', '--dir', dest='targetdir', required=True,
                            metavar='directory',
                            help='''target directory (\'/rest/...\' or
                            \'/fcfs_data/...\')''')
    loadParser.add_argument('-f', '--file', dest="file", required=True,
                            metavar='ingestfile',
                            help="file to be ingested")
    loadParser.add_argument('-r', '--retention', dest="retention",
                            metavar='retention_string', default='0',
                            help="retention (requires valid HCP retention string)")
    loadParser.add_argument('--structure', dest='matrix', type=int,
                            required=True, nargs='+', metavar='#',
                            help='directory structure to be build')
    loadParser.add_argument('--reqlogfile',
                            default=None, required=True,
                            help='log time needed per PUT into file')

    loadParser.set_defaults(func=hcptcmds.hcpload.hcpLoad)

    #===========================================================================
    # create the parser for 'list'
    #===========================================================================
    listDescription = """'%(prog)s' lists all objects in a given subdirectory
    within an HCP namespace while discovering the directory tree top/down.                                               Don't (!!!) run it against \
    large directory trees on a production server - it may kill the server while
    eating up all resources..."""

    listEpilog = """Be aware: when discovering large directory trees, memory
    usage might become a problem, up to the point where this program might hang
    or even crash. You should monitor it by using '-v' or even '-vvv'. Best
    advice is to limit the number of threads (-t) to not more than 50 and limit
    the queues (--QF and --Qdb) to 10.000 and 20.000 respectively. You might
    encounter a deadlock situation, where "--QF" will be at max. and no object
    will be found. In this case, you'll need to unlimit '--QF' and maybe lower
    the threads. Speeding up the garbage collection by tuning '--gc' might help,
    too. But take care: this program might grab as many main memory as
    available, potentially affecting other applications - it\'s up to you
    to monitor that! Expect long (and I mean: really long) run times when
    discovering multi-million object directory trees! If you'd like to work with
    the database generated by this program, you could use tools provided at
    'http://www.sqlite.org/download.html'. The Windows distribution provides an
    executable shell (sqlite3.exe) in the installation folder."""

    listParser = subparsers.add_parser('list', description=listDescription,
                                       epilog=listEpilog,
                                       help='list HCP content')
    listParser.add_argument('--version', action='version',
                           version='%(prog)s {0}'.format(hcptcmds.hcplist.Version),
                           help='show subfunctions version and exit')
    listParser.add_argument('-c', '--cluster', required=True,
                            help='target namespace (full qualified DNS-name)')
    listParser.add_argument('-d', '--dir', dest='targetdir', required=True,
                            metavar='directory',
                            help='''target directory (\'/rest/...\' or
                            \'/fcfs_data/...\')''')
    listParser.add_argument('--all', dest='deltoo', action='store_true',
                            default=False,
                            help='''find deleted objects, too (if versioning is
                            configured for the namespace)''')
    listParser.add_argument('-B', '--database', dest='database',
                            help='''database file (defaults to
                            \'{0}hcptcmds.<timestamp>.[fat|slim].sqlite3\')'''.\
                            format(os.path.splitext(
                                            os.path.basename(sys.argv[0]))[0]))
    listParser.add_argument('--out', dest='out', choices=['db', 'csv', 'both'],
                            default='csv',
                            help='select the output format')
    listParser.add_argument('--fatDB', '--fat', dest='fatDB', action='store_true',
                            default=False,
                            help='include all available information in database')
    # listParser.add_argument('--noKeepDB', dest='keepdb', action='store_false',
    #                         default=True,
    #                         help='delete the database file when finished')
    listParser.add_argument('--QF', dest='QF', default='-1', metavar='queuesize',
                            help='defines the allowed no. of items in FindQueue')
    listParser.add_argument('--Qdb', dest='Qdb', default='-1',
                            metavar='queuesize',
                            help='''defines the allowed no. of items in
                            dbWriterQueue''')
    listParser.add_argument('--delay', type=int, dest='delay', default='0',
                            metavar='milliseconds',
                            help='''add a delay (pause) in ms between two
                            requests executed against HCP by a single thread''')
    listParser.add_argument('--outfile', dest='outfile',
                            default='{0}hcptcmds.csv'.format(os.path.splitext(
                                            os.path.basename(sys.argv[0]))[0]),
                            help='''filename for the resulting .csv file
                            (defaults to \'%(prog)s.csv\')''')
    # listParser.add_argument('--nooutfile', dest='nooutfile',
    #                         action='store_true', default=False,
    #                         help='don\'t write an outfile, but keep database')
    listParser.add_argument('--showThreads', dest='showThreads',
                            action='store_true', default=False,
                            help='show info about running threads')
    listParser.add_argument('--pause_after', dest='pause_after', default=0,
                            action='store',
                            help='pause discovery after <amt> files found')
    listParser.add_argument('--pause_minutes', dest='pause_minutes', default=0,
                            action='store',
                            help='pause discovery for <amt> minutes when --pause_after'
                                 'triggers')
    listParser.set_defaults(func=hcptcmds.hcplist.hcpList)

    #===========================================================================
    # create the parser for 'retention'
    #===========================================================================
    retentionDescription = '''\'%(prog)s\' takes a database generated by
    \'%(prog)s list\', where the column \'flist.new_ret\' has been altered with a new
    retention string (see below). For every object (!) with a value in column
    \'flist.new_ret\', \'%(prog)s\' tries to change the objects retention within
    HCP to the given value.'''

    retentionEpilog = '''To alter the database, you could use \'sqlite3.exe\',
    provided in the installation folder of this tool. For example, if your
    database file is called \'hcplist.sqlite3\' and you want to add 1 year to
    every object\'s retention, you could follow these steps prior to running
    this tool:
    ...
    c:\> sqlite3 hcplist.sqlite3
    sqlite> UPDATE flist SET new_ret=\'R+1y\' WHERE type=\'file\' OR type=\'object\';
    sqlite> .quit
    ...
    It is _YOUR_ responsibility to specify a valid retention string - this
    program will not check it for validity!!!'''


    retentionParser = subparsers.add_parser('retention',
                                            description=retentionDescription,
                                            epilog=retentionEpilog,
                                            help='''change retention setting for
                                                 selected objects within HCP
                                                 (see specific instructions)''')
    retentionParser.add_argument('--version', action='version',
                           version='%(prog)s {0}'.format(
                                               hcptcmds.hcpretention.Version),
                           help='show subfunctions version and exit')
    retentionParser.add_argument('-B', '--database', dest="database",
                                 required=True,
                                 help='''database file generated by \'hcp list\'
                                 and altered as described below'''.format(
                                        os.path.splitext(
                                            os.path.basename(sys.argv[0]))[0]))
    retentionParser.add_argument('--delay', type=int, dest='delay',
                                 default=0,
                                help='''add a delay (pause) in ms between two
                                requests executed against HCP by a single
                                thread''')
    retentionParser.set_defaults(func=hcptcmds.hcpretention.hcpRetention)


    #===========================================================================
    # create the parser for 'test'
    #===========================================================================
    testDescription='''\'%(prog)s\' runs all subcommands agains HCP, making
                    sure that the program works.'''

#    testEpilog=''''''

    testParser = subparsers.add_parser('test',description=testDescription,
#                                       epilog=testEpilog,
                                       help='test-run all the subcommands')
    testParser.add_argument('--version', action='version',
                           version='%(prog)s {0}'.format(hcptcmds.hcptest.Version),
                           help='show subfunctions version and exit')
    testParser.add_argument('-c', '--cluster', required=True,
                            help='target namespace (full qualified DNS-name)')
    testParser.add_argument('-d', '--dir', dest='targetdir', required=True,
                            metavar='directory',
                            help='''target directory (\'/rest/...\' or
                            \'/fcfs_data/...\')''')
    testParser.add_argument('-f', '--file', dest="file", required=True,
                            metavar='ingestfile',
                            help="file to be ingested")
    testParser.add_argument('--versionedNS', dest='versionedNS', action='store_true',
                              default=False,
                              help='''set this if the target namespace has versioning
                              enabled''')
    testParser.add_argument('-r', '--retention', dest="retention",
                            metavar='retention_string', default='N+1s',
                            help="retention (defaults to 'N+1s')")
    testParser.add_argument('--structure', dest='matrix', type=int,
                            required=True, nargs='+', metavar='#',
                            help='directory structure to be build')
    testParser.set_defaults(func=hcptcmds.hcptest.hcpTest)


    #===========================================================================
    # create the parser for 'unload'
    #===========================================================================
    unloadDescription = '''\'%(prog)s\' performs deletion of data within HCP
    namespaces by discovering a directory tree top/down. Will find all
    directories and objects within that tree and will imediately begin with
    object deletion right after one has been found. Directory deletion will
    start down/up when the whole tree has been discovered. It will write a
    sqlite3 database file with a single record for each directory and object
    found, containing all the information available for it. This can grow quite
    large...'''

    unloadEpilog = '''Be aware: if you have directories with a huge number
    (10.000++) of objects, main memory will become excessive used, even more
    the more threads you use. This could lead to runtime errors - in this case
    you will need to serialize the processing by limiting the number of threads
    down to 1 (one) depending on the available main memory. Of course, this will
    lead to a much longer runtime - monitor the processing by using the
    commandline switch \'-v\'.'''

    unloadParser = subparsers.add_parser('unload',
                                         description=unloadDescription,
                                         epilog=unloadEpilog,
                                         help='delete content from HCP')
    unloadParser.add_argument('--version', action='version',
                              version='%(prog)s {0}'.\
                              format(hcptcmds.hcpunload.Version),
                              help='show subfunctions version and exit')
    unloadParser.add_argument('-c', '--cluster',  dest='cluster',
                              required=True,
                              help='target namespace (full qualified dns-name)')
    unloadParser.add_argument('-d', '--dir', dest="targetdir",
                              metavar='directory', required=True,
                              help='''target directory (/rest/... or
                              /fcfs_data/...)''')
    unloadParser.add_argument('--infile', dest='infile',
                      help='''file holding a list of objects to be deleted (full
                      path: \'/rest/.../object\' or \'/fcfs_data/.../object\'.
                      If set, \'--dir\' will be used to determine the type of
                      namespace, only.''')
    unloadParser.add_argument('-B', '--database', dest='database',
                      help='''database file (defaults to
                      \'{0}hcptcmds.<timestamp>.[fat|slim].sqlite3\')'''.\
                      format(os.path.splitext(os.path.basename(sys.argv[0]))[0]))
    unloadParser.add_argument('--fatDB', dest='fatDB',
                              help='''include all available information in
                              database''', action='store_true', default=False)
    unloadParser.add_argument('--keepDB', dest='keepdb',
                              help='''do not delete the database file when
                              finished''', action="store_true", default=False)
    unloadParser.add_argument('--QF', type=int, dest='fQueueSize', default=-1,
                              metavar='queuesize',
                              help='''size of internal queue (defaults to
                              unlimited)''')
    unloadParser.add_argument('--Qdb', type=int, dest='Qdb', default='-1',
                              metavar='queuesize',
                              help='''defines the allowed no. of items in
                              dbWriterQueue''')
    unloadParser.add_argument('--objonly', dest='objonly',
                              help='do not delete directories',
                              action='store_true', default=False)
    unloadParser.add_argument('--purge', dest='purge',
                              help='''purge versions (if not set, directory
                              deletion will fail if versioning is enabled)''',
                              action='store_true', default=False)
    unloadParser.add_argument('--privileged', dest='reason',
                              help='''perform privileged delete (requires a
                              \'reason\')''')
    unloadParser.add_argument('--YES', dest='yes', action='store_true',
                              default=False,
                              help='''...if you really (!) want to delete the
                              found objects/directories (defaults to \'generate
                              a list of objects/directories only\')''')
    unloadParser.add_argument('--versionedNS', dest='versionedNS', action='store_true',
                              default=False,
                              help='''set this if the target namespace has versioning
                              enabled''')
    unloadParser.set_defaults(func=hcptcmds.hcpunload.hcpUnload)

    #===========================================================================
    # parse the arguments
    #===========================================================================
    args = mainParser.parse_args()

    ############################################################################
    ## now: handle global arguments!
    ##      (subCmd specific arguments will be handles within the subCmd)
    ############################################################################

    #===========================================================================
    # --gc - set garbage collection thresholds
    #===========================================================================
    if args.gc:
        try:
            gcThresholds(args.gc)
        except:
            mainParser.exit(status=1,
                message="--gc='t0.t1.t2': you need to provide integers!")

    #===========================================================================
    # if needed, initialize the logging facility (handle verbosity, also)
    #===========================================================================
    if args.subCmdName != 'cookie':
        if args.subCmdName == 'test' and args.verbose < 1:
            args.verbose = 1
        try:
            if not args.logfile:
                args.logfile='{0}_{1}.log'.\
                    format(os.path.splitext(os.path.basename(sys.argv[0]))[0],
                           args.subCmdName)
            logger = initLogging(args.logfile, args.verbose)
        except:
            mainParser.exit(status=1,
                            message="initialization of logging facility failed")
    else:
        logger = None

    #===========================================================================
    # call the subParser's dedicated function, thus execute the specific
    # subcommand
    #===========================================================================
    try:
        args.func(vars(args), logger)
    except hcptcmds.hcpf.hcpError as e:
        mainParser.exit(status=1, message=e.errText)


#===============================================================================
# gcThresholds - set Garbage Collector thresholds
#===============================================================================
def gcThresholds(gcThresholds):
    '''
    Garbage Collector thresholds must be given in the form of 't0.t1.t2'
    and will be converted to a list of integers here.
    '''
    import gc

    l=gcThresholds.split('.')
    gc.set_threshold(int(l[0]),int(l[1]),int(l[2]))

#===============================================================================
# initLogging - initialize the logging facility
#===============================================================================
def initLogging(logFile, verbosity):
    import logging
    import gc

    strhandler = logging.StreamHandler(sys.stdout)
    fhandler = logging.FileHandler(logFile, "w")
    frm = logging.Formatter("%(asctime)s [%(levelname)-8s] %(message)s", "%m/%d %H:%M:%S")
    strhandler.setFormatter(frm)
    fhandler.setFormatter(frm)
    logging.addLevelName(49, "STARTUP")
    logging.addLevelName(48, "STOPDOWN")
    l = logging.getLogger()
    l.addHandler(strhandler)
    l.addHandler(fhandler)
    if not verbosity:
        l.setLevel(logging.WARNING)
    elif verbosity == 1:
        l.setLevel(logging.INFO)
    elif verbosity == 2:
        l.setLevel(logging.DEBUG)
    else:
        l.setLevel(logging.DEBUG)
        ## enable garbage collector statistics
        l.debug("enabling Garbage Collector statistics to sys.stderr")
        gc.set_debug(gc.DEBUG_STATS)

    return(l)


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]
    hcpArgs()

#===============================================================================
# __main__ - program progess flow starter
#===============================================================================
if __name__ == '__main__':
    main()
