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

import http.client
import time
import queue
import threading
import os.path
import sys
import xml.sax
import sqlite3
import socket
from xml.sax import handler
import ssl
try:
    SSL_NOVERIFY = ssl._create_unverified_context()
except (AttributeError, NameError):
    SSL_NOVERIFY = None

from hcptcmds import hcpf

# initialized needed variables
#
_version="1.1.13"
_build="2016-02-12/Sm"
Version = "v.{0} ({1})".format(_version, _build)
Author = "\nContact: sw@snomis.de"
optionen = None
logger = None


## Check Arguments
#
def checkArgs(progVers):
#    usage = """usage: %prog -c cluster|ip-adress [-H namespace] -d targetdir
#    [--infile='input file'] -u user [-p password] [-l logfile] [-i log_interval]
#    [-B database] [--fatDB] [--keepDB] [-t noofthreads] [--QF='no.']
#    [--Qdb='no.'] [--objonly] [--nossl] [--purge [--privileged='reason']]
#    [-v[v[v]]] [--YES]"""

#    description = """%prog: performs deletion of data within HCP namespaces by discovering
#a directory tree top/down. Will find all directories and objects within that tree and will imediately begin
#with object deletion right after one has been found. Directory deletion will start down/up when the whole tree has been discovered. It
#will write a sqlite3 database file with a single record for each and every directory and object, containing
#all the information available for it - this can grow quite large..."""

#    epilog = """Be aware: if you have directories with a huge number (10.000++) of objects, main memory will become excessive used,
#even more the more threads you use. This could lead to runtime errors - in this case you will need to serialize the
#processing by limiting the number of threads down to 1 (one) depending on the available main memory.
#Of course, this will lead to a much longer runtime - monitor the processing by
#using the commandline switch '-v'."""


#    parser = OptionParser(usage=usage, description=description, epilog=epilog, version=progVers)
#    parser.add_option("-c", type="string", dest="cluster",
#                      help="target namespace (full qualified dns-name or an ip-adress if you don't have dns))")
#    parser.add_option("-H", type="string", dest="namespace",
#                      help="dns-name of target namespace if you use an ip-adress with '-c' (namespace.tenant.hcp.domain.local)")
#    parser.add_option("-d", type="string", dest="targetdir", help="target directory (/rest/test)")
#    parser.add_option("--infile", type="string", dest="infile",
#                      help="""file holding a list of objects to be deleted (full
#                      path: '/rest/.../object' or '/fcfs_data/.../object'. If
#                      set, '-d' will only be used to determine the type of
#                      namespace used.""")
#    parser.add_option("-u", type="string", dest="user", help="data access acount")
#    parser.add_option("-p", type="string", dest="password", help="password (will require manual input if not given)")
#    parser.add_option("-l", type="string", dest="logfile",
#                      help="logfile (defaults to {0:3}.log)".format(os.path.splitext(os.path.basename(sys.argv[0]))[0]))
#    parser.add_option("-i", type="int", dest="loginterval", help="logging interval (defaults to 10 sec.)")
#    parser.add_option("-B", type="string", dest="database",
#                      help="database file (defaults to {0:3}.db.<timestamp>)".format(os.path.splitext(os.path.basename(sys.argv[0]))[0]))
#    parser.add_option("--fatDB", dest="fatDB", help="include all available information in database",
#                      action="store_true", default=False)
#    parser.add_option("--keepDB", dest="keepdb", help="do not delete the database file when finished",
#                      action="store_true", default=False)
#    parser.add_option("-t", type="int", dest="NoOfThreads", help="no. of parallel threads (defaults to 1)")
#    parser.add_option("--QF", type="int", dest="fQueueSize", help="size of internal queue (defaults to unlimited)")
#    parser.add_option("--Qdb", type="string", dest="Qdb", default="-1",
#                      help="defines the allowed no. of items in dbWriterQueue")
#    parser.add_option("--objonly", dest="objonly", help="do not delete directories", action="store_true", default=False)
#    parser.add_option("--nossl", dest="nossl", help="use http instead of https", action="store_true", default=False)
#    parser.add_option("--purge", dest="purge", help="purge versions (if not set, directory deletion will fail if versioning is enabled)",
#                      action="store_true", default=False)
#    parser.add_option("--privileged", type="string", dest="reason", help="perform privileged delete (requires a 'reason')")
#    parser.add_option("-v", dest="verbose", help="verbose (more v's, more verbose)", action="count", default=0)
#    parser.add_option("--YES", dest="yes", action="store_true", default=False,
#                      help="...if you really (!) want to delete the found objects/directories (defaults to 'generate a list of objects/directories only')")

#    (optionen, args) = parser.parse_args()

#    if not optionen["targetdir"]:
#        parser.error("need to specify a target directory")
#    else:
#        if optionen["targetdir"][1:5] == "rest":
#            optionen["authNamespace"] = True
#            optionen["urlName"] = 'urlName'
#            if not optionen["user"]:
#                parser.error("need to specify data access account")
#            if optionen["reason"] and not optionen["purge"]:
#                parser.error("'--purge' is required for '--privileged' delete")
#            if optionen["reason"]:
#                optionen["reason"] = urllib.parse.quote_plus(optionen["reason"])
#        elif optionen["targetdir"][1:10] == "fcfs_data":
#            optionen["authNamespace"] = False
#            optionen["urlName"] = 'name'
#        else:
#            parser.error("target directory is invalid (/rest/... or /fcfs_data/...")



    return(optionen)

## Initialize Logging Facility
#
#def initLogging(LogFile):
#    strhandler = logging.StreamHandler(sys.stdout)
#    fhandler = logging.FileHandler(LogFile, "w")
#    frm = logging.Formatter("%(asctime)s [%(levelname)-8s] %(message)s", "%m/%d %H:%M:%S")
#    strhandler.setFormatter(frm)
#    fhandler.setFormatter(frm)
#    logging.addLevelName(49, "STARTUP")
#    logging.addLevelName(48, "STOPDOWN")
#    l = logging.getLogger()
#    l.addHandler(strhandler)
#    l.addHandler(fhandler)
#    if not optionen["verbose"]:
#        l.setLevel(logging.WARNING)
#    elif optionen["verbose"] == 1:
#        l.setLevel(logging.INFO)
#    else:
#        l.setLevel(logging.DEBUG)
#    return(l)

## Print startup messages
#
def printStartMsgs():
    global optionen, logger

    msg = ["{0} {1} {2}".format(os.path.splitext(os.path.basename(sys.argv[0]))[0],
                                optionen["subCmdName"], Version),\
          "    Logfile: " + optionen["logfile"],
          "Loginterval: " + str(optionen["loginterval"]) + " sec.",
          "   Database: " + optionen["database"]]
    if optionen["keepdb"]:
        msg.append("             (will be kept when finished)")
    if optionen["fatDB"]:
        msg.append("             (will include all available information)")
    if optionen["nossl"]:
        msg.append("     Target: http://" + optionen["cluster"]+ optionen["targetdir"])
    else:
        msg.append("     Target: https://" + optionen["cluster"]+ optionen["targetdir"])
    if optionen["infile"]:
        msg.append("     infile: " + optionen["infile"])
    msg.append("DataAccAcnt: " + optionen["user"])
    msg.append("    Threads: " + str(optionen["NoOfThreads"]))
    msg.append("  QueueSize: " + str(optionen["fQueueSize"]))
    if optionen["purge"]:
        msg.append("      Purge: yes")
    if optionen["reason"]:
        msg.append(" Privileged: yes (Reason: '" + str(optionen["reason"]) + "')")
    msg.append("  Verbosity: " + str(optionen["verbose"]))
    if optionen["yes"]:
        if optionen["objonly"]:
            msg.append(" DeleteMode: REQUESTED - Objects")
        else:
            msg.append(" DeleteMode: REQUESTED - Objects and Directories")
    else:
        msg.append(" DeleteMode: not requested (just collecting information)")
#    optionen["StartTime"] = time.time()
    msg.append(" Started at: " + time.strftime("%a, %d.%m., %H:%M:%S", time.localtime(optionen["StartTime"])))
    msg.append(79 * "-")
    # log messages...
    for logline in msg:
        logger.log(49, logline)

## Print startup messages
#
def printEndMsgs():
    global optionen, logger
    msg = [79 * "-",
           " Started at: " + time.strftime("%a, %d.%m., %H:%M:%S", time.localtime(optionen["StartTime"])),
           "   Ended at: " + time.strftime("%a, %d.%m., %H:%M:%S", time.localtime(optionen["EndTime"])),
           "    Runtime: " + "{0:.2f}".format(optionen["EstTime"]) + " Sekunden",
           "      Found: " + str(optionen["NoOfDirsFound"]) + " Directories, " + str(optionen["NoOfFilesFound"]) + " Objects",
           "    Deleted: " + str(optionen["NoOfDeletedDirs"]) + " Directories, " + str(optionen["NoOfDeletedFiles"]) + " Objects",
           "     Errors: " + str(optionen["NoOfErrors"])]
    # log messages...
    for logline in msg:
        logger.log(48, logline)

## from a given no. of bytes, calculate the biggest possible representation
#
def calcSize(bytes):
    sz = ["Byte", "Kbyte", "Mbyte", "Gbyte", "Tbyte"]
    i = 0
    while bytes > 1023:
                    bytes = bytes / 1024
                    i = i + 1
    return("{0:.2f} {1:}".format(bytes, sz[i]))

## Parse the XML returned by GET on a Directory
#
class SaxDocumentHandler(handler.ContentHandler):
    global optionen, logger

    def startDocument(self):
        self.url = None

    def startElement(self, name, attrs):
        if name == "directory": # remind actual url
            self.url = attrs.get("path")
        elif attrs.get("type") == 'directory' or attrs.get("fileType") == 'directory':
            if attrs.get(optionen["urlName"]) != '.':
                optionen["QFbox"].put(self.url + "/" + attrs.get(optionen["urlName"]))
                if not optionen["fatDB"]:
                    if optionen['authNamespace']:
                        optionen["QdbWriter"].put((self.url+"/"+attrs.get(
                                       optionen["urlName"]),
                                       attrs.get("type")))
                    else:
                        optionen["QdbWriter"].put((self.url+"/"+attrs.get(
                                       optionen["urlName"]),
                                       attrs.get("fileType")))
                else:
                    if optionen['authNamespace']:
                        optionen["QdbWriter"].put((self.url+"/"+attrs.get(
                                                   optionen["urlName"]),
                                                   self.url+"/"+attrs.get("utf8Name"),
                                                   attrs.get("type"),
                                                   None, None, None, None, None,
                                                   None, None, None, None, None,
                                                   None, None, None, None,
                                                   attrs.get("state")))
                    else:
                        optionen["QdbWriter"].put((self.url+"/"+attrs.get(
                                       optionen["urlName"]),
                                       self.url+"/"+attrs.get("utf8Name"),
                                       attrs.get("fileType"),
                                       None, None, None, None, None,
                                       None, None, None, None, None,
                                       None, None, None, None,
                                       attrs.get("state")))

                FindWorker.WorkerLock.acquire()
                optionen["NoOfDirsFound"] += 1
                FindWorker.WorkerLock.release()
        elif attrs.get("type") == 'object' or attrs.get("fileType") == 'file':
            if optionen["yes"]:
                optionen["QDbox"].put(self.url + "/" + attrs.get(optionen["urlName"]))
            if not optionen["fatDB"]:
                optionen["QdbWriter"].put((self.url+"/"+attrs.get(optionen["urlName"]),
                               attrs.get("type")))

            else:
                optionen["QdbWriter"].put((self.url+"/"+attrs.get(optionen["urlName"]),
                               self.url+"/"+attrs.get("utf8Name"),
                               attrs.get("type"),
                               attrs.get("size"),
                               attrs.get("hashScheme"),
                               attrs.get("hash"),
                               attrs.get("retention"),
                               attrs.get("retentionString"),
                               attrs.get("retentionClass"),
                               attrs.get("ingestTime"),
                               attrs.get("ingString"),
                               attrs.get("hold"),
                               attrs.get("shred"),
                               attrs.get("dpl"),
                               attrs.get("index"),
                               attrs.get("customMetadata"),
                               attrs.get("version"),
                               attrs.get("state")))

            FindWorker.WorkerLock.acquire()
            optionen["NoOfFilesFound"] += 1
            FindWorker.WorkerLock.release()

    def endDocument(self):
        self.url = None

## Worker Threads used to find all Directories and Objects
#
class FindWorker(threading.Thread):
    global optionen, logger
    # static members
    WorkerLock = threading.Lock()

    def run(self):
        stayAlive = True

        while stayAlive:
            url = optionen["QFbox"].get()
            if url != "exit":
                (result, reason) = self.work(url)

                if int(result) != 200:
                    if result == 302:
                        logger.critical("http " + str(result) + ": - password invalid")
                    elif result == 404:
                        logger.critical("http " + str(result) + ": - targetdirectory not found")
                    elif int(result) != 999:
                            logger.error(str(result) + " " + reason + " (" + url + ")")
                    self.WorkerLock.acquire()
                    optionen["NoOfDirErrors"] += 1
                    optionen["NoOfErrors"] += 1
                    self.WorkerLock.release()

            else:
                stayAlive = False
            optionen["QFbox"].task_done()



    def work(self, url):
        httpStatus = 0

        if optionen["nossl"]:
            httpConnection = http.client.HTTPConnection(optionen["cluster"])
        else:
            # set context to NOVERIFY to work around restrictions in Python 3.5
            httpConnection = http.client.HTTPSConnection(optionen["cluster"],
                                                         context=SSL_NOVERIFY)
        if optionen["authNamespace"]:
            if optionen["versionedNS"]:
                urli = url + "?deleted=true"
            else:
                urli = url
        else:
            urli = url
        logger.debug(self.name + ": discovering " + urli) # debug

        try:
            if optionen["authNamespace"]:
                httpConnection.request("GET", urli, headers=optionen["header"])
            else:
                httpConnection.request("GET", urli)
        except:
            logger.exception()
            logger.info(self.name + ": http (GET) error: " + url + " (rescheduled for later discovery)")
            optionen["QFbox"].put(url)
            httpStatus = 999
            httpReason = "Connection Error (FindWorker)"

        if not httpStatus:
            r1 = httpConnection.getresponse()
            httpStatus = r1.status
            httpReason = r1.reason
            if r1.status == 200:
                # Good status, get and parse the response
                if url == optionen["targetdir"]:
                    if not optionen["fatDB"]:
                        optionen["QdbWriter"].put((optionen["targetdir"],
                                       "directory"))
                    else:
                        optionen["QdbWriter"].put((optionen["targetdir"],
                                       optionen["targetdir"],
                                       "directory",
                                       None, None, None, None, None,
                                       None, None, None, None, None,
                                       None, None, None, None, 'Created'))
                    self.WorkerLock.acquire()
                    optionen["NoOfDirsFound"] += 1
                    self.WorkerLock.release()
                handler = SaxDocumentHandler()
                xml.sax.parseString(r1.read(), handler) # parse the BODY piece of the received - problem: needs much memory on large dirs!

        httpConnection.close()
        return httpStatus, httpReason



## Worker Threads used to delete all Objects and Directories
#
class DelWorker(threading.Thread):
    global optionen, logger
    # static members
    DWorkerLock = threading.Lock()

    def run(self):
        while True:
            url = optionen["QDbox"].get()
            if url[len(url) - 1] == "/":
                url = url[:len(url) - 1]
                modeDir = True
            else:
                modeDir = False

            (result, reason) = self.work(url, modeDir)
            if int(result) == 200:
                self.DWorkerLock.acquire()
                if modeDir:
                    optionen["NoOfDeletedDirs"] += 1
                else:
                    optionen["NoOfDeletedFiles"] += 1
                self.DWorkerLock.release()
            elif int(result) == 403 or int(result) == 999:
                # if deletion of a dir earns a 403 (only dirs) or 999 error, reschedule it!
                if modeDir:
                    time.sleep(1)
                    optionen["QDbox"].put(url + "/")
                    logger.info(self.name + ": http (DELETE) error: "\
                                + str(result) + ":"\
                                + url + " (re-scheduled for later deletion)")
                else:
                    if int(result) == 403:
                        self.DWorkerLock.acquire()
                        optionen["NoOfErrors"] += 1
                        self.DWorkerLock.release()
                        logger.error(self.name + ": http (DELETE) error: "\
                                    + str(result) + ":"\
                                    + url + " (unrecoverable)")
                    else:
                        optionen["QDbox"].put(url)
                        logger.error(self.name + ": http (DELETE) error: "\
                                    + str(result) + ":"\
                                    + url + " (re-scheduled for later deletion)")
            else:
                logger.error(str(result) + " " + reason + " (" + url + ")")
                self.DWorkerLock.acquire()
                optionen["NoOfErrors"] += 1
                self.DWorkerLock.release()
            optionen["QDbox"].task_done()

    def work(self, url, modeDir):
        if not modeDir:
            if optionen["authNamespace"]:
                x = '?'
                if optionen["purge"]:
                    x += 'purge=true'
                if optionen["reason"]:
                    if len(x) > 1:
                        x += '&'
                    x += "privileged=true&reason=\"" + optionen["reason"] + "\""
                if len(x) > 1:
                    urli = url + x
                else:
                    urli = url
#            if optionen["authNamespace"] and optionen["purge"]:
#                urli = url + "?purge=true"
#                if optionen["reason"]:
#                    urli += "&privileged=true&reason=\"" + optionen["reason"] + "\""
#            else:
#                urli = url
            else:
                urli = url
        else:
            urli = url
        logger.debug(self.name + ": deleting " + url)


        if optionen["nossl"]:
            httpConnection = http.client.HTTPConnection(optionen["cluster"])
        else:
            # Set context to NOVERIFY to work around restrictions in Python 3.5
            httpConnection = http.client.HTTPSConnection(optionen["cluster"],
                                                         context=SSL_NOVERIFY)


        try:
            if optionen['authNamespace']:
                httpConnection.request("DELETE", urli,
                                       headers=optionen["header"])
            else:
                httpConnection.request("DELETE", urli)
        except (http.client.NotConnected, http.client.InvalidURL, http.client.UnknownProtocol,
                http.client.UnknownTransferEncoding, http.client.UnimplementedFileMode,
                http.client.IncompleteRead, http.client.ImproperConnectionState,
                http.client.CannotSendRequest, http.client.CannotSendHeader,
                http.client.ResponseNotReady, http.client.BadStatusLine,
                socket.gaierror) as e:
            httpStatus = 999
            httpReason = "Connection Error(DelWorker)"
            if e.args[0] != "11001": # getaddrinfo failed
                logger.critical(str(e.args[0]) + " : " + str(e.args[1]))
        else:
            r1 = httpConnection.getresponse()
            httpStatus = r1.status
            httpReason = r1.reason

        httpConnection.close()
        return httpStatus, httpReason


## dbWriter thread - the only one writing the database
#
class dbWriter(threading.Thread):
    global optionen, logger
    def __init__(self, name=None):
        threading.Thread.__init__(self, name)
        logger.info("*** dbWriter started ***")

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
                           ('hcpunload', "{0}/{1}".format(_version, _build),
                           optionen["cluster"]))

        # make the 'flist' table
        if not optionen["fatDB"]:
            initcursor.execute('''create table flist
                                    (urlName TEXT PRIMARY KEY, type TEXT)''')
        else:
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
        dbConn.close()

    def run(self):
        sqlCmd = "INSERT INTO flist VALUES "
        if not optionen["fatDB"]:
            sqlCmd += "(?,?)"
        else:
            sqlCmd += "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"

        dbConn = sqlite3.connect(optionen["database"])
        dbConn.isolation_level = "DEFERRED" # use manual COMMIT mode
        dbCursor = dbConn.cursor()

        while True:
            qEntry = optionen["QdbWriter"].get()
            if qEntry != "exit":
                dbCursor.execute(sqlCmd, tuple(qEntry))
                optionen["NoOfdbWrites"] += 1
                optionen["QdbWriter"].task_done()
                if optionen["NoOfdbWrites"] % 1000 == 0: # do a commit every 1.000 recs
                    dbConn.commit()
            else:
                optionen["QdbWriter"].task_done()
                break
        dbConn.commit()
        dbConn.close()


## Monitor Thread einrichten
#
class Monitor(threading.Thread):
    global optionen, logger
    def run(self):
        stayAlive = True

        logger.warning("MonitorThread started - monitoring Worker Threads")
        while stayAlive:
            time.sleep(int(optionen["loginterval"]))
            FindWorker.WorkerLock.acquire()
            if not optionen["infile"]:
                logger.info("Dirs: {0}/{1}, Objects: {2}/{3} (found/deleted), Errors: {4} [Q:{5}/{6}/{7} (find/del/dbW)]".\
                            format(optionen["NoOfDirsFound"], optionen["NoOfDeletedDirs"], optionen["NoOfFilesFound"],
                                   optionen["NoOfDeletedFiles"], optionen["NoOfErrors"],
                                   optionen["QFbox"].qsize(), optionen["QDbox"].qsize(), optionen["QdbWriter"].qsize()))
            else:
                logger.info("Dirs: {0}/{1}, Objects: {2}/{3} (found/deleted), Errors: {4} [Q:{5} (del)]".\
                            format(optionen["NoOfDirsFound"], optionen["NoOfDeletedDirs"], optionen["NoOfFilesFound"],
                                   optionen["NoOfDeletedFiles"], optionen["NoOfErrors"],
                                   optionen["QDbox"].qsize()))
            FindWorker.WorkerLock.release()
            # all FindWorker and DelWorker Threads have ended
            if optionen["findThreadsEnded"] and optionen["objectDeletionEnded"] and optionen["directoryDeletionEnded"]:
                stayAlive = False
                logger.warning("MonitorThread exits - all Worker Threads ended")


#===============================================================================
# hcpUnload - main subcommand process flow
#===============================================================================
def hcpUnload(opts, logr):
    global optionen, logger
    optionen = opts
    logger = logr

    ## first of all, check parameters...
    #
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
        optionen["urlName"] = 'urlName'
        if not optionen["password"]:
            optionen["password"] = hcpf.getPassword(optionen["user"])
        optionen["header"] = {"Cookie": hcpf.makeAccToken("daac", optionen["user"],
                                                       optionen["password"]),
                           "User-Agent": Version}
        del optionen["password"] # burn it from memory!
    elif optionen["targetdir"][1:10] == "fcfs_data":
        optionen["authNamespace"] = False
        optionen["urlName"] = 'name'
    else:
        raise hcpf.hcpError(hcpf.hcpError._fatalError,
                    "target directory is invalid (/rest/... or /fcfs_data/...")


    if optionen["infile"]:
        optionen["objonly"] = True
        if not os.path.isfile(optionen["infile"]):
            raise hcpf.hcpError(hcpf.hcpError._fatalError,
                        "input file '{0:}' needs to be a readable file!".\
                        format(optionen["infile"]))
        else:
            if not optionen["yes"]:
                raise hcpf.hcpError(hcpf.hcpError._fatalError,
                        '''providing an input file without the strong will
                        to delete doesn't make sense - provide \'--YES\' !''')


    ## define global vars
    #
    optionen["NoOfFilesFound"] = 0
    optionen["NoOfDirsFound"] = 0
    optionen["NoOfDirErrors"] = 0
    optionen["NoOfDeletedFiles"] = 0
    optionen["NoOfDeletedDirs"] = 0
    optionen["NoOfErrors"] = 0
    optionen["NoOfdbWrites"] = 0
    optionen["findThreadsEnded"]       = False  # used to signal the ending of all FindWorker Threads

    if optionen["yes"]:
        optionen["objectDeletionEnded"]    = False  # used to signal the ending of object deletion
        optionen["directoryDeletionEnded"] = False  # used to signal the ending of directory deletion
    else:
        optionen["objectDeletionEnded"]    = True   # used to signal the ending of object deletion
        optionen["directoryDeletionEnded"] = True  # used to signal the ending of directory deletion

    ## startup information
    #
    optionen["StartTime"] = time.time()
    printStartMsgs()

    ## start Monitor thread
    #
    MonitorThread = Monitor(name="Monitor1")
    MonitorThread.setDaemon(True)
    MonitorThread.start()

    # if we do not have an input file:
    if not optionen["infile"]:
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
        optionen["QFbox"] = queue.Queue(optionen["fQueueSize"]) # Queue used while finding all Directories and Objects
        FindWorkerThreads = [FindWorker() for i in range(optionen["NoOfThreads"])]
        for thread in FindWorkerThreads:
            thread.setDaemon(True)
            thread.start()

    ## start DelWorker threads to delete Objects and Directories
    #
    optionen["QDbox"] = queue.Queue(optionen["Qdb"]) # Queue used to submit delete requests
    if optionen["yes"]:
        DelWorkerThreads = [DelWorker() for i in range(optionen["NoOfThreads"])]
        for thread in DelWorkerThreads:
            thread.setDaemon(True)
            thread.start()

    # generate work orders and wait for Queue to be processed
    #
    # if we do not have an input file:
    if not optionen["infile"]:
        optionen["QFbox"].put(optionen["targetdir"])
        optionen["QFbox"].join() # wait for all FindWorker threads
        optionen["findThreadsEnded"] = True # signal for MonitorThread
        for i in range(0, optionen["NoOfThreads"]): # signal FindWorker Threads to quit
            optionen["QFbox"].put("exit")
        logger.warning("***Discovery finished***")

        # stop dbWriter thread
        optionen["QdbWriter"].put("exit")
    else:
        # we have an input file; read it and put all the items into the optionen["QFbox"]
        anzInItems = 0
        with open(optionen["infile"], "rt", newline=None) as inFile:
            for inItem in inFile.readlines():
                if len(inItem) > 1:
                    logger.debug("read from infile: '{0}'".format(inItem.strip()))
                    optionen["QDbox"].put(inItem.strip())
                    anzInItems = anzInItems + 1
        logger.info("read {0:,} items from '{1}'".format(anzInItems,
                                                       optionen["infile"]))

    if optionen["yes"]:
        optionen["QDbox"].join() # wait for all found objects to be deleted
        optionen["objectDeletionEnded"] = True
        logger.warning("***Object deletion finished***")
        if optionen["objonly"]:
            logger.warning("***Directory deletion skipped***")
            optionen["directoryDeletionEnded"] = True
        else:
            # read directories from the database and fill the deletion queue
            DBconnect = sqlite3.connect(optionen["database"])
            DBcursor = DBconnect.cursor()
            if optionen["authNamespace"]:
                DBcursor.execute('''SELECT urlName FROM flist WHERE type="directory" \
                                    AND NOT urlName="/rest/.lost%2bfound" \
                                    AND NOT urlName="/rest" \
                                    ORDER BY urlName DESC''')
            else:
                DBcursor.execute('''SELECT urlName FROM flist WHERE type="directory" \
                                    AND NOT urlName="/fcfs_data/.lost%2bfound" \
                                    AND NOT urlName="/fcfs_data" \
                                    ORDER BY urlName DESC''')
            for row in DBcursor:
                while optionen["QDbox"].qsize() >= 500: # keep space in the queue to buffer re-scheduled items
                    time.sleep(1)
                else:
                    optionen["QDbox"].put(row[0]+"/")
            DBconnect.close()
            optionen["QDbox"].join()
            optionen["directoryDeletionEnded"] = True
            logger.warning("***Directory deletion finished***")


    ## wait for Monitor thread exiting
    #
    MonitorThread.join(5)

    ## remove Database files
    #
    if not optionen["keepdb"]:
        logger.warning("***removing database files***")
        journal = optionen["database"] + "-journal"
        if os.path.exists(journal):
            try:
                os.remove(journal)
            except:
                logger.error("can't remove " + journal)
        if os.path.exists(optionen["database"]):
            try:
                os.remove(optionen["database"])
            except:
                logger.error("can't remove " + optionen["database"])

    ## shutdown information
    #
    optionen["EndTime"] = time.time()
    optionen["EstTime"] = optionen["EndTime"] - optionen["StartTime"]
    printEndMsgs()
