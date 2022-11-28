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
DB_URI="mongodb+srv://yagizzha:asddsaasd1@cluster0.rexda.mongodb.net/wproject?retryWrites=true&w=majority"
app.config["MONGODB_HOST"]=DB_URI
client = pymongo.MongoClient("mongodb+srv://yagizzha:asddsaasd1@cluster0.rexda.mongodb.net/wproject?retryWrites=true&w=majority")
db = MongoEngine()
db.init_app(app)
wprojectSub=client['wproject']["subscriber"]
wprojectReseller=client['wproject']["reseller"]
wprojectResellerOrder=client['wproject']["reseller_order"]

key = "WhFa4z-9FZ1fDUYMXdkgwIjxaS17JWHv3BnSQ_82OEw="
fernet = Fernet(key)

class resellerOrder(db.Document):
    _id=db.ObjectIdField()
    guid=db.FloatField()
    idkey=db.StringField()
    thirtyPack=db.FloatField()
    ninetyPack=db.FloatField()
    trialPack=db.FloatField()
    total=db.FloatField()
    createdDate=db.DateTimeField(default=datetime.datetime.now())
    versionKey=False
    def to_json(self):
        return {
            "id": self.guid,
            "idkey": self.idkey,
            "thirtyPack":self.thirtyPack,
            "ninetyPack":self.ninetyPack,
            "trialPack":self.trialPack,
            "createdDate":self.createdDate,
            "total":self.total
        }
       
class reseller(db.Document):
    _id=db.ObjectIdField()
    idkey=db.StringField()
    thirtyPack=db.FloatField()
    ninetyPack=db.FloatField()
    trialPack=db.FloatField()
    total=db.FloatField()
    currentResellerOrder=db.DynamicField()
    resellerOrders=db.ListField()
    versionKey=False
    def to_json(self):
        return {
            "idkey": self.idkey,
            "thirtyPack":self.thirtyPack,
            "ninetyPack":self.ninetyPack,
            "trialPack":self.trialPack,
            "currentResellerOrder":self.currentResellerOrder,
            "resellerOrders":self.resellerOrders,
            "total":self.total
        }


class subscriber(db.Document):
    _id=db.ObjectIdField()
    guid=db.FloatField()
    HWID=db.StringField()
    custTime=db.FloatField()
    idkey=db.ListField()
    lastDate=db.DateTimeField(default=datetime.datetime.now())
    versionKey=False
    def to_json(self):
        return {
            "guid": self.guid,
            "HWID": self.HWID,
            "custType":self.custTime,
            "lastDate":self.lastDate,
            "idkey":self.idkey
        }
   
class updater(db.Document):
    _id=db.ObjectIdField()
    link=db.StringField()
    version=db.StringField()
    versionKey=False
    def to_json(self):
        return {
            "link": self.link,
            "version":self.version
        }

class builder(db.Document):
    _id=db.ObjectIdField()
    link=db.StringField()
    build=db.StringField()
    versionKey=False
    def to_json(self):
        return {
            "link": self.link,
            "build":self.build
        }

@app.route('/test',methods=['GET'])
def testshit():
    currReseller=resellerOrder(guid=wprojectResellerOrder.count_documents({}),idkey="guru1234",thirtyPack=0,ninetyPack=0,trialPack=0)
    currReseller.save()
    currReseller2=resellerOrder(guid=wprojectResellerOrder.count_documents({}),idkey="guru1234",thirtyPack=0,ninetyPack=0,trialPack=0)
    currReseller2.save()
    currReseller3=resellerOrder(guid=wprojectResellerOrder.count_documents({}),idkey="guru1234",thirtyPack=0,ninetyPack=0,trialPack=0)
    currReseller3.save()
    test=reseller(idkey="guru1234",
                thirtyPack=0,
                ninetyPack=0,
                trialPack=0,
                resellerOrders=[currReseller2.guid,currReseller3.guid],
                currentResellerOrder=currReseller.guid)
    test.save()
    print(currReseller.guid)
    return make_response(jsonify(test.to_json()),201)

def newResellerOrder(idkey):
    currResellerOrder=resellerOrder(guid=wprojectResellerOrder.count_documents({}),idkey=idkey,thirtyPack=0,ninetyPack=0,trialPack=0,total=0)
    currResellerOrder.save()
    return currResellerOrder.guid

@app.route('/reseller/populate',methods=['POST'])
def populateReseller():
    jfile = request.json
    Reseller=reseller(idkey=jfile['idkey'],
                thirtyPack=0,
                ninetyPack=0,
                trialPack=0,
                resellerOrders=[],
                currentResellerOrder=newResellerOrder(jfile['idkey']),
                total=0)
    Reseller.save()
    return make_response(jsonify(Reseller.to_json()),201)

@app.route('/reseller/newcurrent',methods=['POST'])
def resetReseller():
    jfile = request.json
    obj=reseller.objects(idkey=jfile["idkey"]).first()
    if obj==None:
        return make_response(jsonify(False),405)
    currOrder=resellerOrder.objects(guid=obj.currentResellerOrder).first()
    obj.total+=currOrder.total
    obj.resellerOrders.append(obj.currentResellerOrder)
    obj.currentResellerOrder=newResellerOrder(obj.idkey)
    obj.save()
    return make_response(jsonify(obj.to_json()),201)

@app.route('/subscriber/populate',methods=['POST'])
def populateSub():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        jsonfile = request.json
        currReseller=reseller.objects(idkey=jsonfile["idkey"]).first()
        if currReseller==None:
            return make_response(jsonify(False),405)
        sub1=subscriber.objects(HWID=jsonfile["HWID"]).first()
        subTime=0
        if "Trial"==jsonfile["custType"]:
            subTime=3
        if "Thirty"==jsonfile["custType"]:
            subTime=30
        if "Ninety"==jsonfile["custType"]:
            subTime=90
        if sub1==None:
            sub1=subscriber(guid=wprojectSub.count_documents({}),HWID=jsonfile["HWID"],custTime=subTime,idkey=[jsonfile["idkey"]],lastDate=datetime.datetime.now())
        else:
            sub1.idkey.append(jsonfile["idkey"])
            timeSpent=(datetime.datetime.now()-sub1.lastDate).total_seconds()/86400
            timeSpent=sub1.custTime-timeSpent
            if timeSpent<0:
                sub1.lastDate=datetime.datetime.now()
                sub1.custTime=subTime
            else:
                sub1.lastDate=datetime.datetime.now()
                sub1.custTime=subTime+timeSpent


        sub1.save()
        currOrder=resellerOrder.objects(guid=currReseller.currentResellerOrder).first()
        if jsonfile["custType"]=="Trial":
            currOrder.trialPack+=1
            currOrder.total+=0
        elif jsonfile["custType"]=="Thirty":
            currOrder.thirtyPack+=1
            currOrder.total+=18
        elif jsonfile["custType"]=="Ninety":
            currOrder.ninetyPack+=1
            currOrder.total+=48
  
        currOrder.save()
        currReseller.save()
        return make_response(jsonify((currOrder.to_json()),(sub1.to_json())),201)
    else:
        return 'Content-Type not supported!'


@app.route('/subscriber/trial',methods=['POST'])
def populateSubTrial():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        jsonfile = request.json
        sub1=subscriber.objects(HWID=jsonfile["HWID"]).first()
        if sub1==None:
            currReseller=reseller.objects(idkey="TMAKE#61!aTq/3-").first()
            sub1=subscriber(guid=wprojectSub.count_documents({}),HWID=jsonfile["HWID"],custTime=3,idkey=["TMAKE#61!aTq/3-"],lastDate=datetime.datetime.now())
            currOrder=resellerOrder.objects(guid=currReseller.currentResellerOrder).first()
            currOrder.trialPack+=1
            currOrder.save()
            sub1.save()
            return make_response(jsonify(True),201)
        return make_response(jsonify(False),201)
@app.route('/subscriber/access',methods=['POST'])
def accessSub():
    jsonfile = request.json
    sub1=subscriber.objects(HWID=jsonfile["HWID"]).first()
    if sub1==None:
        encmessage=fernet.encrypt((jsonfile["HWID"]+"FAI").encode())
        resp=encmessage.decode()
        return make_response(jsonify(resp,0),200)
    else:
        timeSpent=(datetime.datetime.now()-sub1.lastDate).total_seconds()/86400
        encmessage=fernet.encrypt((jsonfile["HWID"]+"SUC").encode())
        resp=encmessage.decode()
        return make_response(jsonify(resp,9999),200)
        if timeSpent<sub1.custTime:
            encmessage=fernet.encrypt((jsonfile["HWID"]+"SUC").encode())
            resp=encmessage.decode()
        else:
            encmessage=fernet.encrypt((jsonfile["HWID"]+"FAI").encode())
            resp=encmessage.decode()
        return make_response(jsonify(resp,sub1.custTime-timeSpent),200)

@app.route('/builder/',methods=['GET'])
def buildercurrent():
    obj=builder.objects().first()
    if obj==None:
        return make_response(jsonify(False),404)
    return make_response(jsonify(obj.to_json()),201)

@app.route('/builder/add',methods=['POST'])
def builderpopulate():
    content_type = request.headers.get('Content-Type')
    jsonfile = request.json
    obj=builder(link=jsonfile["link"],build=jsonfile["build"])
    obj.save()
    return make_response(jsonify(obj.to_json()),201)

@app.route('/builder/change',methods=['POST'])
def builderchange():
    content_type = request.headers.get('Content-Type')
    jsonfile = request.json
    obj=builder.objects().first()
    obj.link=jsonfile["link"]
    obj.build=jsonfile["build"]
    obj.save()
    return make_response(jsonify(obj.to_json()),201)





if __name__=='__main__':
    app.run(host='0.0.0.0',port=2998)

