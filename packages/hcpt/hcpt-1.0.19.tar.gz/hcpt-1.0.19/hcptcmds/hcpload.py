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

### hcp-load.py - bulk load of data into HCP for testing purposes
#

import time
import queue
import threading
import os.path
import logging
import sys
import hcpsdk

from hcptcmds import hcpf

# initialized needed variables
#
_version="1.1.0"
_build="2015-02-20/Sm"
Version = "v.{0} ({1})".format(_version, _build)
Author  = "\nContact: sw@snomis.de"
optionen = None
logger = None


## from a given no. of bytes, calculate the biggest possible representation
#
def calcSize(bytes):
    sz = ["Byte", "Kbyte", "Mbyte", "Gbyte", "Tbyte"]
    i = 0
    while bytes > 1023:
                    bytes = bytes / 1024
                    i = i + 1
    return("{0:.2f} {1:}".format(bytes, sz[i]))

## Threading einrichten ~> worker definieren
#
class Worker(threading.Thread):
    global optionen, logger
    # static members
    Qbox = queue.Queue(1000)
    WorkerLock = threading.Lock()
    perf = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.con = hcpsdk.Connection(optionen['target'])

    def run(self):
        while True:
            url = Worker.Qbox.get()
            try:
                (result, reason) = self.work(url)
            except:
                logger.critical("connect to cluster failed - abort")
                os._exit(1)

            self.WorkerLock.acquire()
            if int(result) == 201:
                optionen["NoOfWrites"] += 1
            else:
                optionen["NoOfErrors"] += 1
                logger.warning("error: " + str(result) + " " + reason + " (" + url + ")")
            Worker.WorkerLock.release()
            Worker.Qbox.task_done()

        self.con.close()

    def work(self, url):
        fileHandle = open(optionen["file"], "rb")
        if optionen["retention"]:
            headers = {'retention': optionen['retention']}
        else:
            headers = {}
        r1 = self.con.PUT(url, fileHandle, headers=headers)
        fileHandle.close()
        p = self.con.service_time2
        Worker.WorkerLock.acquire()
        Worker.perf.append(p)
        if optionen['reqloghdl']:
            print(str(p).replace('.',','), file=optionen["reqloghdl"])
        Worker.WorkerLock.release()
        return self.con.response_status, self.con.response_reason

## Monitor Thread einrichten
#
class Monitor(threading.Thread):
    global optionen, logger
    def run(self):
        stayAlive = True

        if optionen["verbose"]:
            logger.info("MonitorThread started monitoring Worker.Qbox.qsize()")
        while stayAlive:
            time.sleep(int(optionen["loginterval"]))
            Worker.WorkerLock.acquire()
            logger.info("files sent: " + str(optionen["NoOfWrites"]) + ", errors: " + \
                        str(optionen["NoOfErrors"]) + ", PUTs/sec.: " + \
                        str("{0:0.1f}".format((optionen["NoOfWrites"])/
                                              (time.time()-optionen["StartTime"]))))
            Worker.WorkerLock.release()
            if Worker.Qbox.qsize() == 0:
                stayAlive = False
                Worker.Qbox.join()
                logger.info("MonitorThread exits on Worker.Qbox.qsize() == 0")
                logger.info(50 * "-")

# function to generate the work orders to be processed by the Worker threads
#
def do_it(targetdir, matrix):
    global optionen, logger
    for i in range(matrix[0]):
        if len(matrix) > 1:
            url = targetdir + "{0:04}/".format(i)
            do_it(url, matrix[1:])
        else:
            url = targetdir + "{0:04}.{1}".format(i, os.path.basename(optionen["file"]))
            Worker.Qbox.put(url)


#-- start main -----------------------------------------------------------------------------------

def hcpLoad(opts, logr):
    global optionen, logger
    optionen = opts
    logger = logr

    ## first of all, check parameters...
    #
    optionen["StartTime"] = time.time()

    if optionen["targetdir"][len(optionen["targetdir"]) - 1] != "/":
                optionen["targetdir"] += "/"

    # calculate number of puts needed
    NoOfPuts        = optionen["matrix"][0]
    for i in range(1,len(optionen["matrix"])):
        NoOfPuts    = NoOfPuts * optionen["matrix"][i]
    try:
        fileSize        = os.path.getsize(optionen["file"])
    except Exception as e:
        sys.exit('error: {}'.format(e))
    if not optionen["password"]:
        optionen["password"] = hcpf.getPassword(optionen["user"])
    if optionen['nossl']:
        p = 80
    else:
        p = 443
    optionen['target'] = hcpsdk.Target(optionen['cluster'],
                                       hcpsdk.NativeAuthorization(optionen["user"],
                                                                  optionen["password"]),
                                       port=p)
    del optionen["password"] # burn it from memory!

    optionen["NoOfWrites"] = 0
    optionen["NoOfErrors"] = 0

    ## startup information
    #
    logger.info("{0} {1} {2}".format(os.path.splitext(
                                        os.path.basename(sys.argv[0]))[0],
                                optionen["subCmdName"], Version))
    logger.info("    Logfile: " + optionen["logfile"])
    logger.info("Loginterval: " + str(optionen["loginterval"]) + " sec.")
    if "reqlogfile" in optionen:
        logger.info("    Logfile: " + optionen["reqlogfile"])
    if optionen["nossl"]:
        logger.info("     Target: http://" + optionen["cluster"] +  optionen["targetdir"])
    else:
        logger.info("     Target: https://" + optionen["cluster"] +  optionen["targetdir"])
    logger.info("DataAccAcnt: " + optionen["user"])
    logger.info(" Ingestfile: " + optionen["file"])
    logger.info("   Filesize: " + str(fileSize) + " Bytes (= " + calcSize(fileSize) + ")")
    if optionen["retention"]:
        logger.info("  Retention: " + str(optionen["retention"]))
    logger.info("  Structure: " + str(optionen["matrix"]) + " = " + "{0:,.0f}".format(NoOfPuts) + " PUTs" + " (= " + calcSize(NoOfPuts * fileSize) + ")")
    logger.info("    Threads: " + str(optionen["NoOfThreads"]))
    StartTime = time.time()
    logger.info(" Started at: " + time.strftime("%a, %d.%m., %H:%M:%S", time.localtime(StartTime)))
    logger.info(50 * "-")
    ## start Monitor thread
    #
    if optionen["verbose"]:
        MonitorThread = Monitor(name="Monitor")
        MonitorThread.setDaemon(True)
        MonitorThread.start()

    ## start Worker threads
    #
    WorkerThreads = [Worker() for i in range(optionen["NoOfThreads"])]
    for thread in WorkerThreads:
        thread.setDaemon(True)
        thread.start()

    ## if needed, open reqlogfile
    #
    if "reqlogfile" in optionen.keys():
        try:
            optionen["reqloghdl"] = open(optionen["reqlogfile"], 'w')
            print('seconds per request', file=optionen["reqloghdl"])
        except:
            sys.exit("Open of {} failed".format(optionen["reqlogfile"]))
    else:
        optionen['reqloghdl'] = None

    # generate work orders
    #
    do_it(optionen["targetdir"], optionen["matrix"])

    ## wait for all Worker threads exiting
    #
    Worker.Qbox.join()

    ## close reqlogfile if needed
    #
    try:
        optionen["reqlogfile"].flush()
        optionen["reqlogfile"].close()
    except:
        pass

    ## wait for Monitor thread exiting
    #
    if optionen["verbose"]:
        MonitorThread.join(30)

    ## shutdown information
    #
    EndTime = time.time()
    EstTime = EndTime - StartTime
    logger.info(" Started at: " + time.strftime("%a, %d.%m., %H:%M:%S", time.localtime(StartTime)))
    logger.info("   Ended at: " + time.strftime("%a, %d.%m., %H:%M:%S", time.localtime(EndTime)))
    logger.info("    Runtime: " + "{0:.2f}".format(EstTime) + " Sekunden")
    logger.info("    Success: " + str(optionen["NoOfWrites"]))
    logger.info("     Errors: " + str(optionen["NoOfErrors"]))
    logger.info(" Statistics:")
    logger.info("  Obj./Sec.: " + "{0:.1f}".format(optionen["NoOfWrites"] / EstTime))
    logger.info("   Transfer: " + "{0:}".format(calcSize(fileSize * optionen["NoOfWrites"] / EstTime)) + "/sec.")

    Worker.perf.sort()
    p = Worker.perf
    sum = 0.0
    for i in range(0,len(p)-1):
        sum += p[i]
    average = sum/len(p)
    if type(len(p)/2) == float:
        median = p[int(len(p)/2)]
    else:
        median = (p[int(len(p)/2)]+p[int((len(p)/2)-1)])/2

    logger.info("      t-sum: {:>9,.0f} ms".format(sum*1000))
    logger.info("  t-average: {:>9,.0f} ms".format(average*1000))
    logger.info("      t-min: {:>9,.0f} ms".format(p[0]*1000))
    logger.info("      t-max: {:>9,.0f} ms".format(p[len(p)-1]*1000))
    logger.info("   t-median: {:>9,.0f} ms".format(median*1000))
    logger.info(" t-90%-line: {:>9,.0f} ms".format(p[int(len(p)*0.9)]*1000))
