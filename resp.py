from asyncio import gather
from email.policy import default
from ensurepip import version
from gc import collect
from flask import Flask,make_response,jsonify
from flask import request 
import pymongo
from flask_mongoengine import MongoEngine
import datetime
import json
import dns.resolver
from cryptography.fernet import Fernet

dns.resolver.default_resolver=dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers=['8.8.8.8']

#json.JSONEncoder.default = lambda self,obj: (obj if isinstance(obj, datetime.datetime) else None)
app = Flask(__name__)
DB_URI="mongodb+srv://yagizzha:asddsaasd1@cluster0.rexda.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
app.config["MONGODB_HOST"]=DB_URI
client = pymongo.MongoClient("mongodb+srv://yagizzha:asddsaasd1@cluster0.rexda.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = MongoEngine()
db.init_app(app)

key = "WhFa4z-9FZ1fDUYMXdkgwIjxaS17JWHv3BnSQ_82OEw="
fernet = Fernet(key)