"""" Main process for Crossroads """
# Imports
import linecache
import sys #, os
import xmltodict
import flask
from flask import Flask, Blueprint, render_template, request, redirect, abort, flash
from flask import url_for, abort, session, json, jsonify, Response, make_response
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_wtf import Form
from wtforms import BooleanField, TextField, SelectField, PasswordField, validators, RadioField, SelectMultipleField, TextAreaField, BooleanField, SubmitField, ValidationError
from wtforms.validators import Required
import wtforms_json
from wtforms_json import flatten_json, InvalidData

from jinja2 import TemplateNotFound
from itsdangerous import URLSafeTimedSerializer
from functools import wraps
from werkzeug.exceptions import default_exceptions, HTTPException
from werkzeug import ImmutableMultiDict, MultiDict

from logentries import LogentriesHandler
try:
    import logging
except ImportError:
    print "UNABLE TO LOAD LOGGING LIB"
import time
import datetime
from datetime import timedelta

# Custom Imports
import ebay_new
from forms import ContactForm, EbayStoreForm, ActiveEditForm
#import sha2
import hashlib

import re
import md5
import base64
#print dir(logging)

from urlparse import urlparse

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import json

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

errors = Blueprint('errors', __name__, template_folder='templates/errors')
auth = Blueprint('auth', __name__, template_folder='templates/auth')
app = Flask(__name__)
domain = ""

wtforms_json.init()

# Configurations
app.config.from_object('config')
app.config.update(
    REMEMBER_COOKIE_DURATION = timedelta(hours=app.config["COOKIE_TIME"]),
    TODAY = datetime.date.today(),
    YEAR = datetime.date.today().year
)
log = logging.getLogger(__name__) #logging.getLogger('logentries')
log.setLevel(logging.INFO)
#test = LogentriesHandler('d1fc594b-4438-42a7-b2df-c0068c8ea910') #str(app.config["LOG_TOKEN"]))
#log.addHandler(test)

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

##################################################
# ERROR HANDLERS
##################################################
def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)




@app.errorhandler(400)
def bad_request(e):
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    PAGENAME = "400 Error for ",
    TITLE = " - the forbidden city" + str(domain),
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "")
    PrintException()
    log.error("400 ERROR:" + str(e))
    if request_wants_json():
        return make_response(jsonify({'error': 'Bad Request.'}), 400)
    else:
        return flask.render_template('errors/400.html', app=app), 400



@app.errorhandler(403)
def forbidden(e):
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    PAGENAME = "403 Error for ",
    TITLE = "" + str(domain),
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "")
    PrintException()
    log.error("403 ERROR:" + str(e))
    if request_wants_json():
        return make_response(jsonify({'error': 'Forbidden'}), 403)
    else:
        return flask.render_template('errors/403.html', app=app), 403



@app.errorhandler(404)
def page_not_found(e):
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    PAGENAME = "404 Error for ",
    TITLE = "" + str(domain),
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "")
    PrintException()
    log.error(" 404 ERROR FOR (" + str(request.headers.get("Referer")) + "):" + str(e))
    if request_wants_json():
        return make_response(jsonify({'error': 'Not found'}), 404)
    else:
        return flask.render_template('errors/404.html', app=app), 404





@app.errorhandler(410)
def missing_resource(e):
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    PAGENAME = "410 Error for ",
    TITLE = "" + str(domain),
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "")
    PrintException()
    log.error("410 ERROR:" + str(e))
    if request_wants_json():
        return make_response(jsonify({'error': 'Resource/Location is gone.'}), 410)
    else:
        return flask.render_template('errors/410.html', app=app), 410



@app.errorhandler(500)
def internal_error(e):
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    PAGENAME = "500 Error for ",
    TITLE = "" + str(domain),
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "")
    PrintException()
    log.error(" ERROR:" + str(e))
    if request_wants_json():
        return make_response(jsonify(e.to_dict()), 500)
    else:
        return flask.render_template('errors/500.html', app=app), 500



@app.errorhandler(Exception)
def exception_handler(error):
    print "*** EXCEPTION HANDLER ***"
    PrintException()
    print "*****************"
    log.error(" EXPEPTION ERROR: " + str(repr(error)) )
    PrintException()
    if request_wants_json():
        return make_response(jsonify(error.to_dict()), 500)
    else:
        #return "!!!! "  + repr(error)
        return flask.render_template('errors/500.html', app=app), 500


# Register blueprint(s)
app.register_blueprint(errors)


# Build the database:
# This will create the database file using SQLAlchemy
#db.create_all()




tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]


##################################################
# request_wants_json
# CHECK HEADER FOR TYPE
# IF JSON return True
# Otherwise False
##################################################
def request_wants_json():
    """ Check header for type """
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']


##################################################
# indent
# Given a level indent elemnts in given objectE
##################################################
def indent(elem, level=0):
    """Do an indent for xml object """
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def is_email_address_valid(email):
    """Validate the email address using a regex."""
    if not re.match("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$", email):
        return False
    return True


##################################################
# hash_pass
# Hash routine --encryption based on config value
##################################################
def hash_pass(password):
    """
    Return the  APP.HASH hash of the password+salt
    """
    #print sha2.sha256('Can you keep a secret?').hexdigest()
    h = hashlib.new(app.config["HASH"])
    salted_password = password + app.secret_key
    h.update(salted_password)
    #log.info(app.config["LOG_TOKEN"] + " " + h.hexdigest())
    return h.hexdigest()  #md5.new(salted_password).hexdigest()


##################################################
# User
# Class for User Object
##################################################
class User(UserMixin):
    """User class """
    # proxy for a database of users
    global USERDB
    USERDB = (("teddy@vcommerce.com", hash_pass("bobafett"), "Teddy", "Benson", "AgAAAA**AQAAAA**aAAAAA**cMsBVQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wJlYGhC5SAqQmdj6x9nY+seQ**j70CAA**AAMAAA**8C79zRs8jk5reI5YP7fgF4GoGLvO/q93k7vfirqnZfeGllMA+r/RYoENiPTL0OifnN0BsTrZH6g8gNrjDezmj/RCKVLAlnV1/6sDvZvVAxUPjVaGarUnpy5P46lnkoSljOAqni7m/lpUiE1TbDREvovXmWhJ6+hvCMABkEJXi2aMesaeDB5Iwv7Xmds4FXmBdruc8vABCH9kjXf254ZX7aMaWOgPEaxWDS2XGjNiMas2jkqDFhzZEH6BoOo2TrhOBNczornXgan+WMFUGuyLc0sp08UEVGcQn96N+NO+/c9pilUXid5KemVeWztFSYNaZAyMcu7Fhz3F/I043xPkZvU0ZNj4HHmlxoKqM7p8ziPqhu/d607GHhy4R91ZvztZPhBkMlEp/TAvKUNRv70UoKdxan3sO3qCvyFYaXtyNUcQNlXFUewFSF8viF80A+zXnFKN0nB5bgeZcpUslVhPPePtcj+khXg5FBAN4KHuWEPfYu/ZroYZ2zwkwXpXOM5NYeoR/DllC/i/NpGY8P6GE+oV3ogrgJAayjKZl0SxuK24zd7FF7JDnA0jBjvUThKqA/llp92nz6jtfmR6XoQbJjI671pWpooxjc6xEafUGZUL0yG3GbpFMCSLvqGD/w/pb6B0SVxxU0RZZyk7mL/e44IRG19MsAA6YthZXbL+wfxE2HmKhszIYI8WoejZBYvVlgaIY4Wu8qpJaZGOEc4yQJVbAjjdOCJEhMIKwC/dMYD82K+YvQDeRJkZN9ZWFoDC"),
            ("rob@vcommerce.com", hash_pass("youknowbest"), "Rob", "Wight", "AgAAAA**AQAAAA**aAAAAA**cMsBVQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wJlYGhC5SAqQmdj6x9nY+seQ**j70CAA**AAMAAA**8C79zRs8jk5reI5YP7fgF4GoGLvO/q93k7vfirqnZfeGllMA+r/RYoENiPTL0OifnN0BsTrZH6g8gNrjDezmj/RCKVLAlnV1/6sDvZvVAxUPjVaGarUnpy5P46lnkoSljOAqni7m/lpUiE1TbDREvovXmWhJ6+hvCMABkEJXi2aMesaeDB5Iwv7Xmds4FXmBdruc8vABCH9kjXf254ZX7aMaWOgPEaxWDS2XGjNiMas2jkqDFhzZEH6BoOo2TrhOBNczornXgan+WMFUGuyLc0sp08UEVGcQn96N+NO+/c9pilUXid5KemVeWztFSYNaZAyMcu7Fhz3F/I043xPkZvU0ZNj4HHmlxoKqM7p8ziPqhu/d607GHhy4R91ZvztZPhBkMlEp/TAvKUNRv70UoKdxan3sO3qCvyFYaXtyNUcQNlXFUewFSF8viF80A+zXnFKN0nB5bgeZcpUslVhPPePtcj+khXg5FBAN4KHuWEPfYu/ZroYZ2zwkwXpXOM5NYeoR/DllC/i/NpGY8P6GE+oV3ogrgJAayjKZl0SxuK24zd7FF7JDnA0jBjvUThKqA/llp92nz6jtfmR6XoQbJjI671pWpooxjc6xEafUGZUL0yG3GbpFMCSLvqGD/w/pb6B0SVxxU0RZZyk7mL/e44IRG19MsAA6YthZXbL+wfxE2HmKhszIYI8WoejZBYvVlgaIY4Wu8qpJaZGOEc4yQJVbAjjdOCJEhMIKwC/dMYD82K+YvQDeRJkZN9ZWFoDC"),
            ("risa@mycuteroom.com", hash_pass("r1sawight"), "Risa", "Wight", "AgAAAA**AQAAAA**aAAAAA**cMsBVQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wJlYGhC5SAqQmdj6x9nY+seQ**j70CAA**AAMAAA**8C79zRs8jk5reI5YP7fgF4GoGLvO/q93k7vfirqnZfeGllMA+r/RYoENiPTL0OifnN0BsTrZH6g8gNrjDezmj/RCKVLAlnV1/6sDvZvVAxUPjVaGarUnpy5P46lnkoSljOAqni7m/lpUiE1TbDREvovXmWhJ6+hvCMABkEJXi2aMesaeDB5Iwv7Xmds4FXmBdruc8vABCH9kjXf254ZX7aMaWOgPEaxWDS2XGjNiMas2jkqDFhzZEH6BoOo2TrhOBNczornXgan+WMFUGuyLc0sp08UEVGcQn96N+NO+/c9pilUXid5KemVeWztFSYNaZAyMcu7Fhz3F/I043xPkZvU0ZNj4HHmlxoKqM7p8ziPqhu/d607GHhy4R91ZvztZPhBkMlEp/TAvKUNRv70UoKdxan3sO3qCvyFYaXtyNUcQNlXFUewFSF8viF80A+zXnFKN0nB5bgeZcpUslVhPPePtcj+khXg5FBAN4KHuWEPfYu/ZroYZ2zwkwXpXOM5NYeoR/DllC/i/NpGY8P6GE+oV3ogrgJAayjKZl0SxuK24zd7FF7JDnA0jBjvUThKqA/llp92nz6jtfmR6XoQbJjI671pWpooxjc6xEafUGZUL0yG3GbpFMCSLvqGD/w/pb6B0SVxxU0RZZyk7mL/e44IRG19MsAA6YthZXbL+wfxE2HmKhszIYI8WoejZBYvVlgaIY4Wu8qpJaZGOEc4yQJVbAjjdOCJEhMIKwC/dMYD82K+YvQDeRJkZN9ZWFoDC"),
            ("kari@vcommerce.com", hash_pass("vcommerce"), "Kari", "Calderon", "AgAAAA**AQAAAA**aAAAAA**cMsBVQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wJlYGhC5SAqQmdj6x9nY+seQ**j70CAA**AAMAAA**8C79zRs8jk5reI5YP7fgF4GoGLvO/q93k7vfirqnZfeGllMA+r/RYoENiPTL0OifnN0BsTrZH6g8gNrjDezmj/RCKVLAlnV1/6sDvZvVAxUPjVaGarUnpy5P46lnkoSljOAqni7m/lpUiE1TbDREvovXmWhJ6+hvCMABkEJXi2aMesaeDB5Iwv7Xmds4FXmBdruc8vABCH9kjXf254ZX7aMaWOgPEaxWDS2XGjNiMas2jkqDFhzZEH6BoOo2TrhOBNczornXgan+WMFUGuyLc0sp08UEVGcQn96N+NO+/c9pilUXid5KemVeWztFSYNaZAyMcu7Fhz3F/I043xPkZvU0ZNj4HHmlxoKqM7p8ziPqhu/d607GHhy4R91ZvztZPhBkMlEp/TAvKUNRv70UoKdxan3sO3qCvyFYaXtyNUcQNlXFUewFSF8viF80A+zXnFKN0nB5bgeZcpUslVhPPePtcj+khXg5FBAN4KHuWEPfYu/ZroYZ2zwkwXpXOM5NYeoR/DllC/i/NpGY8P6GE+oV3ogrgJAayjKZl0SxuK24zd7FF7JDnA0jBjvUThKqA/llp92nz6jtfmR6XoQbJjI671pWpooxjc6xEafUGZUL0yG3GbpFMCSLvqGD/w/pb6B0SVxxU0RZZyk7mL/e44IRG19MsAA6YthZXbL+wfxE2HmKhszIYI8WoejZBYvVlgaIY4Wu8qpJaZGOEc4yQJVbAjjdOCJEhMIKwC/dMYD82K+YvQDeRJkZN9ZWFoDC"),
            ("shawna@vcommerce.com", hash_pass("4X-roads"), "Shawna", "VanDiepenbos", "AgAAAA**AQAAAA**aAAAAA**RiDeVQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AAkIGnDpiBpg2dj6x9nY+seQ**j70CAA**AAMAAA**JnP5Gg7jLIcEcmdji/Z5b/IJUBFNlg+jQt3j1pMzkU6c57R44Qi0bf1eTqZofF0Cn3NtEn8M4ancFBEOEhyXc+UtWqqEyrvocm5Ppld4qdpuwCJ8qWXjKRvuWmCDjE7x7/Lk2mp3o3j2ga+zv2Q/yzbY/62GG9vEwcss5RJMgtnOhXqhQXPENCR1g/NyWfnMDlplwBl54lWBMPBer4h4IVvbAmhJAyp5DoBCig+9kwSqrVxey5AgaalCYdw5UBY7asilzzTpRrIwf79v5wdtljQbcdFKUX5HD9crNxqAv3cB7NZxpxmdCT6NvQm1CuRnztu31LhYDSZlfxgLepeXVUvhsXxAdoIcUouE6ZviHIrhABlMt6Wgc7lvUlSYM+WV3UJ72WSmYYo+NRlKTeZQTpYcRTnZfGit/FIxlljqyaFoYErz7C1L7bo5BccySLCJFGXYDeUVMpy+mHiO3N3D0pYHLKLyWLZTA5QHTeSdHaYQTMJYJfbfBVLuOLidiqhrcIzy7Oi+wjG2IqCbu89qZhUIypT84hoYAClhFz66l7saVA69alsZd8aosUxyNIU62keImcQCVf2WBCBT15HSQZ1I37o5wKTN6gQ9cSZ9SFMr3T9Jb+XXBWHbD6ao6bPdUP7LVvrioiC7gv2oYRor5eA8ygbYdZ1paZwvGV3k9pShJf+mRmM0W90904HQ/uYBWcrg+DzZRxUK0qEULaS3wR1r+kW/8csZ9HRe0coEy6tVFHqxZYxskdDImdZOfCJY"),
            ("xrsync@cox.net", hash_pass("Cr0$$r0@ds"), "Kari", "Calderon", "AgAAAA**AQAAAA**aAAAAA**IWN3VQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AHl4aoDpaBpQmdj6x9nY+seQ**j70CAA**AAMAAA**PT/ANlinkISBEUola+dVPmCMWVpsD/8L8wAYCQ/8nN1IBXArone+hVnJMEfiJwNZboNZmZN8mDZtju+Io2rz2Z4p/CcmDlp86qEZycMuqI+PVdeaHBkzvnrSVvSE+GLABYA9ZMGNvdDnMKriy2brHkJv46zCKPWbxKFh5Cann7eAag7mPJLMMZ0PUKlnAoDLq3LuqX4ievbYM6tQm36wd0sgFD9u6pyp0nvSxs0ojvumwSgrbzgyPli5bzbe1DIosPf/9b8Vxxx2HrG+AYF50451KcAWVz8hrN8U4L668CcRm0z+/Qe0UuaQyP383Vi0fPu7E9fmcKYAfBOxsaDYtlPHpA+igzeKKTd97Xi/kI5VzPyWQaqm0Obcoo+HtIG7oA+iyxTgWtfSxNqVJSHfVUzR9CnS+JBEaM9XQ2BXb7+5kGvOLIl5svMTCbYEPWjuQsF1KYSX4n5tQSF/ErinOFZWKpY2A3t69dHvc8qP9DBFsvALfDqb+v0L4yZA7iY9FOAjoWqUhlVlCS6cxdf7iDR6J3/b1hcIx2f2FCgHpF7l6cLdJkjWkeR3sAJnS8ax9rFcKKdByEVNBUq4W4Lw1s7z7rpEhborDzyizZ/U+XRRK0JsRZ7S01EKuJVBAUSeqiEbVdoz5ecXPxSNAq/coGTm4Ud1LiJ39ikomZzvxEtySoNyULpvpf34gTPsdbv0TPQMadGjRoOsC+Ja0PmNbs33KffXU1nXZBNynxtZSYzXOMoiCc6jqQk0MSa4tLxJ"),
            ("test@test.com", hash_pass("TEST"), "Mr.", "Tester", "-1"))

    def __init__(self, username, password, first, last, EbayToken):
        self.id = username
        self.password = password
        self.First = first
        self.Last = last
        self.EbayToken = EbayToken

    def get_auth_token(self):
        """
        Encode a secure token for cookie
        """
        data = [str(self.id), self.password]
        return login_serializer.dumps(data)

    @classmethod
    def get(cls, userid):
        """
        Static method to search the database and see if userid exists.  If it
        does exist then return a User Object.  If not then return None as
        required by Flask-Login.
        """
        log.info(" INSIDE USER GET " + str(userid))
        #For this example the USERS database is a list consisting of
        #(user,hased_password, first, last) of users.
        for user in USERDB:
            if user[0].upper() == userid.upper():
                app.config.update(
                EMAIL = user[0],
                FIRST_NAME = user[2],
                LAST_NAME = user[3],
                EBAYTOKEN = user[4])
                return User(user[0], user[1], user[2], user[3], user[4])
        return None


##################################################
# LoginForm
# Check POST input for login page
##################################################
class LoginForm(Form):
    username = TextField('user', [validators.Required()])
    password = PasswordField('password', [validators.Required()])
    rememberme = BooleanField('rememberme', default=True)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        #user = User.query.filter_by(username=self.username.data).first()
        #Find the User
        user = User.get(username=self.username.data)
        if user is None:
            self.username.errors.append('Unknown username')
            return False

        #If we found a user based on username then compare that the submitted
        #password matches the password in the database.  The password is stored
        #is a slated hash format, so you must hash the password before comparing
        #it.
        if not (user and hash_pass(request.form['password']) == user.password):
            self.password.errors.append('Invalid password')
            return False

        login_user(user, remember=rememberme)
        self.user = user
        return True


##################################################
# AUTHENTICATION
##################################################
login_manager = LoginManager()
login_manager.init_app(app)
#Login_serializer used to encrypt and decrypt the cookie token for the remember
#me option of flask-login
login_serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])


@login_manager.user_loader
def load_user(userid):
    """
    Flask-Login user_loader callback.
    The user_loader function asks this function to get a User Object or return
    None based on the userid.
    The userid was stored in the session environment by Flask-Login.
    user_loader stores the returned User object in current_user during every
    flask request.
    """
    return User.get(userid)


@login_manager.token_loader
def load_token(token):
    """
    Flask-Login token_loader callback.
    The token_loader function asks this function to take the token that was
    stored on the users computer process it to check if its valid and then
    return a User Object if its valid or None if its not valid.
    """

    #The Token itself was generated by User.get_auth_token.  So it is up to
    #us to known the format of the token data itself.

    #The Token was encrypted using itsdangerous.URLSafeTimedSerializer which
    #allows us to have a max_age on the token itself.  When the cookie is stored
    #on the users computer it also has a exipry date, but could be changed by
    #the user, so this feature allows us to enforce the exipry date of the token
    #server side and not rely on the users cookie to exipre.
    max_age = app.config["REMEMBER_COOKIE_DURATION"].total_seconds()

    #Decrypt the Security Token, data = [username, hashpass]
    data = login_serializer.loads(token, max_age=max_age)

    #Find the User
    user = User.get(data[0])

    #Check Password and return user or None
    if user and data[1] == user.password:
        return user
    return None


@login_manager.unauthorized_handler
def unauthorized():
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    print "UNAUTHORIZED ACCESS"
    app.config.update(
    TITLE = str(domain),
    PAGETITLE = " Login",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")

    form = LoginForm()
    trusted_proxies = {'127.0.0.1'}  # define your own set
    route = request.access_route + [request.remote_addr]

    remote_addr = next((addr for addr in reversed(route) if addr not in trusted_proxies), request.remote_addr)
    log.info(" REMOTE IP:" + remote_addr)
    if request.headers.getlist("X-Forwarded-For"):
       ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
       ip = request.remote_addr

    log.info(" IP:" + str(ip))
    log.info(" ENVIRON:" + str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr)))
    log.info(" REMOTE_ADDR:" + str(request.remote_addr))
    log.info(" " + str(request))

    rule = request.url_rule
    return flask.render_template('login.html', app=app, url=str(rule.rule), form=form, login_results='You must login in first to go there.')


@app.route('/login/', methods=['GET', 'POST'])
@app.route('/Login/', methods=['GET', 'POST'])
@app.route('/LOGIN/', methods=['GET', 'POST'])
def login_page():
    """
    Web Page to Display Login Form and process form.
    """
    print "LOGIN PAGE"
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    TITLE = str(domain),
    PAGETITLE = " Login",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")

    form = LoginForm()
    
    trusted_proxies = {'127.0.0.1'}  # define your own set
    route = request.access_route + [request.remote_addr]

    remote_addr = next((addr for addr in reversed(route) if addr not in trusted_proxies), request.remote_addr)
    log.info(" REMOTE IP:" + remote_addr)
    if request.headers.getlist("X-Forwarded-For"):
       ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
       ip = request.remote_addr
    log.info(" IP:" + str(ip))
    log.info(" ENVIRON:" + str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr)))
    log.info(" REMOTE_ADDR:" + str(request.remote_addr))
    log.info(" " + str(request))
    
    if request.method == "POST":
        user = User.get(request.form['user'])

        #If we found a user based on username then compare that the submitted
        #password matches the password in the database.  The password is stored
        #is a slated hash format, so you must hash the password before comparing
        #it.
        if user and hash_pass(request.form['password']) == user.password:
            login_user(user, remember=True)
            return redirect(request.args.get("next") or "/home/")

    log.info(" Login Page Loaded...")
    return render_template("login.html", app=app, url="/LOGIN/", form=form, login_results=' ')


@app.route('/login_action/', methods=['GET', 'POST'])
@app.route('/Login_Action/', methods=['GET', 'POST'])
@app.route('/LOGIN_ACTION/', methods=['GET', 'POST'])
def login_action():
    """
    Web Page to process login form.
    """
    print "LOGIN ACTION"
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    TITLE = str(domain),
    PAGETITLE = " Login",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")

    form = LoginForm()

    if request.method == "POST":
        logout_user()
        user = User.get(request.form['user'])

        #If we found a user based on username then compare that the submitted
        #password matches the password in the database.  The password is stored
        #is a slated hash format, so you must hash the password before comparing
        #it.
        if user and hash_pass(request.form['password']) == user.password:
            login_user(user, remember=True)
            rule = request.url_rule
            if '/LOGIN/' in request.form['url'].upper():
                # normal request by 
                print "STANDARD LOGIN REQUEST" + str(request.form['url'])
                return redirect(request.args.get("next") or "/home/")
            else:
                print "(LOGIN ACTION)ACCESS TO PAGE DENINED BY LOGIN " + str(request.form['url'])
                return redirect(request.args.get("next") or str(request.form['url']))

    return render_template("login.html", app=app, url=request.form['url'], form=form, login_results='Your Credentials were Incorrect.')


#Logout function
@app.route('/logout')
@app.route('/Logout')
@app.route('/LOGOUT')
@app.route("/logout")
@login_required
def logout():
    now = time.strftime("%c")
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    TITLE = str(domain),
    PAGETITLE = " Main",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "You have logged out at " + now + " UTC")
    #flask.session.clear()
    logout_user()
    log.info("User Logged out.")
    return flask.render_template('index.html', app=app)


@app.route("/get_my_ip", methods=["GET"])
@app.route("/Get_my_ip", methods=["GET"])
@app.route("/GET_MY_IP", methods=["GET"])
@app.route("/get_my_ip/", methods=["GET"])
@app.route("/Get_my_ip/", methods=["GET"])
@app.route("/GET_MY_IP/", methods=["GET"])
def get_my_ip():
    trusted_proxies = {'127.0.0.1'}  # define your own set
    route = request.access_route + [request.remote_addr]
    remote_addr = next((addr for addr in reversed(route) if addr not in trusted_proxies), request.remote_addr)

    if request.headers.getlist("X-Forwarded-For"):
       ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
       ip = request.remote_addr

    return jsonify(
    {'X-FOR-IP': ip, 
    'REMOTE IP': remote_addr,
    'X-REAL-IP': str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr)), 
    'RAW REMOTE_ADDR': str(request.remote_addr), 
    'REQUEST': str(request)}), 200


@app.route('/')
@app.route('/index')
@app.route('/Index')
@app.route('/INDEX')
def index():
    """ Displays the home page accessible at '/'
    """
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    TITLE = str(domain),
    PAGETITLE = " by VCOMMSYNC",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")

    user_id = (current_user.get_id() or "No User Logged In")
    return flask.render_template('index.html',app=app, user_id=user_id)


@app.route('/home')
@app.route('/Home')
@app.route('/HOME')
@app.route('/home/')
@app.route('/Home/')
@app.route('/HOME/')
@app.route('/main')
@app.route('/Main')
@app.route('/MAIN')
@app.route('/main/')
@app.route('/Main/')
@app.route('/MAIN/')
@login_required
def home():
    """ Displays the home page accessible at '/'
    """
    print "HOME"
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    TITLE = str(domain),
    PAGETITLE = "Home",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")

    return flask.render_template('home.html', app=app)


@app.route('/contact/', methods=['GET', 'POST'])
@app.route('/Contact/', methods=['GET', 'POST'])
@app.route('/CONTACT/', methods=['GET', 'POST'])
def contact():
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    TITLE = str(domain),
    PAGETITLE = "Contact",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")

    form = ContactForm()
    print form.errors
    print request.method
    if form.is_submitted():
        print "submitted"
    if form.validate():
        print "valid"
    if request.method == 'POST':
        print "IN POST for contact "
        if not form.validate_on_submit():
        #if form.validate() == False:
            flash('All fields are required.')
            return render_template('contact.html', app=app, form=form)
        else:
            return 'Contact Form posted.'
    elif request.method == 'GET':
        print "IN GET for contact"
        return render_template('contact.html', app=app, form=form)


@app.route('/help')
@app.route('/Help')
@app.route('/HELP')
def help():
    """ Displays the help page accessible at '/'
    """
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    TITLE = str(domain),
    PAGETITLE = "Help",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")

    user_id = (current_user.get_id() or "No User Logged In")
    return flask.render_template('help.html',app=app, user_id=user_id)


@app.route('/faq')
@app.route('/Faq')
@app.route('/FAQ')
def FAQ():
    """ Displays the FAQ page accessible at '/'
    """
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    TITLE = str(domain),
    PAGETITLE = "FAQ",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")

    user_id = (current_user.get_id() or "No User Logged In")
    return flask.render_template('faq.html',app=app, user_id=user_id)


@app.route('/myorders')
@app.route('/Myorders')
@app.route('/MYORDERS')
def myorders():
    """ Displays the myorders page accessible at '/'
    """
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    TITLE = str(domain),
    PAGETITLE = "MyOrders",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")

    user_id = (current_user.get_id() or "No User Logged In")
    return flask.render_template('myorders.html',app=app, user_id=user_id)


@app.route('/settings')
@app.route('/Settings')
@app.route('/SETTINGS')
def settings():
    """ Displays the settings page accessible at '/'
    """
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    TITLE = str(domain),
    PAGETITLE = "Settings",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")

    user_id = (current_user.get_id() or "No User Logged In")
    return flask.render_template('settings.html',app=app, user_id=user_id)


@app.route('/ebaystore/', methods=['GET', 'POST'])
@app.route('/Ebaystore/', methods=['GET', 'POST'])
@app.route('/EBAYSTORE/', methods=['GET', 'POST'])
@login_required
def ebaystore():

    class opt:
        debug = True
        list = ""
        days = 120

    opts = opt()
    opts.list = True

    session = ebay_new.Session()
    session.Initialize() #(opts, FilePath, "Production")

    print "\n\n\n\n\n###############################################################################"
    print "Runame: " + str(app.config["EBAY_RUNAME"])
    print "EMAIL: " + str(app.config["EMAIL"])
    print "app.config['EBAYTOKEN']: " + str(app.config["EBAYTOKEN"])
    print "app.config['EBAYSESSIONID']: " + str(app.config["EBAYSESSIONID"])
    print "###############################################################################\n"

    if app.config["EBAYTOKEN"] != "-1":
        parsed_uri = urlparse(request.url_root)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        if domain.find('-stage') > 0:
            domain = "STAGING"
        else:
            domain = "Crossroads"
        app.config.update(
        TITLE = str(domain),
        PAGETITLE = "eBay Store Configuration",
        MYPRODUCTS = "",
        MYORDERS = "",
        MYSTORES = "text-danger",
        MYSUPPLIERS = "",
        LASTPAGE = "",
        MESSAGE = "")
        return render_template('ebaystore.html', app=app)
    else:
        print "*** CHECK FOR SESSION ID ***"
        #session = ebay_new.Session()
        #session.Initialize() #(opts, FilePath, "Production")
        print "app.config['EBAYSESSIONID']: " + str(app.config["EBAYSESSIONID"])
        if app.config["EBAYSESSIONID"] == "-1":
            sessionID = ebay_new.GetSessionID()
            session.SessionID  = str(sessionID.Get(opts))
            app.config.update(EBAYSESSIONID = session.SessionID)
            print "app.config['EBAYSESSIONID']: " + str(app.config["EBAYSESSIONID"])

            URL = "https://signin.ebay.com/ws/eBayISAPI.dll?SignIn&RuName=" + app.config["EBAY_RUNAME"] + "&SessID=" + str(session.SessionID)

            print "Runame: " + str(app.config["EBAY_RUNAME"])
            print str(app.config["EMAIL"]) + " session.SessionID: " + str(session.SessionID)
            print "URL: " + str(URL)

            #Get SessionID
            #Send user to Ebay to confirm access
            #RETURN URL SHOULD SNED USER BACK -- REQUIRES SSL SO WE WILL DEFAULT TO EBAYS PAGE.
            #https://signin.ebay.com/ws/eBayISAPI.dll?SignIn&RuName=app.config["EBAY_RUNAME"]&SessID=YourSessionIDHere

            return redirect(URL, code=302) #'Ebaystore Form posted.'  #redirect(URL, code=302)

        else:
            session.SessionID  = str(app.config["EBAYSESSIONID"])
            #Check to see if this is a new Session ID so fetch Token
            FetchToken = ebay_new.FetchToken(session.SessionID)
            session.Token = FetchToken.Get(opts)
            print "FETCH TOKEN GOT IT:---->" + str(session.Token)
            
            if session.Token != -1:
                parsed_uri = urlparse(request.url_root)
                domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
                if domain.find('-stage') > 0:
                    domain = "STAGING"
                else:
                    domain = "Crossroads"
                app.config.update(
                TITLE = str(domain),
                PAGETITLE = "eBay Store Configuration",
                MYPRODUCTS = "",
                MYORDERS = "",
                MYSTORES = "text-danger",
                MYSUPPLIERS = "",
                LASTPAGE = "",
                MESSAGE = "",
                EBAYTOKEN = session.Token)
                return render_template('ebaystore.html', app=app)

        if request.method == 'POST':

            URL = "https://signin.ebay.com/ws/eBayISAPI.dll?SignIn&RuName=" + app.config["EBAY_RUNAME"] + "&SessID=" + str(session.SessionID)

            print "Runame: " + str(app.config["EBAY_RUNAME"])
            print str(app.config["EMAIL"]) + " session.SessionID: " + str(session.SessionID)
            print "URL: " + str(URL)

            #Get SessionID
            #Send user to Ebay to confirm access
            #RETURN URL SHOULD SNED USER BACK -- REQUIRES SSL SO WE WILL DEFAULT TO EBAYS PAGE.
            #https://signin.ebay.com/ws/eBayISAPI.dll?SignIn&RuName=app.config["EBAY_RUNAME"]&SessID=YourSessionIDHere

            return redirect(URL, code=302) #'Ebaystore Form posted.'  #redirect(URL, code=302)

        elif request.method == 'GET':
            parsed_uri = urlparse(request.url_root)
            domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
            if domain.find('-stage') > 0:
                domain = "STAGING"
            else:
                domain = "Crossroads"
            app.config.update(
            TITLE = str(domain),
            PAGETITLE = "eBay Store Setup",
            MYPRODUCTS = "",
            MYORDERS = "",
            MYSTORES = "text-danger",
            MYSUPPLIERS = "",
            LASTPAGE = "",
            MESSAGE = "")
            form = EbayStoreForm()
            return render_template('ebaystore_new.html', app=app, form=form)


@app.route('/signup')
@app.route('/Signup')
@app.route('/SIGNUP')
@app.route('/register')
@app.route('/Register')
@app.route('/REGISTER')
@app.route('/signup/')
@app.route('/Signup/')
@app.route('/SIGNUP/')
@app.route('/register/')
@app.route('/Register/')
@app.route('/REGISTER/')
def signup():
    """ Displays the signup page accessible at '/'
    """
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    TITLE = str(domain),
    PAGETITLE = "Signup",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")

    return flask.render_template('register.html', app=app)


@app.route('/ebay_risa_test')
def ebay_risa_test():
    """ Displays the index page accessible at '/'
    """
    return flask.render_template('ebay_risa_test.html', title='Ebay Risa Test')


@app.route('/ebay_test')
def ebay_test():
    """ Displays the index page accessible at '/'
    """
    return flask.render_template('ebay_test.html', title='Ebay Search Test')


@app.route('/ebay')
@app.route('/Ebay')
@app.route('/EBAY')
def ebay():
    """Ebay"""
    dump = ""
    class opt:
        debug = False
        list = ""

    opts = opt()
    opts.list = True

    userinfo = ""
    try:
        session = ebay_new.Session()
        session.Initialize()

        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=120)
        end = str(end).replace(" ", "T", 1) + "Z" #.strftime('%Y-%M-%D %H:%M:%S:%f')
        start = str(start).replace(" ", "T", 1) + "Z" #.strftime('%Y-%M-%D %H:%M:%S:%f')

        #Token, Start, End, Page
        GetSellerList = ebay_new.GetSellerList(app.Risa, start, end, app.Page)
        userinfo = str(GetSellerList.Get(opts))

        return flask.render_template('ebay_user.html', userinfo=userinfo, title='Ebay User')
    except:
        #dump += e
        dump += "ERROR"
        return dump


@app.route('/api/v1.0/JSON_EBAY-LIST_API', methods=['GET'])
@app.route('/api/v1.0/json_ebay-list_api', methods=['GET'])
@app.route('/api/v1.0/Json_Ebay-List_Api', methods=['GET'])
@app.route('/api/v1.0/JSON_EBAY-LIST_API', methods=['POST'])
@app.route('/api/v1.0/json_ebay-list_api', methods=['POST'])
@app.route('/api/v1.0/Json_Ebay-List_Api', methods=['POST'])
def json_ebay_list_api():
    """JSON API"""
    #if not request.json:
    #    abort(400)

    class opt:
        debug = False
        list = ""
        days = 120

    opts = opt()
    opts.list = True

    listdata = ""
    listdict = {}
    
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    TITLE = "",
    PAGETITLE = "",
    PAGENAME = "",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")

    try:
        session = ebay_new.Session()
        session.Initialize()

        end = datetime.datetime.now()
        #end = end - datetime.timedelta(days = 60)
        start = end - datetime.timedelta(days=opts.days)
        end = str(end).replace(" ", "T", 1) + "Z" #.strftime('%Y-%M-%D %H:%M:%S:%f')
        start = str(start).replace(" ", "T", 1) + "Z" #.strftime('%Y-%M-%D %H:%M:%S:%f')

        GetSellerList = ebay_new.GetSellerList(app.config["EBAYTOKEN"], start, end, app.config["PAGE"])
        listdata = GetSellerList.Get(opts).replace("{urn:ebay:apis:eBLBaseComponents}", "")

        root = ET.ElementTree(ET.fromstring(listdata)).getroot()
        listdata = ""
        listdata = '{ "data": [ '
        flag = 0
        ItemCount = 0
        for node in root.findall(".//{urn:ebay:apis:eBLBaseComponents}ItemArray//{urn:ebay:apis:eBLBaseComponents}Item"):
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
                        Price = nlist[0].text

                    if child.tag == "{urn:ebay:apis:eBLBaseComponents}Listingstatus":
                        Listingstatus = child.text
                    if child.tag == "{urn:ebay:apis:eBLBaseComponents}HasUnansweredQuestions":
                        Questions = child.text
                if flag == 1:
                    listdata += ", "
                flag = 1
                listdata += '{ "PictureURL": "' + Picture.replace('"', '\\"') + '", '
                listdata += '"SKU": "' + SKU.replace('"', '\\"') + '", '
                listdata += '"Title": "' + Title.replace('"', '\\"') + '", '
                listdata += '"Price": "' + Price.replace('"', '\\"') + '", '
                listdata += '"Amazon": "' + Amazon.replace('"', '\\"') + '", '
                listdata += '"eBay": "' + eBay.replace('"', '\\"') + '", '
                listdata += '"Etsy": "' + Etsy.replace('"', '\\"') + '", '
                listdata += '"ItemID": "' + ItemID.replace('"', '\\"') + '" } '

        listdata += '] }'

#        x2 = xml2.xml2()
#        x2.Initialize(listdata, "xml2json", 1)


    except IOError as (errno, strerror):
        log.error(" I/O error({0}): {1}".format(errno, strerror))
    except ValueError:
        log.error(" No valid integer in line.")
    except:
        log.error(" Unexpected error:", sys.exc_info()[0])
        for error in sys.exc_info():
            log.error(" " + error)
    #finally:
        #listdata = "ERROR"
    return listdata


@app.route('/api/v1.0/JSON_EBAY-INV_API', methods=['GET'])
@app.route('/api/v1.0/json_ebay-inv_api', methods=['GET'])
@app.route('/api/v1.0/Json_Ebay-Inv_Api', methods=['GET'])
@app.route('/api/v1.0/JSON_EBAY-INV_API', methods=['POST'])
@app.route('/api/v1.0/json_ebay-inv_api', methods=['POST'])
@app.route('/api/v1.0/Json_Ebay-Inv_Api', methods=['POST'])
def json_ebay_inv_api():
    """JSON INV API"""
    #if not request.json:
    #    abort(400)

    class opt:
        debug = False
        list = ""
        days = 120

    opts = opt()
    opts.list = True

    listdata = ""
    listdict = {}
    
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    TITLE = "",
    PAGETITLE = "",
    PAGENAME = "",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")

    try:
        session = ebay_new.Session()
        session.Initialize()

        session.Page = "200"
        session.PageNum = 1
        flag = 0
        GetSellingManagerInventory = ebay_new.GetSellingManagerInventory(\
        app.config["EBAYTOKEN"], session.Page, session.PageNum)
        if opts.debug:
            log.info(" " + str(SessionObj.debug))

        listdata = str(GetSellingManagerInventory.Get(opts))
        #print str(listdata)
        root = ET.ElementTree(ET.fromstring(listdata)).getroot()
        listdata = ""
        Timestamp = ""
        Ack = ""
        Version = ""
        ProductName = ""
        ProductID = ""
        QuantityAvailable = ""
        UnitCost = ""
        FolderID = ""
        QuantityScheduled = ""
        QuantitySold = ""
        SuccessPercent = ""
        TotalNumberOfPages = ""
        TotalNumberOfEntries = ""
        listdata = '{ "data": [ '
        for node in root:
            if node.tag == "{urn:ebay:apis:eBLBaseComponents}Timestamp":
                Timestamp = str(node.text).replace('"', '\\"')
            if node.tag == "{urn:ebay:apis:eBLBaseComponents}Ack":
                Ack = str(node.text).replace('"', '\\"')
            if node.tag == "{urn:ebay:apis:eBLBaseComponents}Version":
                Version = str(node.text).replace('"', '\\"')

        for elem in root.iter('{urn:ebay:apis:eBLBaseComponents}PaginationResult'):
            for child in elem:
                if child.tag == "{urn:ebay:apis:eBLBaseComponents}TotalNumberOfPages":
                    TotalNumberOfPages = str(child.text).replace('"', '\\"')
                if child.tag == "{urn:ebay:apis:eBLBaseComponents}TotalNumberOfEntries":
                    TotalNumberOfEntries = str(child.text).replace('"', '\\"')

        for elem in root.iter('{urn:ebay:apis:eBLBaseComponents}SellingManagerProduct'):
            if flag == 1:
                listdata += ', '
            else:
                flag = 1
            for child in elem:
                if child.tag == "{urn:ebay:apis:eBLBaseComponents}SellingManagerProductDetails":
                    for e in child:
                        if e.tag == "{urn:ebay:apis:eBLBaseComponents}ProductName":
                            ProductName = str(e.text).replace('"', '\\"')
                        if e.tag == "{urn:ebay:apis:eBLBaseComponents}ProductID":
                            ProductID = str(e.text).replace('"', '\\"')
                        if e.tag == "{urn:ebay:apis:eBLBaseComponents}QuantityAvailable":
                            QuantityAvailable = str(e.text).replace('"', '\\"')
                        if e.tag == "{urn:ebay:apis:eBLBaseComponents}UnitCost":
                            UnitCost = str(e.text).replace('"', '\\"')
                        if e.tag == "{urn:ebay:apis:eBLBaseComponents}FolderID":
                            FolderID = str(e.text).replace('"', '\\"')

                if child.tag == "{urn:ebay:apis:eBLBaseComponents}QuantityScheduled":
                    QuantityScheduled = str(child.text).replace('"', '\\"')
                if child.tag == "{urn:ebay:apis:eBLBaseComponents}QuantityActive":
                    QuantityScheduled = str(child.text).replace('"', '\\"')
                if child.tag == "{urn:ebay:apis:eBLBaseComponents}QuantitySold":
                    QuantitySold = str(child.text).replace('"', '\\"')
                if child.tag == "{urn:ebay:apis:eBLBaseComponents}QuantityUnsold":
                    QuantityUnsold = str(child.text).replace('"', '\\"')
                if child.tag == "{urn:ebay:apis:eBLBaseComponents}SuccessPercent":
                    SuccessPercent = str(child.text).replace('"', '\\"')

            listdata += '{ "ProductName": "' + ProductName + '", "ProductID": "' + ProductID
            listdata += '", "QuantityAvailable": "' + QuantityAvailable + '",  "UnitCost": "' + \
            UnitCost + '", "FolderID": "' + FolderID + '"}'
            ProductName = ""
            ProductID = ""
            QuantityAvailable = ""
            UnitCost = ""
            FolderID = ""
        listdata += '] }'

    except IOError as (errno, strerror):
        log.error(" I/O error({0}): {1}".format(errno, strerror))
    except ValueError:
        log.error(" No valid integer in line.")
    except:
        log.error(" Unexpected error:", sys.exc_info()[0])
        for error in sys.exc_info():
            log.error(" " + error)
    #finally:
        #listdata = "ERROR"
    return listdata




@app.route('/api/v1.0/JSON_EBAY-ACTIVE_API', methods=['GET'])
@app.route('/api/v1.0/json_ebay-active_api', methods=['GET'])
@app.route('/api/v1.0/Json_Ebay-Active_Api', methods=['GET'])
@app.route('/api/v1.0/JSON_EBAY-ACTIVE_API', methods=['POST'])
@app.route('/api/v1.0/json_ebay-active_api', methods=['POST'])
@app.route('/api/v1.0/Json_Ebay-Active_Api', methods=['POST'])
def json_ebay_active_api():
    """JSON ACTIVE API"""
    #print "content_type: ", str(request.content_type)
    #print "request.json: ", str(request.json)
    #print "RWJ0: " + str(request_wants_json())
    #print "Request: " + str(request.data)
    if not request_wants_json():
        #abort(400)
        abort(400, {'errors': dict(error="Not a valid JSON request")})
    #print request.json['webURL']
    #if not request.json:
    #    abort(400)

    class opt:
        debug = False
        list = ""
        days = 120

    opts = opt()
    opts.list = True

    listdata = ""
    listdict = {}
    
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    TITLE = "",
    PAGETITLE = "",
    PAGENAME = "",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")

    resp = ""
    try:
        session = ebay_new.Session()
        session.Initialize()

        session.Page = "200"
        session.PageNum = 1
        if request.json['token']:
            session.Token = request.json['token']
        if session.Page:
            session.Page = request.json['page']
        if session.PageNum:
            session.PageNum = int(request.json['pagenum'])

        listdata = '{ "data": [ '
        flag = 0
        ItemCount = 0
        Timestamp = "infinite"
        Ack = "NONE"
        Version = "x.xx"
        TotalNumberOfPages = 1
        TotalNumberOfEntries = "NONE"

        while int(session.PageNum) <= int(TotalNumberOfPages):
            GetMyeBaySelling = ebay_new.GetMyeBaySelling(\
            session.Token, session.Page, session.PageNum)
            #print "Session.Page: " + str(Session.Page)
            #print "Session.PageNum: " + str(Session.PageNum)
            #print "TNOP: " + str(TotalNumberOfPages)
            #print "TNOE: " + str(TotalNumberOfEntries)
            rawdata = GetMyeBaySelling.Get(opts).replace("{urn:ebay:apis:eBLBaseComponents}", "")
            #print str(rawdata)
            root = ET.ElementTree(ET.fromstring(rawdata)).getroot()
            dump = session.PageNum + 1
            session.PageNum = dump

            for elem in root.iter('{urn:ebay:apis:eBLBaseComponents}PaginationResult'):
                for child in elem:
                    if child.tag == "{urn:ebay:apis:eBLBaseComponents}TotalNumberOfPages":
                        TotalNumberOfPages = str(child.text).replace('"', '\\"')
                    if child.tag == "{urn:ebay:apis:eBLBaseComponents}TotalNumberOfEntries":
                        TotalNumberOfEntries = str(child.text).replace('"', '\\"')

            for node in root:
                if node.tag == "{urn:ebay:apis:eBLBaseComponents}Timestamp":
                    Timestamp = str(node.text).replace('"', '\\"')
                if node.tag == "{urn:ebay:apis:eBLBaseComponents}Ack":
                    Ack = str(node.text).replace('"', '\\"')
                if node.tag == "{urn:ebay:apis:eBLBaseComponents}Version":
                    Version = str(node.text).replace('"', '\\"')

            if Ack == "Success":
                for node in root.findall(".//{urn:ebay:apis:eBLBaseComponents}ItemArray//{urn:ebay:apis:eBLBaseComponents}Item"):
                    ItemID = ""
                    SKU = "NONE"
                    ViewItemURL = ""
                    Title = ""
                    Quantity = ""
                    ConditionDescription = ""
                    StartTime = ""
                    EndTime = ""
                    Quantity = ""
                    MinBid = ""
                    eBay = 0
                    Amazon = -1
                    Etsy = 0
                    ItemCount += 1
                    #print node.tag
                    if node.tag == "{urn:ebay:apis:eBLBaseComponents}Item":
                        #print "\n\n\nNODE: " + node.tag
                        for child in node:
                            #print "CHILD: " + child.tag
                            if child.tag == "{urn:ebay:apis:eBLBaseComponents}ItemID":
                                ItemID = child.text
                            if child.tag == "{urn:ebay:apis:eBLBaseComponents}SKU":
                                SKU = child.text
                            if child.tag == "{urn:ebay:apis:eBLBaseComponents}Title":
                                Title = child.text
                            if child.tag == "{urn:ebay:apis:eBLBaseComponents}QuantityAvailable":
                                Quantity = child.text
                            if child.tag == "{urn:ebay:apis:eBLBaseComponents}PictureDetails":
                                nlist = child.findall("{urn:ebay:apis:eBLBaseComponents}GalleryURL")
                                Picture = nlist[0].text
                            if child.tag == "{urn:ebay:apis:eBLBaseComponents}SellingStatus":
                                nlist = child.findall(
                                    "{urn:ebay:apis:eBLBaseComponents}CurrentPrice")
                                Price = nlist[0].text
                            if child.tag == "{urn:ebay:apis:eBLBaseComponents}ListingDetails":
                                print "FOUND LISTINGS DETAILS"
                                for child2 in child:
                                    if child2.tag == "{urn:ebay:apis:eBLBaseComponents}ViewItemURL":
                                        ViewItemURL = child2.text
                        if flag == 1:
                            listdata += ", "
                        flag = 1
                        listdata += '{ "PictureURL": "' + Picture.replace('"', '\\"') + '|' + ViewItemURL.replace('"', '\\"') + '", '
                        listdata += '"DT_RowId": "row_' + str(ItemCount) + '", '
                        listdata += '"SKU": "'          + SKU.replace('"', '\\"') + '", '
                        listdata += '"ViewItemURL": "'  + ViewItemURL.replace('"', '\\"') + '", '
                        listdata += '"Title": "'        + Title.replace('"', '\\"') + '", '
                        listdata += '"Price": "'        + Price.replace('"', '\\"') + '", '
                        listdata += '"Quantity": "'     + Quantity.replace('"', '\\"') + '", '
                        listdata += '"Amazon": "'       + str(Amazon) + '", '
                        listdata += '"eBay": "'         + Quantity.replace('"', '\\"') + '", '
                        listdata += '"Etsy": "'         + str(Etsy) + '", '
                        listdata += '"ItemID": "'       + ItemID.replace('"', '\\"') + '" } '
        listdata += '] '
        listdata += ', "header": [ { "Timestamp": "' + str(Timestamp) + '", "Ack": "' + str(Ack)
        listdata += '", "Version": "' + str(Version) + '", "TotalNumberOfPages": "' + \
        str(TotalNumberOfPages)
        listdata += '", "TotalNumberOfEntries": "' + str(TotalNumberOfEntries) + '"} ] }'
        print listdata
        #print "ItemCount: " + str(ItemCount)
        resp = Response(response=listdata, status=200, mimetype="application/json")
    except IOError as (errno, strerror):
        log.error(" I/O error({0}): {1}".format(errno, strerror))
        resp = ""
    except ValueError:
        log.error(" No valid integer in line.")
        resp = ""
    except:
        log.error(" Unexpected error:", sys.exc_info()[0])
        for error in sys.exc_info():
            log.error(" " + error)
        resp = ""
    #finally:
        #listdata = "ERROR"
    return resp
    #return listdata


@app.route('/api/v1.0/JSON_EBAY_ITEM_API', methods=['GET'])
@app.route('/api/v1.0/json_ebay_item_api', methods=['GET'])
@app.route('/api/v1.0/Json_Ebay_Item_Api', methods=['GET'])
@app.route('/api/v1.0/JSON_EBAY_ITEM_API', methods=['POST'])
@app.route('/api/v1.0/json_ebay_item_api', methods=['POST'])
@app.route('/api/v1.0/Json_Ebay_Item_Api', methods=['POST'])
def json_ebay_item_api():
    """JSON ITEM INFO API"""
    #print "content_type: ", str(request.content_type)
    #print "request.json: ", str(request.json)
    #print "RWJ0: " + str(request_wants_json())
    #print "Request: " + str(request.data)
    if not request_wants_json():
        #abort(400)
        #abort(400, {'errors': dict(error="Not a valid JSON request")})
        log.error("400 Error: Not a valid JSON request for JSON_EBAY_ITEM_API")
        return jsonify({'errors': dict(error="Not a valid JSON request")})

    print "IN JSON_EBAY_ITEM_API"
    class opt:
        debug = False
        list = ""
        days = 120

    opts = opt()
    opts.list = True
    opts.debug = False

    listdata = ""
    listdict = {}

    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    TITLE = "",
    PAGETITLE = "",
    PAGENAME = "",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")

    resp = ""
    try:
        session = ebay_new.Session()
        session.Initialize()

        Ack = "NONE"
        Version = "x.xx"
        Timestamp = ""
        listdata = ""

        if request.method == 'GET':
            session.Token = request.args.get('token', -1)
            session.ItemID = request.args.get('itemid', -1)
        else:
            content = request.get_json()
            print content
            if request.json['token']:
                session.Token = request.json['token']
            if session.ItemID:
                session.ItemID = request.json['itemid']

        #print "\n\nTOKEN: " + str(session.Token) + "\n\n"
        #print "ITEMID: " + str(session.ItemID) + "\n\n\n"

        GetItem = ebay_new.GetItem(session.ItemID, session.Token)
        o = str(GetItem.Get(opts))

        listdata = xmltodict.parse(o)
        #print(json.dumps(listdata) + "\n\n")

        root = ET.ElementTree(ET.fromstring(o)).getroot()
        for node in root:
            if node.tag == "{urn:ebay:apis:eBLBaseComponents}Timestamp":
                Timestamp = node.text
            if node.tag == "{urn:ebay:apis:eBLBaseComponents}Ack":
                Ack = node.text
            if node.tag == "{urn:ebay:apis:eBLBaseComponents}Version":
                Version = node.text

        #print "\nTimestamp: " + Timestamp
        #print "Ack: " + Ack
        #print "Version: " + Version

        if Ack != "Success":
            listdata = ""

        resp = Response(response=listdata, status=200, mimetype="application/json")
    except IOError as (errno, strerror):
        log.error(" I/O error({0}): {1}".format(errno, strerror))
        resp = ""
    except ValueError:
        log.error(" No valid integer in line.")
        resp = ""
    except:
        log.error(" Unexpected error: "  + repr(sys.exc_info()[0])) #.format(sys.exc_info()[0]))
        for error in sys.exc_info():
            log.error(" " + repr(error))
        resp = ""
    #finally:

    return resp
    #return jsonify(items=listdata)


############################################################################

#@app.route('/todo/api/v1.0/tasks', methods=['GET'])
#def get_tasks():
#    return jsonify({'tasks': tasks})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """GET TASK"""
    if not request.json:
        abort(400)
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    """CREATE TASK"""
    if not request.json or not 'title' in request.json:
        #abort(400)
        abort(400, {'errors': dict(error="Not a valid JSON request")})
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """UODATE TASK"""
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})


##########################################################################


@app.route('/myproducts2')
@app.route('/MyProducts2')
@app.route('/myProducts2')
@app.route('/Myproducts2')
@app.route('/MYPRODUCTS2')
@app.route('/myPRODUCTS2')
@app.route('/MYproducts2')
def myproducts():
    "MYPRDUCTS"
    class opt:
        debug = False
        list = ""
        days = 120

    opts = opt()
    opts.list = True

    listdata = ""
    listdict = {}

    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    TITLE = "",
    PAGETITLE = "MyProducts Dashboard",
    PAGENAME = "MyProducts Dashboard",
    MYPRODUCTS = "text-danger",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")

    try:
        session = ebay_new.Session()
        session.Initialize()

        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=opts.days)
        end = str(end).replace(" ", "T", 1) + "Z" #.strftime('%Y-%M-%D %H:%M:%S:%f')
        start = str(start).replace(" ", "T", 1) + "Z" #.strftime('%Y-%M-%D %H:%M:%S:%f')

        GetSellerList = ebay_new.GetSellerList(app.config["EBAYTOKEN"], start, end, app.config["PAGE"])
        listdata = str(GetSellerList.Get(opts))

        root = ET.ElementTree(ET.fromstring(listdata)).getroot()
        listdata = ""
        for node in root.findall(\
        ".//{urn:ebay:apis:eBLBaseComponents}ItemArray//{urn:ebay:apis:eBLBaseComponents}Item"):
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

            for node in root.findall(\
            ".//{urn:ebay:apis:eBLBaseComponents}ItemArray//{urn:ebay:apis:eBLBaseComponents}Item"):
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
                            Price = nlist[0].text

                        if child.tag == "{urn:ebay:apis:eBLBaseComponents}Listingstatus":
                            Listingstatus = child.text
                        if child.tag == "{urn:ebay:apis:eBLBaseComponents}HasUnansweredQuestions":
                            Questions = child.text
                    listdata += "<tr>\n\t\t\t<td style='vertical-align:middle;'></td>\n\t\t\t"
                    listdata += "<td><img height='90px' width='90px' src='" + Picture + \
                    "' /></td>\n\t\t\t"
                    listdata += "<td style = 'vertical-align: middle;'>"    + SKU     + \
                    "</td>\n\t\t\t"
                    listdata += "<td style = 'vertical-align: middle;'>"    + Title   + \
                    "</td>\n\t\t\t"
                    listdata += "<td style = 'text-align:right;vertical-align: middle;" + \
                    "font-size:22px;'>" + Price  + "</td>\n\t\t\t"
                    listdata += "<td style = 'background-color:#ED4337;text-align:center;" + \
                    "font-weight:bold;vertical-align: middle;font-size:22px;'>"  + \
                    Amazon + "</td>\n\t\t\t"
                    listdata += "<td style = 'background-color:#519548;text-align:center;" + \
                    "font-weight:bold;vertical-align: middle;font-size:22px;'>"  + \
                    eBay   + "</td>\n\t\t\t"
                    listdata += "<td style = 'background-color:#F9D423;text-align:center;" + \
                    "font-weight:bold;vertical-align: middle;font-size:22px;'>"  + \
                    Etsy   + "</td>\n\t\t</tr>\n"
    except IOError as (errno, strerror):
        log.error(" I/O error({0}): {1}".format(errno, strerror))
    except ValueError:
        log.error(" No valid integer in line.")
    except:
        log.error(" Unexpected error:", sys.exc_info()[0])
        log.error(" " + sys.exc_info()[1])
    #finally:
        #listdata = "ERROR"
    return flask.render_template('myproducts.html', app=app, listdata=listdata)


@app.route('/myproducts/', methods=['GET', 'POST'])
@app.route('/MyProducts/', methods=['GET', 'POST'])
@app.route('/myProducts/', methods=['GET', 'POST'])
@app.route('/Myproducts/', methods=['GET', 'POST'])
@app.route('/MYPRODUCTS/', methods=['GET', 'POST'])
@app.route('/myPRODUCTS/', methods=['GET', 'POST'])
@app.route('/MYproducts/', methods=['GET', 'POST'])
@app.route('/myactivelistings/', methods=['GET', 'POST'])
@app.route('/MyActiveListings/', methods=['GET', 'POST'])
@app.route('/myActiveListings/', methods=['GET', 'POST'])
@app.route('/Myactivelistings/', methods=['GET', 'POST'])
@app.route('/MYACTIVELISTINGS/', methods=['GET', 'POST'])
@app.route('/myACTIVELISTINGS/', methods=['GET', 'POST'])
@app.route('/MYactivelistings/', methods=['GET', 'POST'])
@login_required
def myactivelistings():
    """LISTINGS"""
    print "MYACTIVELISTINGS"
    #this is just to display the username in the template not required as part
    #of any Flask-Login requirements.
    user_id = (current_user.get_id() or "No User Logged In")
    
    parsed_uri = urlparse(request.url_root)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    if domain.find('-stage') > 0:
        domain = "STAGING"
    else:
        domain = "Crossroads"
    app.config.update(
    TITLE = str(domain), 
    PAGETITLE = "MyActiveListings Dashboard", 
    PAGENAME = "MyActiveListings Dashboard", 
    MYPRODUCTS = "text-danger", 
    MYORDERS = "", 
    MYSTORES = "", 
    MYSUPPLIERS = "", 
    LASTPAGE = "", 
    MESSAGE = "")

    try:
        session = ebay_new.Session()
        session.Initialize()
    except IOError as (errno, strerror):
        log.error(" I/O error({0}): {1}".format(errno, strerror))
    except ValueError:
        log.error(" No valid integer in line.")
    except:
        log.error(" Unexpected error:", sys.exc_info()[0])
        log.error(" " + sys.exc_info()[1])
    #finally:
        #listdata = "ERROR"
    return flask.render_template('myactivelistings.html', user_id=user_id, app=app)


@app.route('/api/v1.0/HTML_GRID_EBAY-INV_API', methods=['GET', 'POST'])
@app.route('/api/v1.0/html_grid_ebay-inv_api', methods=['GET', 'POST'])
@app.route('/api/v1.0/Html_Grid_Ebay-Inv_Api', methods=['GET', 'POST'])
@login_required
def json_grid_ebay_inv_api():
    """JSON GRID INV API"""
    class opt:
        debug = False
        list = ""
        days = 120

    opts = opt()
    opts.list = True

    listdata = ""
    listdict = {}

    XMLerrors = ""
    eBay= -1
    Timestamp = ""
    Ack = ""
    Version = ""
    opts.debug = True
    if opts.debug:
        print "DEBUG: " + str(opts.debug)
    try:
        session = ebay_new.Session()
        session.Initialize()
        if request.method == 'POST':
            print "################ STARTING UPDATE OF INV FOR PRODUCT FROM POST ###############"
            print "content_type: ", str(request.content_type)
            f = request.form
            #for key in f.keys():
            #    for value in f.getlist(key):
            #        print key,":",value
            print "PictureURL: " + str(f["data[PictureURL]"])
            print "SKU: " + str(f["data[SKU]"])
            print "Title: " + str(f["data[Title]"])
            print "Price: " + str(f["data[Price]"])
            print "Quantity: " + str(f["data[Quantity]"])
            print "ItemId: " + str(f["data[ItemID]"])
            print "Amazon: " + str(f["data[Amazon]"])
            print "eBay: " + str(f["data[eBay]"])
            print "Etsy: " + str(f["data[Etsy]"])
            print "DT_RowId: " + str(f["id"])
            RequestData = '''<?xml version="1.0" encoding="utf-8"?>
            <ReviseItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
            <eBayAuthToken>%(token)s</eBayAuthToken>
            </RequesterCredentials>
            <Item ComplexType="ItemType">
            <ItemID>%(itemid)s</ItemID>
            <Quantity>%(quantity)s</Quantity>
            <Title>%(title)s</Title>
            </Item>
            <MessageID>1</MessageID>
            <WarningLevel>High</WarningLevel>
            </ReviseItemRequest>
            '''
            RequestData = RequestData % {
                'token': str(app.config["EBAYTOKEN"]), 
                'itemid': str(f["data[ItemID]"]), 
                'quantity': str(f["data[eBay]"]),
                'title': str(f["data[Title]"])
            }
            print str(RequestData)
            ReviseItem = ebay_new.ReviseItem(RequestData)
            print "DO GET OPTION"
            listdata = str(ReviseItem.Get(opts))
            print str(listdata) + "\n" + "LISTDATA"
            #o = xmltodict.parse(listdata)
            #print(json.dumps(o))
            root = ET.ElementTree(ET.fromstring(listdata)).getroot()
            #print (root.toprettyxml())
            for node in root:
                #if node.tag == "Errors":
                #    XMLerrors = XMLerrors + "\n",node.toprettyxml("  ") + "\n\n"
                #    print str(XMLerrors.data())
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
        elif request.method == 'GET':
            print "IN GET for ActiveEdit"
            abort(400)

    except IOError as (errno, strerror):
        log.error(" I/O error({0}): {1}".format(errno, strerror))
    except ValueError:
        log.error(" No valid integer in line.")
    except:
        log.error(" Unexpected error:", sys.exc_info()[0])
        log.error(" " + sys.exc_info()[1])
    #finally:
        #listdata = "ERROR"

    print "#################################################################"
    print "################# START OF PRODUCT PULL #########################"
    print "#################################################################"
    user_id = (current_user.get_id() or "No User Logged In")

    app.config.update(
    TITLE = str(domain),
    PAGETITLE = "MyActiveListings Dashboard",
    PAGENAME = "MyActiveListings Dashboard",
    MYPRODUCTS = "text-danger",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")
    
    resp = ""
    print "################ STARTING GET PRODUCT INFO ###############"
    Timestamp = ""
    Ack = ""
    Version = ""
    GetItem = ebay_new.GetItem(f["data[ItemID]"], app.config["EBAYTOKEN"])

    listdata = str(GetItem.Get(opts))
    print str(listdata) + "\n\n"
    o = xmltodict.parse(listdata)

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

    listdata = '{ "row":  '
    flag = 0
    ItemCount = 0
    TotalNumberOfPages = 1
    TotalNumberOfEntries = 1

    for node in root:  #root.findall(".//{urn:ebay:apis:eBLBaseComponents}ItemArray//{urn:ebay:apis:eBLBaseComponents}Item"):
        ItemID = ""
        SKU = "NONE"
        Title = ""
        Quantity = ""
        ConditionDescription = ""
        StartTime = ""
        EndTime = ""
        Quantity = ""
        MinBid = ""
        ViewItemURL = ""
        eBay = 0
        Amazon = -1
        Etsy = 0
        ItemCount += 1
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
                if child.tag == "{urn:ebay:apis:eBLBaseComponents}Quantity":
                    Quantity = child.text
                if child.tag == "{urn:ebay:apis:eBLBaseComponents}PictureDetails":
                    nlist = child.findall("{urn:ebay:apis:eBLBaseComponents}GalleryURL")
                    Picture = nlist[0].text
                if child.tag == "{urn:ebay:apis:eBLBaseComponents}SellingStatus":
                    nlist = child.findall(
                        "{urn:ebay:apis:eBLBaseComponents}CurrentPrice")
                    Price = nlist[0].text
                if child.tag == "{urn:ebay:apis:eBLBaseComponents}ListingDetails":
                    print "FOUND LISTINGS DETAILS"
                    for child2 in child:
                        if child2.tag == "{urn:ebay:apis:eBLBaseComponents}ViewItemURL":
                            ViewItemURL = child2.text
            if flag == 1:
                listdata += ", "
            flag = 1
            listdata += '{"DT_RowId": "' + str(f["id"]) + '", '
            #listdata += '"EditButton": "", '
            #listdata += '"Counter": "' + str(f["data[Counter]"]) + '", '
            #listdata += '"PictureURL": "' + Picture.replace('"', '\\"') + '", '
            listdata += '"PictureURL": "' + Picture.replace('"', '\\"') + '|' + ViewItemURL.replace('"', '\\"') + '", '
            listdata += '"SKU": "'          + SKU.replace('"', '\\"') + '", '
            listdata += '"Title": "'        + Title.replace('"', '\\"') + '", '
            listdata += '"Price": "'        + Price.replace('"', '\\"') + '", '
            listdata += '"Quantity": "'     + Quantity.replace('"', '\\"') + '", '
            listdata += '"ItemID": "'       + ItemID.replace('"', '\\"') + '", '
            listdata += '"Amazon": "'       + str(Amazon) + '", '
            listdata += '"eBay": "'         + Quantity.replace('"', '\\"') + '", '
            listdata += '"Etsy": "'         + str(Etsy) + '" }  } '
    #listdata += ' '
    #listdata += ', "header": [ { "Timestamp": "' + str(Timestamp) + '", "Ack": "' + str(Ack)
    #listdata += '", "Version": "' + str(Version) + '", "TotalNumberOfPages": "' + \
    #str(TotalNumberOfPages)
    #listdata += '", "TotalNumberOfEntries": "' + str(TotalNumberOfEntries) + '"} ] }'

    print "################ END OF GET PRODUCT INFO ###############"
    print str(listdata) + "\n\n"
    #print "ItemCount: " + str(ItemCount)
    resp = Response(response=listdata, status=200, mimetype="application/json")

    #return listdata
    #return redirect(url_for("myactivelistings"), code=302)
    return resp

@app.route('/myactiveedit/', methods=['GET', 'POST'])
@app.route('/MyActiveEdit/', methods=['GET', 'POST'])
@app.route('/myActiveEdit/', methods=['GET', 'POST'])
@app.route('/Myactiveedit/', methods=['GET', 'POST'])
@app.route('/MYACTIVEEDIT/', methods=['GET', 'POST'])
@app.route('/myACTIVEEDIT/', methods=['GET', 'POST'])
@app.route('/MYactiveedit/', methods=['GET', 'POST'])
@login_required
def myactiveedit():
    """ACTIVEEDIT"""
    user_id = (current_user.get_id() or "No User Logged In")

    class opt:
        debug = False
        list = ""
        days = 120

    opts = opt()
    opts.list = True

    listdata = ""
    listdict = {}

    app.config.update(
    TITLE = str(domain),
    PAGETITLE = "MyActiveListing Edit ",
    PAGENAME = "MyActiveListing Edit Dashboard",
    MYPRODUCTS = "text-danger",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "",
    MESSAGE = "")

    XMLerrors = ""

    opts.debug = True
    if opts.debug:
        print "DEBUG: " + str(opts.debug)

    #print form.data

    if request.method == 'POST':
        print "################ STARTING REVISE PRODUCT INFO FROM POST ###############"
        form = ActiveEditForm()
        if form.is_submitted():
            print "submitted"
            app.config.update(FORM_SUBMIT = True)
        else:
            app.config.update(FORM_SUBMIT = False)
        #if form.validate():
        #    print "valid"
        #if not form.validate_on_submit():
        #if form.validate() == False:
        #    flash('All fields are required.')
        #    return render_template('myactiveedit.html', app=app, form=form, itemid=itemid, listdata=listdata)
        #else:
        #user = User.get(request.form['user'])
        itemid = str(request.form['ItemId'])
        if itemid is None:
            itemid = -1
        Timestamp = ""
        Ack = ""
        Version = ""
        RequestData = '''<?xml version="1.0" encoding="utf-8"?>
        <ReviseItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
          <RequesterCredentials>
            <eBayAuthToken>%(token)s</eBayAuthToken>
          </RequesterCredentials>
          <Item ComplexType="ItemType">
          <ItemID>%(itemid)s</ItemID>
          <AutoPay>%(autopay)s</AutoPay>
          <PrivateListing>%(privatelisting)s</PrivateListing>
          <HitCounter>%(hitcounter)s</HitCounter>
          <Quantity>%(quantity)s</Quantity>
          <Currency>%(currency)s</Currency>
          <Title>%(title)s</Title>
          <Country>%(country)s</Country>
          <PostalCode>%(postalcode)s</PostalCode>
          <StartPrice currencyID="%(startpricecurrency)s">%(startprice)s</StartPrice>
          <BuyItNowPrice currencyID="%(buyitnowpricecurrency)s">%(buyitnowprice)s</BuyItNowPrice>
          </Item>
          <MessageID>1</MessageID>
          <WarningLevel>High</WarningLevel>
        </ReviseItemRequest>
        '''
        if not request.form.getlist('AutoPay'):
            AutoPay = False
        else:
            AutoPay = True
        if not request.form.getlist('PrivateListing'):
            PrivateListing = False
        else:
            PrivateListing = True
            
        RequestData = RequestData % {
            'token': str(app.config["EBAYTOKEN"]), 
            'itemid': str(itemid), 
            'autopay': AutoPay, 
            'quantity': str(request.form['Quantity']), 
            'currency': str(request.form['Currency']), 
            'title': str(request.form['Title']),
            'country': str(request.form['Country']), 
            'postalcode': str(request.form['PostalCode']),
            'hitcounter': str(request.form['HitCounter']), 
            'privatelisting': PrivateListing,
            'startpricecurrency' : str(request.form['StartPrice_currencyID']), 
            'buyitnowprice': str(request.form['BuyItNowPrice_text']), 
            'buyitnowpricecurrency': str(request.form['BuyItNowPrice_currencyID']), 
            'startprice': str(request.form['StartPrice_text'])
        }
        print str(RequestData)
        ReviseItem = ebay_new.ReviseItem(RequestData)
        print "DO GET OPTION"
        listdata = str(ReviseItem.Get(opts))
        print str(listdata) + "\n" + "LISTDATA"
        #o = xmltodict.parse(listdata)
        #print(json.dumps(o))
        root = ET.ElementTree(ET.fromstring(listdata)).getroot()
        #print (root.toprettyxml())
        for node in root:
            #if node.tag == "Errors":
            #    XMLerrors = XMLerrors + "\n",node.toprettyxml("  ") + "\n\n"
            #    print str(XMLerrors.data())
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
        print "################ STARTING GET PRODUCT INFO ###############"
        Timestamp = ""
        Ack = ""
        Version = ""
        GetItem = ebay_new.GetItem(itemid, app.config["EBAYTOKEN"])

        listdata = str(GetItem.Get(opts))
        #print str(listdata) + "\n\n"
        o = xmltodict.parse(listdata)

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
    
        listdata = o
        # print str(listdata) + "\n\n"

        print "################ END OF GET PRODUCT INFO ###############"
        return render_template('myactiveedit.html', app=app, form=form, itemid=itemid, listdata=json.dumps(listdata), XMLerrors=XMLerrors) #return 'Contact Form posted.'
    elif request.method == 'GET':
        print "IN GET for ActiveEdit"
        print "################ STARTING GET PRODUCT INFO ###############"
        itemid = request.args.get("itemid")
        if itemid is None:
            itemid = -1
        Timestamp = ""
        Ack = ""
        Version = ""
        GetItem = ebay_new.GetItem(itemid, app.config["EBAYTOKEN"])
        listdata = str(GetItem.Get(opts))
        #print str(listdata) + "\n\n"
        o = xmltodict.parse(listdata)
        form = ActiveEditForm() #(formdata=MultiDict(o))
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
    
        listdata = o
        # print str(listdata) + "\n\n"

        print "################ END OF GET PRODUCT INFO ###############"


        #new_o = flatten_json(ActiveEditForm, o)
        print str(json.dumps(o))
        if form.is_submitted():
            print "submitted"
        if form.validate():
            print "valid"
        print "\n\nFORM ERROR: " + str(form.errors) + "\n\n"
        print "REQUEST METHOD: " + str(request.method)
        return render_template('myactiveedit.html', app=app, form=form, itemid=itemid, listdata=json.dumps(listdata), XMLerrors=XMLerrors)


@app.route('/myinventory')
@app.route('/MyInventory')
@app.route('/myInventory')
@app.route('/Myinventory')
@app.route('/MYINVENTORY')
@app.route('/myINVENTORY')
@app.route('/MYinventory')
def myinventory():
    class opt:
        debug = False
        list = ""
        days = 120

    opts = opt()
    opts.list = True

    listdata = ""
    listdict = {}

    TITLE = ""
    PAGETITLE = "MyInventory Dashboard"
    PAGENAME = "MyInventory Dashboard"
    MYPRODUCTS = "text-danger"
    MYORDERS = ""
    MYSTORES = ""
    MYSUPPLIERS = ""
    LASTPAGE = ""
    MESSAGE = ""

    try:
        session = ebay_new.Session()
        session.Initialize()

    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    except ValueError:
        print "No valid integer in line."
    except:
        print "Unexpected error:", sys.exc_info()[0]
        print  sys.exc_info()[1]
    #finally:
        #listdata = "ERROR"
    return flask.render_template('myinventory.html', app=app)


@app.route('/ebaylist')
@app.route('/EbayList')
@app.route('/EBAYLIST')
def listings():
    class opt:
        debug = False
        list = ""
        days = 120

    opts = opt()
    opts.list = True

    listdata = ""
    try:
        session = ebay_new.Session()
        session.Initialize()

        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=opts.days)
        end = str(end).replace(" ", "T", 1) + "Z" #.strftime('%Y-%M-%D %H:%M:%S:%f')
        start = str(start).replace(" ", "T", 1) + "Z" #.strftime('%Y-%M-%D %H:%M:%S:%f')

        GetSellerList = ebay_new.GetSellerList(app.config["EBAYTOKEN"], start, end, app.config["PAGE"])
        listdata = str(GetSellerList.Get(opts))
        root = ET.ElementTree(ET.fromstring(listdata)).getroot()
        listdata = ""
        for node in root.iter():
            if node.tag.find("ItemID") > 0:
                listdata = listdata + "<p>#############################################################################</p>"
            if node.text is not None:
                #print node.tag, node.text
                listdata = listdata + "<p><b>" + str(node.tag).replace("{urn:ebay:apis:eBLBaseComponents}", "") + ":</b> " + str(node.text) + "</p>"
        #listdata = str(GetSellerList.Get(opts).replace("><", "><br />\n<").replace("</Item>", "<sepaerator>******************************</sepaerator></Item>"))
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    except ValueError:
        print "No valid integer in line."
    except:
        print "Unexpected error:", sys.exc_info()[0]
    #finally:
        #listdata = "ERROR"
    return flask.render_template('ebay_list.html', listdata=listdata, app=app)


@app.route('/ebayuser')
@app.route('/EbayUser')
@app.route('/EBAYUSER')
def user():
    class opt:
        debug = False
        username = "cute_room"

    opts = opt()
    opts.list = True

    userinfo = ""
    try:
        Session = ebay_new.Session()
        Session.Initialize()

        GetUser = ebay_new.GetUser(app.config["EBAYTOKEN"], opts.username)
        userinfo = str(GetUser.Get(opts))
        root = ET.ElementTree(ET.fromstring(userinfo)).getroot()
        userinfo = ""
        for node in root.iter():
            if node.text is not None:
                userinfo = userinfo + "<p><b>" + str(node.tag) + ":</b> " + str(node.text) + "</p>"
        #node.attrib
        #indent(root)
        #ET.dump(root)
        #userinfo = str(GetUser.Get(opts).replace("><", "><br />\n<"))

        #print userinfo
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    except ValueError:
        print "No valid integer in line."
    except:
        print "Unexpected error:", sys.exc_info()[0]
    #finally:
        #userinfo = "ERROR"
    return flask.render_template('ebay_user.html', userinfo=userinfo, app=app)


##################################################
# ERROR PAGES
##################################################
@app.route('/400')
def error400():
    """ Displays the 400 page accessible everywhere '/'
    """
    app.config.update(
    PAGENAME = "400 Error for ",
    TITLE = "",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "")
    return flask.render_template('errors/400.html', app=app)


@app.route('/403')
def error403():
    """ Displays the 403 page accessible everywhere '/'
    """
    app.config.update(
    PAGENAME = "403 Error for ",
    TITLE = "",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "")
    return flask.render_template('errors/403.html', app=app)


@app.route('/404')
def error404():
    """ Displays the 404 page accessible everywhere '/'
    """
    app.config.update(
    PAGENAME = "404 Error for ",
    TITLE = "",
    MYPRODUCTS = "",
    MYORDERS = "",
    MYSTORES = "",
    MYSUPPLIERS = "",
    LASTPAGE = "")
    print "404 came from: " + str(request.headers.get("Referer"))
    return flask.render_template('errors/404.html', app=app)


@app.route('/410')
def error410():
    """ Displays the 410 page accessible everywhere '/'
    """
    return flask.render_template('errors/410.html', app=app)


@app.route('/500')
def error500():
    """ Displays the 500 page accessible everywhere '/'
    """
    return flask.render_template('errors/500.html', app=app)



if __name__ == '__main__':
    app.debug = True
    #Tell the login manager where to redirect users to display the login page
    login_manager.login_view = "login"
    login_manager.login_message_category = "info"
    login_manager.login_message = u"You must please log in to access this page."
    #Setup the login manager.
    login_manager.setup_app(app)
    app.run()

