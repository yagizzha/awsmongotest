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
collectionSub=client['myFirstDatabase']["subscribers"]
collectionReseller=client['myFirstDatabase']["resellers"]
collectionUpgradedReseller=client['myFirstDatabase']["upgradedresellers"]
collectionUpgradedSub=client['myFirstDatabase']["upgradedsubscribers"]

key = "WhFa4z-9FZ1fDUYMXdkgwIjxaS17JWHv3BnSQ_82OEw="
fernet = Fernet(key)

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
class upgradedresellers(db.Document):
    _id=db.ObjectIdField()
    idkey=db.StringField()
    Trial=db.FloatField()
    Subscriber=db.FloatField()
    Lifetime=db.FloatField()
    una=db.FloatField()
    gather=db.FloatField()
    total=db.FloatField()
    chaos=db.FloatField()
    versionKey=False
    def to_json(self):
        return {
            "idkey": self.idkey,
            "Trial":self.Trial,
            "Subscriber":self.Subscriber,
            "Lifetime":self.Lifetime,
            "una":self.una,
            "gather":self.gather,
            "chaos":self.chaos,
            "total":self.total
        }
class subscribers(db.Document):
    _id=db.ObjectIdField()
    HWID=db.StringField()
    custType=db.StringField()
    idkey=db.StringField()
    lastDate=db.DateTimeField(default=datetime.datetime.now())
    versionKey=False
    def to_json(self):
        return {
            "HWID": self.HWID,
            "custType":self.custType,
            "lastDate":self.lastDate,
            "idkey":self.idkey
        }
class upgradedsubscribers(db.Document):
    _id=db.ObjectIdField()
    HWID=db.StringField()
    custType=db.StringField()
    idkey=db.StringField()
    lastDate=db.DateTimeField(default=datetime.datetime.now())
    chaos=db.BooleanField(default=False)
    una=db.BooleanField(default=False)
    gather=db.BooleanField(default=False)
    state=db.StringField(default="empty")
    versionKey=False
    def to_json(self):
        return {
            "HWID": self.HWID,
            "custType":self.custType,
            "lastDate":self.lastDate,
            "idkey":self.idkey,
            "chaos":self.chaos,
            "una":self.una,
            "gather":self.gather,
            "state":self.state
        }
   
class customsubscribers(db.Document):
    _id=db.ObjectIdField()
    HWID=db.StringField()
    custType=db.StringField()
    cust=db.StringField()
    type=db.StringField()
    idkey=db.StringField()
    lastDate=db.DateTimeField(default=datetime.datetime.now())

    versionKey=False
    def to_json(self):
        return {
            "HWID": self.HWID,
            "custType":self.custType,
            "cust":self.cust,
            "type":self.type,
            "idkey":self.idkey,
            "lastDate":self.lastDate
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

@app.route('/subscribers/testing',methods=['POST'])
def db_populate():
    #print(datetime.datetime.now())
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        jsonfile = request.json
        obj=resellers.objects(idkey=jsonfile["idkey"]).first()
        if obj==None:
            return make_response(jsonify(False),404)
        if obj.TrialLeft>0 and jsonfile["custType"]=="Trial":
            pass
        elif obj.SubscribeLeft>0 and jsonfile["custType"]=="Sub":
            pass
        elif obj.LifetimeLeft>0 and jsonfile["custType"]=="Perma":
            pass
        else:
            return make_response(jsonify(False),401)
        sub1=subscribers.objects(HWID=jsonfile["HWID"]).first()
        if sub1==None:
            sub1=subscribers(HWID=jsonfile["HWID"],custType=jsonfile["custType"],idkey=jsonfile["idkey"])
            sub1.lastDate=datetime.datetime.now()
        else:
            sub1.custType=jsonfile["custType"]
            sub1.idkey=jsonfile["idkey"]
            sub1.lastDate=datetime.datetime.now()
        sub1.save()
        search=subscribers.objects(HWID=jsonfile["HWID"]).first()
        if search==None:
            return make_response(jsonify(False),405)
        if search.HWID==jsonfile["HWID"]:
            if obj.TrialLeft>0 and jsonfile["custType"]=="Trial":
                obj.TrialLeft-=1
            elif obj.SubscribeLeft>0 and jsonfile["custType"]=="Sub":
                obj.SubscribeLeft-=1
            elif obj.LifetimeLeft>0 and jsonfile["custType"]=="Perma":
                obj.LifetimeLeft-=1
            obj.save()
        return make_response(jsonify((obj.to_json()),(search.to_json())),201)
    else:
        return 'Content-Type not supported!'

@app.route('/upgradedsubscribers/populate',methods=['POST'])
def db_populateUpgraded():
    #print(datetime.datetime.now())
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        jsonfile = request.json
        obj=upgradedresellers.objects(idkey=jsonfile["idkey"]).first()
        if obj==None:
            return make_response(jsonify(False),405)
        sub1=upgradedsubscribers.objects(HWID=jsonfile["HWID"]).first()
        if sub1==None:
            sub1=upgradedsubscribers(HWID=jsonfile["HWID"],custType=jsonfile["custType"],idkey=jsonfile["idkey"],chaos=jsonfile["chaos"],gather=jsonfile["gather"],una=jsonfile["una"])
            sub1.lastDate=datetime.datetime.now()
        else:
            if sub1.custType=="Trial":
                sub1.una=False
                sub1.gather=False
            sub1.idkey=jsonfile["idkey"]
            if jsonfile["una"]:
                sub1.una=True
            if jsonfile["chaos"]:
                sub1.custType=jsonfile["custType"]
                sub1.chaos=True
            if jsonfile["gather"]:
                sub1.gather=True
            if jsonfile["custType"]=="Sub":
                sub1.lastDate=datetime.datetime.now()
        sub1.save()

        if not jsonfile["chaos"]:
            pass
        elif jsonfile["custType"]=="Trial":
            obj.Trial+=1
        elif jsonfile["custType"]=="Sub":
            obj.Subscriber+=1
        elif jsonfile["custType"]=="Perma":
            obj.Lifetime+=1

        if jsonfile["una"]:
            obj.una+=1
        if jsonfile["chaos"]:
            obj.chaos+=1
        if jsonfile["gather"]:
            obj.gather+=1
        obj.total+=jsonfile["total"]   
        obj.save()
        return make_response(jsonify((obj.to_json()),(sub1.to_json())),201)
    else:
        return 'Content-Type not supported!'

@app.route('/upgradedsubscribers/dereseller',methods=['POST'])
def db_populatedeUpgraded():
    #print(datetime.datetime.now())
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        jsonfile = request.json
        obj=upgradedresellers.objects(idkey=jsonfile["idkey"]).first()
        if obj==None:
            return make_response(jsonify(False),405)
        sub1=upgradedsubscribers.objects(HWID=jsonfile["HWID"]).first()

        if not jsonfile["chaos"]:
            pass
        elif jsonfile["custType"]=="Trial":
            if obj.Trial>0:
                obj.Trial-=1
            else:
                return make_response(jsonify(False),405)
        elif jsonfile["custType"]=="Sub":
            if obj.Subscriber>0:
                obj.Subscriber-=1
            else:
                return make_response(jsonify(False),405)
        elif jsonfile["custType"]=="Perma":
            if obj.Lifetime>0:
                obj.Lifetime-=1
            else:
                return make_response(jsonify(False),405)

        if jsonfile["una"]:
            if obj.una>0:
                obj.una-=1
            else:
                return make_response(jsonify(False),405)
        if jsonfile["chaos"]:
            if obj.chaos>0:
                obj.chaos-=1
            else:
                return make_response(jsonify(False),405)
        if jsonfile["gather"]:
            if obj.gather>0:
                obj.gather-=1
            else:
                return make_response(jsonify(False),405)
        obj.total+=jsonfile["total"]   

        if sub1==None:
            sub1=upgradedsubscribers(HWID=jsonfile["HWID"],custType=jsonfile["custType"],idkey=jsonfile["idkey"],chaos=jsonfile["chaos"],gather=jsonfile["gather"],una=jsonfile["una"])
            sub1.lastDate=datetime.datetime.now()
        else:
            if sub1.custType=="Trial":
                sub1.una=False
                sub1.gather=False
            sub1.idkey=jsonfile["idkey"]
            if jsonfile["una"]:
                sub1.una=True
            if jsonfile["chaos"]:
                sub1.custType=jsonfile["custType"]
                sub1.chaos=True
            if jsonfile["gather"]:
                sub1.gather=True
            if jsonfile["custType"]=="Sub":
                sub1.lastDate=datetime.datetime.now()
        sub1.save()
        obj.save()
        return make_response(jsonify((obj.to_json()),(sub1.to_json())),201)
    else:
        return 'Content-Type not supported!'

@app.route('/customsubscribers/populate',methods=['POST'])
def db_populateCustom():
    #print(datetime.datetime.now())
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        jsonfile = request.json
        obj=upgradedresellers.objects(idkey=jsonfile["idkey"]).first()
        if obj==None:
            return make_response(jsonify(False),405)
        sub1=customsubscribers.objects(HWID=jsonfile["HWID"]).first()
        if sub1==None:
            sub1=customsubscribers(HWID=jsonfile["HWID"],custType=jsonfile["custType"],cust=jsonfile["cust"],type=jsonfile["type"],idkey=jsonfile["idkey"])
            sub1.lastDate=datetime.datetime.now()
        else:
            pass
        sub1.save()
        obj.save()
        return make_response(jsonify((obj.to_json()),(sub1.to_json())),201)
    else:
        return 'Content-Type not supported!'



@app.route('/subscribers/<HWID>',methods=['GET'])
def HWIDExists(HWID):
    obj=subscribers.objects(HWID=HWID).first()
    if obj==None:
        return make_response(jsonify(False),404)
    return make_response(jsonify(True),201)

@app.route('/updater/',methods=['GET'])
def updatercurrent():
    obj=updater.objects().first()
    if obj==None:
        return make_response(jsonify(False),404)
    return make_response(jsonify(obj.to_json()),201)

@app.route('/updater/add',methods=['POST'])
def updaterpopulate():
    content_type = request.headers.get('Content-Type')
    jsonfile = request.json
    obj=updater(link=jsonfile["link"],version=jsonfile["version"])
    obj.save()
    return make_response(jsonify(obj.to_json()),201)

@app.route('/updater/change',methods=['POST'])
def updaterchange():
    content_type = request.headers.get('Content-Type')
    jsonfile = request.json
    obj=updater.objects().first()
    obj.link=jsonfile["link"]
    obj.version=jsonfile["version"]
    obj.save()
    return make_response(jsonify(obj.to_json()),201)

@app.route('/trial/',methods=['POST'])
def GetTrial():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        jsonfile = request.json
        obj=upgradedsubscribers.objects(HWID=jsonfile["HWID"]).first()
        if obj==None:
            #print(jsonfile["HWID"])
            sub1=upgradedsubscribers(HWID=jsonfile["HWID"],custType="Trial",idkey="TrialMaker",chaos=True,una=True,gather=True)
            sub1.lastDate=datetime.datetime.now()
            sub1.save()
            return make_response(jsonify(True),201)
        else:
            return make_response(jsonify(False),201)
    else:
        return 'Content-Type not supported!'

        
"""
@app.route('/trial/getAll',methods=['GET'])
def GetAllTrials():
    objects=upgradedsubscribers.objects(custType="Trial")
    for obj in objects:
        #print(obj.idkey,"--",obj.custType,"--",obj.HWID,"--")
        #obj.HWID=" "
        #print(obj.idkey,"--",obj.custType,"--",obj.HWID,"--")
        #obj.save()
        #print(obj.idkey,"--",obj.custType,"--",obj.HWID,"--")
        collectionUpgradedSub.delete_one({"HWID":obj.HWID})
"""




@app.route('/subscribers/test',methods=['POST'])
def getbyHWID():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        jsonfile = request.json
        #print(jsonfile["HWID"])
        obj=subscribers.objects(HWID=jsonfile["HWID"]).first()
        if obj==None:
            return make_response(jsonify(False),404)
        timeSpent=(datetime.datetime.now()-obj.lastDate).total_seconds()/86400
        if obj.custType=="Perma" or (obj.custType=="Sub" and timeSpent<30) or (obj.custType=="Trial" and timeSpent<1):
            return make_response(jsonify(True),201)
        return make_response(jsonify(False),201)
    else:
        return 'Content-Type not supported!'


@app.route('/upgradedsubscribers/access',methods=['POST'])
def getbyupgradedHWID():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        jsonfile = request.json
        #print(encmessage)
        #decmessage = fernet.decrypt(encmessage).decode()
        #print(decmessage)
        obj=upgradedsubscribers.objects(HWID=jsonfile["HWID"]).first()
        response=[]
        if obj==None:
            return make_response(jsonify(False),404)
        timeSpent=(datetime.datetime.now()-obj.lastDate).total_seconds()/86400
        if obj.custType=="Perma" or (obj.custType=="Sub" and timeSpent<30) or (obj.custType=="Trial" and timeSpent<1):
            encmessage=fernet.encrypt((jsonfile["HWID"]+"CHA").encode())
        else:
            encmessage=fernet.encrypt((jsonfile["HWID"]+"FAI").encode())
        response.append(encmessage.decode())
        
        if obj.una and (obj.custType=="Trial" and timeSpent>1):
            obj.una=False
            obj.gather=False
            obj.save()

        if obj.una:
        #if True:
            encmessage=fernet.encrypt((jsonfile["HWID"]+"UNA").encode())
        else:
            encmessage=fernet.encrypt((jsonfile["HWID"]+"FAI").encode())
        response.append(encmessage.decode())
        
        #if obj.gather:
        if True:
            encmessage=fernet.encrypt((jsonfile["HWID"]+"GAT").encode())
        else:
            encmessage=fernet.encrypt((jsonfile["HWID"]+"FAI").encode())
        response.append(encmessage.decode())

        return make_response(jsonify(response[0],response[1],response[2]),201)
    else:
        return 'Content-Type not supported!'

@app.route('/customsubscribers/access',methods=['POST'])
def getbycustomHWID():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        jsonfile = request.json
        obj=customsubscribers.objects(HWID=jsonfile["HWID"]).first()
        response=[]
        if obj==None or obj.type!=jsonfile["type"]:
            return make_response(jsonify(False),404)
        timeSpent=(datetime.datetime.now()-obj.lastDate).total_seconds()/86400
        if obj.custType=="Perma" or (obj.custType=="Sub" and timeSpent<30) or (obj.custType=="Trial" and timeSpent<1):
            encmessage=fernet.encrypt((jsonfile["HWID"]+"CUS").encode())
            #print("Succ")
        else:
            encmessage=fernet.encrypt((jsonfile["HWID"]+"FAI").encode())
            #print("SFAc")
        response.append(encmessage.decode())

        return make_response(jsonify(response[0]),201)
    else:
        return 'Content-Type not supported!'




@app.route('/subscribers/patch',methods=['PUT'])
def subpatch():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        jsonfile = request.json
        obj=subscribers.objects(HWID=jsonfile["HWID"]).first()
        obj.custType=jsonfile["custType"]
        obj.lastDate=datetime.datetime.now()
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

@app.route('/upgradedresellers',methods=['POST'])
def db_upgradedpopulateReseller():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        jsonfile = request.json
        sub1=upgradedresellers.objects(idkey=jsonfile["idkey"]).first()
        if sub1==None:
            sub1=upgradedresellers(idkey=jsonfile["idkey"],Trial=jsonfile["Trial"],Subscriber=jsonfile["Subscriber"],Lifetime=jsonfile["Lifetime"],chaos=jsonfile["chaos"],gather=jsonfile["gather"],una=jsonfile["una"],total=0)
            sub1.save()
        else:
            sub1.Trial=jsonfile["Trial"]
            sub1.Subscriber=jsonfile["Subscriber"]
            sub1.Lifetime=jsonfile["Lifetime"]
            sub1.chaos=jsonfile["chaos"]
            sub1.gather=jsonfile["gather"]
            sub1.una=jsonfile["una"]
            sub1.total=0
            sub1.save()
        return make_response(jsonify(sub1.to_json()),201)
    else:
        return 'Content-Type not supported!'

@app.route('/upgradedsubscribers/fill',methods=['GET'])
def copyOver():
    obj=subscribers.objects()
    for i in range(len(obj)):
        #print(obj[i].HWID)
        currUpgSub=upgradedsubscribers(HWID=obj[i].HWID,custType=obj[i].custType,idkey=obj[i].idkey,lastDate=obj[i].lastDate,chaos=True,una=False,gather=False)
        currUpgSub.save()
    return make_response(jsonify(True),201)



@app.route('/resellers/<idkey>',methods=['GET'])
def idkeyupgradedreturn(idkey):
    obj=resellers.objects(idkey=idkey).first()
    if obj==None:
        return make_response(jsonify(False),404)
    return make_response(jsonify(obj.to_json()),201)

@app.route('/upgradedresellers/<idkey>',methods=['GET'])
def idkeyreturn(idkey):
    obj=upgradedresellers.objects(idkey=idkey).first()
    if obj==None:
        return make_response(jsonify(False),404)
    return make_response(jsonify(obj.to_json()),201)

@app.route('/resellerssold/<idkey>',methods=['GET'])
def idkeyreturnsolds(idkey):
    if idkey=="All":
        obj=subscribers.objects()
    else:
        obj=subscribers.objects(idkey=idkey)
    trcount=0
    subcount=0
    permacount=0
    for i in obj:
        if i.custType=="Trial":
            trcount+=1
        elif i.custType=="Sub":
            subcount+=1
        elif i.custType=="Perma":
            permacount+=1
    if obj==None:
        return make_response(jsonify(False),404)
    return make_response(jsonify(True,trcount,subcount,permacount),201)


if __name__=='__main__':
    app.run(host='0.0.0.0',port=2999)

