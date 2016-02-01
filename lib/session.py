# -*- coding: utf-8 -*-
##################################################
# session.py
# Python wrapper classes for Crossroads.
#  - Session
#
#
import yaml
import urlparse
import ConfigParser
##################################################
########## Session Class
##################################################
class Session(object):

    def Initialize(self, opts, FilePath, ServiceCall):
        if ServiceCall.lower() == "sandbox":
            self.ServerURL = "https://api.ebay.com/ws/api.dll"
            self.ServerType = "Sandbox"
        else:
            self.ServerURL = "https://sandbox.ebay.com/ws/api.dll"
            self.ServerType = "Production"

        urldat = urlparse.urlparse(self.ServerURL)
        self.Server = urldat[1]   # e.g., api.sandbox.ebay.com
        self.Command = urldat[2]  # e.g., /ws/api.dll

        self.Error = 0
        self.ErrorMessage = ""

        self.Token = ""
        self.TokenStatus = ""
        self.Session = ""
        self.SessionID = ""
        self.Start = ""
        self.End = ""
        self.Days = 120
        self.ItemID = ""
        self.Page = "0"
        self.PageNum = 1
        self.debug = "False"
        self.RequestData = ""


        try:
            config = ConfigParser.ConfigParser()
            with open(FilePath, 'r') as f:
                doc = yaml.load(f)

            if self.ServerType == "production":
                self.Developer = doc["api.ebay.com"]["devid"]
                self.Application = doc["api.ebay.com"]["appid"]
                self.Certificate = doc["api.ebay.com"]["certid"]
                self.Runame =  doc["api.ebay.com"]["Runame"]
            else:
                self.Developer = doc["api.sandbox.ebay.com"]["devid"]
                self.Application = doc["api.sandbox.ebay.com"]["appid"]
                self.Certificate = doc["api.sandbox.ebay.com"]["certid"]
                self.Runame =  doc["api.sandbox.ebay.com"]["Runame"]
        except IOError as (errno, strerror):
            self.Error = self.Error + 100
            self.ErrorMessage = "I/O error({0}): {1}".format(errno, strerror)
        except ValueError:
            self.ErrorMessage = "No valid integer in line."
        except:
            self.ErrorMessage = "Unexpected error:", sys.exc_info()[0]
        #finally:
            

