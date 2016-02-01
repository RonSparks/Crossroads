# -*- coding: utf-8 -*-
import sys
import os
import os.path
import datetime
import xmltodict
import json
#import time
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from optparse import OptionParser
import inspect
import pprint
import collections

# use this if you want to include modules from a subfolder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"lib")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import session
import ebay_new


def init_options():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option("-a", "--active",
                      action="store_true", dest="active", default=False,
                      help="Get user active inventory")
    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug", default=False,
                      help="Enabled debugging [default: %default]")
    parser.add_option("-f", "--fetch",
                      action="store_true", dest="fetch", default=False,
                      help="Fetch token for given user")
    parser.add_option("-i", "--inventory",
                      action="store_true", dest="inv", default=False,
                      help="Get user list inventory")
    parser.add_option("-k", "--token",
                      action="store_true", dest="token", default=False,
                      help="Get eBay token status")
    parser.add_option("-l", "--list",
                      action="store_true", dest="list", default=False,
                      help="Get user list")
    parser.add_option("-p", "--product",
                      action="store_true", dest="prod", default=False,
                      help="Get product details")
    parser.add_option("-r", "--revise",
                      action="store_true", dest="revise", default=False,
                      help="Revise product details")
    parser.add_option("-s", "--session",
                      action="store_true", dest="session", default=False,
                      help="Get session id")
    parser.add_option("-t", "--time",
                      action="store_true", dest="time", default=False,
                      help="Get eBay Current Time")
    parser.add_option("-u", "--user",
                      action="store_true", dest="user", default=False,
                      help="Get user Information")

    (opts, args) = parser.parse_args()
    return opts, args

def main(opts):
    FilePath = "./ebay.yaml"
    SessionObj = session.Session()
    SessionObj.Initialize(opts, FilePath, "Production")

    if SessionObj.Error == 0:
        ka_ge = "AgAAAA**AQAAAA**aAAAAA**fDkDVQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wJnYCnCZODow6dj6x9nY+seQ**j70CAA**AAMAAA**h4cBTuLnj1JSYsez+q6+QCj46TM+1Ea0WEGo6OU8swEHrsuRo+WZDmV5/KsJN8nNDzCmeYAeq4GegtF6hJlB1gTJmMZnqVQ3lxtNfumlKhYTtC9YmngyQQ04k7UIARqDJIpZlrcs4/DveNZwS5Za8oL67FqLPEEtaEPEbzxg0Ba3wsJDncnSVOiS+NOGoQXASP4kZoZTF/6jzr4R+HrrCv1oaYivhcAOQVwD4c/Zuw1RMSuUgfas3mx14yHq81Sb/8DMdWEJ9jpyvUG32WVFchOELR18tbQkcKVCOuTdtuKxhY0WPVuH5yM9bybfiySeNBJixJyomZEUBGxu+HaXgTLmUTA2/sQ/fKSFu4t/jG1hgZw/DcLvOiUiP+Qr4VMh8JtpZX3dfzr36kYNaTCxg7UdUnVHD/tppvnJQ6GP+ZqrTtlfeI63vYazTymMxz5d4z4FjD6VA+piLoRjzsk83vbmF/3Ey4SzwByiF0P/GVN6grRKl9J+/P3XySdaFVfSu4aWKXpgVtaurVfsG8wLxqMlXYqVzouP5N/VfLBRaHn3lM5dhIxqlg0DBS3+Ck5cI3wSG1uv5bsT+awsyQLzovnC+dZ6mmNYfJ309viCEbNnJzjchODOVecO4BLZefI+H7FDyY8TBoABTARA1AddneN7WTcj5Q8ykfV2LmPxXvb3KtRfwTb+GPE4BPkvdqRtu6Lnuq4YqO6+25MBoWfNp3HOgrG3poGeBBeKVwY2jLscNTTjtpI257oZ/Orrk1qy"
        risa = "AgAAAA**AQAAAA**aAAAAA**cMsBVQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wJlYGhC5SAqQmdj6x9nY+seQ**j70CAA**AAMAAA**8C79zRs8jk5reI5YP7fgF4GoGLvO/q93k7vfirqnZfeGllMA+r/RYoENiPTL0OifnN0BsTrZH6g8gNrjDezmj/RCKVLAlnV1/6sDvZvVAxUPjVaGarUnpy5P46lnkoSljOAqni7m/lpUiE1TbDREvovXmWhJ6+hvCMABkEJXi2aMesaeDB5Iwv7Xmds4FXmBdruc8vABCH9kjXf254ZX7aMaWOgPEaxWDS2XGjNiMas2jkqDFhzZEH6BoOo2TrhOBNczornXgan+WMFUGuyLc0sp08UEVGcQn96N+NO+/c9pilUXid5KemVeWztFSYNaZAyMcu7Fhz3F/I043xPkZvU0ZNj4HHmlxoKqM7p8ziPqhu/d607GHhy4R91ZvztZPhBkMlEp/TAvKUNRv70UoKdxan3sO3qCvyFYaXtyNUcQNlXFUewFSF8viF80A+zXnFKN0nB5bgeZcpUslVhPPePtcj+khXg5FBAN4KHuWEPfYu/ZroYZ2zwkwXpXOM5NYeoR/DllC/i/NpGY8P6GE+oV3ogrgJAayjKZl0SxuK24zd7FF7JDnA0jBjvUThKqA/llp92nz6jtfmR6XoQbJjI671pWpooxjc6xEafUGZUL0yG3GbpFMCSLvqGD/w/pb6B0SVxxU0RZZyk7mL/e44IRG19MsAA6YthZXbL+wfxE2HmKhszIYI8WoejZBYvVlgaIY4Wu8qpJaZGOEc4yQJVbAjjdOCJEhMIKwC/dMYD82K+YvQDeRJkZN9ZWFoDC"
        kari = "AgAAAA**AQAAAA**aAAAAA**IWN3VQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AHl4aoDpaBpQmdj6x9nY+seQ**j70CAA**AAMAAA**PT/ANlinkISBEUola+dVPmCMWVpsD/8L8wAYCQ/8nN1IBXArone+hVnJMEfiJwNZboNZmZN8mDZtju+Io2rz2Z4p/CcmDlp86qEZycMuqI+PVdeaHBkzvnrSVvSE+GLABYA9ZMGNvdDnMKriy2brHkJv46zCKPWbxKFh5Cann7eAag7mPJLMMZ0PUKlnAoDLq3LuqX4ievbYM6tQm36wd0sgFD9u6pyp0nvSxs0ojvumwSgrbzgyPli5bzbe1DIosPf/9b8Vxxx2HrG+AYF50451KcAWVz8hrN8U4L668CcRm0z+/Qe0UuaQyP383Vi0fPu7E9fmcKYAfBOxsaDYtlPHpA+igzeKKTd97Xi/kI5VzPyWQaqm0Obcoo+HtIG7oA+iyxTgWtfSxNqVJSHfVUzR9CnS+JBEaM9XQ2BXb7+5kGvOLIl5svMTCbYEPWjuQsF1KYSX4n5tQSF/ErinOFZWKpY2A3t69dHvc8qP9DBFsvALfDqb+v0L4yZA7iY9FOAjoWqUhlVlCS6cxdf7iDR6J3/b1hcIx2f2FCgHpF7l6cLdJkjWkeR3sAJnS8ax9rFcKKdByEVNBUq4W4Lw1s7z7rpEhborDzyizZ/U+XRRK0JsRZ7S01EKuJVBAUSeqiEbVdoz5ecXPxSNAq/coGTm4Ud1LiJ39ikomZzvxEtySoNyULpvpf34gTPsdbv0TPQMadGjRoOsC+Ja0PmNbs33KffXU1nXZBNynxtZSYzXOMoiCc6jqQk0MSa4tLxJ"
        SessionObj.Token = risa
        SessionObj.Page = "200"
        SessionObj.PageNum = 1
        SessionObj.Days = 120
        SessionObj.ItemID  = "151711221147" #"370927252175"
        SessionObj.Quantity = "2"
        SessionObj.ebug = opts.debug
        """2010-02-12T21:59:59.005Z   2010-02-26T21:59:59.00Z """
        SessionObj.End = datetime.datetime.now()
        #SessionObj.End = SessionObj.End - datetime.timedelta(days = 60)
        SessionObj.Start = SessionObj.End - datetime.timedelta(days=SessionObj.Days)
        SessionObj.End = str(SessionObj.End).replace(" ", "T",1) + "Z" #.strftime('%Y-%M-%D %H:%M:%S:%f')
        SessionObj.Start = str(SessionObj.Start).replace(" ", "T",1) + "Z" #.strftime('%Y-%M-%D %H:%M:%S:%f')

        if opts.active:
            print "############## STARTING GET USER ACTIVE INVENTORY ##############"
            Timestamp = ""
            Ack = ""
            Version = ""
            TotalNumberOfPages = -1
            TotalNumberOfEntries = -1
            GetMyeBaySelling = ebay_new.GetMyeBaySelling(risa, 6, SessionObj.PageNum)
            if opts.debug:
                print str(SessionObj.debug)

            listdata = str(GetMyeBaySelling.Get(opts))
            print str(listdata)
            root = ET.ElementTree(ET.fromstring(listdata)).getroot()
            for node in root:
                if node.tag == "{urn:ebay:apis:eBLBaseComponents}Timestamp":
                    Timestamp = node.text
                if node.tag == "{urn:ebay:apis:eBLBaseComponents}Ack":
                    Ack = node.text
                if node.tag == "{urn:ebay:apis:eBLBaseComponents}Version":
                    Version = node.text
            for elem in root.iter('{urn:ebay:apis:eBLBaseComponents}PaginationResult'):
                for child in elem:
                    if child.tag == "{urn:ebay:apis:eBLBaseComponents}TotalNumberOfPages":
                        TotalNumberOfPages = child.text
                    if child.tag == "{urn:ebay:apis:eBLBaseComponents}TotalNumberOfEntries":
                        TotalNumberOfEntries = child.text
            print "Timestamp: " + Timestamp
            print "Ack: " + Ack
            print "Version: " + Version
            print "TotalNumberOfPages: " + str(TotalNumberOfPages)
            print "TotalNumberOfEntries: " + str(TotalNumberOfEntries)


            #print "GOT IT:---->\n" + listdata
            print "#################################################################"
            print "\n\n"
        if opts.debug:
            print "Developer: " + SessionObj.Developer + "\n"
            print "Application: " + SessionObj.Application + "\n"
            print "Certificate: " + SessionObj.Certificate + "\n"
            print "Runame: " + SessionObj.Runame + "\n"
            print "Error: " + str(SessionObj.Error) + "\n"
            print "Token: " + SessionObj.Token + "\n"
            print "TokenStatus: " + SessionObj.TokenStatus + "\n"
            print "Session: " + SessionObj.Session + "\n"
            print "Session: " + SessionObj.SessionID + "\n"
            print "Start: " + SessionObj.Start + "\n"
            print "End: " + SessionObj.End + "\n"
            print "Page: " + SessionObj.Page + "\n"
            print "debug: " + SessionObj.debug + "\n"

        if opts.fetch:
            print "################### STARTING FETCH TOKEN STATUS #################"
            FetchToken = ebay_new.FetchToken(sessionID.SessionID)
            SessionObj.Token = FetchToken.Get(opts)
            print "GOT IT:---->" + str(SessionObj.Token)
            print "#################################################################"
            print "\n\n"
        if opts.inv:
            print "################ STARTING GET USER LIST INVENTORY ###############"
            Timestamp = ""
            Ack = ""
            Version = ""
            TotalNumberOfPages = -1
            TotalNumberOfEntries = -1
            GetSellingManagerInventory = ebay_new.GetSellingManagerInventory(risa, SessionObj.Page, SessionObj.PageNum)
            if opts.debug:
                print str(SessionObj.debug)

            listdata = str(GetSellingManagerInventory.Get(opts))
            #print str(listdata)
            root = ET.ElementTree(ET.fromstring(listdata)).getroot()
            for node in root:
                if node.tag == "{urn:ebay:apis:eBLBaseComponents}Timestamp":
                    Timestamp = node.text
                if node.tag == "{urn:ebay:apis:eBLBaseComponents}Ack":
                    Ack = node.text
                if node.tag == "{urn:ebay:apis:eBLBaseComponents}Version":
                    Version = node.text
            for elem in root.iter('{urn:ebay:apis:eBLBaseComponents}PaginationResult'):
                for child in elem:
                    if child.tag == "{urn:ebay:apis:eBLBaseComponents}TotalNumberOfPages":
                        TotalNumberOfPages = child.text
                    if child.tag == "{urn:ebay:apis:eBLBaseComponents}TotalNumberOfEntries":
                        TotalNumberOfEntries = child.text
            print "Timestamp: " + Timestamp
            print "Ack: " + Ack
            print "Version: " + Version
            print "TotalNumberOfPages: " + str(TotalNumberOfPages)
            print "TotalNumberOfEntries: " + str(TotalNumberOfEntries)


            #print "GOT IT:---->\n" + listdata
            print "#################################################################"
            print "\n\n"
        if opts.list:
            print "##################### STARTING GET USER LIST ####################"
            #Token, Start, End, Page
            GetSellerList = ebay_new.GetSellerList(risa, SessionObj.Start, SessionObj.End, SessionObj.Page)
            if opts.debug:
                print str(SessionObj.debug)
                
            listdata = str(GetSellerList.Get(opts))  #.replace("><", ">\n<")
            listdata = listdata.replace("{urn:ebay:apis:eBLBaseComponents}", "")
            print str(listdata)
            root = ET.ElementTree(ET.fromstring(listdata)).getroot()
            listdata = ""
            ItemID = ""
            SKU = ""
            Title = ""
            ConditionDescription = ""
            StartTime = ""
            EndTime = ""
            Quantity = ""
            MinBid = ""
            Listingstatus = ""
            Questions = ""
            eBay = "Yes"
            Amazon = "No"
            Etsy = "No"
            for node in root.findall(".//{urn:ebay:apis:eBLBaseComponents}ItemArray//{urn:ebay:apis:eBLBaseComponents}Item"):
                #print node.tag
                if node.tag == "{urn:ebay:apis:eBLBaseComponents}Item":
                    #print node.tag + "\n\n\n"
                    for child in node:
                        #print child.tag
                        if child.tag == "{urn:ebay:apis:eBLBaseComponents}ItemID":
                            ItemID = child.text
                        if child.tag == "{urn:ebay:apis:eBLBaseComponents}SKU":
                            SKU = child.text
                        if child.tag == "{urn:ebay:apis:eBLBaseComponents}Title":
                            Title = child.text
                        if child.tag == "{urn:ebay:apis:eBLBaseComponents}PictureDetails":
                            nlist = child.findall("{urn:ebay:apis:eBLBaseComponents}PictureURL")
                            Picture = nlist[0].text

                        if child.tag == "{urn:ebay:apis:eBLBaseComponents}SellingStatus":
                            nlist = child.findall("{urn:ebay:apis:eBLBaseComponents}CurrentPrice")
                            Price =  nlist[0].text
                        
                        if child.tag == "{urn:ebay:apis:eBLBaseComponents}Listingstatus":
                            Listingstatus = child.text
                        if child.tag == "{urn:ebay:apis:eBLBaseComponents}HasUnansweredQuestions":
                            Questions = child.text
                    listdata += "<tr><td><img height='90px' width='90px' src='" + Picture + "' /></td><td>" + SKU + "</td><td>"
                    listdata += Title + "</td>"
                    listdata += "<td>" + Price + "</td><td>"
                    listdata += Amazon + "</td><td>" + eBay + "</td><td>"
                    listdata += Etsy + "</td></tr>"
                
                
                
                
                
                
                
                
            #listdict = XmlDictConfig(root)
            #listdata = ""
            """for node in root.iter():
                if node.tag.find("ItemID") > 0:
                    listdata = listdata + "\n#############################################################################\n"
                if node.text is not None:
                    #print node.tag, node.text
                    listdata = listdata + str(node.tag).replace("{urn:ebay:apis:eBLBaseComponents}", "") + ": " + str(node.text) + "\n"

                """
            #pp = pprint.PrettyPrinter(indent=1)
            #pp.pprint(listdict)
            #listdict = list(keypaths(listdict))
            
            #print str(getFromDict("listdict",["ItemArray","Item","AutoPay"]))
            #listdict = listdict['ItemArray']
            #pp.pprint(listdict)
            #print listdict["Ack"]
            print "GOT IT:---->\n" + listdata
            print "#################################################################"
            print "\n\n"
        if opts.prod:
            print "################ STARTING GET PRODUCT INFO ###############"
            Timestamp = ""
            Ack = ""
            Version = ""
            GetItem = ebay_new.GetItem(SessionObj.ItemID, kari)
            if opts.debug:
                print "DEBUG: " + str(opts.debug)

            listdata = str(GetItem.Get(opts))
            print str(listdata)
            o = xmltodict.parse(listdata)
            print(json.dumps(o))
            root = ET.ElementTree(ET.fromstring(listdata)).getroot()
            for node in root:
                if node.tag == "{urn:ebay:apis:eBLBaseComponents}Timestamp":
                    Timestamp = node.text
                if node.tag == "{urn:ebay:apis:eBLBaseComponents}Ack":
                    Ack = node.text
                if node.tag == "{urn:ebay:apis:eBLBaseComponents}Version":
                    Version = node.text
            for elem in root.iter('{urn:ebay:apis:eBLBaseComponents}PaginationResult'):
                for child in elem:
                    if child.tag == "{urn:ebay:apis:eBLBaseComponents}TotalNumberOfPages":
                        TotalNumberOfPages = child.text
                    if child.tag == "{urn:ebay:apis:eBLBaseComponents}TotalNumberOfEntries":
                        TotalNumberOfEntries = child.text
            print "\nTimestamp: " + Timestamp
            print "Ack: " + Ack
            print "Version: " + Version



            #print "GOT IT:---->\n" + listdata
            print "#################################################################"
            print "\n\n"
        if opts.revise:
            print "################ STARTING REVISE PRODUCT INFO ###############"
            Timestamp = ""
            Ack = ""
            Version = ""
            SessionObj.Token = kari
            SessionObj.RequestData = '''<?xml version="1.0" encoding="utf-8"?>
            <ReviseItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
              <RequesterCredentials>
                <eBayAuthToken>%(token)s</eBayAuthToken>
              </RequesterCredentials>
              <Item ComplexType="ItemType">
              <ItemID>%(itemid)s</ItemID>
              <Quantity>%(quantity)s</Quantity>
              </Item>
              <MessageID>1</MessageID>
              <WarningLevel>High</WarningLevel>
            </ReviseItemRequest>
            '''
            SessionObj.RequestData = SessionObj.RequestData % {'token': SessionObj.Token, 'itemid': SessionObj.ItemID, 'quantity': SessionObj.Quantity}
            ReviseItem = ebay_new.ReviseItem(SessionObj.RequestData)
            if opts.debug:
                print "DEBUG: " + str(SessionObj.debug)

            listdata = str(ReviseItem.Get(opts))
            print str(listdata) + "\n"
            o = xmltodict.parse(listdata)
            print(json.dumps(o))
            root = ET.ElementTree(ET.fromstring(listdata)).getroot()
            for node in root:
                if node.tag == "{urn:ebay:apis:eBLBaseComponents}Timestamp":
                    Timestamp = node.text
                if node.tag == "{urn:ebay:apis:eBLBaseComponents}Ack":
                    Ack = node.text
                if node.tag == "{urn:ebay:apis:eBLBaseComponents}Version":
                    Version = node.text
            for elem in root.iter('{urn:ebay:apis:eBLBaseComponents}PaginationResult'):
                for child in elem:
                    if child.tag == "{urn:ebay:apis:eBLBaseComponents}TotalNumberOfPages":
                        TotalNumberOfPages = child.text
                    if child.tag == "{urn:ebay:apis:eBLBaseComponents}TotalNumberOfEntries":
                        TotalNumberOfEntries = child.text
            print "\nTimestamp: " + Timestamp
            print "Ack: " + Ack
            print "Version: " + Version



            #print "GOT IT:---->\n" + listdata
            print "#################################################################"
            print "\n\n"
        if opts.session:
            print "###################### GET SESSION ID ############################"
            sessionID = ebay_new.GetSessionID()
            SessionObj.SessionID = str(sessionID.Get(opts))
            print "GOT IT:---->" + SessionObj.SessionID
            print "#################################################################"
            print "\n\n"
        if opts.time:
            print "################# STARTING GET EBAY OFFICAL TIME ################"
            eBayTime = ebay_new.eBayTime()
            print "GOT IT:---->" + eBayTime.Get(opts)
            print "#################################################################"
            print "\n\n"
        if opts.token:
            print "#################### STARTING GET TOKEN STATUS ##################"
            GetTokenStatus = ebay_new.GetTokenStatus(risa)
            SessionObj.TokenStatus = str(GetTokenStatus.Get(opts))
            print "GOT IT:---->" + SessionObj.TokenStatus
            print "#################################################################"
            print "\n\n"
        if opts.user:
            print "################## STARTING GET USER INFORMATION ################"
            GetUser = ebay_new.GetUser(risa, "cute_room")
            if opts.debug:
                print str(SessionObj.debug)
            print "GOT IT:---->" + GetUser.Get(opts)
            print "#################################################################"
            print "\n\n"
# Get a given data from a dictionary with position provided as a list
def getFromDict(dataDict, mapList):
    return reduce(lambda d, k: d[k], mapList, dataDict)

# Set a given data in a dictionary with position provided as a list
def setInDict(dataDict, mapList, value):
    getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value

def keypaths(nested):
    for key, value in nested.iteritems():
        if isinstance(value, collections.Mapping):
            for subkey, subvalue in keypaths(value):
                yield [key] + subkey, subvalue
        else:
            yield [key], value

class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if len(element):
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)

class XmlDictConfig(dict):
    '''
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    '''
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if len(element):  # is not None:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself 
                    aDict = {element[0].tag.replace("{urn:ebay:apis:eBLBaseComponents}", ""): XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag.replace("{urn:ebay:apis:eBLBaseComponents}", ""): aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a 
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag.replace("{urn:ebay:apis:eBLBaseComponents}", ""): dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag.replace("{urn:ebay:apis:eBLBaseComponents}", ""): element.text})


if __name__ == '__main__':
    (opts, args) = init_options()
    main(opts)