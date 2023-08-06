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

### hcpretention.py - changes retention of objects stored in HCP
#

import http.client
import time
import queue
import threading
import sqlite3
import socket
import os
import sys
import ssl
try:
    SSL_NOVERIFY = ssl._create_unverified_context()
except (AttributeError, NameError):
    SSL_NOVERIFY = None

from hcptcmds import hcpf

# initialized needed variables
#
_version="0.9.6"
_build="2016-02-12/Sm"
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
          "Loginterval: " + str(optionen["loginterval"]) + " sec.",
          "   Database: " + optionen["database"] + " (" + optionen["dbVersion"] + ")"]
    if optionen["nossl"]:
        msg.append("     Target: http://" + optionen["cluster"])
    else:
        msg.append("     Target: https://" + optionen["cluster"])
    if optionen["user"]:
        msg.append("DataAccAcnt: " + optionen["user"])
    msg.append("    Threads: " + str(optionen["NoOfThreads"]))
    if optionen["delay"]:
        msg.append("      Delay: {0:,} ms between requests within each thread".format(int(optionen["delay"])))
    msg.append("  Verbosity: " + str(optionen["verbose"]))
    StartTime = time.time()
    msg.append(" Started at: " + time.strftime("%a, %d.%m., %H:%M:%S", time.localtime(StartTime)))
    msg.append(79 * "-")
    # log messages...
    for logline in msg:
        logger.log(49, logline)


## Print shutdown messages
#
def printEndMsgs():
    global optionen, logger
    msg = [79 * "-",
           " Started at: " + time.strftime("%a, %d.%m., %H:%M:%S", time.localtime(optionen["StartTime"])),
           "   Ended at: " + time.strftime("%a, %d.%m., %H:%M:%S", time.localtime(optionen["EndTime"])),
           "    Runtime: " + calcTime(optionen["EstTime"]) + " h:m:s.ms",
           "    Changed: " + str(optionen["NoOfChanged"]),
           "   Warnings: " + str(optionen["NoOfWarnings"]),
           "     Errors: " + str(optionen["NoOfErrors"])]
    # log messages...
    for logline in msg:
        logger.log(48, logline)

## from a given no. of seconds, calculate a time string
#
def calcTime(t):
    msec = int("{0:.2f}".format(t%1)[2:])
    min  = int(t//60)
    sec  = int(t%60)
    hour = int(min//60)
    min  = int(min%60)
    return("{0:02}:{1:02}:{2:02}.{3}".format(hour, min, sec, msec))


## Worker Threads used to find all Directories and Objects
#
class ChangeWorker(threading.Thread):
    global optionen, logger
    # static members
    WorkerLock = threading.Lock()

    def run(self):
        stayAlive = True
        while stayAlive:
            try:
                if optionen["delay"]:        # add a delay (pause) between requests
                    time.sleep(float(optionen["delay"]/1000))
                (url, newRetention) = optionen["Qbox"].get()
            except:
                logger.error("invalid entry in Qbox()")
                self.WorkerLock.acquire()
                optionen["NoOfErrors"] += 1
                self.WorkerLock.release()
                continue
            if url != "exit":
                (result, reason) = self.work(url, newRetention)

                if int(result) == 200 or int(result) == 201:
                    self.WorkerLock.acquire()
                    optionen["NoOfChanged"] += 1
                    self.WorkerLock.release()
                else:
                    if result == 302:
                        logger.critical("http " + str(result) + ": - password invalid")
                    elif result == 404:
                        logger.critical("http " + str(result) + ": - targetdirectory not found")
                    elif result == 998:
                        self.WorkerLock.acquire()
                        optionen["NoOfWarnings"] += 1
                        optionen["NoOfErrors"] -= 1
                        self.WorkerLock.release()
                    elif int(result) != 999:
                            logger.error(str(result) + " " + reason + " (" + url + ")")
                    self.WorkerLock.acquire()
                    optionen["NoOfErrors"] += 1
                    self.WorkerLock.release()

            else:
                stayAlive = False
            optionen["Qbox"].task_done()

    def work(self, url, newRetention):
        httpStatus = 0
        try:
            if optionen["nossl"]:
                httpConnection = http.client.HTTPConnection(optionen["cluster"])
            else:
                # set context to NOVERIFY to work around a restriction in Python 3.5
                httpConnection = http.client.HTTPSConnection(optionen["cluster"],
                                                             context=SSL_NOVERIFY)
            if optionen["verbose"] == 3:
                httpConnection.set_debuglevel(9)

            logger.debug(self.name+": changing retention of "+url) # debug
            if url[1:5] == "rest":                     # authenticated namespace
                tmpheader = optionen["header"].copy()
                tmpheader["Content-Type"] = "application/x-www-form-urlencoded"
                httpConnection.request("POST", url, headers=tmpheader,
                                       body="retention={0:s}".format(str(newRetention)))
            else:                                            # default namespace
                # transform the object-url to the metadata-url
                retentionUrl = url[:6]+"meta"+url[6:]+"/retention.txt"
                if optionen["verbose"] == 3:
                    logger.debug("metadataUrl = "+retentionUrl)
                httpConnection.request("PUT", retentionUrl, body=str(newRetention))

        except socket.gaierror as e:
            # this typically is a 'Errno 11001 - getaddrinfo failed' error...
            # log it and put the affected URL back into the queue for a later 'try again'
            # also, sleep a second to take the pressure out of the sockets ;-)
            logger.warning("'{0}' on '{1}' - re-scheduled".format(str(e), url))
            optionen["Qbox"].put(url)
            time.sleep(1)
            httpStatus = 998 # aka 'warning'
            httpReason = "'{0}' on '{1}'".format(str(e), url)
        except (http.client.NotConnected, http.client.InvalidURL, http.client.UnknownProtocol,
                http.client.UnknownTransferEncoding, http.client.UnimplementedFileMode,
                http.client.IncompleteRead, http.client.ImproperConnectionState,
                http.client.CannotSendRequest, http.client.CannotSendHeader,
                http.client.ResponseNotReady, http.client.BadStatusLine,
                IOError) as e:
            logger.critical("'{0}' on '{1}'".format(str(e), url))
            httpStatus = 999 # aka 'error'
            httpReason = "'{0}' on '{1}'".format(str(e), url)

        if not httpStatus:
            r1 = httpConnection.getresponse()
            httpStatus = r1.status
            httpReason = r1.reason
        httpConnection.close()
        return(httpStatus, httpReason)


## Monitor Thread einrichten
#
class Monitor(threading.Thread):
    global optionen, logger
    def run(self):
        logger.info("*** monitor started ***")
        stayAlive = True

        while stayAlive:
            time.sleep(int(optionen["loginterval"]))
            logger.info("Changed: {0:,}, Errors={1:,}, Warnings={2:,}".format(optionen["NoOfChanged"], optionen["NoOfErrors"], optionen["NoOfWarnings"]))
            # all Worker  Threads have ended
            if optionen["workThreadsEnded"]:
                stayAlive = False
                logger.info("*** monitor exits ***")


#===============================================================================
# hcpRetention - change the retention setting for a set of objects
#===============================================================================
def hcpRetention(opts, logr):
    global optionen, logger
    optionen = opts
    logger = logr

    # read 'admin' table and make sure, that the database is usable
    try:
        DBconnect = sqlite3.connect(optionen["database"])
        DBcursor = DBconnect.cursor()
        DBcursor.execute('SELECT * FROM admin')
        for row in DBcursor:
            optionen["magic"]     = row[0]
            optionen["dbVersion"] = row[1]
            optionen["cluster"]   = row[2]
            break
        DBconnect.close()
    except:
        logger.error("can't access database {0}".format(optionen["database"]))
        raise hcpf.hcpError(hcpf.hcpError._fatalError,
                    "can't access database {0}".format(optionen["database"]))
    if optionen["magic"] != "hcp list":
        logger.error("database {0} is not a valid database".format(
                                                        optionen["database"]))
        raise hcpf.hcpError(hcpf.hcpError._fatalError,
                    "database {0} is not a valid database".format(
                                                        optionen["database"]))
    if optionen["dbVersion"][:5] < '1.2.7':
        logger.error("database version of {0} is invalid ({1})".\
                     format(optionen["database"], optionen["dbVersion"]))
        raise hcpf.hcpError(hcpf.hcpError._fatalError,
                    "database version of {0} is invalid ({1})".\
                     format(optionen["database"], optionen["dbVersion"]))

    # find out if we run against an authenticated namespace or not
    if optionen["cluster"][:3]  != "www" and \
       optionen["cluster"][:16] != "default.default.":          # default namespace
        optionen["authNamespace"] = True
    else:
        optionen["authNamespace"] = False

    # make sure a data access account is given, if not ask for one
    if optionen["authNamespace"]:
        if not optionen["password"]:
            optionen["password"] = hcpf.getPassword(optionen["user"])
        optionen["header"] = {"Cookie": hcpf.makeAccToken("daac", optionen["user"],
                                                       optionen["password"]),
                           "User-Agent": Version}
        del optionen["password"] # burn it from memory!

    ## define global vars
    #
    optionen["NoOfErrors"] = 0
    optionen["NoOfWarnings"] = 0
    optionen["NoOfChanged"] = 0

    #
    optionen["workThreadsEnded"]       = False  # used to signal the ending of all Worker Threads

    ## startup information
    #
    optionen["StartTime"] = time.time()
    printStartMsgs()

    ## start Monitor thread
    #
    MonitorThread = Monitor(name="Monitor")
    MonitorThread.setDaemon(True)
    MonitorThread.start()

    ## start FindWorker threads to find all Directories and Files
    #
    optionen["Qbox"] = queue.Queue(10000) # Queue used to process all changes
    startChangeWorkers = time.time()
    WorkerThreads = [ChangeWorker() for i in range(optionen["NoOfThreads"])]
    for thread in WorkerThreads:
        thread.setDaemon(True)
        thread.start()

    ## read db here and fill queue...
    #
    DBconnect = sqlite3.connect(optionen["database"])
    DBcursor = DBconnect.cursor()
    if not optionen["authNamespace"]:                           # default namespace
        logger.debug("*** working with the default namespace ***")
        DBcursor.execute('SELECT urlname, new_ret FROM flist WHERE type="file" AND new_ret NOT NULL')
    else:                                              # authenticated namespace
        logger.debug("*** working with an authenticated namespace ***")
        DBcursor.execute('SELECT urlname, new_ret FROM flist WHERE type="object" AND new_ret NOT NULL')
    logger.info("*** Changing retentions started ***")
    for row in DBcursor:
        if len(row) == 2:
            optionen["Qbox"].put(row)
        else:
            logger.error("invalid DB entry ({0}) - skipped".format(str(row)))
            ChangeWorker.WorkerLock.acquire()
            optionen["NoOfErrors"] += 1
            ChangeWorker.WorkerLock.release()
    DBconnect.close()


    optionen["Qbox"].join() # wait for all FindWorker threads
    optionen["workThreadsEnded"] = True # signal for MonitorThread
    for i in range(0, optionen["NoOfThreads"]): # signal FindWorker Threads to quit
        optionen["Qbox"].put(["exit", ""])
    logger.info("*** Changing retentions finished after {0} ***".\
                   format(calcTime(time.time()-startChangeWorkers)))

    ## wait for Monitor thread exiting
    #
    MonitorThread.join(5)

    ## shutdown information
    #
    optionen["EndTime"] = time.time()
    optionen["EstTime"] = optionen["EndTime"] - optionen["StartTime"]
    printEndMsgs()
