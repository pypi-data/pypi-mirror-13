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

import sys
import getpass
import base64
import hashlib
import http.client
import xml.sax
from xml.sax import handler
import socket


#===============================================================================
# hcpError - error class for HCP
#===============================================================================
class hcpError(Exception):
    '''
    used to signal error in 'hcpt' - will provide status code and text as
    self.errStatus and
    self.errText
    '''
    _fatalError = 999

    def __init__(self, status, reason):
        self.errStatus = status
        self.errText = reason
    def __str__(self):
        return repr(self.errStatus), repr(self.errText)


#===============================================================================
# getPassword - request password entry from interactive user
#===============================================================================
def getPassword(user):
    sys.stderr = sys.stdout
    password = getpass.getpass("Enter Password for user '{0}': "\
                                    .format(user))
    sys.stderr = sys.__stderr__
    return(password)


#===============================================================================
# makeAccToken - generate a valid HCP access token from user, password and
#                acctype might be 'daac' and 'mapi'
#===============================================================================
def makeAccToken(acctype, user, password):
    '''
    Return an access cookie to be used with HCP
    acctype == 'mapi' or 'daac'
    '''
    token = base64.b64encode(user.encode()).decode() \
                    + ":" + hashlib.md5(password.encode()).hexdigest()
    if acctype == "mapi":
        return("hcp-api-auth={0}".format(token))
    elif acctype == "daac":
        return("hcp-ns-auth={0}".format(token))


#------------------
#===============================================================================
# SaxDocumentHandlerProc - Parse the XML returned by GET on /proc
#===============================================================================
class SaxDocHandler(handler.ContentHandler):
    def __init__(self, caller):
        handler.ContentHandler.__init__(self)
        self.caller = caller
    def startElement(self, name, attrs):
        if name == "namespace":
            if attrs.get("name") == self.caller.nameSpaceName:
                self.caller.name = attrs.get("name")
                self.caller.nameIDNA = attrs.get("nameIDNA")
                self.caller.versioningEnabled = attrs.get("versioningEnabled")
                self.caller.searchEnabled = attrs.get("searchEnabled")
                self.caller.retentionMode = attrs.get("retentionMode")
                self.caller.defaultShredValue = attrs.get("defaultShredValue")
                self.caller.defaultIndexValue = attrs.get("defaultIndexValue")
                self.caller.defaultRetentionValue = attrs.get("defaultRetentionValue")
                self.caller.hashScheme = attrs.get("hashScheme")
                self.caller.dpl = attrs.get("dpl")
        if name == "statistics":
            self.caller.totalCapacityBytes = attrs.get("totalCapacityBytes")
            self.caller.usedCapacityBytes = attrs.get("usedCapacityBytes")
            self.caller.softQuotaPercent = attrs.get("softQuotaPercent")
            self.caller.objectCount = attrs.get("objectCount")
            self.caller.shredObjectCount = attrs.get("shredObjectCount")
            self.caller.shredObjectBytes = attrs.get("shredObjectBytes")
            self.caller.customMetadataObjectCount = attrs.get("customMetadataObjectCount")
            self.caller.customMetadataObjectBytes = attrs.get("customMetadataObjectBytes")


class HCPnsStats():
    '''
    HCPnsStats provides available information for a given namespace
    '''
    def __init__(self, nameSpaceUrl, headers=None, SSL=True):
        '''
        Constructor
        '''
        self.nameSpaceUrl = nameSpaceUrl
        self.nameSpaceName = self.nameSpaceUrl.split('.')[0]
        self.headers = headers
        self.SSL = SSL
        # <namespace url>/proc
        self.name = None
        self.nameIDNA = None
        self.versioningEnabled = None
        self.searchEnabled = None
        self.retentionMode = None
        self.defaultShredValue = None
        self.defaultIndexValue = None
        self.defaultRetentionValue = None
        self.hashScheme = None
        self.dpl = None
        # <namespace url>/proc/statistics
        self.totalCapacityBytes = None
        self.usedCapacityBytes = None
        self.softQuotaPercent = None
        self.objectCount = None
        self.shredObjectCount = None
        self.shredObjectBytes = None
        self.customMetadataObjectCount = None
        self.customMetadataObjectBytes = None

        # get values from /proc
        if self.SSL:
            httpConnection = http.client.HTTPSConnection(self.nameSpaceUrl)
        else:
            httpConnection = http.client.HTTPConnection(self.nameSpaceUrl)
        try:
            httpConnection.request("GET", "/proc", headers=self.headers)
        except (http.client.NotConnected, http.client.InvalidURL, http.client.UnknownProtocol,
                http.client.UnknownTransferEncoding, http.client.UnimplementedFileMode,
                http.client.IncompleteRead, http.client.ImproperConnectionState,
                http.client.CannotSendRequest, http.client.CannotSendHeader,
                http.client.ResponseNotReady, http.client.BadStatusLine,
                socket.gaierror, IOError) as e:
            raise hcpError(999, str(e))
        else:
            r1 = httpConnection.getresponse()
            if r1.status == 200:
                # Good status, get and parse the response
                handler = SaxDocHandler(self)
                xml.sax.parseString(r1.read(), handler)
                httpConnection.close()
            else:
                raise hcpError(r1.status, r1.reason)

        # get values from /proc/statistics
        if self.SSL:
            httpConnection = http.client.HTTPSConnection(self.nameSpaceUrl)
        else:
            httpConnection = http.client.HTTPConnection(self.nameSpaceUrl)
        try:
            httpConnection.request("GET", "/proc/statistics", headers=self.headers)
        except (http.client.NotConnected, http.client.InvalidURL, http.client.UnknownProtocol,
                http.client.UnknownTransferEncoding, http.client.UnimplementedFileMode,
                http.client.IncompleteRead, http.client.ImproperConnectionState,
                http.client.CannotSendRequest, http.client.CannotSendHeader,
                http.client.ResponseNotReady, http.client.BadStatusLine,
                socket.gaierror, IOError) as e:
            raise hcpError(999, str(e))
        else:
            r1 = httpConnection.getresponse()
            if r1.status == 200:
                # Good status, get and parse the response
                handler = SaxDocHandler(self)
                xml.sax.parseString(r1.read(), handler)
                httpConnection.close()
            else:
                raise hcpError(r1.status, r1.reason)

#===============================================================================
# calcByteSize -from a given no. of bytes, calculate the biggest possible representation
#===============================================================================
def calcByteSize(bytes, formLang=False):
    sz = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    szl = ["Byte", "Kilobyte", "Megabyte", "Gigabyte", "Terabyte",
           "Petabyte", "Exabyte", "Zettabyte", "Yottabyte"]
    i = 0
    neg = False
    if bytes < 0:
        neg = True
        bytes *= -1

    while bytes > 1023:
                    bytes = bytes / 1024
                    i = i + 1
    if neg:
        bytes *= -1
    if formLang:
        return("{0:.2f} {1:}".format(bytes, szl[i]))
    else:
        return("{0:.2f} {1:}".format(bytes, sz[i]))

#-------------
# test routine
#-------------
if __name__ == '__main__':

    print()
    print("Test 2: Query the paramaters of an example namespace")
    user = "ns1"
    password = "ns101"
    namespace = "ns1.matrix.hcp1.vm.local"
    header = {"Cookie": makeAccToken('daac', user, password)}
    mystats = HCPnsStats(namespace, headers=header, SSL=True)

    print("name =", mystats.name)
    print("nameIDNA =", mystats.nameIDNA)
    print("versioningEnabled = ", mystats.versioningEnabled)
    print("searchEnabled = ", mystats.searchEnabled)
    print("retentionMode = ", mystats.retentionMode)
    print("defaultShredValue = ", mystats.defaultShredValue)
    print("defaultIndexValue = ", mystats.defaultIndexValue)
    print("defaultRetentionValue = ", mystats.defaultRetentionValue)
    print("hashScheme = ", mystats.hashScheme)
    print("dpl = ", mystats.dpl)
    print()
    print("totalCapacityBytes = ", mystats.totalCapacityBytes)
    print("usedCapacityBytes = ", mystats.usedCapacityBytes)
    print("softQuotaPercent = ", mystats.softQuotaPercent)
    print("objectCount = ", mystats.objectCount)
    print("shredObjectCount = ", mystats.shredObjectCount)
    print("shredObjectBytes = ", mystats.shredObjectBytes)
    print("customMetadataObjectCount = ", mystats.customMetadataObjectCount)
    print("customMetadataObjectBytes = ", mystats.customMetadataObjectBytes)



