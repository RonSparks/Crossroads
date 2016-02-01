# config.py

#from authomatic.providers import oauth2, oauth1, openid, gaeopenid
#import authomatic


# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "ITSASECRET"

#Change the duration of how long the Remember Cookie is valid on the users
#computer.  This can not really be trusted as a user can edit it.
REMEMBER_COOKIE_DURATION = ""
COOKIE_TIME = 8

HASH = "sha256"
#Default settings for
TITLE = "Crossroads"
COMPANY = "Vcommsync"
AUTHOR = "Teddy Benson"
KEYWORDS = "ecommerce, ebay, etsy, shopify, shopping, selling, shipping"
URL = "http://VCOMSYNC.com"
TWITTER = "vcommsync"
GOOGLEPLUS = "vcommsync"
VERSION = "0.0.88"
LOG_TOKEN = "d1fc594b-4438-42a7-b2df-c0068c8ea910"
TODAY = ""
YEAR = "1500"
KA_GE = "AgAAAA**AQAAAA**aAAAAA**fDkDVQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wJnYCnCZODow6dj6x9nY+seQ**j70CAA**AAMAAA**h4cBTuLnj1JSYsez+q6+QCj46TM+1Ea0WEGo6OU8swEHrsuRo+WZDmV5/KsJN8nNDzCmeYAeq4GegtF6hJlB1gTJmMZnqVQ3lxtNfumlKhYTtC9YmngyQQ04k7UIARqDJIpZlrcs4/DveNZwS5Za8oL67FqLPEEtaEPEbzxg0Ba3wsJDncnSVOiS+NOGoQXASP4kZoZTF/6jzr4R+HrrCv1oaYivhcAOQVwD4c/Zuw1RMSuUgfas3mx14yHq81Sb/8DMdWEJ9jpyvUG32WVFchOELR18tbQkcKVCOuTdtuKxhY0WPVuH5yM9bybfiySeNBJixJyomZEUBGxu+HaXgTLmUTA2/sQ/fKSFu4t/jG1hgZw/DcLvOiUiP+Qr4VMh8JtpZX3dfzr36kYNaTCxg7UdUnVHD/tppvnJQ6GP+ZqrTtlfeI63vYazTymMxz5d4z4FjD6VA+piLoRjzsk83vbmF/3Ey4SzwByiF0P/GVN6grRKl9J+/P3XySdaFVfSu4aWKXpgVtaurVfsG8wLxqMlXYqVzouP5N/VfLBRaHn3lM5dhIxqlg0DBS3+Ck5cI3wSG1uv5bsT+awsyQLzovnC+dZ6mmNYfJ309viCEbNnJzjchODOVecO4BLZefI+H7FDyY8TBoABTARA1AddneN7WTcj5Q8ykfV2LmPxXvb3KtRfwTb+GPE4BPkvdqRtu6Lnuq4YqO6+25MBoWfNp3HOgrG3poGeBBeKVwY2jLscNTTjtpI257oZ/Orrk1qy"
RISA = "AgAAAA**AQAAAA**aAAAAA**cMsBVQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wJlYGhC5SAqQmdj6x9nY+seQ**j70CAA**AAMAAA**8C79zRs8jk5reI5YP7fgF4GoGLvO/q93k7vfirqnZfeGllMA+r/RYoENiPTL0OifnN0BsTrZH6g8gNrjDezmj/RCKVLAlnV1/6sDvZvVAxUPjVaGarUnpy5P46lnkoSljOAqni7m/lpUiE1TbDREvovXmWhJ6+hvCMABkEJXi2aMesaeDB5Iwv7Xmds4FXmBdruc8vABCH9kjXf254ZX7aMaWOgPEaxWDS2XGjNiMas2jkqDFhzZEH6BoOo2TrhOBNczornXgan+WMFUGuyLc0sp08UEVGcQn96N+NO+/c9pilUXid5KemVeWztFSYNaZAyMcu7Fhz3F/I043xPkZvU0ZNj4HHmlxoKqM7p8ziPqhu/d607GHhy4R91ZvztZPhBkMlEp/TAvKUNRv70UoKdxan3sO3qCvyFYaXtyNUcQNlXFUewFSF8viF80A+zXnFKN0nB5bgeZcpUslVhPPePtcj+khXg5FBAN4KHuWEPfYu/ZroYZ2zwkwXpXOM5NYeoR/DllC/i/NpGY8P6GE+oV3ogrgJAayjKZl0SxuK24zd7FF7JDnA0jBjvUThKqA/llp92nz6jtfmR6XoQbJjI671pWpooxjc6xEafUGZUL0yG3GbpFMCSLvqGD/w/pb6B0SVxxU0RZZyk7mL/e44IRG19MsAA6YthZXbL+wfxE2HmKhszIYI8WoejZBYvVlgaIY4Wu8qpJaZGOEc4yQJVbAjjdOCJEhMIKwC/dMYD82K+YvQDeRJkZN9ZWFoDC"
KARI = "AgAAAA**AQAAAA**aAAAAA**IWN3VQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AHl4aoDpaBpQmdj6x9nY+seQ**j70CAA**AAMAAA**PT/ANlinkISBEUola+dVPmCMWVpsD/8L8wAYCQ/8nN1IBXArone+hVnJMEfiJwNZboNZmZN8mDZtju+Io2rz2Z4p/CcmDlp86qEZycMuqI+PVdeaHBkzvnrSVvSE+GLABYA9ZMGNvdDnMKriy2brHkJv46zCKPWbxKFh5Cann7eAag7mPJLMMZ0PUKlnAoDLq3LuqX4ievbYM6tQm36wd0sgFD9u6pyp0nvSxs0ojvumwSgrbzgyPli5bzbe1DIosPf/9b8Vxxx2HrG+AYF50451KcAWVz8hrN8U4L668CcRm0z+/Qe0UuaQyP383Vi0fPu7E9fmcKYAfBOxsaDYtlPHpA+igzeKKTd97Xi/kI5VzPyWQaqm0Obcoo+HtIG7oA+iyxTgWtfSxNqVJSHfVUzR9CnS+JBEaM9XQ2BXb7+5kGvOLIl5svMTCbYEPWjuQsF1KYSX4n5tQSF/ErinOFZWKpY2A3t69dHvc8qP9DBFsvALfDqb+v0L4yZA7iY9FOAjoWqUhlVlCS6cxdf7iDR6J3/b1hcIx2f2FCgHpF7l6cLdJkjWkeR3sAJnS8ax9rFcKKdByEVNBUq4W4Lw1s7z7rpEhborDzyizZ/U+XRRK0JsRZ7S01EKuJVBAUSeqiEbVdoz5ecXPxSNAq/coGTm4Ud1LiJ39ikomZzvxEtySoNyULpvpf34gTPsdbv0TPQMadGjRoOsC+Ja0PmNbs33KffXU1nXZBNynxtZSYzXOMoiCc6jqQk0MSa4tLxJ"
SHAWNA = "AgAAAA**AQAAAA**aAAAAA**RiDeVQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AAkIGnDpiBpg2dj6x9nY+seQ**j70CAA**AAMAAA**JnP5Gg7jLIcEcmdji/Z5b/IJUBFNlg+jQt3j1pMzkU6c57R44Qi0bf1eTqZofF0Cn3NtEn8M4ancFBEOEhyXc+UtWqqEyrvocm5Ppld4qdpuwCJ8qWXjKRvuWmCDjE7x7/Lk2mp3o3j2ga+zv2Q/yzbY/62GG9vEwcss5RJMgtnOhXqhQXPENCR1g/NyWfnMDlplwBl54lWBMPBer4h4IVvbAmhJAyp5DoBCig+9kwSqrVxey5AgaalCYdw5UBY7asilzzTpRrIwf79v5wdtljQbcdFKUX5HD9crNxqAv3cB7NZxpxmdCT6NvQm1CuRnztu31LhYDSZlfxgLepeXVUvhsXxAdoIcUouE6ZviHIrhABlMt6Wgc7lvUlSYM+WV3UJ72WSmYYo+NRlKTeZQTpYcRTnZfGit/FIxlljqyaFoYErz7C1L7bo5BccySLCJFGXYDeUVMpy+mHiO3N3D0pYHLKLyWLZTA5QHTeSdHaYQTMJYJfbfBVLuOLidiqhrcIzy7Oi+wjG2IqCbu89qZhUIypT84hoYAClhFz66l7saVA69alsZd8aosUxyNIU62keImcQCVf2WBCBT15HSQZ1I37o5wKTN6gQ9cSZ9SFMr3T9Jb+XXBWHbD6ao6bPdUP7LVvrioiC7gv2oYRor5eA8ygbYdZ1paZwvGV3k9pShJf+mRmM0W90904HQ/uYBWcrg+DzZRxUK0qEULaS3wR1r+kW/8csZ9HRe0coEy6tVFHqxZYxskdDImdZOfCJY"
EBAYTOKEN = "-1"
EBAYSESSIONID = "-1"
EBAY_RUNAME = "Vcommerce__LLC-Vcommerc-da4e-4-idcctuys"
PAGE = "200"

FORM_SUBMIT = False

ETSYTOKEN = ""

PAGETITLE = ""
PAGENAME = ""
MYPRODUCTS = ""
MYORDERS = ""
MYSTORES = ""
MYSUPPLIERS = ""
LASTPAGE = ""

EMAIL = ''
FIRST_NAME = ''
LAST_NAME = ''