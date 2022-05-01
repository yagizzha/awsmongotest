from email.policy import default
from gc import collect
from flask import Flask,make_response,jsonify
from flask import request 
import pymongo
from flask_mongoengine import MongoEngine
import datetime
import json
import dns.resolver
dns.resolver.default_resolver=dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers=['8.8.8.8']

#json.JSONEncoder.default = lambda self,obj: (obj.isoformat() if isinstance(obj, datetime.datetime) else None)
app = Flask(__name__)
DB_URI="mongodb+srv://yagizzha:asddsaasd1@cluster0.rexda.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
app.config["MONGODB_HOST"]=DB_URI
client = pymongo.MongoClient("mongodb+srv://yagizzha:asddsaasd1@cluster0.rexda.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = MongoEngine()
db.init_app(app)
collectionSub=client['myFirstDatabase']["subscribers"]
collectionReseller=client['myFirstDatabase']["resellers"]

class resellers(db.Document):
    _id=db.ObjectIdField()
    idkey=db.StringField()
    TrialLeft=db.FloatField()
    SubscribeLeft=db.FloatField()
    LifetimeLeft=db.FloatField()
    versionKey=False
    def to_json(self):
        return {
            "idkey": self.idkey,
            "TrialLeft":self.TrialLeft,
            "SubscribeLeft":self.SubscribeLeft,
            "LifetimeLeft":self.LifetimeLeft
        }

class subscribers(db.Document):
    _id=db.ObjectIdField()
    HWID=db.StringField()
    custType=db.StringField()
    idkey=db.StringField()
    lastDate=db.DateTimeField(default=datetime.datetime.utcnow().isoformat())
    versionKey=False
    def to_json(self):
        return {
            "HWID": self.HWID,
            "custType":self.custType,
            "lastDate":self.lastDate,
            "idkey":self.idkey
        }

@app.route('/subscribers/testing',methods=['POST'])
def db_populate():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        jsonfile = request.json
        obj=resellers.objects(idkey=jsonfile["idkey"]).first()
        if obj==None:
            return make_response(jsonify(False),404)
        if obj.TrialLeft>0 and jsonfile["custType"]=="Trial":
            obj.TrialLeft-=1
        elif obj.SubscribeLeft>0 and jsonfile["custType"]=="Sub":
            obj.SubscribeLeft-=1
        elif obj.LifetimeLeft>0 and jsonfile["custType"]=="Perma":
            obj.LifetimeLeft-=1
        else:
            return make_response(jsonify(False),401)
        sub1=subscribers(HWID=jsonfile["HWID"],custType=jsonfile["custType"],idkey=jsonfile["idkey"])
        obj.save()
        sub1.save()
        return make_response(jsonify(obj.to_json()),201)
    else:
        return 'Content-Type not supported!'


@app.route('/subscribers/<HWID>',methods=['GET'])
def HWIDExists(HWID):
    obj=subscribers.objects(HWID=HWID).first()
    if obj==None:
        return make_response(jsonify(False),404)
    return make_response(jsonify(True),201)


@app.route('/subscribers/test',methods=['POST'])
def getbyHWID():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        jsonfile = request.json
        obj=subscribers.objects(HWID=jsonfile["HWID"]).first()
        if obj==None:
            return make_response(jsonify(False),404)
        timeSpent=(datetime.datetime.utcnow()-obj.lastDate).total_seconds()/86400
        if obj.custType=="Perma" or (obj.custType=="Sub" and timeSpent<30) or (obj.custType=="Trial" and timeSpent<1):
            return make_response(jsonify(True),201)
        return make_response(jsonify(False),201)
    else:
        return 'Content-Type not supported!'
@app.route('/subscribers/patch',methods=['PUT'])
def subpatch():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        jsonfile = request.json
        obj=subscribers.objects(HWID=jsonfile["HWID"]).first()
        obj.custType=jsonfile["custType"]
        obj.lastDate=datetime.datetime.utcnow().isoformat()
        returnobj=obj.save()
        return make_response(jsonify(returnobj.to_json()),201)
    else:
        return 'Content-Type not supported!'




@app.route('/resellers',methods=['POST'])
def db_populateReseller():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        jsonfile = request.json
        res1=resellers(idkey=jsonfile["idkey"],TrialLeft=jsonfile["TrialLeft"],SubscribeLeft=jsonfile["SubscribeLeft"],LifetimeLeft=jsonfile["LifetimeLeft"])
        res1.save()
        return make_response(jsonify(res1.to_json()),201)
    else:
        return 'Content-Type not supported!'


@app.route('/resellers/<idkey>',methods=['GET'])
def idkeyreturn(idkey):
    obj=resellers.objects(idkey=idkey).first()
    if obj==None:
        return make_response(jsonify(False),404)
    return make_response(obj.to_json(),201)



if __name__=='__main__':
    app.run(host='0.0.0.0',port=2999)

