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

import os
import sys
import time
import sqlite3
import pprint


from hcptcmds import hcpf
import hcptcmds.hcpcookie
import hcptcmds.hcpload
import hcptcmds.hcplist
import hcptcmds.hcpretention
import hcptcmds.hcpunload


# initialized needed variables
#
_version="0.9.3"
_build="2011-07-07/Sm"
Version = "v.{0} ({1})".format(_version, _build)
Author = "\nContact: sw@snomis.de"
optionen = None
logger = None


#===============================================================================
# hcpTest - runs all subcommands to make sure they work
#===============================================================================
def hcpTest(opts, logr):
    global optionen
    optionen = opts
    logger = logr
#    print("optionen: ", opts)

    ## startup information
    #
    logger.info("{0} {1} {2}".format(os.path.splitext(
                                        os.path.basename(sys.argv[0]))[0],
                                optionen["subCmdName"], Version))
    logger.info("    Logfile: " + optionen["logfile"])
    if optionen["nossl"]:
        logger.info("     Target: http://" + optionen["cluster"] +  optionen["targetdir"])
    else:
        logger.info("     Target: https://" + optionen["cluster"] +  optionen["targetdir"])
    logger.info("DataAccAcnt: " + optionen["user"])
    logger.info(" Ingestfile: " + optionen["file"])
    StartTime = time.time()
    logger.info(" Started at: " + time.strftime("%a, %d.%m., %H:%M:%S", time.localtime(StartTime)))
    logger.info(53 * '=')
    logger.info(' ')

    ## check the argurments provided
    #
    if not optionen["password"]:
        optionen["password"] = hcpf.getPassword(optionen["user"])

    dbName='{0}_{1}.{2}.db'.format(
                os.path.splitext(os.path.basename(sys.argv[0]))[0], 'list',
                                 time.strftime("%Y%d%m%H%M%S",
                                               time.localtime(time.time())))

    hcpTests = [['Test 1: generate a cookie for a DataAccessAccount',
                 hcptcmds.hcpcookie.hcpCookie,
                 {'subCmdName':'cookie',
                  'user':optionen['user'],
                  'password':optionen['password'],
                  'acctype':'daac',
                  }],
                ['Test 2: generate a cookie for MAPI access',
                 hcptcmds.hcpcookie.hcpCookie,
                 {'subCmdName':'cookie',
                  'user':optionen['user'],
                  'password':optionen['password'],
                  'acctype':'mapi',
                  }],
                ['Test 3: ingest some objects into HCP',
                 hcptcmds.hcpload.hcpLoad,
                 {'subCmdName':'load',
                  'acctype':'daac',
                  'user':optionen['user'],
                  'password':optionen['password'],
                  'verbose':1,
                  'nossl':optionen['nossl'],
                  'loginterval':optionen['loginterval'],
                  'logfile':optionen['logfile'],
                  'NoOfThreads':optionen['NoOfThreads'],
                  'cluster':optionen['cluster'],
                  'targetdir':optionen['targetdir'],
                  'file':optionen['file'],
                  'retention':'0',
                  'matrix':optionen["matrix"],
                  }],
                ['Test 4: list the newly ingested objects',
                 hcptcmds.hcplist.hcpList,
                 {'subCmdName':'list',
                  'acctype':'daac',
                  'user':optionen['user'],
                  'password':optionen['password'],
                  'verbose':1,
                  'nossl':optionen['nossl'],
                  'loginterval':optionen['loginterval'],
                  'logfile':optionen['logfile'],
                  'NoOfThreads':optionen['NoOfThreads'],
                  'cluster':optionen['cluster'],
                  'targetdir':optionen['targetdir'],
                  'keepdb':True,
                  'database':dbName,
                  'nooutfile':False,
                  'fatDB':False,
                  'deltoo':True,
                  'outfile':'{0}_{1}.csv'.format(os.path.splitext(
                                            os.path.basename(sys.argv[0]))[0],
                                            optionen["subCmdName"]),
                  'QF':-1,
                  'Qdb':-1,
                  'delay':0,
                  'gc':None,
                  'showThreads':False,
                  'pause_after': 0,
                  'pause_minutes':0,
                  'out': 'db',
                  }],
                ['Test 5: prepare the database file for retention changes',
                 chgRetentionDB,
                 {'database':dbName,
                  'targetdir':optionen['targetdir'],
                  'retention':optionen['retention'],
                  }],
                ['Test 6: change the retention of the newly ingested objects',
                 hcptcmds.hcpretention.hcpRetention,
                 {'subCmdName':'retention',
                  'user':optionen['user'],
                  'password':optionen['password'],
                  'verbose':1,
                  'nossl':optionen['nossl'],
                  'loginterval':optionen['loginterval'],
                  'logfile':optionen['logfile'],
                  'NoOfThreads':optionen['NoOfThreads'],
                  'database':dbName,
                  'delay':0,
                  'gc':None,
                  }],
                ['Test 7: delete the newly ingested objects',
                 hcptcmds.hcpunload.hcpUnload,
                 {'subCmdName':'unload',
                  'acctype':'daac',
                  'user':optionen['user'],
                  'password':optionen['password'],
                  'verbose':1,
                  'nossl':optionen['nossl'],
                  'loginterval':optionen['loginterval'],
                  'logfile':optionen['logfile'],
                  'NoOfThreads':optionen['NoOfThreads'],
                  'versionedNS':optionen['versionedNS'],
                  'cluster':optionen['cluster'],
                  'targetdir':optionen['targetdir'],
                  'keepdb':True,
                  'database':'{0}_{1}.{2}.db'.format(os.path.splitext(
                                            os.path.basename(sys.argv[0]))[0],
                                            'unload',
                                            time.strftime("%Y%d%m%H%M%S",
                                                time.localtime(time.time()))),
                  'nooutfile':False,
                  'fatDB':False,
                  'deltoo':True,
                  'QF':-1,
                  'Qdb':-1,
                  'fQueueSize':-1,
                  'delay':0,
                  'gc':None,
                  'showThreads':False,
                  'purge':True,
                  'reason':'hcpthcptcmds',
                  'objonly':False,
                  'yes':True,
                  'infile':None,
                  }],
                ]

    for tst in hcpTests:
        logger.info('-' * len(tst[0]))
        logger.info(tst[0])
        logger.info('-' * len(tst[0]))
        logger.debug('==> \'{0}\':'.format(tst[2]))
        tst[1](tst[2], logger)
        logger.info(' ')

    ## shutdown information
    #
    EndTime = time.time()
    EstTime = EndTime - StartTime
    logger.info(53 * '=')
    logger.info(" Started at: " + time.strftime("%a, %d.%m., %H:%M:%S", time.localtime(StartTime)))
    logger.info("   Ended at: " + time.strftime("%a, %d.%m., %H:%M:%S", time.localtime(EndTime)))
    logger.info("    Runtime: " + "{0:.2f}".format(EstTime) + " Sekunden")


#===============================================================================
# chgRetentionDB - change the retention field in a (hcp list-) database
#===============================================================================
def chgRetentionDB(optionen, logger):

    if optionen["targetdir"][1:5] == "rest":
        optionen["authNamespace"] = True
    else:
        optionen["authNamespace"] = False

    logger.info("*** database update begins ***")
    logger.info("*** changing all object's retention to '{0}' ***".format(
                                                        optionen["retention"]))
    DBconnect = sqlite3.connect(optionen["database"])
    DBcursor = DBconnect.cursor()
    if optionen["authNamespace"]:
        DBcursor.execute("UPDATE flist SET new_ret=? WHERE type='object'",
                         (optionen["retention"],))
    else:
        DBcursor.execute("UPDATE flist SET new_ret=? WHERE type='file'",
                         (optionen["retention"],))
    DBconnect.commit()
    DBconnect.close()
    logger.info("*** database update finished ***")



    pass


if __name__ == '__main__':
    print("not for standalone use")
    pass