# -*- coding: utf-8 -*-
##################################################
# eBay_new.py
# Python wrapper classes for eBay API.
#  - Session
#
# API calls implemented by this module:
#  - eBayTime
#  - GetSessionID
#  - GetTokenStatus
#  - FecthToken
#  - GetUser
#  - GetSellerList
# - GetSellingManagerInventory
# - GetMyeBaySellingRequest



#  - GeteBayOfficialTime
#  - GetSearchResults
#  - GetCategories (heavy call only)
#  - AddItem
#  - GetSellerList (one page of 200 items max only)
#  - GetFinanceOffers (works in production, not in sandbox)
#  - ValidateTestUserRegistration
#  - GetFeedback
#  - GetToken (works in sandbox, not in production)
#  - ReviseItem
#  - GetItem
#
# Calls on the to-do list:
#  - GetCategory2FinanceOffer
#  - RelistItem, VerifyAddItem
#  - GetSellerEvents
#  - AddToItemDescription
#  - GetItemTransactions
#  - GetSellerTransactions
#  - GetHighBidders, GetBidderList
#  - GetCategoryListings
#  - AddSecondChanceItem, VerifySecondChanceItem
#  - GetAccount
#  - LeaveFeedback
#  - GetCategory2CS, GetAttributesCS, GetAttributesXSL
#  - GetProductSearchPage, GetProductFinder, GetProductFinderXSL
#  - GetProductSearchResults, GetProductFamilyMembers, GetProductSellingPages
##################################################
import linecache
import sys
import httplib, ConfigParser, urlparse
import xml.dom.minidom
from xml.dom.minidom import parse, parseString
from datetime import datetime
import yaml

##################################################
########## Session Class
##################################################
class Session:
    #print "INSIDE Session"
    ServerURL = "https://api.ebay.com/ws/api.dll"
    
    def Initialize(self):
        config = ConfigParser.ConfigParser()
        with open('ebay.yaml', 'r') as f:
            doc = yaml.load(f)

        Token = doc["api.ebay.com"]["devid"]
        ServerURL = "https://api.ebay.com/ws/api.dll"
        self.Developer = doc["api.ebay.com"]["devid"]
        self.Application = doc["api.ebay.com"]["appid"]
        self.Certificate = doc["api.ebay.com"]["certid"]
        self.Token = doc["api.ebay.com"]["token"]
        self.TokenStatus = ""
        self.Runame =  doc["api.ebay.com"]["Runame"]
        self.Session = ""
        self.Start = ""
        self.End = ""
        self.Page = ""
        self.debug = ""
        #self.SessionID = ""
        self.ServerURL = "https://api.ebay.com/ws/api.dll" #config.get("Server", "URL")
        urldat = urlparse.urlparse(self.ServerURL)
        self.Server = urldat[1]   # e.g., api.sandbox.ebay.com
        self.Command = urldat[2]  # e.g., /ws/api.dll


##################################################
########## GeteBayOfficialTime
##################################################
class eBayTime:
    #print "INSIDE eBayTime"
    Session = Session()
    
    def __init__(self):
        self.Session.Initialize()
    
    def Get(self, opts):   
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version='1.0' encoding='UTF-8'?><GeteBayOfficialTimeRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>%(token)s</eBayAuthToken>
  </RequesterCredentials></GeteBayOfficialTimeRequest>"""
        if opts.debug:
            api.Session.debug = "\nPARAMETERS\n1. "
            api.Session.debug += str(self.Session.Token) + "\n2. "
            api.Session.debug += str(self.Session.DetailLevel) + "\n"
            
        api.RequestData = api.RequestData % { 'token': self.Session.Token, 'detail': api.DetailLevel }
        if opts.debug:
            api.Session.debug += "\nREQUEST RESULTS\n"
            api.Session.debug += str(api.RequestData) + "\n"

        """
        OUTPUT/RETURN REPSONSE
        <GeteBayOfficialTimeResponse xmlns="urn:ebay:apis:eBLBaseComponents">
          <Timestamp>2009-10-05T19:27:40.754Z</Timestamp>
          <Ack>Success</Ack>
          <Version>635</Version>
          <Build>E635_CORE_BUNDLED_10123275_R1</Build>
        </GeteBayOfficialTimeResponse>"""
        
        responseDOM = api.MakeCall("GeteBayOfficialTime", opts.debug)
        if opts.debug:
            api.Session.debug +=  "\n\nRETURN RESULTS\n"
            api.Session.debug +=  str(responseDOM) + "\n"
            print api.Session.debug
            
        # check for the <Timestamp> tag and return results
        if str(responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data) == "Success":
            timeElement = responseDOM.getElementsByTagName('Timestamp')
            if (timeElement != []):
                return timeElement[0].childNodes[0].data
            else:
                 return "-1"
        else:
            return "-1"
        # force garbage collection of the DOM object
        responseDOM.unlink()


##################################################
########## SessionID retrieval
##################################################
class GetSessionID:
    """ Retrieves a SessionId for a supplied user.
    """
    #print "INSIDE GetSessionID"
    Session = Session()
    
    def __init__(self):
        self.Session.Initialize()
        
    def Get(self, opts):
        api = Call()
        api.Session = self.Session
        api.DetailLevel = "128"
        api.RequestData = """<?xml version='1.0' encoding='utf-8'?><GetSessionIDRequest xmlns='urn:ebay:apis:eBLBaseComponents'><RuName>%(user)s</RuName></GetSessionIDRequest>"""
        if opts.debug:
            api.Session.debug = "\nGETSESSIONID PARAMETERS\n1. "
            api.Session.debug += str(self.Session.Runame) + "\n"

        api.RequestData = api.RequestData % { 'user': self.Session.Runame}
        if opts.debug:
            api.Session.debug += "\nGETSESSIONID REQUEST RESULTS\n"
            api.Session.debug += str(api.RequestData) + "\n"
        
        
        self.Xml = api.MakeCall("GetSessionID", opts.debug)
        if opts.debug:
            api.Session.debug +=  "\n\nGETSESSIONID RETURN RESULTS\n"
            api.Session.debug +=  str(self.Xml.getElementsByTagName('SessionID')[0].childNodes[0].data) + "\n"
            print api.Session.debug

        """
        RETURN STRUCTURE
        <?xml version="1.0" encoding="UTF-8"?>
        <GetSessionIDResponse xmlns="urn:ebay:apis:eBLBaseComponents">
          <Timestamp>2010-11-10T01:31:34.148Z</Timestamp>
          <Ack>Success</Ack>
          <Version>693</Version>
          <Build>E693_CORE_BUNDLED_12301500_R1</Build>
          <SessionID>MySessionID</SessionID>
        </GetSessionIDResponse>
        """

        #self.SessionID = self.Xml.getElementsByTagName('SessionID')[0].childNodes[0].data
        return str(self.Xml.getElementsByTagName('SessionID')[0].childNodes[0].data)
        
    def Save(self, filename):
        # TODO: If Xml property is blank then it's an exception
        if self.Xml != "":
            f = open(filename, 'w')
            s = self.SessionID
            f.write(s)
            f.close()


##################################################
########## Fetch Token retrieval
##################################################
class FetchToken(object):
    """ Fetches a token when a conventional token is available.
    """
    #print "INSIDE FETCH TOKEN"
    Session = Session()

    def __init__(self, SessionID):
        self.Session.Initialize()
        #print "INSIDE FETCH TOKEN INIT"
        self.Token = ""
        self.SessionID = SessionID

    def Get(self, opts):
        print "INSIDE FETCH TOKEN GET"
        api = Call()
        api.Session = self.Session
        api.DetailLevel = "128"
        api.RequestData = '''<?xml version='1.0' encoding='UTF-8'?><FetchTokenRequest xmlns='urn:ebay:apis:eBLBaseComponents'><Version>613</Version><RequesterCredentials><DevId>%(devid)s</DevId><AppId>%(appid)s</AppId><AuthCert>%(cert)s</AuthCert></RequesterCredentials><SessionID>%(sessionid)s</SessionID></FetchTokenRequest>'''
        if opts.debug:
            api.Session.debug += "\nFETCHTOKEN PARAMETERS\n"
            api.Session.debug += str(self.SessionID) + "\n"
            api.Session.debug += "devid: " + str(self.Session.Developer) + "\n"
            api.Session.debug += "appid: " + str(self.Session.Application) + "\n"
            api.Session.debug += "cert: " + str(self.Session.Certificate) + "\n"
            api.Session.debug += "sessionid: " + str(self.SessionID) + "\n"

        api.RequestData = api.RequestData % { 'devid': self.Session.Developer, 'appid': self.Session.Application, 'cert': self.Session.Certificate, 'sessionid': self.SessionID}
        if opts.debug:
            api.Session.debug += "\nFETCHTOKEN REQUEST RESULTS\n"
            api.Session.debug += str(api.RequestData) + "\n"

        self.Xml = api.MakeCall("FetchToken", opts.debug)
        if opts.debug:
            api.Session.debug +=  "\n\nFETCHTOKEN RETURN RESULTS\n"
            api.Session.debug +=  str(self.Xml.toprettyxml()) + "\n"
            print api.Session.debug
        """
        OUTPUT XML
        <?xml version='1.0' encoding='utf-8'?>
        <FetchTokenResponse xmlns='urn:ebay:apis:eBLBaseComponents'>
          <!-- Call-specific Output Fields -->
          <eBayAuthToken> string </eBayAuthToken>
          <HardExpirationTime> dateTime </HardExpirationTime>
          <RESTToken> string </RESTToken>
          <!-- Standard Output Fields -->
          <Ack> AckCodeType </Ack>
          <Build> string </Build>
          <CorrelationID> string </CorrelationID>
          <Errors> ErrorType
            <ErrorClassification> ErrorClassificationCodeType </ErrorClassification>
            <ErrorCode> token </ErrorCode>
            <ErrorParameters ParamID='string'> ErrorParameterType
              <Value> string </Value>
            </ErrorParameters>
            <!-- ... more ErrorParameters nodes allowed here ... -->
            <LongMessage> string </LongMessage>
            <SeverityCode> SeverityCodeType </SeverityCode>
            <ShortMessage> string </ShortMessage>
          </Errors>
          <!-- ... more Errors nodes allowed here ... -->
          <Timestamp> dateTime </Timestamp>
          <Version> string </Version>
        </FetchTokenResponse>
        """
        if self.Xml.getElementsByTagName('Ack')[0].childNodes[0].data != "Success" :
            self.Token = -1
        else:
            self.Token = self.Xml.getElementsByTagName('eBayAuthToken')[0].childNodes[0].data

        return self.Token

    def Save(self, filename):
        # TODO: If Xml property is blank then it's an exception
        if self.Xml != "":
            f = open(filename, 'w')
            s = self.Token
            f.write(s)
            f.close()


##################################################
########## Fetch Token Buy Userretrieval
##################################################
class FetchTokenByUser(object):
    """ Fetches a token when a conventional token is available.
    """
    #print "INSIDE FETCH TOKEN"
    Session = Session()

    def __init__(self, SessionID):
        self.Session.Initialize()
        #print "INSIDE FETCH TOKEN BY USER INIT"
        self.Token = ""
        self.SessionID = SessionID

    def Get(self, opts):
        print "INSIDE FETCH TOKEN BY USER GET"
        api = Call()
        api.Session = self.Session
        api.DetailLevel = "128"
        api.RequestData = '''<?xml version='1.0' encoding='UTF-8'?><FetchTokenRequest xmlns='urn:ebay:apis:eBLBaseComponents'>
  <Version>613</Version>
   <RequesterCredentials>
     <DevId>%(devid)s</DevId>
     <AppId>%(appid)s</AppId>
     <AuthCert>%(cert)s</AuthCert>
   </RequesterCredentials>
   <SessionID>%(sessionid)s</SessionID></FetchTokenRequest>'''
        if opts.debug:
            api.Session.debug += "\nFETCHTOKEN BY USER PARAMETERS\n"
            api.Session.debug += str(self.SessionID) + "\n"
            api.Session.debug += "devid: " + str(self.Session.Developer) + "\n"
            api.Session.debug += "appid: " + str(self.Session.Application) + "\n"
            api.Session.debug += "cert: " + str(self.Session.Certificate) + "\n"
            api.Session.debug += "sessionid: " + str(self.SessionID) + "\n"

        api.RequestData = api.RequestData % { 'devid': self.Session.Developer, 'appid': self.Session.Application, 'cert': self.Session.Certificate, 'sessionid': self.SessionID}
        if opts.debug:
            api.Session.debug += "\nFETCHTOKEN BY USER REQUEST RESULTS\n"
            api.Session.debug += str(api.RequestData) + "\n"

        self.Xml = api.MakeCall("FetchToken", opts.debug)
        if opts.debug:
            api.Session.debug +=  "\n\nFETCHTOKEN BY USER RETURN RESULTS\n"
            api.Session.debug +=  str(self.Xml.toprettyxml()) + "\n"
            print api.Session.debug
        """
        OUTPUT XML
        <?xml version='1.0' encoding='utf-8'?>
        <FetchTokenResponse xmlns='urn:ebay:apis:eBLBaseComponents'>
          <!-- Call-specific Output Fields -->
          <eBayAuthToken> string </eBayAuthToken>
          <HardExpirationTime> dateTime </HardExpirationTime>
          <RESTToken> string </RESTToken>
          <!-- Standard Output Fields -->
          <Ack> AckCodeType </Ack>
          <Build> string </Build>
          <CorrelationID> string </CorrelationID>
          <Errors> ErrorType
            <ErrorClassification> ErrorClassificationCodeType </ErrorClassification>
            <ErrorCode> token </ErrorCode>
            <ErrorParameters ParamID='string'> ErrorParameterType
              <Value> string </Value>
            </ErrorParameters>
            <!-- ... more ErrorParameters nodes allowed here ... -->
            <LongMessage> string </LongMessage>
            <SeverityCode> SeverityCodeType </SeverityCode>
            <ShortMessage> string </ShortMessage>
          </Errors>
          <!-- ... more Errors nodes allowed here ... -->
          <Timestamp> dateTime </Timestamp>
          <Version> string </Version>
        </FetchTokenResponse>
        """
        if self.Xml.getElementsByTagName('Ack')[0].childNodes[0].data != "Success" :
            self.Token = -1
        else:
            self.Token = self.Xml.getElementsByTagName('eBayAuthToken')[0].childNodes[0].data

        return self.Token

    def Save(self, filename):
        # TODO: If Xml property is blank then it's an exception
        if self.Xml != "":
            f = open(filename, 'w')
            s = self.Token
            f.write(s)
            f.close()


##################################################
########## Get Token Status
##################################################
class GetTokenStatus:
    """ Checks a given token's status.
    """
    Session = Session()

    def __init__(self, Token):
        self.Session.Initialize()
        self.Session.Token = Token

    def Get(self, opts):
        api = Call()
        api.Session = self.Session
        api.DetailLevel = "128"
        api.RequestData = '''<?xml version="1.0" encoding="utf-8"?><GetTokenStatusRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>%(token)s</eBayAuthToken>
  </RequesterCredentials></GetTokenStatusRequest>'''
        if opts.debug:
            api.Session.debug += "\nPARAMETERS\n1. "
            api.Session.debug += str(self.Session.Token) + "\n"
            
        api.RequestData = api.RequestData % { 'token': self.Session.Token}
        if opts.debug:
            api.Session.debug += "\nREQUEST RESULTS\n"
            api.Session.debug += str(api.RequestData) + "\n"
            
        self.Xml = api.MakeCall("GetTokenStatus", opts.debug)
        if opts.debug:
            api.Session.debug +=  "\n\nRETURN RESULTS\n"
            api.Session.debug +=  str(self.Xml.getElementsByTagName('Status')[0].childNodes[0].data) + "\n"
            print api.Session.debug
        """
        OUTPUT XML
        <?xml version="1.0" encoding="utf-8"?>
        <GetTokenStatusResponse xmlns="urn:ebay:apis:eBLBaseComponents">
          <!-- Call-specific Output Fields -->
          <TokenStatus> TokenStatusType
            <EIASToken> string </EIASToken>
            <ExpirationTime> dateTime </ExpirationTime>
            <RevocationTime> dateTime </RevocationTime>
            <Status> TokenStatusCodeType </Status>
          </TokenStatus>
          <!-- Standard Output Fields -->
          <Ack> AckCodeType </Ack>
          <Build> string </Build>
          <CorrelationID> string </CorrelationID>
          <Errors> ErrorType
            <ErrorClassification> ErrorClassificationCodeType </ErrorClassification>
            <ErrorCode> token </ErrorCode>
            <ErrorParameters ParamID="string"> ErrorParameterType
              <Value> string </Value>
            </ErrorParameters>
            <!-- ... more ErrorParameters nodes allowed here ... -->
            <LongMessage> string </LongMessage>
            <SeverityCode> SeverityCodeType </SeverityCode>
            <ShortMessage> string </ShortMessage>
          </Errors>
          <!-- ... more Errors nodes allowed here ... -->
          <HardExpirationWarning> string </HardExpirationWarning>
          <Timestamp> dateTime </Timestamp>
          <Version> string </Version>
        </GetTokenStatusResponse>
        """

        #self.TokenStatus = self.Xml.getElementsByTagName('Status')[0].childNodes[0].data
        return str(self.Xml.getElementsByTagName('Status')[0].childNodes[0].data)
    def Save(self, filename):
        # TODO: If Xml property is blank then it's an exception
        if self.Xml != "":
            f = open(filename, 'w')
            s = self.Token
            f.write(s)
            f.close()


##################################################
########## Get User
##################################################
class GetUser:
    """ Checks a given User's information.
    """
    Session = Session()

    def __init__(self, Token, User):
        self.Session.Initialize()
        self.Session.Token = Token
        self.Session.User = User

    def Get(self, opts):
        api = Call()
        api.Session = self.Session
        api.DetailLevel = "128"
        api.RequestData = '''<?xml version="1.0" encoding="utf-8"?> <GetUserRequest xmlns="urn:ebay:apis:eBLBaseComponents"> 
  <RequesterCredentials> 
    <eBayAuthToken>%(token)s</eBayAuthToken> 
  </RequesterCredentials> 
  <UserID>%(user)s</UserID></GetUserRequest> '''
        if opts.debug:
            api.Session.debug += "\nPARAMETERS\n1. "
            api.Session.debug += str(self.Session.Token) + "\n2. "
            api.Session.debug += str(self.Session.User) + "\n"
            
        api.RequestData = api.RequestData % { 'token': self.Session.Token, 'user': self.Session.User}
        if opts.debug:
            api.Session.debug += "\nREQUEST RESULTS\n"
            api.Session.debug += str(api.RequestData) + "\n"

        responseDOM = api.MakeCall("GetUser", opts.debug)

        """
        OUTPUT
        <?xml version="1.0" encoding="utf-8"?>
        <GetUserResponse xmlns="urn:ebay:apis:eBLBaseComponents">
          <!-- Call-specific Output Fields -->
          <User> UserType
            <AboutMePage> boolean </AboutMePage>
            <BillingEmail> string </BillingEmail>
            <BusinessRole> BusinessRoleType </BusinessRole>
            <eBayGoodStanding> boolean </eBayGoodStanding>
            <eBayWikiReadOnly> boolean </eBayWikiReadOnly>
            <EIASToken> string </EIASToken>
            <Email> string </Email>
            <EnterpriseSeller> boolean </EnterpriseSeller>
            <FeedbackPrivate> boolean </FeedbackPrivate>
            <FeedbackRatingStar> FeedbackRatingStarCodeType </FeedbackRatingStar>
            <FeedbackScore> int </FeedbackScore>
            <IDVerified> boolean </IDVerified>
            <MotorsDealer> boolean </MotorsDealer>
            <NewUser> boolean </NewUser>
            <PayPalAccountLevel> PayPalAccountLevelCodeType </PayPalAccountLevel>
            <PayPalAccountStatus> PayPalAccountStatusCodeType </PayPalAccountStatus>
            <PayPalAccountType> PayPalAccountTypeCodeType </PayPalAccountType>
            <PositiveFeedbackPercent> float </PositiveFeedbackPercent>
            <QualifiesForSelling> boolean </QualifiesForSelling>
            <RegistrationAddress> AddressType
              <CityName> string </CityName>
              <CompanyName> string </CompanyName>
              <Country> CountryCodeType </Country>
              <CountryName> string </CountryName>
              <Name> string </Name>
              <Phone> string </Phone>
              <PostalCode> string </PostalCode>
              <StateOrProvince> string </StateOrProvince>
              <Street> string </Street>
              <Street1> string </Street1>
              <Street2> string </Street2>
            </RegistrationAddress>
            <RegistrationDate> dateTime </RegistrationDate>
            <SellerInfo> SellerType
              <AllowPaymentEdit> boolean </AllowPaymentEdit>
              <CharityAffiliationDetails> CharityAffiliationDetailsType
                <CharityAffiliationDetail> CharityAffiliationDetailType
                  <AffiliationType> CharityAffiliationTypeCodeType </AffiliationType>
                  <CharityID> string </CharityID>
                  <LastUsedTime> dateTime </LastUsedTime>
                </CharityAffiliationDetail>
                <!-- ... more CharityAffiliationDetail nodes allowed here ... -->
              </CharityAffiliationDetails>
              <CharityRegistered> boolean </CharityRegistered>
              <CheckoutEnabled> boolean </CheckoutEnabled>
              <CIPBankAccountStored> boolean </CIPBankAccountStored>
              <DomesticRateTable> boolean </DomesticRateTable>
              <FeatureEligibility> FeatureEligibilityType
                <QualifiedForAuctionOneDayDuration> boolean </QualifiedForAuctionOneDayDuration>
                <QualifiedForFixedPriceOneDayDuration> boolean </QualifiedForFixedPriceOneDayDuration>
                <QualifiesForBuyItNow> boolean </QualifiesForBuyItNow>
                <QualifiesForBuyItNowMultiple> boolean </QualifiesForBuyItNowMultiple>
                <QualifiesForVariations> boolean </QualifiesForVariations>
              </FeatureEligibility>
              <GoodStanding> boolean </GoodStanding>
              <IntegratedMerchantCreditCardInfo> IntegratedMerchantCreditCardInfoType
                <SupportedSite> SiteCodeType </SupportedSite>
                <!-- ... more SupportedSite values allowed here ... -->
              </IntegratedMerchantCreditCardInfo>
              <InternationalRateTable> boolean </InternationalRateTable>
              <MerchandizingPref> MerchandizingPrefCodeType (token) </MerchandizingPref>
              <PaisaPayEscrowEMIStatus> int </PaisaPayEscrowEMIStatus>
              <PaisaPayStatus> int </PaisaPayStatus>
              <PaymentMethod> SellerPaymentMethodCodeType </PaymentMethod>
              <ProStoresPreference> ProStoresCheckoutPreferenceType </ProStoresPreference>
              <QualifiesForB2BVAT> boolean </QualifiesForB2BVAT>
              <RecoupmentPolicyConsent> RecoupmentPolicyConsentType
                <Site> SiteCodeType </Site>
                <!-- ... more Site values allowed here ... -->
              </RecoupmentPolicyConsent>
              <RegisteredBusinessSeller> boolean </RegisteredBusinessSeller>
              <SafePaymentExempt> boolean </SafePaymentExempt>
              <SchedulingInfo> SchedulingInfoType
                <MaxScheduledItems> int </MaxScheduledItems>
                <MaxScheduledMinutes> int </MaxScheduledMinutes>
                <MinScheduledMinutes> int </MinScheduledMinutes>
              </SchedulingInfo>
              <SellerBusinessType> SellerBusinessCodeType </SellerBusinessType>
              <SellerLevel> SellerLevelCodeType </SellerLevel>
              <SellerPaymentAddress> AddressType
                <CityName> string </CityName>
                <Country> CountryCodeType </Country>
                <CountryName> string </CountryName>
                <InternationalName> string </InternationalName>
                <InternationalStateAndCity> string </InternationalStateAndCity>
                <InternationalStreet> string </InternationalStreet>
                <Name> string </Name>
                <Phone> string </Phone>
                <PostalCode> string </PostalCode>
                <StateOrProvince> string </StateOrProvince>
                <Street1> string </Street1>
                <Street2> string </Street2>
              </SellerPaymentAddress>
              <StoreOwner> boolean </StoreOwner>
              <StoreSite> SiteCodeType </StoreSite>
              <StoreURL> anyURI </StoreURL>
              <TopRatedSeller> boolean </TopRatedSeller>
              <TopRatedSellerDetails> TopRatedSellerDetailsType
                <TopRatedProgram> TopRatedProgramCodeType </TopRatedProgram>
                <!-- ... more TopRatedProgram values allowed here ... -->
              </TopRatedSellerDetails>
              <TransactionPercent> float </TransactionPercent>
            </SellerInfo>
            <Site> SiteCodeType </Site>
            <SkypeID> string </SkypeID>
            <!-- ... more SkypeID values allowed here ... -->
            <Status> UserStatusCodeType </Status>
            <TUVLevel> int </TUVLevel>
            <UniqueNegativeFeedbackCount> int </UniqueNegativeFeedbackCount>
            <UniqueNeutralFeedbackCount> int </UniqueNeutralFeedbackCount>
            <UniquePositiveFeedbackCount> int </UniquePositiveFeedbackCount>
            <UserID> UserIDType (string) </UserID>
            <UserIDChanged> boolean </UserIDChanged>
            <UserIDLastChanged> dateTime </UserIDLastChanged>
            <UserSubscription> EBaySubscriptionTypeCodeType </UserSubscription>
            <!-- ... more UserSubscription values allowed here ... -->
            <VATID> string </VATID>
            <VATStatus> VATStatusCodeType </VATStatus>
          </User>
          <!-- Standard Output Fields -->
          <Ack> AckCodeType </Ack>
          <Build> string </Build>
          <CorrelationID> string </CorrelationID>
          <Errors> ErrorType
            <ErrorClassification> ErrorClassificationCodeType </ErrorClassification>
            <ErrorCode> token </ErrorCode>
            <ErrorParameters ParamID="string"> ErrorParameterType
              <Value> string </Value>
            </ErrorParameters>
            <!-- ... more ErrorParameters nodes allowed here ... -->
            <LongMessage> string </LongMessage>
            <SeverityCode> SeverityCodeType </SeverityCode>
            <ShortMessage> string </ShortMessage>
          </Errors>
          <!-- ... more Errors nodes allowed here ... -->
          <HardExpirationWarning> string </HardExpirationWarning>
          <Timestamp> dateTime </Timestamp>
          <Version> string </Version>
        </GetUserResponse>"""

        if opts.debug:
            api.Session.debug +=  "\n\nRETURN RESULTS\n"
            api.Session.debug +=  str(responseDOM.toxml()) + "\n"
            print api.Session.debug

        if str(responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data) == "Success":
            #userData = responseDOM.getElementsByTagName('User')
            userRaw = parseString(responseDOM.toxml()) #responseDOM.childNodes
            userData = userRaw.getElementsByTagName('User')[0].toxml()
            return userData
        else:
            return "<User></User>"

    def Save(self, filename):
        # TODO: If Xml property is blank then it's an exception
        if self.Xml != "":
            f = open(filename, 'w')
            s = self.Token
            f.write(s)
            f.close()


##################################################
########## Get Seller List
##################################################
class GetSellerList:
    """ Checks a given User's information.
    """
    Session = Session()

    def __init__(self, Token, Start, End, Page):
        self.Session.Initialize()
        self.Session.Token = Token
        self.Session.Start = Start
        self.Session.End = End
        self.Session.Page = Page

    def Get(self, opts):
        api = Call()
        api.Session = self.Session
        api.DetailLevel = "128"
        api.RequestData = '''<?xml version="1.0" encoding="utf-8"?>
 <GetSellerListRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>%(token)s</eBayAuthToken>
  </RequesterCredentials>
  <ErrorLanguage>en_US</ErrorLanguage>
  <WarningLevel>High</WarningLevel>
  <GranularityLevel>Fine</GranularityLevel> 
  <StartTimeFrom>%(startdate)s</StartTimeFrom> 
  <StartTimeTo>%(enddate)s</StartTimeTo> 
  <EndTimeFrom>%(startdate)s</EndTimeFrom> 
  <EndTimeTo>%(enddate)s</EndTimeTo> 
  <IncludeWatchCount>false</IncludeWatchCount> 
  <Pagination> 
    <EntriesPerPage>%(page)s</EntriesPerPage> 
  </Pagination> 
 </GetSellerListRequest>'''
        """2010-02-12T21:59:59.005Z   2010-02-26T21:59:59.005Z """
        if opts.debug:
            api.Session.debug += "\nPARAMETERS\n1. "
            api.Session.debug += str(self.Session.Token) + "\n2. "
            api.Session.debug += str(self.Session.Start) + "\n3. "
            api.Session.debug += str(self.Session.End) + "\n4. "
            api.Session.debug += str(self.Session.Page) + "\n"
            
        api.RequestData = api.RequestData % { 'token': self.Session.Token, 'startdate': self.Session.Start, 'enddate': self.Session.End, 'page': self.Session.Page}

        if opts.debug:
            api.Session.debug += "\nREQUEST RESULTS"
            api.Session.debug += str(api.RequestData)

        responseDOM = api.MakeCall("GetSellerList", opts.debug)

        """OUTPUT
        <GetSellerListResponse xmlns="urn:ebay:apis:eBLBaseComponents">
          <Timestamp>2010-02-26T22:02:38.968Z</Timestamp>
          <Ack>Success</Ack>
          <Version>657</Version>
          <Build>E657_CORE_BUNDLED_10708779_R1</Build>
          <PaginationResult>
            <TotalNumberOfPages>14</TotalNumberOfPages>
            <TotalNumberOfEntries>27</TotalNumberOfEntries>
          </PaginationResult>
          <HasMoreItems>true</HasMoreItems>
          <ItemArray>
            <Item>
              <AutoPay>false</AutoPay>
              <BuyerProtection>ItemIneligible</BuyerProtection>
              <Country>US</Country>
              <Currency>USD</Currency>
              <GiftIcon>0</GiftIcon>
              <HitCounter>NoHitCounter</HitCounter>
              <ItemID>110043597553</ItemID>
              <ListingDetails>
                <StartTime>2010-02-12T23:35:27.000Z</StartTime>
                <EndTime>2010-02-19T23:35:27.000Z</EndTime>
                <ViewItemURL>http://cgi.sandbox.ebay.com/ws/eBayISAPI.dll?ViewItem&
                   item=110043597553&category=41393</ViewItemURL>
                <HasUnansweredQuestions>false</HasUnansweredQuestions>
                <HasPublicMessages>false</HasPublicMessages>
                <BuyItNowAvailable>true</BuyItNowAvailable>
                <ExpressListing>false</ExpressListing>
              </ListingDetails>
              <ListingDuration>Days_7</ListingDuration>
              <Location>Santa Cruz, California</Location>
              <PrimaryCategory>
                <CategoryID>41393</CategoryID>
                <CategoryName>Collectibles:Decorative Collectibles:Other</CategoryName>
              </PrimaryCategory>
              <Quantity>1</Quantity>
              <ReviseStatus>
                <ItemRevised>false</ItemRevised>
              </ReviseStatus>
              <SecondaryCategory>
                <CategoryID>95116</CategoryID>
                <CategoryName>Collectibles:Disneyana:Contemporary (1968-Now):Bobblehead Figures</CategoryName>
              </SecondaryCategory>
              <SellingStatus>
                <BidCount>0</BidCount>
                <BidIncrement currencyID="USD">0.5</BidIncrement>
                <ConvertedCurrentPrice currencyID="USD">11.49</ConvertedCurrentPrice>
                <CurrentPrice currencyID="USD">11.49</CurrentPrice>
                <MinimumToBid currencyID="USD">11.49</MinimumToBid>
                <QuantitySold>0</QuantitySold>
                <SecondChanceEligible>false</SecondChanceEligible>
                <ListingStatus>Completed</ListingStatus>
              </SellingStatus>
              <ShippingDetails>
                <TaxTable/>
              </ShippingDetails>
              <ShipToLocations>US</ShipToLocations>
              <Site>US</Site>
              <Storefront>
                <StoreCategoryID>1</StoreCategoryID>
                <StoreCategory2ID>0</StoreCategory2ID>
                <StoreURL>http://www.stores.sandbox.ebay.com/id=132854966</StoreURL>
              </Storefront>
              <SubTitle>Micky, with the ears!</SubTitle>
              <TimeLeft>PT0S</TimeLeft>
              <Title>Kelly's Kitsch</Title>
              <WatchCount>0</WatchCount>
              <LocationDefaulted>true</LocationDefaulted>
              <PostalCode>95062</PostalCode>
              <PictureDetails>
                <GalleryURL>http://thumbs.ebaystatic.com/pict/41007087008080_0.jpg</GalleryURL>
                <PhotoDisplay>None</PhotoDisplay>
                <PictureURL>http://thumbs.ebaystatic.com/pict/41007087008080_0.jpg</PictureURL>
              </PictureDetails>
              <ProxyItem>false</ProxyItem>
              <BuyerGuaranteePrice currencyID="USD">20000.0</BuyerGuaranteePrice>
              <ReturnPolicy>
                <RefundOption>MoneyBack</RefundOption>
                <Refund>Money Back</Refund>
                <ReturnsWithinOption>Days_30</ReturnsWithinOption>
                <ReturnsWithin>30 Days</ReturnsWithin>
                <ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>
                <ReturnsAccepted>Returns Accepted</ReturnsAccepted>
                <Description>Returns accepted only if item is not as described.</Description>
                <ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption>
                <ShippingCostPaidBy>Buyer</ShippingCostPaidBy>
              </ReturnPolicy>
              <PaymentAllowedSite>US</PaymentAllowedSite>
            </Item>
            ...
          <ItemsPerPage>2</ItemsPerPage>
          <PageNumber>1</PageNumber>
          <ReturnedItemCountActual>2</ReturnedItemCountActual>
        </GetSellerListResponse>"""
        
        if opts.debug:
            api.Session.debug +=  "\n\nRETURN RESULTS\n"
            api.Session.debug +=  str(responseDOM.toxml()) + "\n"
            print api.Session.debug

        if str(responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data) == "Success":
            #userData = responseDOM.getElementsByTagName('User')
            #userRaw = parseString(responseDOM.toxml()) #responseDOM.childNodes
            #userData = userRaw.getElementsByTagName('User')[0].toxml()
            return str(responseDOM.toxml())
        else:
            return "<GetSellerListResponse></GetSellerListResponse>"

        
    def Save(self, filename):
        # TODO: If Xml property is blank then it's an exception
        if self.Xml != "":
            f = open(filename, 'w')
            s = self.Token
            f.write(s)
            f.close()


##################################################
########## Get Seller List
##################################################
class GetSellingManagerInventory:
    """ Checks a given User's information.
    """
    Session = Session()

    def __init__(self, Token, Page, PageNum):
        self.Session.Initialize()
        self.Session.Token = Token
        self.Session.Page = Page
        self.Session.PageNum = PageNum
    def Get(self, opts):
        api = Call()
        api.Session = self.Session
        api.RequestData = '''<?xml version="1.0" encoding="utf-8"?>
 <GetSellingManagerInventoryRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>%(token)s</eBayAuthToken>
  </RequesterCredentials>
  <Version>613</Version>
  <Pagination>
    <EntriesPerPage>%(page)s</EntriesPerPage>
    <PageNumber>%(pagenum)s</PageNumber>
  </Pagination>
 </GetSellingManagerInventoryRequest>'''
        """2010-02-12T21:59:59.005Z   2010-02-26T21:59:59.005Z """
        if opts.debug:
            api.Session.debug += "\nPARAMETERS\n1. "
            api.Session.debug += str(self.Session.Token) + "\n"
            
        api.RequestData = api.RequestData % { 'token': self.Session.Token, 'page': self.Session.Page, 'pagenum': self.Session.PageNum}

        if opts.debug:
            api.Session.debug += "\nREQUEST RESULTS"
            api.Session.debug += str(api.RequestData)

        responseDOM = api.MakeCall("GetSellingManagerInventory", opts.debug)

        """OUTPUT
 <?xml version="1.0" encoding="utf-8"?>
 <GetSellingManagerInventoryResponse xmlns="urn:ebay:apis:eBLBaseComponents">
  <Timestamp>2009-03-20T19:32:30.229Z</Timestamp>
  <Ack>Success</Ack>
  <Version>609</Version>
  <Build>e609_core_Bundled_8177180_R1</Build>
  <InventoryCountLastCalculatedDate>2009-03-06T12:32:26.000Z</InventoryCountLastCalculatedDate>
  <SellingManagerProduct>
    <SellingManagerProductDetails>
      <ProductName>Final Product</ProductName>
      <ProductID>432576</ProductID>
      <CustomLabel>4646455</CustomLabel>
      <QuantityAvailable>100</QuantityAvailable>
      <UnitCost currencyID="USD">10.0</UnitCost>
      <FolderID>32499</FolderID>
    </SellingManagerProductDetails>
    <SellingManagerTemplateDetailsArray>
      <SellingManagerTemplateDetails>
        <SaleTemplateID>95121</SaleTemplateID>
      </SellingManagerTemplateDetails>
    </SellingManagerTemplateDetailsArray>
    <SellingManagerProductInventoryStatus>
      <QuantityScheduled>0</QuantityScheduled>
      <QuantityActive>0</QuantityActive>
      <QuantitySold>0</QuantitySold>
      <QuantityUnsold>0</QuantityUnsold>
    </SellingManagerProductInventoryStatus>
  </SellingManagerProduct>
  <SellingManagerProduct>
    <SellingManagerProductDetails>
      <ProductName>EPS Product</ProductName>
      <ProductID>581292</ProductID>
      <QuantityAvailable>10</QuantityAvailable>
      <UnitCost currencyID="USD">1.99</UnitCost>
      <FolderID>37699</FolderID>
    </SellingManagerProductDetails>
    <SellingManagerTemplateDetailsArray>
      <SellingManagerTemplateDetails>
        <SaleTemplateID>110857</SaleTemplateID>
      </SellingManagerTemplateDetails>
    </SellingManagerTemplateDetailsArray>
    <SellingManagerProductInventoryStatus>
      <QuantityScheduled>0</QuantityScheduled>
      <QuantityActive>0</QuantityActive>
      <QuantitySold>0</QuantitySold>
      <QuantityUnsold>0</QuantityUnsold>
    </SellingManagerProductInventoryStatus>
  </SellingManagerProduct>
 ...
  <PaginationResult>
    <TotalNumberOfPages>572</TotalNumberOfPages>
    <TotalNumberOfEntries>28586</TotalNumberOfEntries>
  </PaginationResult>
 </GetSellingManagerInventoryResponse>"""
        
        if opts.debug:
            api.Session.debug +=  "\n\nRETURN RESULTS\n"
            api.Session.debug +=  str(responseDOM.toxml()) + "\n"
            print api.Session.debug

        if str(responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data) == "Success":
            #userData = responseDOM.getElementsByTagName('User')
            #userRaw = parseString(responseDOM.toxml()) #responseDOM.childNodes
            #userData = userRaw.getElementsByTagName('User')[0].toxml()
            return str(responseDOM.toxml())
        else:
            return "<GetSellingManagerInventoryResponse></GetSellingManagerInventoryResponse>"

        
    def Save(self, filename):
        # TODO: If Xml property is blank then it's an exception
        if self.Xml != "":
            f = open(filename, 'w')
            s = self.Token
            f.write(s)
            f.close()


##################################################
########## Get Seller List
##################################################
class GetMyeBaySelling:
    """ Checks a given User's information.
    """
    Session = Session()

    def __init__(self, Token, Page, PageNum):
        self.Session.Initialize()
        self.Session.Token = Token
        self.Session.Page = Page
        self.Session.PageNum = PageNum
    def Get(self, opts):
        api = Call()
        api.Session = self.Session
        api.RequestData = '''<?xml version="1.0" encoding="utf-8"?>
 <GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>%(token)s</eBayAuthToken>
  </RequesterCredentials>
  <Version>613</Version>
  <ActiveList>
    <Include>true</Include>
    <Sort>TimeLeft</Sort>
    <Pagination>
    <EntriesPerPage>%(page)s</EntriesPerPage>
    <PageNumber>%(pagenum)s</PageNumber>
    </Pagination>
  </ActiveList>
 </GetMyeBaySellingRequest>'''
        if opts.debug:
            api.Session.debug += "\nPARAMETERS\n1. "
            api.Session.debug += str(self.Session.Token) + "\n"
            
        api.RequestData = api.RequestData % { 'token': self.Session.Token, 'page': self.Session.Page, 'pagenum': self.Session.PageNum}

        if opts.debug:
            api.Session.debug += "\nREQUEST RESULTS"
            api.Session.debug += str(api.RequestData)

        responseDOM = api.MakeCall("GetMyeBaySelling", opts.debug)

        """OUTPUT
 <?xml version="1.0" encoding="utf-8"?>
 <GetMyeBaySellingResponse xmlns="urn:ebay:apis:eBLBaseComponents">
  <Timestamp>2005-07-26T18:12:49.667Z</Timestamp>
  <Ack>Success</Ack>
  <Version>539</Version>
  <Build>e539_core_Bundled_5642307_R1</Build>
  <SellingSummary>
    <ActiveAuctionCount>3</ActiveAuctionCount>
    <AuctionSellingCount>5</AuctionSellingCount>
    <AuctionBidCount>2</AuctionBidCount>
    <TotalAuctionSellingValue currencyID="USD">0.0</TotalAuctionSellingValue>
    <TotalSoldCount>5</TotalSoldCount>
    <TotalSoldValue currencyID="USD">1235.22</TotalSoldValue>
    <SoldDurationInDays>31</SoldDurationInDays>
  </SellingSummary>
  <ActiveList>
    <ItemArray>
      <Item>
        <ItemID>110025737313</ItemID>
        <ListingDetails>
          <ConvertedStartPrice currencyID="USD">0.99</ConvertedStartPrice>
          <ConvertedReservePrice currencyID="USD">0.0</ConvertedReservePrice>
          <StartTime>2007-12-12T18:41:12.000Z</StartTime>
        </ListingDetails>
        <ListingType>Chinese</ListingType>
        <Quantity>1</Quantity>
        <ReservePrice currencyID="MYR">0.0</ReservePrice>
        <SellingStatus>
          <ConvertedCurrentPrice currencyID="USD">10.95</ConvertedCurrentPrice>
          <CurrentPrice currencyID="MYR">11.0</CurrentPrice>
          <ReserveMet>true</ReserveMet>
        </SellingStatus>
        <StartPrice currencyID="MYR">11.0</StartPrice>
        <TimeLeft>PT28M17S</TimeLeft>
        <Title>Test Auction Title</Title>
        <QuantityAvailable>1</QuantityAvailable>
      </Item>
      <Item>
        <ItemID>110045137699</ItemID>
        <ListingDetails>
          <StartTime>2007-12-13T17:23:04.000Z</StartTime>
        </ListingDetails>
        <ListingType>Chinese</ListingType>
        <Quantity>1</Quantity>
        <PrivateNotes>6:IDNew3My notes for Relist here (#*%$).</PrivateNotes>
        <ReservePrice currencyID="USD">0.0</ReservePrice>
        <SellingStatus>
          <CurrentPrice currencyID="USD">1.0</CurrentPrice>
          <ReserveMet>true</ReserveMet>
        </SellingStatus>
        <StartPrice currencyID="USD">1.0</StartPrice>
        <TimeLeft>PT28M45S</TimeLeft>
        <Title>Test for ExternalProductIdentifier</Title>
        <QuantityAvailable>1</QuantityAvailable>
      </Item>
      <Item>
        <ItemID>110029733452</ItemID>
        <ListingDetails>
          <StartTime>2007-12-14T11:44:56.000Z</StartTime>
        </ListingDetails>
        <ListingType>Chinese</ListingType>
        <Quantity>1</Quantity>
        <PrivateNotes>7:ID99999My notes here (#*%$).</PrivateNotes>
        <ReservePrice currencyID="USD">0.0</ReservePrice>
        <SellingStatus>
          <CurrentPrice currencyID="USD">1.0</CurrentPrice>
          <ReserveMet>true</ReserveMet>
        </SellingStatus>
        <StartPrice currencyID="USD">1.0</StartPrice>
        <TimeLeft>PT29M35S</TimeLeft>
        <Title>Test for ExternalProductIdentifier</Title>
        <QuantityAvailable>1</QuantityAvailable>
      </Item>
    </ItemArray>
    <PaginationResult>
      <TotalNumberOfPages>1</TotalNumberOfPages>
      <TotalNumberOfEntries>3</TotalNumberOfEntries>
    </PaginationResult>
  </ActiveList>
 </GetMyeBaySellingResponse>"""
        
        if opts.debug:
            api.Session.debug +=  "\n\nRETURN RESULTS\n"
            api.Session.debug +=  str(responseDOM.toxml()) + "\n"
            print api.Session.debug

        if str(responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data) == "Success":
            #userData = responseDOM.getElementsByTagName('User')
            #userRaw = parseString(responseDOM.toxml()) #responseDOM.childNodes
            #userData = userRaw.getElementsByTagName('User')[0].toxml()
            return str(responseDOM.toxml())
        else:
            return "<GetMyeBaySellingResponse></GetMyeBaySellingResponse>"

        
    def Save(self, filename):
        # TODO: If Xml property is blank then it's an exception
        if self.Xml != "":
            f = open(filename, 'w')
            s = self.Token
            f.write(s)
            f.close()


##################################################
########## Get an Item
##################################################
class GetItem:
    """ Get a givne Item details.
    """
    Session = Session()

    def __init__(self, Itemid, Token):
        self.Session.Initialize()
        self.Session.ItemID = Itemid
        self.Session.Token = Token

    def Get(self, opts):
        api = Call()
        api.Session = self.Session
        api.RequestData = '''<?xml version="1.0" encoding="utf-8"?>
 <GetItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>%(token)s</eBayAuthToken>
  </RequesterCredentials>
  <ItemID>%(itemid)s</ItemID>
 </GetItemRequest>'''
        if opts.debug:
            api.Session.debug += "\nGetItem PARAMETERS\n1. "
            api.Session.debug += str(self.Session.ItemID) + "\n2. "
            api.Session.debug += str(self.Session.Token) + "\n"

        api.RequestData = api.RequestData % {'token': self.Session.Token, 'itemid': self.Session.ItemID}

        if opts.debug:
            api.Session.debug += "\nGetItem REQUEST RESULTS:\n"
            api.Session.debug += str(api.RequestData)
            print api.Session.debug
        responseDOM = api.MakeCall("GetItem", opts.debug)

        """OUTPUT
         <?xml version="1.0" encoding="utf-8"?>
         <GetItemResponse xmlns="urn:ebay:apis:eBLBaseComponents">
          <!-- Call-specific Output Fields -->
          <Item> ItemType
            <ApplicationData> string </ApplicationData>
            <ApplyBuyerProtection> BuyerProtectionDetailsType
              <BuyerProtectionSource> BuyerProtectionSourceCodeType </BuyerProtectionSource>
              <BuyerProtectionStatus> BuyerProtectionCodeType </BuyerProtectionStatus>
            </ApplyBuyerProtection>
            <AutoPay> boolean </AutoPay>
            <BestOfferDetails> BestOfferDetailsType
              <BestOfferCount> int </BestOfferCount>
              <BestOfferEnabled> boolean </BestOfferEnabled>
              <NewBestOffer> boolean </NewBestOffer>
            </BestOfferDetails>
            <BusinessSellerDetails> BusinessSellerDetailsType
              <AdditionalContactInformation> string </AdditionalContactInformation>
              <Address> AddressType
                <FirstName> string </FirstName>
                <LastName> string </LastName>
              </Address>
              <Email> string </Email>
              <Fax> string </Fax>
              <LegalInvoice> boolean </LegalInvoice>
              <TermsAndConditions> string </TermsAndConditions>
              <TradeRegistrationNumber> string </TradeRegistrationNumber>
              <VATDetails> VATDetailsType
                <BusinessSeller> boolean </BusinessSeller>
                <RestrictedToBusiness> boolean </RestrictedToBusiness>
                <VATID> string </VATID>
                <VATPercent> float </VATPercent>
                <VATSite> string </VATSite>
              </VATDetails>
            </BusinessSellerDetails>
            <BuyerGuaranteePrice currencyID="CurrencyCodeType"> AmountType (double) </BuyerGuaranteePrice>
            <BuyerProtection> BuyerProtectionCodeType </BuyerProtection>
            <BuyerRequirementDetails> BuyerRequirementDetailsType
              <LinkedPayPalAccount> boolean </LinkedPayPalAccount>
              <MaximumBuyerPolicyViolations> MaximumBuyerPolicyViolationsType
                <Count> int </Count>
                <Period> PeriodCodeType </Period>
              </MaximumBuyerPolicyViolations>
              <MaximumItemRequirements> MaximumItemRequirementsType
                <MaximumItemCount> int </MaximumItemCount>
                <MinimumFeedbackScore> int </MinimumFeedbackScore>
              </MaximumItemRequirements>
              <MaximumUnpaidItemStrikesInfo> MaximumUnpaidItemStrikesInfoType
                <Count> int </Count>
                <Period> PeriodCodeType </Period>
              </MaximumUnpaidItemStrikesInfo>
              <MinimumFeedbackScore> int </MinimumFeedbackScore>
              <ShipToRegistrationCountry> boolean </ShipToRegistrationCountry>
              <VerifiedUserRequirements> VerifiedUserRequirementsType
                <MinimumFeedbackScore> int </MinimumFeedbackScore>
                <VerifiedUser> boolean </VerifiedUser>
              </VerifiedUserRequirements>
              <ZeroFeedbackScore> boolean </ZeroFeedbackScore>
            </BuyerRequirementDetails>
            <BuyerResponsibleForShipping> boolean </BuyerResponsibleForShipping>
            <BuyItNowPrice currencyID="CurrencyCodeType"> AmountType (double) </BuyItNowPrice>
            <Charity> CharityType
              <CharityID> string </CharityID>
              <CharityName> string </CharityName>
              <CharityNumber> int </CharityNumber>
              <DonationPercent> float </DonationPercent>
              <LogoURL> string </LogoURL>
              <Mission> string </Mission>
              <Status> CharityStatusCodeType </Status>
            </Charity>
            <ConditionDescription> string </ConditionDescription>
            <ConditionDisplayName> string </ConditionDisplayName>
            <ConditionID> int </ConditionID>
            <Country> CountryCodeType </Country>
            <CrossBorderTrade> string </CrossBorderTrade>
            <!-- ... more CrossBorderTrade values allowed here ... -->
            <CrossPromotion> CrossPromotionsType
              <ItemID> ItemIDType (string) </ItemID>
              <PrimaryScheme> PromotionSchemeCodeType </PrimaryScheme>
              <PromotedItem> PromotedItemType </PromotedItem>
              <!-- ... more PromotedItem nodes allowed here ... -->
              <PromotionMethod> PromotionMethodCodeType </PromotionMethod>
              <SellerID> string </SellerID>
              <ShippingDiscount> boolean </ShippingDiscount>
            </CrossPromotion>
            <Currency> CurrencyCodeType </Currency>
            <Description> string </Description>
            <DisableBuyerRequirements> boolean </DisableBuyerRequirements>
            <DiscountPriceInfo> DiscountPriceInfoType
              <MadeForOutletComparisonPrice currencyID="CurrencyCodeType"> AmountType (double) </MadeForOutletComparisonPrice>
              <MinimumAdvertisedPrice currencyID="CurrencyCodeType"> AmountType (double) </MinimumAdvertisedPrice>
              <MinimumAdvertisedPriceExposure> MinimumAdvertisedPriceExposureCodeType </MinimumAdvertisedPriceExposure>
              <OriginalRetailPrice currencyID="CurrencyCodeType"> AmountType (double) </OriginalRetailPrice>
              <PricingTreatment> PricingTreatmentCodeType </PricingTreatment>
              <SoldOffeBay> boolean </SoldOffeBay>
              <SoldOneBay> boolean </SoldOneBay>
            </DiscountPriceInfo>
            <DispatchTimeMax> int </DispatchTimeMax>
            <eBayNowAvailable> boolean </eBayNowAvailable>
            <ExtendedSellerContactDetails> ExtendedContactDetailsType
              <ClassifiedAdContactByEmailEnabled> boolean </ClassifiedAdContactByEmailEnabled>
              <ContactHoursDetails> ContactHoursDetailsType
                <Hours1AnyTime> boolean </Hours1AnyTime>
                <Hours1Days> DaysCodeType </Hours1Days>
                <Hours1From> time </Hours1From>
                <Hours1To> time </Hours1To>
                <Hours2AnyTime> boolean </Hours2AnyTime>
                <Hours2Days> DaysCodeType </Hours2Days>
                <Hours2From> time </Hours2From>
                <Hours2To> time </Hours2To>
                <TimeZoneID> string </TimeZoneID>
              </ContactHoursDetails>
            </ExtendedSellerContactDetails>
            <FreeAddedCategory> CategoryType
              <CategoryID> string </CategoryID>
              <CategoryName> string </CategoryName>
            </FreeAddedCategory>
            <GiftIcon> int </GiftIcon>
            <GiftServices> GiftServicesCodeType </GiftServices>
            <!-- ... more GiftServices values allowed here ... -->
            <HideFromSearch> boolean </HideFromSearch>
            <HitCount> long </HitCount>
            <HitCounter> HitCounterCodeType </HitCounter>
            <IgnoreQuantity> boolean </IgnoreQuantity>
            <IntegratedMerchantCreditCardEnabled> boolean </IntegratedMerchantCreditCardEnabled>
            <InventoryTrackingMethod> InventoryTrackingMethodCodeType </InventoryTrackingMethod>
            <IsIntermediatedShippingEligible> boolean </IsIntermediatedShippingEligible>
            <ItemCompatibilityCount> int </ItemCompatibilityCount>
            <ItemCompatibilityList> ItemCompatibilityListType
              <Compatibility> ItemCompatibilityType
                <CompatibilityNotes> string </CompatibilityNotes>
                <NameValueList> NameValueListType
                  <Name> string </Name>
                  <Source> ItemSpecificSourceCodeType </Source>
                  <Value> string </Value>
                  <!-- ... more Value values allowed here ... -->
                </NameValueList>
                <!-- ... more NameValueList nodes allowed here ... -->
              </Compatibility>
              <!-- ... more Compatibility nodes allowed here ... -->
            </ItemCompatibilityList>
            <ItemID> ItemIDType (string) </ItemID>
            <ItemPolicyViolation> ItemPolicyViolationType
              <PolicyID> long </PolicyID>
              <PolicyText> string </PolicyText>
            </ItemPolicyViolation>
            <ItemSpecifics> NameValueListArrayType
              <NameValueList> NameValueListType
                <Name> string </Name>
                <Source> ItemSpecificSourceCodeType </Source>
                <Value> string </Value>
                <!-- ... more Value values allowed here ... -->
              </NameValueList>
              <!-- ... more NameValueList nodes allowed here ... -->
            </ItemSpecifics>
            <ListingCheckoutRedirectPreference> ListingCheckoutRedirectPreferenceType
              <ProStoresStoreName> string </ProStoresStoreName>
              <SellerThirdPartyUsername> string </SellerThirdPartyUsername>
            </ListingCheckoutRedirectPreference>
            <ListingDesigner> ListingDesignerType
              <LayoutID> int </LayoutID>
              <OptimalPictureSize> boolean </OptimalPictureSize>
              <ThemeID> int </ThemeID>
            </ListingDesigner>
            <ListingDetails> ListingDetailsType
              <Adult> boolean </Adult>
              <BestOfferAutoAcceptPrice currencyID="CurrencyCodeType"> AmountType (double) </BestOfferAutoAcceptPrice>
              <BindingAuction> boolean </BindingAuction>
              <BuyItNowAvailable> boolean </BuyItNowAvailable>
              <CheckoutEnabled> boolean </CheckoutEnabled>
              <ConvertedBuyItNowPrice currencyID="CurrencyCodeType"> AmountType (double) </ConvertedBuyItNowPrice>
              <ConvertedReservePrice currencyID="CurrencyCodeType"> AmountType (double) </ConvertedReservePrice>
              <ConvertedStartPrice currencyID="CurrencyCodeType"> AmountType (double) </ConvertedStartPrice>
              <EndingReason> EndReasonCodeType </EndingReason>
              <EndTime> dateTime </EndTime>
              <HasPublicMessages> boolean </HasPublicMessages>
              <HasReservePrice> boolean </HasReservePrice>
              <HasUnansweredQuestions> boolean </HasUnansweredQuestions>
              <MinimumBestOfferPrice currencyID="CurrencyCodeType"> AmountType (double) </MinimumBestOfferPrice>
              <RelistedItemID> ItemIDType (string) </RelistedItemID>
              <SecondChanceOriginalItemID> ItemIDType (string) </SecondChanceOriginalItemID>
              <StartTime> dateTime </StartTime>
              <TCROriginalItemID> ItemIDType (string) </TCROriginalItemID>
              <ViewItemURL> anyURI </ViewItemURL>
              <ViewItemURLForNaturalSearch> anyURI </ViewItemURLForNaturalSearch>
            </ListingDetails>
            <ListingDuration> token </ListingDuration>
            <ListingEnhancement> ListingEnhancementsCodeType </ListingEnhancement>
            <!-- ... more ListingEnhancement values allowed here ... -->
            <ListingSubtype2> ListingSubtypeCodeType </ListingSubtype2>
            <ListingType> ListingTypeCodeType </ListingType>
            <LiveAuction> boolean </LiveAuction>
            <Location> string </Location>
            <LocationDefaulted> boolean </LocationDefaulted>
            <LotSize> int </LotSize>
            <MechanicalCheckAccepted> boolean </MechanicalCheckAccepted>
            <MotorsGermanySearchable> boolean </MotorsGermanySearchable>
            <PaymentAllowedSite> SiteCodeType </PaymentAllowedSite>
            <!-- ... more PaymentAllowedSite values allowed here ... -->
            <PaymentDetails> PaymentDetailsType
              <DaysToFullPayment> int </DaysToFullPayment>
              <DepositAmount currencyID="CurrencyCodeType"> AmountType (double) </DepositAmount>
              <DepositType> DepositTypeCodeType </DepositType>
              <HoursToDeposit> int </HoursToDeposit>
            </PaymentDetails>
            <PaymentMethods> BuyerPaymentMethodCodeType </PaymentMethods>
            <!-- ... more PaymentMethods values allowed here ... -->
            <PayPalEmailAddress> string </PayPalEmailAddress>
            <PickupInStoreDetails> PickupInStoreDetailsType
              <EligibleForPickupDropOff> boolean </EligibleForPickupDropOff>
              <EligibleForPickupInStore> boolean </EligibleForPickupInStore>
            </PickupInStoreDetails>
            <PictureDetails> PictureDetailsType
              <ExtendedPictureDetails> ExtendedPictureDetailsType
                <PictureURLs> PictureURLsType
                  <eBayPictureURL> anyURI </eBayPictureURL>
                  <!-- ... more eBayPictureURL values allowed here ... -->
                  <ExternalPictureURL> anyURI </ExternalPictureURL>
                </PictureURLs>
                <!-- ... more PictureURLs nodes allowed here ... -->
              </ExtendedPictureDetails>
              <ExternalPictureURL> anyURI </ExternalPictureURL>
              <GalleryDuration> token </GalleryDuration>
              <GalleryErrorInfo> string </GalleryErrorInfo>
              <GalleryStatus> GalleryStatusCodeType </GalleryStatus>
              <GalleryType> GalleryTypeCodeType </GalleryType>
              <GalleryURL> anyURI </GalleryURL>
              <PhotoDisplay> PhotoDisplayCodeType </PhotoDisplay>
              <PictureSource> PictureSourceCodeType </PictureSource>
              <PictureURL> anyURI </PictureURL>
              <!-- ... more PictureURL values allowed here ... -->
            </PictureDetails>
            <PostalCode> string </PostalCode>
            <PostCheckoutExperienceEnabled> boolean </PostCheckoutExperienceEnabled>
            <PrimaryCategory> CategoryType
              <CategoryID> string </CategoryID>
              <CategoryName> string </CategoryName>
            </PrimaryCategory>
            <PrivateListing> boolean </PrivateListing>
            <ProductListingDetails> ProductListingDetailsType
              <BrandMPN> BrandMPNType
                <Brand> string </Brand>
                <MPN> string </MPN>
              </BrandMPN>
              <Copyright> string </Copyright>
              <!-- ... more Copyright values allowed here ... -->
              <EAN> string </EAN>
              <IncludePrefilledItemInformation> boolean </IncludePrefilledItemInformation>
              <IncludeStockPhotoURL> boolean </IncludeStockPhotoURL>
              <ISBN> string </ISBN>
              <ProductID> string </ProductID>
              <StockPhotoURL> anyURI </StockPhotoURL>
              <UPC> string </UPC>
              <UseStockPhotoURLAsGallery> boolean </UseStockPhotoURLAsGallery>
            </ProductListingDetails>
            <ProxyItem> boolean </ProxyItem>
            <Quantity> int </Quantity>
            <QuantityAvailableHint> QuantityAvailableHintCodeType </QuantityAvailableHint>
            <QuantityInfo> QuantityInfoType
              <MinimumRemnantSet> int </MinimumRemnantSet>
            </QuantityInfo>
            <QuantityThreshold> int </QuantityThreshold>
            <ReasonHideFromSearch> ReasonHideFromSearchCodeType </ReasonHideFromSearch>
            <RelistParentID> long </RelistParentID>
            <ReservePrice currencyID="CurrencyCodeType"> AmountType (double) </ReservePrice>
            <ReturnPolicy> ReturnPolicyType
              <Description> string </Description>
              <EAN> string </EAN>
              <ExtendedHolidayReturns> boolean </ExtendedHolidayReturns>
              <Refund> string </Refund>
              <RefundOption> token </RefundOption>
              <RestockingFeeValue> token </RestockingFeeValue>
              <RestockingFeeValueOption> token </RestockingFeeValueOption>
              <ReturnsAccepted> string </ReturnsAccepted>
              <ReturnsAcceptedOption> token </ReturnsAcceptedOption>
              <ReturnsWithin> string </ReturnsWithin>
              <ReturnsWithinOption> token </ReturnsWithinOption>
              <ShippingCostPaidBy> string </ShippingCostPaidBy>
              <ShippingCostPaidByOption> token </ShippingCostPaidByOption>
              <WarrantyDuration> string </WarrantyDuration>
              <WarrantyDurationOption> token </WarrantyDurationOption>
              <WarrantyOffered> string </WarrantyOffered>
              <WarrantyOfferedOption> token </WarrantyOfferedOption>
              <WarrantyType> string </WarrantyType>
              <WarrantyTypeOption> token </WarrantyTypeOption>
            </ReturnPolicy>
            <ReviseStatus> ReviseStatusType
              <BuyItNowAdded> boolean </BuyItNowAdded>
              <BuyItNowLowered> boolean </BuyItNowLowered>
              <ItemRevised> boolean </ItemRevised>
              <ReserveLowered> boolean </ReserveLowered>
              <ReserveRemoved> boolean </ReserveRemoved>
            </ReviseStatus>
            <SecondaryCategory> CategoryType
              <CategoryID> string </CategoryID>
              <CategoryName> string </CategoryName>
            </SecondaryCategory>
            <Seller> UserType
              <AboutMePage> boolean </AboutMePage>
              <eBayGoodStanding> boolean </eBayGoodStanding>
              <Email> string </Email>
              <FeedbackPrivate> boolean </FeedbackPrivate>
              <FeedbackRatingStar> FeedbackRatingStarCodeType </FeedbackRatingStar>
              <FeedbackScore> int </FeedbackScore>
              <IDVerified> boolean </IDVerified>
              <MotorsDealer> boolean </MotorsDealer>
              <NewUser> boolean </NewUser>
              <PositiveFeedbackPercent> float </PositiveFeedbackPercent>
              <RegistrationAddress> AddressType
                <CityName> string </CityName>
                <Country> CountryCodeType </Country>
                <CountryName> string </CountryName>
                <FirstName> string </FirstName>
                <LastName> string </LastName>
                <Name> string </Name>
                <Phone> string </Phone>
                <PostalCode> string </PostalCode>
                <Street> string </Street>
                <Street1> string </Street1>
                <Street2> string </Street2>
              </RegistrationAddress>
              <RegistrationDate> dateTime </RegistrationDate>
              <SellerInfo> SellerType
                <AllowPaymentEdit> boolean </AllowPaymentEdit>
                <CheckoutEnabled> boolean </CheckoutEnabled>
                <CIPBankAccountStored> boolean </CIPBankAccountStored>
                <GoodStanding> boolean </GoodStanding>
                <MerchandizingPref> MerchandizingPrefCodeType (token) </MerchandizingPref>
                <QualifiesForB2BVAT> boolean </QualifiesForB2BVAT>
                <SafePaymentExempt> boolean </SafePaymentExempt>
                <SellerBusinessType> SellerBusinessCodeType </SellerBusinessType>
                <SellerLevel> SellerLevelCodeType </SellerLevel>
                <StoreOwner> boolean </StoreOwner>
                <StoreURL> anyURI </StoreURL>
                <TopRatedSeller> boolean </TopRatedSeller>
              </SellerInfo>
              <Site> SiteCodeType </Site>
              <Status> UserStatusCodeType </Status>
              <UserID> UserIDType (string) </UserID>
              <UserIDChanged> boolean </UserIDChanged>
              <UserIDLastChanged> dateTime </UserIDLastChanged>
              <VATStatus> VATStatusCodeType </VATStatus>
            </Seller>
            <SellerContactDetails> AddressType
              <CompanyName> string </CompanyName>
              <County> string </County>
              <FirstName> string </FirstName>
              <LastName> string </LastName>
              <Phone2AreaOrCityCode> string </Phone2AreaOrCityCode>
              <Phone2CountryCode> CountryCodeType </Phone2CountryCode>
              <Phone2CountryPrefix> string </Phone2CountryPrefix>
              <Phone2LocalNumber> string </Phone2LocalNumber>
              <PhoneAreaOrCityCode> string </PhoneAreaOrCityCode>
              <PhoneCountryCode> CountryCodeType </PhoneCountryCode>
              <PhoneCountryPrefix> string </PhoneCountryPrefix>
              <PhoneLocalNumber> string </PhoneLocalNumber>
              <Street1> string </Street1>
              <Street2> string </Street2>
            </SellerContactDetails>
            <SellerProfiles> SellerProfilesType
              <SellerPaymentProfile> SellerPaymentProfileType
                <PaymentProfileID> long </PaymentProfileID>
                <PaymentProfileName> string </PaymentProfileName>
              </SellerPaymentProfile>
              <SellerReturnProfile> SellerReturnProfileType
                <ReturnProfileID> long </ReturnProfileID>
                <ReturnProfileName> string </ReturnProfileName>
              </SellerReturnProfile>
              <SellerShippingProfile> SellerShippingProfileType
                <ShippingProfileID> long </ShippingProfileID>
                <ShippingProfileName> string </ShippingProfileName>
              </SellerShippingProfile>
            </SellerProfiles>
            <SellerProvidedTitle> string </SellerProvidedTitle>
            <SellerVacationNote> string </SellerVacationNote>
            <SellingStatus> SellingStatusType
              <AdminEnded> boolean </AdminEnded>
              <BidCount> int </BidCount>
              <BidIncrement currencyID="CurrencyCodeType"> AmountType (double) </BidIncrement>
              <ConvertedCurrentPrice currencyID="CurrencyCodeType"> AmountType (double) </ConvertedCurrentPrice>
              <CurrentPrice currencyID="CurrencyCodeType"> AmountType (double) </CurrentPrice>
              <HighBidder> UserType
                <AboutMePage> boolean </AboutMePage>
                <BuyerInfo> BuyerType
                  <ShippingAddress> AddressType
                    <Country> CountryCodeType </Country>
                    <FirstName> string </FirstName>
                    <LastName> string </LastName>
                    <PostalCode> string </PostalCode>
                  </ShippingAddress>
                </BuyerInfo>
                <eBayGoodStanding> boolean </eBayGoodStanding>
                <Email> string </Email>
                <FeedbackPrivate> boolean </FeedbackPrivate>
                <FeedbackRatingStar> FeedbackRatingStarCodeType </FeedbackRatingStar>
                <FeedbackScore> int </FeedbackScore>
                <IDVerified> boolean </IDVerified>
                <NewUser> boolean </NewUser>
                <PositiveFeedbackPercent> float </PositiveFeedbackPercent>
                <RegistrationAddress> AddressType
                  <CityName> string </CityName>
                  <Country> CountryCodeType </Country>
                  <CountryName> string </CountryName>
                  <FirstName> string </FirstName>
                  <LastName> string </LastName>
                  <Name> string </Name>
                  <Phone> string </Phone>
                  <PostalCode> string </PostalCode>
                  <Street> string </Street>
                  <Street1> string </Street1>
                  <Street2> string </Street2>
                </RegistrationAddress>
                <RegistrationDate> dateTime </RegistrationDate>
                <Site> SiteCodeType </Site>
                <Status> UserStatusCodeType </Status>
                <UserAnonymized> boolean </UserAnonymized>
                <UserID> UserIDType (string) </UserID>
                <UserIDChanged> boolean </UserIDChanged>
                <UserIDLastChanged> dateTime </UserIDLastChanged>
                <VATStatus> VATStatusCodeType </VATStatus>
              </HighBidder>
              <LeadCount> int </LeadCount>
              <ListingStatus> ListingStatusCodeType </ListingStatus>
              <MinimumToBid currencyID="CurrencyCodeType"> AmountType (double) </MinimumToBid>
              <PromotionalSaleDetails> PromotionalSaleDetailsType
                <EndTime> dateTime </EndTime>
                <OriginalPrice currencyID="CurrencyCodeType"> AmountType (double) </OriginalPrice>
                <StartTime> dateTime </StartTime>
              </PromotionalSaleDetails>
              <QuantitySold> int </QuantitySold>
              <QuantitySoldByPickupInStore> int </QuantitySoldByPickupInStore>
              <ReserveMet> boolean </ReserveMet>
              <SecondChanceEligible> boolean </SecondChanceEligible>
              <SoldAsBin> boolean </SoldAsBin>
            </SellingStatus>
            <ShippingDetails> ShippingDetailsType
              <AllowPaymentEdit> boolean </AllowPaymentEdit>
              <CalculatedShippingDiscount> CalculatedShippingDiscountType
                <DiscountName> DiscountNameCodeType </DiscountName>
                <DiscountProfile> DiscountProfileType
                  <DiscountProfileID> string </DiscountProfileID>
                  <DiscountProfileName> string </DiscountProfileName>
                  <MappedDiscountProfileID> string </MappedDiscountProfileID>
                  <WeightOff unit="token" measurementSystem="MeasurementSystemCodeType"> MeasureType (decimal) </WeightOff>
                </DiscountProfile>
                <!-- ... more DiscountProfile nodes allowed here ... -->
              </CalculatedShippingDiscount>
              <CalculatedShippingRate> CalculatedShippingRateType
                <InternationalPackagingHandlingCosts currencyID="CurrencyCodeType"> AmountType (double) </InternationalPackagingHandlingCosts>
                <OriginatingPostalCode> string </OriginatingPostalCode>
                <PackageDepth unit="token" measurementSystem="MeasurementSystemCodeType"> MeasureType (decimal) </PackageDepth>
                <PackageLength unit="token" measurementSystem="MeasurementSystemCodeType"> MeasureType (decimal) </PackageLength>
                <PackageWidth unit="token" measurementSystem="MeasurementSystemCodeType"> MeasureType (decimal) </PackageWidth>
                <PackagingHandlingCosts currencyID="CurrencyCodeType"> AmountType (double) </PackagingHandlingCosts>
                <ShippingIrregular> boolean </ShippingIrregular>
                <ShippingPackage> ShippingPackageCodeType </ShippingPackage>
                <WeightMajor unit="token" measurementSystem="MeasurementSystemCodeType"> MeasureType (decimal) </WeightMajor>
                <WeightMinor unit="token" measurementSystem="MeasurementSystemCodeType"> MeasureType (decimal) </WeightMinor>
              </CalculatedShippingRate>
              <CODCost currencyID="CurrencyCodeType"> AmountType (double) </CODCost>
              <ExcludeShipToLocation> string </ExcludeShipToLocation>
              <!-- ... more ExcludeShipToLocation values allowed here ... -->
              <FlatShippingDiscount> FlatShippingDiscountType
                <DiscountName> DiscountNameCodeType </DiscountName>
                <DiscountProfile> DiscountProfileType
                  <DiscountProfileID> string </DiscountProfileID>
                  <DiscountProfileName> string </DiscountProfileName>
                  <EachAdditionalAmount currencyID="CurrencyCodeType"> AmountType (double) </EachAdditionalAmount>
                  <EachAdditionalAmountOff currencyID="CurrencyCodeType"> AmountType (double) </EachAdditionalAmountOff>
                  <EachAdditionalPercentOff> float </EachAdditionalPercentOff>
                </DiscountProfile>
                <!-- ... more DiscountProfile nodes allowed here ... -->
              </FlatShippingDiscount>
              <GlobalShipping> boolean </GlobalShipping>
              <InsuranceDetails> InsuranceDetailsType
                <InsuranceFee currencyID="CurrencyCodeType"> AmountType (double) </InsuranceFee>
                <InsuranceOption> InsuranceOptionCodeType </InsuranceOption>
              </InsuranceDetails>
              <InsuranceFee currencyID="CurrencyCodeType"> AmountType (double) </InsuranceFee>
              <InsuranceOption> InsuranceOptionCodeType </InsuranceOption>
              <InternationalCalculatedShippingDiscount> CalculatedShippingDiscountType
                <DiscountName> DiscountNameCodeType </DiscountName>
                <DiscountProfile> DiscountProfileType
                  <DiscountProfileID> string </DiscountProfileID>
                  <DiscountProfileName> string </DiscountProfileName>
                  <MappedDiscountProfileID> string </MappedDiscountProfileID>
                  <WeightOff unit="token" measurementSystem="MeasurementSystemCodeType"> MeasureType (decimal) </WeightOff>
                </DiscountProfile>
                <!-- ... more DiscountProfile nodes allowed here ... -->
              </InternationalCalculatedShippingDiscount>
              <InternationalFlatShippingDiscount> FlatShippingDiscountType
                <DiscountName> DiscountNameCodeType </DiscountName>
                <DiscountProfile> DiscountProfileType
                  <DiscountProfileID> string </DiscountProfileID>
                  <DiscountProfileName> string </DiscountProfileName>
                  <EachAdditionalAmount currencyID="CurrencyCodeType"> AmountType (double) </EachAdditionalAmount>
                  <EachAdditionalAmountOff currencyID="CurrencyCodeType"> AmountType (double) </EachAdditionalAmountOff>
                  <EachAdditionalPercentOff> float </EachAdditionalPercentOff>
                </DiscountProfile>
                <!-- ... more DiscountProfile nodes allowed here ... -->
              </InternationalFlatShippingDiscount>
              <InternationalInsuranceDetails> InsuranceDetailsType
                <InsuranceFee currencyID="CurrencyCodeType"> AmountType (double) </InsuranceFee>
                <InsuranceOption> InsuranceOptionCodeType </InsuranceOption>
              </InternationalInsuranceDetails>
              <InternationalPromotionalShippingDiscount> boolean </InternationalPromotionalShippingDiscount>
              <InternationalShippingDiscountProfileID> string </InternationalShippingDiscountProfileID>
              <InternationalShippingServiceOption> InternationalShippingServiceOptionsType
                <ShippingService> token </ShippingService>
                <ShippingServiceAdditionalCost currencyID="CurrencyCodeType"> AmountType (double) </ShippingServiceAdditionalCost>
                <ShippingServiceCost currencyID="CurrencyCodeType"> AmountType (double) </ShippingServiceCost>
                <ShippingServicePriority> int </ShippingServicePriority>
                <ShipToLocation> string </ShipToLocation>
                <!-- ... more ShipToLocation values allowed here ... -->
              </InternationalShippingServiceOption>
              <!-- ... more InternationalShippingServiceOption nodes allowed here ... -->
              <PaymentInstructions> string </PaymentInstructions>
              <PromotionalShippingDiscount> boolean </PromotionalShippingDiscount>
              <PromotionalShippingDiscountDetails> PromotionalShippingDiscountDetailsType
                <DiscountName> DiscountNameCodeType </DiscountName>
                <ItemCount> int </ItemCount>
                <OrderAmount currencyID="CurrencyCodeType"> AmountType (double) </OrderAmount>
                <ShippingCost currencyID="CurrencyCodeType"> AmountType (double) </ShippingCost>
              </PromotionalShippingDiscountDetails>
              <RateTableDetails> RateTableDetailsType
                <DomesticRateTable> string </DomesticRateTable>
                <InternationalRateTable> string </InternationalRateTable>
              </RateTableDetails>
              <SalesTax> SalesTaxType
                <SalesTaxPercent> float </SalesTaxPercent>
                <SalesTaxState> string </SalesTaxState>
                <ShippingIncludedInTax> boolean </ShippingIncludedInTax>
              </SalesTax>
              <SellerExcludeShipToLocationsPreference> boolean </SellerExcludeShipToLocationsPreference>
              <ShippingDiscountProfileID> string </ShippingDiscountProfileID>
              <ShippingServiceOptions> ShippingServiceOptionsType
                <ExpeditedService> boolean </ExpeditedService>
                <FreeShipping> boolean </FreeShipping>
                <LogisticPlanType> string </LogisticPlanType>
                <ShippingService> token </ShippingService>
                <ShippingServiceAdditionalCost currencyID="CurrencyCodeType"> AmountType (double) </ShippingServiceAdditionalCost>
                <ShippingServiceCost currencyID="CurrencyCodeType"> AmountType (double) </ShippingServiceCost>
                <ShippingServicePriority> int </ShippingServicePriority>
                <ShippingSurcharge currencyID="CurrencyCodeType"> AmountType (double) </ShippingSurcharge>
                <ShippingTimeMax> int </ShippingTimeMax>
                <ShippingTimeMin> int </ShippingTimeMin>
              </ShippingServiceOptions>
              <!-- ... more ShippingServiceOptions nodes allowed here ... -->
              <ShippingType> ShippingTypeCodeType </ShippingType>
              <TaxTable> TaxTableType
                <TaxJurisdiction> TaxJurisdictionType
                  <JurisdictionID> string </JurisdictionID>
                  <SalesTaxPercent> float </SalesTaxPercent>
                  <ShippingIncludedInTax> boolean </ShippingIncludedInTax>
                </TaxJurisdiction>
                <!-- ... more TaxJurisdiction nodes allowed here ... -->
              </TaxTable>
            </ShippingDetails>
            <ShippingPackageDetails> ShipPackageDetailsType
              <PackageDepth unit="token" measurementSystem="MeasurementSystemCodeType"> MeasureType (decimal) </PackageDepth>
              <PackageLength unit="token" measurementSystem="MeasurementSystemCodeType"> MeasureType (decimal) </PackageLength>
              <PackageWidth unit="token" measurementSystem="MeasurementSystemCodeType"> MeasureType (decimal) </PackageWidth>
              <ShippingIrregular> boolean </ShippingIrregular>
              <ShippingPackage> ShippingPackageCodeType </ShippingPackage>
              <WeightMajor unit="token" measurementSystem="MeasurementSystemCodeType"> MeasureType (decimal) </WeightMajor>
              <WeightMinor unit="token" measurementSystem="MeasurementSystemCodeType"> MeasureType (decimal) </WeightMinor>
            </ShippingPackageDetails>
            <ShippingTermsInDescription> boolean </ShippingTermsInDescription>
            <ShipToLocations> string </ShipToLocations>
            <!-- ... more ShipToLocations values allowed here ... -->
            <Site> SiteCodeType </Site>
            <SKU> SKUType (string) </SKU>
            <SkypeContactOption> SkypeContactOptionCodeType </SkypeContactOption>
            <!-- ... more SkypeContactOption values allowed here ... -->
            <SkypeEnabled> boolean </SkypeEnabled>
            <SkypeID> string </SkypeID>
            <StartPrice currencyID="CurrencyCodeType"> AmountType (double) </StartPrice>
            <Storefront> StorefrontType
              <StoreCategory2ID> long </StoreCategory2ID>
              <StoreCategoryID> long </StoreCategoryID>
              <StoreURL> anyURI </StoreURL>
            </Storefront>
            <SubTitle> string </SubTitle>
            <TaxCategory> string </TaxCategory>
            <TimeLeft> duration </TimeLeft>
            <Title> string </Title>
            <TopRatedListing> boolean </TopRatedListing>
            <UnitInfo> UnitInfoType
              <UnitQuantity> double </UnitQuantity>
              <UnitType> string </UnitType>
            </UnitInfo>
            <UUID> UUIDType (string) </UUID>
            <Variations> VariationsType
              <Pictures> PicturesType
                <VariationSpecificName> string </VariationSpecificName>
                <VariationSpecificPictureSet> VariationSpecificPictureSetType
                  <ExtendedPictureDetails> ExtendedPictureDetailsType
                    <PictureURLs> PictureURLsType
                      <eBayPictureURL> anyURI </eBayPictureURL>
                      <!-- ... more eBayPictureURL values allowed here ... -->
                      <ExternalPictureURL> anyURI </ExternalPictureURL>
                    </PictureURLs>
                    <!-- ... more PictureURLs nodes allowed here ... -->
                  </ExtendedPictureDetails>
                  <ExternalPictureURL> anyURI </ExternalPictureURL>
                  <!-- ... more ExternalPictureURL values allowed here ... -->
                  <PictureURL> anyURI </PictureURL>
                  <!-- ... more PictureURL values allowed here ... -->
                  <VariationSpecificValue> string </VariationSpecificValue>
                </VariationSpecificPictureSet>
                <!-- ... more VariationSpecificPictureSet nodes allowed here ... -->
              </Pictures>
              <Variation> VariationType
                <DiscountPriceInfo> DiscountPriceInfoType
                  <MadeForOutletComparisonPrice currencyID="CurrencyCodeType"> AmountType (double) </MadeForOutletComparisonPrice>
                  <MinimumAdvertisedPrice currencyID="CurrencyCodeType"> AmountType (double) </MinimumAdvertisedPrice>
                  <MinimumAdvertisedPriceExposure> MinimumAdvertisedPriceExposureCodeType </MinimumAdvertisedPriceExposure>
                  <OriginalRetailPrice currencyID="CurrencyCodeType"> AmountType (double) </OriginalRetailPrice>
                  <PricingTreatment> PricingTreatmentCodeType </PricingTreatment>
                  <SoldOffeBay> boolean </SoldOffeBay>
                  <SoldOneBay> boolean </SoldOneBay>
                </DiscountPriceInfo>
                <Quantity> int </Quantity>
                <SellingStatus> SellingStatusType
                  <AdminEnded> boolean </AdminEnded>
                  <BidCount> int </BidCount>
                  <BidIncrement currencyID="CurrencyCodeType"> AmountType (double) </BidIncrement>
                  <ConvertedCurrentPrice currencyID="CurrencyCodeType"> AmountType (double) </ConvertedCurrentPrice>
                  <CurrentPrice currencyID="CurrencyCodeType"> AmountType (double) </CurrentPrice>
                  <HighBidder> UserType
                    <AboutMePage> boolean </AboutMePage>
                    <BuyerInfo> BuyerType
                      <ShippingAddress> AddressType
                        <Country> CountryCodeType </Country>
                        <FirstName> string </FirstName>
                        <LastName> string </LastName>
                        <PostalCode> string </PostalCode>
                      </ShippingAddress>
                    </BuyerInfo>
                    <eBayGoodStanding> boolean </eBayGoodStanding>
                    <Email> string </Email>
                    <FeedbackPrivate> boolean </FeedbackPrivate>
                    <FeedbackRatingStar> FeedbackRatingStarCodeType </FeedbackRatingStar>
                    <FeedbackScore> int </FeedbackScore>
                    <IDVerified> boolean </IDVerified>
                    <NewUser> boolean </NewUser>
                    <PositiveFeedbackPercent> float </PositiveFeedbackPercent>
                    <RegistrationAddress> AddressType
                      <CityName> string </CityName>
                      <Country> CountryCodeType </Country>
                      <CountryName> string </CountryName>
                      <FirstName> string </FirstName>
                      <LastName> string </LastName>
                      <Name> string </Name>
                      <Phone> string </Phone>
                      <PostalCode> string </PostalCode>
                      <Street> string </Street>
                      <Street1> string </Street1>
                      <Street2> string </Street2>
                    </RegistrationAddress>
                    <RegistrationDate> dateTime </RegistrationDate>
                    <Site> SiteCodeType </Site>
                    <Status> UserStatusCodeType </Status>
                    <UserAnonymized> boolean </UserAnonymized>
                    <UserID> UserIDType (string) </UserID>
                    <UserIDChanged> boolean </UserIDChanged>
                    <UserIDLastChanged> dateTime </UserIDLastChanged>
                    <VATStatus> VATStatusCodeType </VATStatus>
                  </HighBidder>
                  <LeadCount> int </LeadCount>
                  <ListingStatus> ListingStatusCodeType </ListingStatus>
                  <MinimumToBid currencyID="CurrencyCodeType"> AmountType (double) </MinimumToBid>
                  <PromotionalSaleDetails> PromotionalSaleDetailsType
                    <EndTime> dateTime </EndTime>
                    <OriginalPrice currencyID="CurrencyCodeType"> AmountType (double) </OriginalPrice>
                    <StartTime> dateTime </StartTime>
                  </PromotionalSaleDetails>
                  <QuantitySold> int </QuantitySold>
                  <QuantitySoldByPickupInStore> int </QuantitySoldByPickupInStore>
                  <ReserveMet> boolean </ReserveMet>
                  <SecondChanceEligible> boolean </SecondChanceEligible>
                  <SoldAsBin> boolean </SoldAsBin>
                </SellingStatus>
                <SKU> SKUType (string) </SKU>
                <StartPrice currencyID="CurrencyCodeType"> AmountType (double) </StartPrice>
                <VariationProductListingDetails> VariationProductListingDetailsType
                  <EAN> string </EAN>
                  <ISBN> string </ISBN>
                  <UPC> string </UPC>
                </VariationProductListingDetails>
                <VariationSpecifics> NameValueListArrayType
                  <NameValueList> NameValueListType
                    <Name> string </Name>
                    <Source> ItemSpecificSourceCodeType </Source>
                    <Value> string </Value>
                    <!-- ... more Value values allowed here ... -->
                  </NameValueList>
                  <!-- ... more NameValueList nodes allowed here ... -->
                </VariationSpecifics>
                <!-- ... more VariationSpecifics nodes allowed here ... -->
              </Variation>
              <!-- ... more Variation nodes allowed here ... -->
              <VariationSpecificsSet> NameValueListArrayType
                <NameValueList> NameValueListType
                  <Name> string </Name>
                  <Source> ItemSpecificSourceCodeType </Source>
                  <Value> string </Value>
                  <!-- ... more Value values allowed here ... -->
                </NameValueList>
                <!-- ... more NameValueList nodes allowed here ... -->
              </VariationSpecificsSet>
            </Variations>
            <VATDetails> VATDetailsType
              <BusinessSeller> boolean </BusinessSeller>
              <RestrictedToBusiness> boolean </RestrictedToBusiness>
              <VATID> string </VATID>
              <VATPercent> float </VATPercent>
              <VATSite> string </VATSite>
            </VATDetails>
            <VIN> string </VIN>
            <VINLink> string </VINLink>
            <VRM> string </VRM>
            <VRMLink> string </VRMLink>
            <WatchCount> long </WatchCount>
          </Item>
          <!-- Standard Output Fields -->
          <Ack> AckCodeType </Ack>
          <Build> string </Build>
          <CorrelationID> string </CorrelationID>
          <Errors> ErrorType
            <ErrorClassification> ErrorClassificationCodeType </ErrorClassification>
            <ErrorCode> token </ErrorCode>
            <ErrorParameters ParamID="string"> ErrorParameterType
              <Value> string </Value>
            </ErrorParameters>
            <!-- ... more ErrorParameters nodes allowed here ... -->
            <LongMessage> string </LongMessage>
            <SeverityCode> SeverityCodeType </SeverityCode>
            <ShortMessage> string </ShortMessage>
          </Errors>
          <!-- ... more Errors nodes allowed here ... -->
          <HardExpirationWarning> string </HardExpirationWarning>
          <Timestamp> dateTime </Timestamp>
          <Version> string </Version>
         </GetItemResponse>"""
        
        if opts.debug:
            api.Session.debug +=  "\n\nGetItem RETURN RESULTS:\n"
            api.Session.debug +=  str(responseDOM.toxml()) + "\n"
            print api.Session.debug

        if str(responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data) == "Success":
            #itemData = responseDOM.getElementsByTagName('Item')
            #userRaw = parseString(responseDOM.toxml()) #responseDOM.childNodes
            #itemData = userRaw.getElementsByTagName('Item')[0].toxml()
            return str(responseDOM.toxml())
        else:
            return "<GetItemResponse></GetItemResponse>"

        
    def Save(self, filename):
        # TODO: If Xml property is blank then it's an exception
        if self.Xml != "":
            f = open(filename, 'w')
            s = self.Token
            f.write(s)
            f.close()



##################################################
########## Revise an Item
##################################################
class ReviseItem:
    """ REvise a given Item details.
    """
    Session = Session()

    def __init__(self, RequestData):
        self.Session.Initialize()
        self.Session.RequestData = RequestData

    def Get(self, opts):
        api = Call()
        api.Session = self.Session
        api.RequestData = self.Session.RequestData

        if opts.debug:
            api.Session.debug += "\nReviseItem PARAMETERS\n1. "
            api.Session.debug += str(self.Session.RequestData) + "\n"

        #api.RequestData = api.RequestData % {'token': self.Session.Token, 'itemid': self.Session.ItemID, 'quantity': self.Session.Quantity}

        if opts.debug:
            api.Session.debug += "\nReviseItem REQUEST RESULTS:\n"
            api.Session.debug += str(api.RequestData)

        try:
            responseDOM = api.MakeCall("ReviseItem", opts.debug)
            print "MADE IT HERE"
            #print parse(responseDOM).toxml()
            #root = ET.ElementTree(ET.fromstring(responseDOM)).getroot()
            #print (root.toprettyxml())
            print "DUMP"
            #print(str(responseDOM.toxml()))
            if opts.debug:
                api.Session.debug +=  "\n\nReviseItem RETURN RESULTS:\n"
                api.Session.debug +=  str(responseDOM.toxml()) + "\n"
                print api.Session.debug

            #if str(responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data) == "Success":
                #itemData = responseDOM.getElementsByTagName('Item')
                #userRaw = parseString(responseDOM.toxml()) #responseDOM.childNodes
                #itemData = userRaw.getElementsByTagName('Item')[0].toxml()
            return str(responseDOM.toxml())
            #else:
            #    return "<ReviseItemResponse></ReviseItemResponse>"
        except IOError as (errno, strerror):
            PrintException()
            self.Error = self.Error + 100
            self.ErrorMessage = "I/O error({0}): {1}".format(errno, strerror)
        except ValueError:
            PrintException()
            self.ErrorMessage = "No valid integer in line."
        except:
            PrintException()
            self.ErrorMessage = "Unexpected error:", sys.exc_info()[0]
        print self.ErrorMessage

        """OUTPUT
         <?xml version="1.0" encoding="utf-8"?>
         <ReviseItemResponse xmlns="urn:ebay:apis:eBLBaseComponents">
          <!-- Call-specific Output Fields -->
          <Category2ID> string </Category2ID>
          <CategoryID> string </CategoryID>
          <DiscountReason> DiscountReasonCodeType </DiscountReason>
          <!-- ... more DiscountReason values allowed here ... -->
          <EndTime> dateTime </EndTime>
          <Fees> FeesType
            <Fee> FeeType
              <Fee currencyID="CurrencyCodeType"> AmountType (double) </Fee>
              <Name> string </Name>
              <PromotionalDiscount currencyID="CurrencyCodeType"> AmountType (double) </PromotionalDiscount>
            </Fee>
            <!-- ... more Fee nodes allowed here ... -->
          </Fees>
          <ItemID> ItemIDType (string) </ItemID>
          <ListingRecommendations> ListingRecommendationsType
            <Recommendation> ListingRecommendationType
              <Code> string </Code>
              <FieldName> string </FieldName>
              <Group> string </Group>
              <Message> string </Message>
              <Metadata> MetadataType
                <Name> string </Name>
                <Value> string </Value>
                <!-- ... more Value values allowed here ... -->
              </Metadata>
              <!-- ... more Metadata nodes allowed here ... -->
              <Type> string </Type>
              <Value> string </Value>
              <!-- ... more Value values allowed here ... -->
            </Recommendation>
            <!-- ... more Recommendation nodes allowed here ... -->
          </ListingRecommendations>
          <ProductSuggestions> ProductSuggestionsType
            <ProductSuggestion> ProductSuggestionType
              <EPID> string </EPID>
              <Recommended> boolean </Recommended>
              <StockPhoto> string </StockPhoto>
              <Title> string </Title>
            </ProductSuggestion>
            <!-- ... more ProductSuggestion nodes allowed here ... -->
          </ProductSuggestions>
          <StartTime> dateTime </StartTime>
          <!-- Standard Output Fields -->
          <Ack> AckCodeType </Ack>
          <Build> string </Build>
          <CorrelationID> string </CorrelationID>
          <DuplicateInvocationDetails> DuplicateInvocationDetailsType
            <DuplicateInvocationID> UUIDType (string) </DuplicateInvocationID>
            <InvocationTrackingID> string </InvocationTrackingID>
            <Status> InvocationStatusType </Status>
          </DuplicateInvocationDetails>
          <Errors> ErrorType
            <ErrorClassification> ErrorClassificationCodeType </ErrorClassification>
            <ErrorCode> token </ErrorCode>
            <ErrorParameters ParamID="string"> ErrorParameterType
              <Value> string </Value>
            </ErrorParameters>
            <!-- ... more ErrorParameters nodes allowed here ... -->
            <LongMessage> string </LongMessage>
            <SeverityCode> SeverityCodeType </SeverityCode>
            <ShortMessage> string </ShortMessage>
            <UserDisplayHint> boolean </UserDisplayHint>
          </Errors>
          <!-- ... more Errors nodes allowed here ... -->
          <HardExpirationWarning> string </HardExpirationWarning>
          <Message> string </Message>
          <Timestamp> dateTime </Timestamp>
          <Version> string </Version>
         </ReviseItemResponse>"""


        
    def Save(self, filename):
        # TODO: If Xml property is blank then it's an exception
        if self.Xml != "":
            f = open(filename, 'w')
            s = self.Token
            f.write(s)
            f.close()





##################################################
########## REST Token retrieval
##################################################
class RESTToken:
    """ Retrieves a REST token when a conventional token is available.
    Getting a REST token in this way has the advantage of (cough) not invalidating a conventional token if you have one. """
    Session = Session()
    
    def __init__(self):
        self.Session.Initialize()
        
    def Get(self):
        api = Call()
        api.Session = self.Session
        api.DetailLevel = "128"
        api.RequestData = """<?xml version='1.0' encoding='UTF-8'?>
 <request>
    <RequestToken>%(token)s</RequestToken>
    <DetailLevel>%(detail)s</DetailLevel>
    <ErrorLevel>1</ErrorLevel>
    <SiteId>0</SiteId>
    <Verb>GetUser</Verb>
    <UserId></UserId>
 </request>"""
        api.RequestData = api.RequestData % { 'token': self.Session.Token, 'detail': api.DetailLevel}
        print api.RequestData + "\n"
        self.Xml = api.MakeCall("GetUser", opts.debug)
        self.Token = self.Xml.getElementsByTagName('RestToken')[0].childNodes[0].data
        
    def Save(self, filename):
        # TODO: If Xml property is blank then it's an exception
        if self.Xml != "":
            f = open(filename, 'w')
            s = self.Token
            f.write(s)
            f.close()


########## Feedback
class Feedback:
    Session = Session()
    
    def __init__(self):
        self.Session.Initialize()
        
    def Get(self, UserID):
        api = Call()
        api.Session = self.Session
        api.DetailLevel = "1"
        api.RequestData = """<?xml version='1.0' encoding='UTF-8'?>
 <request>
    <RequestToken>%(token)s</RequestToken>
    <DetailLevel>%(detail)s</DetailLevel>
    <ErrorLevel>1</ErrorLevel>
    <SiteId>0</SiteId>
    <Verb>GetFeedback</Verb>
    <UserId>%(userid)s</UserId>
 </request>"""
        api.RequestData = api.RequestData % { 'token': self.Session.Token,
                                              'detail': api.DetailLevel,
                                              'userid': UserID }
        self.Xml = api.MakeCall("GetFeedback", opts.debug)
        self.UserID = UserID
        # TODO: Parse into FeedbackDetail objects
        
    def Save(self, filename):
        # TODO: If Xml property is blank then it's an exception
        if self.Xml != "":
            f = open(filename, 'w')
            s = self.Xml.toprettyxml().encode('utf-8')
            f.write(s)
            f.close()        


########## Finance Offers
class FinanceOffers:
    Session = Session()
    
    def __init__(self):
        self.Session.Initialize()
        
    def Get(self):
        api = Call()
        api.Session = self.Session
        api.DetailLevel = "1"
        api.RequestData = """<?xml version='1.0' encoding='UTF-8'?>
 <request>
    <RequestToken>%(token)s</RequestToken>
    <DetailLevel>%(detail)s</DetailLevel>
    <ErrorLevel>1</ErrorLevel>
    <SiteId>0</SiteId>
    <Verb>GetFinanceOffers</Verb>
    <LastModifiedDate>2004-01-01 12:00:00</LastModifiedDate>
 </request>"""
        api.RequestData = api.RequestData % { 'token': self.Session.Token,
                                              'detail': api.DetailLevel }
        self.Xml = api.MakeCall("GetFinanceOffers", opts.debug)
        
        # TODO: Populate this dictionary with data from the xml
        self.Offers = dict()
        self.Offers['6060842'] = 'Im waiting for you'

    def Save(self, filename):
        # TODO: If Xml property is blank then it's an exception
        if self.Xml != "":
            f = open(filename, 'w')
            s = self.Xml.toprettyxml().encode('utf-8')
            f.write(s)
            f.close()

class FinanceOffer:
    # TODO: Assign XML to object and have it parse out all the data
    # TODO: Strip out stupid stupid HTML formatting from seller/buyer terms
    Xml = "<xml />"
    SellerTerms = ""
    BuyerTerms = ""
    Priority = 0
    StartDate = "1900-01-01 1:01:00"
    MinimumAmount = 0
    RateFactor = 0.00
    LastModifiedDate = "1900-01-01 1:01:00"

########## GetToken
class Token:
    Session = Session()
    
    def __init__(self):
        self.Session.Initialize()
        self.RequestUserId = 'USER_ID'
        self.RequestPassword = 'PASSWORD'
        
    def Get(self):
        api = Call()
        api.Session = self.Session
        api.DetailLevel = "0" 
        api.RequestData = """<?xml version='1.0' encoding='UTF-8'?>
 <request>
    <RequestToken></RequestToken>
    <RequestUserId>%(userid)s</RequestUserId>
    <RequestPassword>%(password)s</RequestPassword>    
    <DetailLevel>%(detail)s</DetailLevel>
    <ErrorLevel>1</ErrorLevel>
    <SiteId>0</SiteId>
    <Verb>GetToken</Verb>
 </request>"""
        api.RequestData = api.RequestData % { 'detail': api.DetailLevel,
                                              'userid': self.RequestUserId,
                                              'password': self.RequestPassword}
        print api.RequestData
        self.Xml = api.MakeCall("GetToken", opts.debug)
    

########## SellerList
class SellerList:
    Session = Session()
    
    def __init__(self):
        self.Session.Initialize()
        
    def Get(self, SellerUserName):
        api = Call()
        api.Session = self.Session
        api.DetailLevel = "2"  # 16 is minimal data but returns all IDs
        api.RequestData = """<?xml version='1.0' encoding='UTF-8'?>
 <request>
    <RequestToken>%(token)s</RequestToken>
    <DetailLevel>%(detail)s</DetailLevel>
    <ErrorLevel>1</ErrorLevel>
    <SiteId>0</SiteId>
    <Verb>GetSellerList</Verb>
    <ItemsPerPage>200</ItemsPerPage>
    <PageNumber>1</PageNumber>
    <StartTimeFrom>2004-01-01</StartTimeFrom>
    <StartTimeTo>2004-12-31</StartTimeTo>
 </request>"""
        api.RequestData = api.RequestData % { 'token': self.Session.Token,
                                              'detail': api.DetailLevel }
        self.Xml = api.MakeCall("GetSellerList", opts.debug)


########## Item
class Item:
    # TODO: Implement finance offers by:
    #   1) Downloading all offers using GetFinanceOffers
    #   2) Seeing which offers are available for a category using GetCategory2FinanceOffer (always use detail level 1 for this)
    #   3) Assigning a chosen finance offer by assigning its ID to the item's <FinanceOfferId> node
    Session = Session()
    Category = "14111"  # eBay Test topic
    Country = "us"      # TODO: Enumerate/validate country table as found in http://developer.ebay.com/DevZone/docs/API_Doc/Appendixes/AppendixL.htm
    Currency = "1"      # TODO: Since currency is a function of site ID, it should be possible to auto-map between siteIDs and currency IDs (see http://developer.ebay.com/DevZone/docs/API_Doc/Functions/Tables/CurrencyIdTable.htm)
    Description = "This auction was listed with pyeBay."
    Duration = "7"      # TODO: Provide validation (auctions can be 1, 3, 5, 7, 10 etc.)
    Location = "A town near you"
    MinimumBid = "0.99"
    PayPalEmailAddress = "jeffreyp@well.com"  # TODO: If no PP address provided, set PayPalAccepted to 0
    Quantity = "1"
    Region = "60"       # TODO: Enumerate/validate region codes *or* provide for download and lookup of region tables using GeteBayDetails call
    Title = "My Listing Created by pyeBay"
    
    def __init__(self):
        pass
        # self.Session.Initialize()   # must init an Item object manually at least for now

    def Add(self):
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version='1.0' encoding='UTF-8'?>
 <request>
    <RequestToken>%(token)s</RequestToken>
    <DetailLevel>0</DetailLevel>
    <ErrorLevel>1</ErrorLevel>
    <SiteId>0</SiteId>
    <Verb>AddItem</Verb>
    <Category>%(category)s</Category>
    <CheckoutDetailsSpecified>0</CheckoutDetailsSpecified>
    <Country>%(country)s</Country>
    <Currency>%(currency)s</Currency>
    <Description>%(description)s</Description>
    <Duration>%(duration)s</Duration>
    <Location>%(location)s</Location>
    <MinimumBid>%(minimumbid)s</MinimumBid>
    <PayPalAccepted>1</PayPalAccepted>
    <PayPalEmailAddress>%(paypaladdress)s</PayPalEmailAddress>
    <Quantity>%(quantity)s</Quantity>
    <Region>%(region)s</Region>
    <Title>%(title)s</Title>
 </request>""" 
        api.RequestData = api.RequestData % { 'token': self.Session.Token,
                                              'category': self.Category,
                                              'country': self.Country,
                                              'currency': self.Currency,
                                              'description': self.Description,
                                              'duration': self.Duration,
                                              'location': self.Location,
                                              'minimumbid': self.MinimumBid,
                                              'paypaladdress': self.PayPalEmailAddress,
                                              'quantity': self.Quantity,
                                              'region': self.Region,
                                              'title': self.Title }
        self.Xml = api.MakeCall("AddItem", opts.debug)
        self.ID = self.Xml.getElementsByTagName('Id')[0].childNodes[0].data
        self.ListingFee = self.Xml.getElementsByTagName('ListingFee')[0].childNodes[0].data
        # TODO: Make this do the right thing for production as well
        self.URL = "http://cgi.sandbox.ebay.com/ws/eBayISAPI.dll?ViewItem&item=" + self.ID
        
    def Dispose(self):
        self.Xml.unlink()
        

########## Categories

class Categories:
    Session = Session()
    
    def __init__(self):
        self.Session.Initialize()
    
    # TODO: Need to add the lightweight version of this call 
    # (detail level 0) to check version only -- maybe call it GetVersion()
    def Get(self):
        api = Call()
        api.Session = self.Session
        api.DetailLevel = "1"
        api.RequestData = """<?xml version='1.0' encoding='utf-8'?>
 <request>
    <RequestToken>%(token)s</RequestToken>
    <DetailLevel>%(detail)s</DetailLevel>
    <ErrorLevel>1</ErrorLevel>
    <SiteId>0</SiteId>
    <Verb>GetCategories</Verb>
    <ViewAllNodes>1</ViewAllNodes>
 </request>"""
        api.RequestData = api.RequestData % { 'token': self.Session.Token,
                                              'detail': api.DetailLevel }
        self.Xml = api.MakeCall("GetCategories", opts.debug)

    def Save(self, filename):
        # TODO: If Xml property is blank then it's an exception
        if self.Xml != "":
            f = open(filename, 'w')
            s = self.Xml.toprettyxml().encode('utf-8')
            f.write(s)
            f.close()
    
    def Dispose(self):
        self.Xml.unlink()
        
        
########## User

class User:
    Session = Session()
    ID = ""
    
    def __init__(self):
        self.Session.Initialize()
        
    def Get(self):
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version='1.0' encoding='utf-8'?>
  <request>
   <RequestToken>%(token)s</RequestToken>
   <ErrorLevel>1</ErrorLevel>
   <DetailLevel>%(detail)s</DetailLevel>
   <Verb>GetUser</Verb>
   <SiteId>0</SiteId>
   <UserId>%(userid)s</UserId>
  </request>"""
        api.RequestData = api.RequestData % { 'userid': self.ID, 
                                              'token': self.Session.Token, 
                                              'detail': api.DetailLevel }
        
        self.Xml = api.MakeCall("GetUser", opts.debug)
        # TODO: Map more of the XML to properties of the object
        self.Feedback = self.Xml.getElementsByTagName('Score')[0].childNodes[0].data

    def Validate(self):
        # maps to ValidateTestUserRegistration
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version='1.0' encoding='utf-8'?>
 <request>
   <RequestToken>%(token)s</RequestToken>
   <ErrorLevel>1</ErrorLevel>
   <DetailLevel>0</DetailLevel>
   <Verb>ValidateTestUserRegistration</Verb>
   <SiteId>0</SiteId>
 </request>"""
        api.RequestData = api.RequestData % { 'token': self.Session.Token }  
        self.Xml = api.MakeCall("ValidateTestUserRegistration", opts.debug)  
        
    def Dispose(self):
        self.Xml.unlink()
    

########## Search

class Search:
    Session = Session()
    DetailLevel = "0"
    Query = ""
    
    def __init__(self):
        self.Session.Initialize()

    
    def Get(self, Query):
        # TODO: Change this so it returns a list of
        # Item objects (instead of raw xml)
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version='1.0' encoding='utf-8'?>
 <request>
    <RequestToken>%(token)s</RequestToken>
    <ErrorLevel>1</ErrorLevel>
    <DetailLevel>%(detail)s</DetailLevel>
    <Query>%(query)s</Query>
    <Verb>GetSearchResults</Verb>
    <SiteId>0</SiteId>
 </request>"""
        api.RequestData = api.RequestData % { 'query': Query, 
                                              'token': self.Session.Token, 
                                              'detail': api.DetailLevel }
        print api.RequestData                                              
        self.Xml = api.MakeCall("GetSearchResults", opts.debug)

    def Dispose(self):
        self.Xml.unlink()


########## Call        

class Call:
    RequestData = "<xml />"  # just a stub
    DetailLevel = "0"
    SiteID = "0"

    def MakeCall(self, CallName, Debug):
        # specify the connection to the eBay Sandbox environment
        # TODO: Make this configurable in eBay.ini (sandbox/production)
        conn = httplib.HTTPSConnection(self.Session.Server)

        # specify a POST with the results of generateHeaders and generateRequest
        conn.request("POST", self.Session.Command, self.RequestData, self.GenerateHeaders(self.Session, CallName))
        response = conn.getresponse()
        
        # TODO: When you add logging to this, change the
        # following to log statements
        if Debug:
            print "Response status:", response.status
            print "Response reason:", response.reason + "\n"
        
        # store the response data and close the connection
        data = response.read()
        #data1 = data.replace("’" , "&apos;")
        #data2 = data1.replace("•", "&#8226;")
        #data = data2
        #data1 = data.replace("&lt;" , "<")
        #data2 = data1.replace("&gt;" , ">")
        #data1 = data2.replace("&apos;" , "'")
        #data2 = data1.replace("&amp;" , "&")
        #data = data2.replace("&quot;" , '"')
        print "\nRAW RETURN DATA\n" + data + "\n" # T_E_D
        conn.close()
        print "PARISING DATA...\n"
        responseDOM = parseString(data)

        # check for any <Error> tags and print
        # TODO: Return a real exception and log when this happens
        try:
            tag = responseDOM.getElementsByTagName('Errors')
            if (tag.count!=0):
                for error in tag:
                    #if type(error) == str:
                    #    # Ignore errors even if the string is not proper UTF-8 or has
                    #    # broken marker bytes.
                    #    # Python built-in function unicode() can do this.
                    #    error = unicode(error, "utf-8", errors="ignore")
                    #else:
                    #    # Assume the value object has proper __unicode__() method
                    #    error = unicode(error)
                    #error.encode('ascii', 'ignore')
                    print "\n",error.toprettyxml("  ")
                    #print error.data()
            print "errors check complete."
        except:
            PrintException()
        return responseDOM

    def GenerateHeaders(self, Session, CallName):
        headers = {"X-EBAY-API-COMPATIBILITY-LEVEL": "613",
                   "X-EBAY-API-SESSION-CERTIFICATE": Session.Developer + ";" + Session.Application + ";" + Session.Certificate,  
                   "X-EBAY-API-DEV-NAME": Session.Developer,
                   "X-EBAY-API-APP-NAME": Session.Application,
                   "X-EBAY-API-CERT-NAME": Session.Certificate,
                   "X-EBAY-API-CALL-NAME": CallName,
                   "X-EBAY-API-SITEID": self.SiteID,
                   "X-EBAY-API-DETAIL-LEVEL": self.DetailLevel,
                   "Content-Type": "text/xml; charset=utf-8"}
        return headers



def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)


