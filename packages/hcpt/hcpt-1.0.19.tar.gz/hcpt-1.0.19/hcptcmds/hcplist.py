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

### hcp-list.py - list all content within an HCP folder
#

import time
import queue
import threading
from urllib.parse import quote
import os.path
import sys
import xml.sax
import sqlite3
from pprint import pprint
import csv
from xml.sax import handler
import hcpsdk

from hcptcmds import hcpf

# initialize needed variables
#
_version="1.4.6"
_build="2015-05-20/Sm"
Version = "v.{0} ({1})".format(_version, _build)
Author = "\nContact: sw@snomis.de"
optionen = None
logger = None


## Print startup messages
#
def printStartMsgs():
    global optionen, logger

    msg = ["{0} {1} {2}".format(os.path.splitext(os.path.basename(sys.argv[0]))[0],
                                optionen["subCmdName"], Version),\
          "    Logfile: " + optionen["logfile"],
          "Loginterval: " + str(optionen["loginterval"]) + " sec.",]
    if optionen['out'] in ['db', 'both']:
          msg.append("   Database: " + optionen["database"])
    if optionen['out'] in ['csv', 'both']:
          msg.append("   CSV file: " + optionen["outfile"])
    # if optionen["keepdb"]:
    #     msg.append("             (will be kept when finished)")
    if optionen["fatDB"]:
        msg.append("             (will include all available information)")
    if optionen["deltoo"]:
        msg.append("             (will include deleted objects)")
    if optionen["nossl"]:
        msg.append("     Target: http://" + optionen["cluster"] + optionen["targetdir"])
    else:
        msg.append("     Target: https://" + optionen["cluster"] + optionen["targetdir"])
    # if not optionen["nooutfile"]:
    if optionen["authNamespace"]:
        msg.append("DataAccAcnt: " + optionen["user"])
    msg.append("    Threads: " + str(optionen["NoOfThreads"]))
    if optionen["QF"] != '-1':
        msg.append("    FindQue: {0:,}".format(int(optionen["QF"])))
    if optionen["Qdb"] != '-1':
        msg.append("dbWriterQue: {0:,}".format(int(optionen["Qdb"])))
    if optionen["delay"]:
        msg.append("      Delay: {0:,} ms between requests within each thread".format(int(optionen["delay"])))
    msg.append("  Verbosity: " + str(optionen["verbose"]))
    if optionen["gc"]:
        msg.append("  GC tuning: t0={0}, t1={1}, t2={2}".format(optionen["gc"][0],
                                                                optionen["gc"][1],
                                                                optionen["gc"][2]))
    StartTime = time.time()
    msg.append(" Started at: " + time.strftime("%a, %d.%m., %H:%M:%S", time.localtime(StartTime)))
    msg.append(79 * "-")
    # log messages...
    for logline in msg:
        logger.log(49, logline)
    return(StartTime)

## Print shutdown messages
#
def printEndMsgs(StartTime, EndTime, EstTime):

    msg = [79 * "-",
           " Started at: " + time.strftime("%a, %d.%m., %H:%M:%S", time.localtime(StartTime)),
           "   Ended at: " + time.strftime("%a, %d.%m., %H:%M:%S", time.localtime(EndTime)),
           "    Runtime: " + calcTime(EstTime) + " h:m:s.ms",
           "      Found: {0:,} Directories, {1:,} Objects".format(optionen["NoOfDirsFound"],
                                                                  optionen["NoOfFilesFound"]),
#           "      Found: " + str(optionen["NoOfDirsFound"]) + " Directories, " + str(optionen["NoOfFilesFound"]) + " Objects",
           "   Warnings: " + str(optionen["NoOfWarnings"]),
           "     Errors: " + str(optionen["NoOfErrors"])]
    # log messages...
    for logline in msg:
        logger.log(48, logline)

## from a given no. of bytes, calculate the biggest possible representation
#
def calcSize(bytes):
    sz = ["B", "Kb", "Mb", "Gb", "Tb"]
    i = 0
    bytes = int(bytes)
    while bytes > 1023:
                    bytes = bytes / 1024
                    i = i + 1
    return("{0:.2f} {1:}".format(bytes, sz[i]))

## from a given no. of seconds, calculate a time string
#
def calcTime(t):
    msec = int("{0:.2f}".format(t%1)[2:])
    min  = int(t//60)
    sec  = int(t%60)
    hour = int(min//60)
    min  = int(min%60)
    return("{0:02}:{1:02}:{2:02}.{3}".format(hour, min, sec, msec))

## Parse the XML returned by GET on a Directory
#
class SaxDocumentHandler(handler.ContentHandler):
    global optionen, logger

    def __init__(self, con):
        super().__init__()
        self.con = con

    def startElement(self, name, attrs):
        qEntry = None

        if name == "directory": # remind actual url
            self.url = attrs.get("path")
            self.utf8url = attrs.get("utf8Path")
        elif attrs.get("type") == 'directory' or attrs.get("fileType") == 'directory':
            if attrs.get(optionen["urlName"]) != '.':
                optionen["QFbox"].put(self.utf8url + "/" + attrs.get(optionen["urlName"]))
                if not optionen["fatDB"]:
                    if optionen["authNamespace"]:
                        qEntry = (self.url+"/"+attrs.get("urlName"),
                                  self.utf8url+"/"+attrs.get("utf8Name"),
                                  attrs.get("type"),
                                  "","","","","","","","","","","","","","","")
                    else:
                        qEntry = (self.url+"/"+attrs.get("urlName"),
                                  self.utf8url+"/"+attrs.get("utf8Name"),
                                  attrs.get("fileType"), "",
                                  "","","","","","","","","","")
                else:
                    if optionen["authNamespace"]:
                        qEntry = (self.url+"/"+attrs.get("urlName"),
                                  self.utf8url+"/"+attrs.get("utf8Name"),
                                  attrs.get("type"), "",
                                  "","","","","","","","","","","","",
                                  "", attrs.get("state"))
                    else:
                        qEntry = (self.url+"/"+attrs.get("urlName", ''),
                                  self.utf8url+"/"+attrs.get("utf8Name"),
                                  attrs.get("fileType"),   attrs.get("size"),
                                  "",                      "",
                                  attrs.get("mode"),       attrs.get("modeString"),
                                  attrs.get("uid"),        attrs.get("gid"),
                                  attrs.get("accessTime"), attrs.get("accessTimeString"),
                                  attrs.get("modTime"),    attrs.get("modTimeString"))
                optionen["QdbWriter"].put(qEntry)
                FindWorker.WorkerLock.acquire()
                optionen["NoOfDirsFound"] += 1
                FindWorker.WorkerLock.release()
        elif attrs.get("type") == 'object' or attrs.get("fileType") == 'file':
            if not optionen["fatDB"]:
                if optionen["authNamespace"]:
                    qEntry = (self.url+"/"+attrs.get("urlName"),
                              self.utf8url+"/"+attrs.get("utf8Name"),
                              attrs.get("type"), attrs.get("size"),
                              "","","","","","","","","","","",
                              attrs.get("customMetadata"),"","")
                else:
                    qEntry = (self.url+"/"+attrs.get("urlName"),
                              self.utf8url+"/"+attrs.get("utf8Name"),
                              attrs.get("fileType"),   attrs.get("size"),
                              "","","","","","","","","","","",
                              "","","")
            else:
                if optionen["authNamespace"]:
                    qEntry = (self.url+"/"+attrs.get("urlName"),
                              self.utf8url+"/"+attrs.get("utf8Name"),
                              attrs.get("type"),                    attrs.get("size"),
                              attrs.get("hashScheme"),              attrs.get("hash"),
                              attrs.get("retention"),               attrs.get("retentionString"),
                              attrs.get("retentionClass"),          attrs.get("ingestTime"),
                              attrs.get("ingestTimeString"),        attrs.get("hold"),
                              attrs.get("shred"),                   attrs.get("dpl"),
                              attrs.get("index"),                   attrs.get("customMetadata"),
                              attrs.get("version"),                 attrs.get("state"))
                else:
                    try:
                        (ret, retStr, hascm) = self.getMetaData(self.url+"/"+attrs.get(optionen["urlName"]))
                    except:
                        ret = -9
                        retStr = "reading metadata failed"
                        hascm = False
                    '''
                    ["urlName", "utf8Name", "type", "size", 'ret', 'retStr', "mode", "modeString",
                                           "uid", "gid", "accessTime", "accessTimeString",
                                           "modTime", "modTimeString", "customMetadata"]
                    '''

                    qEntry = (self.url+"/"+attrs.get(optionen["urlName"]),
                              self.utf8url+"/"+attrs.get("utf8Name"),
                              attrs.get("fileType"),   attrs.get("size"),
                              ret,                     retStr,
                              attrs.get("mode"),       attrs.get("modeString"),
                              attrs.get("uid"),        attrs.get("gid"),
                              attrs.get("accessTime"), attrs.get("accessTimeString"),
                              attrs.get("modTime"),    attrs.get("modTimeString"),
                              hascm)
            optionen["QdbWriter"].put(qEntry)
            FindWorker.WorkerLock.acquire()
            optionen["NoOfFilesFound"] += 1
            FindWorker.WorkerLock.release()

    def endDocument(self):
        self.url = ""

    #===========================================================================
    # getMetaData - reads the metadata related to a single file in the
    #               default namespace
    #===========================================================================
    def getMetaData(self, dataUrl):
        metaDataUrl = dataUrl[:6] + "meta" + dataUrl[6:]
        httpStatus = 0

        if optionen["delay"]:        # add a delay (pause) between requests
            time.sleep(float(optionen["delay"]/1000))

        # get the objects retention
        try:
            r1 = self.con.GET(metaDataUrl + "/retention.txt")
        except hcpsdk.HcpsdkError as e:
            logger.error("getMetaData (retention): '{0}' on '{1}' - failed".format(str(e),
                                                                                   metaDataUrl))
            httpStatus = 999 # aka 'error'
            httpReason = "'{0}' on '{1}'".format(str(e), metaDataUrl)

        if not httpStatus:
            httpStatus = self.con.response_status
            httpReason = self.con.response_reason
            if httpStatus == 200:
                # Good status, get and parse the response
                ret = r1.readline().strip().decode()
                retStr = r1.readline().strip().decode()
                r1.read()
            else:
                logger.error("http {0} ({1}) on {2}".format(httpStatus,
                                                            httpReason,
                                                            metaDataUrl))

        # see if there is Custom Metadata
        httpStatus = 0
        try:
            r1 = self.con.HEAD(metaDataUrl + '/custom-metadata.xml')
        except hcpsdk.HcpsdkError as e:
            logger.error("getMetaData (CM): '{0}' on '{1}' - failed".format(str(e),
                                                                            metaDataUrl))
            httpStatus = 999 # aka 'error'
            httpReason = "'{0}' on '{1}'".format(str(e), metaDataUrl)

        if not httpStatus:
            httpStatus = self.con.response_status
            if httpStatus == 200:
                # Good status, this object has Custom Metadat
                cm = 'true'
            else:
                cm = 'false'

        logger.debug("Retention: '{0} - {1}', CM = {2} for {3}".format(ret, retStr, cm, metaDataUrl))
        return(ret, retStr, cm)


## Worker Threads used to find all Directories and Objects
#
class FindWorker(threading.Thread):
    global optionen, logger
    # static members
    WorkerLock = threading.Lock()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO: debug for Wal-Mart...
        #
        if optionen['verbose'] >= 3:
            dl = 9
        else:
            dl = 0
        self.con = hcpsdk.Connection(optionen['target'], retries=3, debuglevel=dl)

    def run(self):
        stayAlive = True
        while stayAlive:
            if optionen["shutdownEvent"].is_set():
                break
            # if the 'pause' blocker is set, wait until reset
            optionen['pause'].wait()
            url = optionen["QFbox"].get()
            if url != "*!*exit*!*":
                if optionen["delay"]:        # add a delay (pause) between requests
                    time.sleep(float(optionen["delay"]/1000))
                try:
                    (result, reason) = self.work(url)
                except hcpsdk.HcpsdkTimeoutError as e:
                    with self.WorkerLock:
                        optionen["NoOfWarnings"] += 1
                    result = 998    # Warning, needs retry
                    reason = str(e)
                    optionen["QFbox"].put(url)
                except:
                    ex_type, ex_value = sys.exc_info()[:2]
                    self.WorkerLock.acquire()
                    optionen["NoOfErrors"] += 1
                    self.WorkerLock.release()
                    result = 999 # error
                    reason = "self.work failed"
                    logger.critical("exception in work('{0}') - type='{1}', value='{2}'".\
                                    format(quote(url, safe='/'), ex_type, ex_value))
                    logger.exception(ex_value)

                if int(result) != 200:
                    if int(result) == 302:
                        logger.critical("http " + str(result) + ": - password invalid")
                        self.WorkerLock.acquire()
                        optionen["NoOfErrors"] += 1
                        self.WorkerLock.release()
                    elif int(result) == 404:
                        if url not in [optionen["targetdir"], '/rest/.lost+found', '/fcfs_data/.lost+found']:
                            logger.warning("http {0}: targetdir '{1}' not found - NOT re-queued"\
                                            .format(str(result), quote(url, safe='/')))
                            # optionen["QFbox"].put(url)
                            self.WorkerLock.acquire()
                            optionen["NoOfErrors"] += 1
                            self.WorkerLock.release()
                        elif url not in ['/rest/.lost+found', '/fcfs_data/.lost+found']:
                            logger.critical("http {0}: targetdir '{1}' not found"\
                                            .format(str(result), quote(url, safe='/')))
                            self.WorkerLock.acquire()
                            optionen["NoOfErrors"] += 1
                            self.WorkerLock.release()
                    elif int(result) == 998:
                        logger.warning('request failed -re-queued-, http {}({}) - {}'
                                       .format(result, reason, quote(url, safe='/')))
                        self.WorkerLock.acquire()
                        optionen["NoOfWarnings"] += 1
                        self.WorkerLock.release()
                    elif int(result) != 999:
                        logger.error(str(result) + " " + reason + " (" + quote(url, safe='/') + ")")
                        self.WorkerLock.acquire()
                        optionen["NoOfErrors"] += 1
                        self.WorkerLock.release()

            else:
                stayAlive = False
            optionen["QFbox"].task_done()

        self.con.close()

    def work(self, url):
        httpStatus = 0

        try:
            urli = url
            params = {}
            if optionen["authNamespace"] and optionen["deltoo"]:
                params = {'deleted': 'true'}
            logger.debug(self.name + ": discovering " + urli) # debug

            r1 = self.con.GET(urli, params=params)
        except hcpsdk.HcpsdkTimeoutError as e:
            httpStatus = 998 # aka 'warning'
            httpReason = "GET {} raised '{}'".format(quote(url, safe='/'), str(e))
            optionen["QFbox"].put(url)
            logger.warning("rescheduled: GET {} raised '{}'".format(quote(url, safe='/'), str(e)))
        # hard errors, no retry!
        except hcpsdk.HcpsdkError as e:
            logger.exception("GET {} raised '{}'".format(quote(url, safe='/'), str(e)))
            raise
        else:
            httpStatus = 0
            httpReason = ''

        if not httpStatus:
            httpStatus = self.con.response_status
            httpReason = self.con.response_reason
            if httpStatus == 200:
                # Good status, get and parse the response
                if url == optionen["targetdir"]:
                    if not optionen["fatDB"]:
                        qEntry = (optionen["targetdir"], '', 'directory', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '')
                    else:
                        if optionen["authNamespace"]:
                            qEntry = (optionen["targetdir"], optionen["targetdir"],
                                              "directory", "",
                                              "","","","","","","",
                                              "","","","","","","")
                        else:
                            qEntry = (optionen["targetdir"], optionen["targetdir"],
                                              "directory", "",
                                              "","","","","","","",
                                              "","","")
                    optionen["QdbWriter"].put(qEntry)
                    self.WorkerLock.acquire()
                    optionen["NoOfDirsFound"] += 1
                    self.WorkerLock.release()
                handler = SaxDocumentHandler(self.con)
                # parse the BODY piece of the received XML
                #   - problem: needs much memory on large dirs!
                xml.sax.parseString(self.con.read(), handler)
            else:
                self.con.read()
        else:
            try:
                self.con.read()
            except Exception as e:
                logger.exception('Error on cleanup read() for {}'.format(quote(url, safe='/')))

        return httpStatus, httpReason


## dbWriter Thread - the only one writing the database
#
class dbWriter(threading.Thread):
    global optionen, logger

    def __init__(self, name=None):
        threading.Thread.__init__(self, name=name)
        logger.info("*** dbWriter started ***")

        if optionen['out'] in ['db', 'both']:
            ## Make Database to store found directories and objects
            dbConn = sqlite3.connect(optionen["database"])
            dbConn.isolation_level = None # use AUTOCOMMIT mode

            initcursor = dbConn.cursor()
            # make the 'admin' table
            initcursor.execute('''create table admin
                                    (magic    TEXT,
                                     version  TEXT,
                                     cluster  TEXT)''')
            initcursor.execute('''INSERT INTO admin VALUES (?, ?, ?)''',
                               ('hcp list', "{0}/{1}".format(_version, _build),
                               optionen["cluster"]))

            # make the 'flist' table
            # if not optionen["fatDB"]:
            #     initcursor.execute('''create table flist
            #                             (urlName TEXT PRIMARY KEY, type TEXT)''')
            # else:
            if optionen["authNamespace"]:
                initcursor.execute('''create table flist
                                        (urlName TEXT PRIMARY KEY, utf8Name TEXT,
                                         type TEXT,                size TEXT,
                                         hashScheme TEXT,          hash TEXT,
                                         retention TEXT,           retentionString TEXT,
                                         retentionClass TEXT,      ingestTime TEXT,
                                         ingestTimeString TEXT,    hold TEXT,
                                         shred TEXT,               dpl TEXT,
                                         idx TEXT,                 customMetadata TEXT,
                                         version TEXT,             state TEXT)''')
            else:
                initcursor.execute('''create table flist
                                        (urlName TEXT PRIMARY KEY, utf8Name TEXT,
                                         type TEXT,                size TEXT,
                                         retention TEXT,           retentionString TEXT,
                                         mode TEXT,                modeString TEXT,
                                         uid TEXT,                 gid TEXT,
                                         accessTime TEXT,          accessTimeString TEXT,
                                         modTime TEXT,             modTimeString TEXT,
                                         customMetadata TEXT)''')
            dbConn.close()

        if optionen['out'] in ['csv', 'both']:
            self.excelWriter = csv.writer(open(optionen['outfile'], 'w', encoding='utf-8'),
                                          delimiter=';', quotechar="'", lineterminator="\n")
            if optionen["authNamespace"]:
                self.excelWriter.writerow(["urlName", "utf8Name", "type", "size", "hashScheme", "hash",
                                           "retention", "retentionString", "retentionClass", "ingestTime",
                                           "ingestTimeString", "hold", "shred", "dpl", "idx", "customMetadata",
                                           "version", "state"])
            else:
                self.excelWriter.writerow(["urlName", "utf8Name", "type", "size", "retention", "retentionString",
                                           "mode", "modeString", "uid", "gid", "accessTime", "accessTimeString",
                                           "modTime", "modTimeString", "customMetadata"])

    def run(self):
        try:
            if optionen['out'] in ['db', 'both']:
                sqlCmd = "INSERT INTO flist VALUES "
                # if not optionen["fatDB"]:
                #     sqlCmd += "(?,?)"
                # else:
                if optionen["authNamespace"]:
                    sqlCmd += "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
                else:
                    sqlCmd += "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"

                dbConn = sqlite3.connect(optionen["database"])
                dbConn.isolation_level = "DEFERRED" # use manual COMMIT mode
                dbCursor = dbConn.cursor()

            while True:
                qEntry = optionen["QdbWriter"].get()
                logger.debug("QdbWriter.get() ='{0}".format(str(qEntry)))
                if qEntry != "*!*exit*!*":
                    if optionen['out'] in ['db', 'both']:
                        try:
                            dbCursor.execute(sqlCmd, tuple(qEntry))
                        except Exception as err:
                            logger.exception('dbCursor.execute() failed: {}'
                                             .format(err))
                            logger.critical('sqlCmd = {}'.format(sqlCmd))
                            logger.critical('tuple(qEntry) = {}'.format(tuple(qEntry)))
                        optionen["NoOfdbWrites"] += 1
                        if optionen["NoOfdbWrites"] % 10000 == 0: # do a commit every 10.000 recs
                            dbConn.commit()
                    if optionen['out'] in ['csv', 'both']:
                        self.excelWriter.writerow(list(qEntry))
                    optionen["QdbWriter"].task_done()
                else:
                    optionen["QdbWriter"].task_done()
                    if optionen['out'] in ['db', 'both']:
                        dbConn.commit()
                    optionen["dbWriterThreadEnded"] = True # signal for MonitorThread
                    break

            if optionen['out'] in ['db', 'both']:
                dbConn.commit()
                dbCursor.execute("ALTER TABLE flist ADD COLUMN new_ret TEXT")
                dbConn.close()
        except Exception as e:
            logger.error("dbWriter died on '{0}'".format(str(e)))
            if optionen['out'] in ['csv', 'both']:
                try:
                    dbConn.close()
                except e:
                    pass
            logger.critical("dbWriter died on '{0}'".format(str(e)))
            logger.critical("STOPPING EXECUTION due to an unrecoverable error")
            optionen["shutdownEvent"].set()
            optionen["NoOfErrors"] += 1
            sys.exit(99)


## Monitor Thread
#
class Monitor(threading.Thread):
    global optionen, logger

    def __init__(self, name=None):
        threading.Thread.__init__(self, name=name)
        logger.info("*** monitor started ***")
        # create an Event object used to block findworker threads;
        # set it to True to make it unblocking, initially.
        optionen['pause'] = threading.Event()
        optionen['pause'].set()
        self.pcnt = 0

    def run(self):
        stayAlive = True

        while stayAlive:
            if optionen["shutdownEvent"].is_set():
                break
            time.sleep(int(optionen["loginterval"]))

            # If more than 'pause_after' entries have been found, block the findworker threads and
            # create a timer that releases the blocking Event after 'pause_minutes'.
            if optionen['pause_after'] and optionen['pause'].is_set():
                lcnt = (optionen['NoOfDirsFound'] + optionen["NoOfFilesFound"]) // optionen['pause_after']
                if lcnt > self.pcnt:
                    self.pcnt = lcnt
                    logger.info('now pausing for {} minutes'.format(optionen['pause_minutes']))
                    optionen['pause'].clear()
                    t = threading.Timer(optionen['pause_minutes']*60, optionen['pause'].set)
                    t.start()

            if not optionen['pause'].is_set():
                logger.info('pausing...')
            else:
                with FindWorker.WorkerLock:
                    logger.info("Dirs:{0:,}; Objs:{1:,}; Err/Warn:{2:,}/{3:,}; dbWrites:{4:,} [QF:{5:,}; Qdb:{6:,}]".format(\
                                optionen["NoOfDirsFound"], optionen["NoOfFilesFound"], optionen["NoOfErrors"],
                                optionen["NoOfWarnings"], optionen["NoOfdbWrites"], optionen["QFbox"].qsize(),
                                optionen["QdbWriter"].qsize()))

            # show thread status
            if optionen["showThreads"]:
                thrAll=thrMain=thrdbWriter=thrfindWorker=thrUndef = 0
                undefName = ""
                for i in threading.enumerate():
                    thrAll += 1
                    if i.name == "MainThread":
                        thrMain += 1
                    elif i.name == "dbWriter":
                        thrdbWriter += 1
                    elif i.name[:10] == "findWorker":
                        thrfindWorker += 1
                    else:
                        thrUndef += 1
                        undefName = undefName+i.name+','
                undefName=undefName[:-1]
                logger.info("running threads = {0}: {1} main, {2} dbWriter, {3} findWorker (+{4}:{5})".\
                            format(thrAll, thrMain, thrdbWriter, thrfindWorker,
                                   thrUndef, undefName))

            # all FindWorker and DelWorker Threads have ended
            if optionen["findThreadsEnded"] and optionen["dbWriterThreadEnded"]:
                stayAlive = False
                logger.info("*** monitor exits ***")


#===============================================================================
# hcpList - discovers HCP content
#===============================================================================
def hcpList(opts, logr):
    global optionen, logger
    optionen = opts
    logger = logr

    if (optionen['pause_after'] and not optionen['pause_minutes']) or \
        (not optionen['pause_after'] and optionen['pause_minutes']):
        raise hcpf.hcpError(hcpf.hcpError._fatalError,
                    "--pause_after and --pause_minutes are only allowed together")
    else:
        try:
            optionen['pause_after'] = int(optionen['pause_after'])
            optionen['pause_minutes'] = int(optionen['pause_minutes'])
        except:
            raise hcpf.hcpError(hcpf.hcpError._fatalError,
                        "--pause_after and --pause_minutes both require integer values")


    if optionen["targetdir"][len(optionen["targetdir"]) - 1] == "/":
                optionen["targetdir"] = optionen["targetdir"][:len(optionen["targetdir"])-1]
    if not optionen["database"]:
        if optionen["fatDB"]:
            dbtype = "fat"
        else:
            dbtype = "slim"
        optionen["database"] = "{0:s}_{1:s}.{2:s}.{3:s}.sqlite3".\
            format(os.path.splitext(os.path.basename(sys.argv[0]))[0],
                   optionen["subCmdName"],
                   time.strftime("%Y%d%m%H%M%S", time.localtime(time.time())),
                   dbtype)
        del dbtype

    # find out if we're working with a default or authenticated namespace
    if optionen["targetdir"][1:5] == "rest":
        optionen["authNamespace"] = True
        optionen["urlName"] = 'utf8Name'
#        optionen["urlName"] = 'urlName'
        if not optionen["password"]:
            optionen["password"] = hcpf.getPassword(optionen["user"])
        if optionen['nossl']:
            p = 80
        else:
            p = 443
        try:
            optionen['target'] = hcpsdk.Target(optionen['cluster'],
                                               hcpsdk.NativeAuthorization(optionen["user"],
                                                                          optionen["password"],),
                                               port=p, dnscache=False)
        except hcpsdk.ips.IpsError as e:
            sys.exit('DNS Query failed: {}'.format(e))
        except Exception as e:
            sys.exit('Initialization error: {}'.format(e))
        del optionen["password"] # burn it from memory!
    elif optionen["targetdir"][1:10] == "fcfs_data":
        optionen["authNamespace"] = False
        optionen["urlName"] = 'utf8Name'
#        optionen["urlName"] = 'name'
        if optionen['nossl']:
            p = 80
        else:
            p = 443
        try:
            optionen['target'] = hcpsdk.Target(optionen['cluster'],
                                               hcpsdk.DummyAuthorization(),
                                               port=p, dnscache=False)
        except hcpsdk.ips.IpsError as e:
            sys.exit('DNS Query failed: {}'.format(e))
        except Exception as e:
            sys.exit('Initialization error: {}'.format(e))
    else:
        raise hcpf.hcpError(hcpf.hcpError._fatalError,
                    "target directory is invalid (/rest/... or /fcfs_data/...")

    ## define global vars
    #
    optionen["NoOfFilesFound"] = 0
    optionen["NoOfDirsFound"] = 0
    optionen["NoOfErrors"] = 0
    optionen["NoOfWarnings"] = 0
    optionen["NoOfdbWrites"] = 0
    #
    optionen["dbWriterThreadEnded"] = False  # used to signal the ending of the dbWriter Threads
    optionen["findThreadsEnded"]    = False  # used to signal the ending of all FindWorker Threads

    # Implement an Event as a facility to block threads as long we are in pause state
    optionen['pause'] = threading.Event()
    optionen['pause'].set()

    ## startup information
    #
    StartTime = printStartMsgs()

    ## establish an Event Object, used to signal the need to shutdown all
    #  threads immediately; initially set to 'False'
    optionen["shutdownEvent"] = threading.Event()

    ## start Monitor thread
    #
    MonitorThread = Monitor(name="Monitor")
    MonitorThread.setDaemon(True)
    MonitorThread.start()

    ## start dbWriter thread and setup its Queue
    #
    optionen["QdbWriter"] = queue.Queue(int(optionen["Qdb"]))
    startdbWriter = time.time()
    dbWriterThread = dbWriter()
    dbWriterThread.name = "dbWriter"
    dbWriterThread.setDaemon(True)
    dbWriterThread.start()

    ## start FindWorker threads to find all Directories and Files
    #
    optionen["QFbox"] = queue.Queue(int(optionen["QF"])) # Queue used while finding all Directories and Objects
    startFindWorkers = time.time()
    FindWorkerThreads = [FindWorker(name='finder') for i in range(optionen["NoOfThreads"])]
    i = 0
    for thread in FindWorkerThreads:
        i += 1
        thread.name = "findWorker.{0:03}".format(i)
        thread.setDaemon(True)
        thread.start()

    # generate work orders and wait for Queue to be processed
    #
    optionen["QFbox"].put(optionen["targetdir"])
    # this is to make the program be able to exit if the dbWriter thread dies...
    while True:
        if optionen["shutdownEvent"].is_set() or optionen["QFbox"].empty():
            optionen['pause'].set() # this will make a threads run, even if in pause state
            break
        else:
            time.sleep(1)
    for i in threading.enumerate():
        if i.name == "finder":
            optionen["QFbox"].put("*!*exit*!*")
    optionen["QFbox"].join()
    optionen["findThreadsEnded"] = True # signal for MonitorThread
    logger.info("*** Discovery finished after {0} ***".\
                   format(calcTime(time.time()-startFindWorkers)))

    # wait for dbWriter to get finished
    #
    optionen["QdbWriter"].put("*!*exit*!*")
    optionen["QdbWriter"].join()
    logger.info("*** dbWriter finished after {0}***".\
                   format(calcTime(time.time()-startdbWriter)))

    ## wait for Monitor thread exiting
    #
    MonitorThread.join(5)

    ## shutdown information
    #
    EndTime = time.time()
    EstTime = EndTime - StartTime
    printEndMsgs(StartTime, EndTime, EstTime)

