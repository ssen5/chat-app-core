from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")

db = client['chatapp2']

chatsdb = db['chats']
usersdb = db['users'] 
countersdb = db['counters']
groupsdb = db['groups']

def increment(name):
    document = countersdb.find_one({'id':name})
    value = document['value']
    value += 1
    countersdb.update_one({'id': name}, {"$set": {"value": value}})
    
    return value

def check(username):
    data = usersdb.find_one({"username":username})
    if data :
        return {"status":1,"data":data,"msg":"User Found"}
    else:
        return {"status":0,"msg":"User Not Found"}

def getID(username):
    isValid = check(username)
    if isValid['status']:
        return {"status":1,"data":isValid['data']['user_id'],"msg":"User Found"}
    else:
        return {"status":0,"msg":"User Not Found"}

def getUsername(user_id):
    try:
        data = usersdb.find_one({"user_id":user_id})
        return {"status":1,"msg":"User Found","data":data['username']}
    except:
        return {"status":0,"msg":"User Not Found"}

def sendMessage(snd,rcv,msg,typ="text"):
    sndID = getID(snd)['data']
    rcvID = getID(rcv)['data']

    if typ=="text":
        try:
            value = increment("chats")
            chatsdb.insert_one({
                "isGroup": False,
                "type": "text",
                "chatid": value,
                "snd": sndID,
                "rcv": rcvID,
                "msg": msg,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            return {"status":1,"msg":"Message Send Successfully"}
        except:
            return {"status":0,"msg":"Error Occured"}
    
def sendGroupMessage(snd,group_id,msg,typ="text"):
    sndID = getID(snd)['data']

    if typ=="text":
        try:
            if groupsdb.find_one({"group_id":group_id}):
                value = increment("chats")
                
                chatsdb.insert_one({
                    "isGroup": True,
                    "type": "text",
                    "chatid": value,
                    "snd": sndID,
                    "group_id":group_id,
                    "msg": msg,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                groupsdb.update_one({"group_id":group_id},
                                    {"$set":{"last_chat_id":value}})
                

                return {"status":1,"msg":"Message Send Successfully"}
            else:
                return {"status":0,"msg":"No such group exists"}
        except:
            return {"status":0,"msg":"Error Occured"}

def login(username,password):
    data = usersdb.find_one({"username":username,"password":password})

    if data:
        return {"status":1,"msg":"User Credentials Matched"}
    else:
        return {"status":0,"msg":"Bad Credentials"}
    
def createAccount(username,password,name):
    data = usersdb.find_one({"username":username})
    if not data:
        try:
            value = increment("users")
            usersdb.insert_one({
                "user_id":value,
                "username": username,
                "password": password,
                "name": name
            })

            return {"status":1,"msg":"New User Created"}
        except:
            return {"status":0,"msg":"Error while creating"}
        
    else:
        return {"status":0,"msg":"User Already exists"}

def createGroup(username,group_name):
    user_id = getID(username)['data']
    try:
        value = increment("groups")
        groupsdb.insert_one({
            "group_id": value,
            "name": group_name,
            "users":[ user_id ],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "admin": [ user_id ],
            "last_chat_id": None
        })
        return {"status":1,"msg":"Group Creation Successfull"}
    except:
        return {"status":0,"msg":"Group Creation Failed"}
    
def addUserToGroup(username,friend,group_id):
    user_id = getID(username)['data']
    friend_id = getID(friend)['data']

    data = groupsdb.find_one({"group_id":group_id})

    if data and (user_id in data['admin']):
        lst = list(groupsdb.find_one({"group_id": group_id})['users'])
        lst.append(friend_id)

        groupsdb.update_one({"group_id":group_id},{"$set":{"users":lst}})

        return {"status":1,"msg":"User added to group"}
    else:
        return {"status":0,"msg":"Priviledge denied"}

def getMessages(user1, user2):
    if check(user1)['status'] and check(user2)['status']:
        user1ID = getID(user1)['data']
        user2ID = getID(user2)['data']
        messages = chatsdb.find(
            {
                "$or": [
                    {"snd": user1ID, "rcv": user2ID},
                    {"snd": user2ID, "rcv": user1ID}
                ]
            },
            {"_id": 0}
        )

        if messages:
            return {"status":1,"msg":"Messages Fetched Succesfully","data":list(messages)}
        else:
            return {"status":1,"msg":"No messages"}
    else:
        return {"status":1,"msg":"One of the users not Found"}

def getGroupMessages(group_id):
    chat_doc = chatsdb.find({"group_id":group_id},{"_id": 0})
    if chat_doc:
        return {"status":1,"msg":"Chats Found for this group","data":list(chat_doc)}
    else:
        return {"status":0,"msg":"No chats found for this group"}

def getChatUsers(username):
    user_id = getID(username)['data']
    users = chatsdb.aggregate([
        {"$match": {"$or": [{"snd": user_id}, {"rcv": user_id}], "isGroup": False}},

        {"$sort": {"time": -1}},

        {"$group": {
            "_id": {"$cond": [{"$eq": ["$snd", user_id]}, "$rcv", "$snd"]},
            "latestChat": {"$first": "$$ROOT"}  
        }},

        {"$replaceRoot": {"newRoot": "$latestChat"}},
        {"$project": {"_id": 0}}
    ])

    datas = list(users)

    return datas

def getChatGroups(username):
    user_id = getID(username)['data']

    arr=[]
    datas = groupsdb.find({"users":user_id})

    for data in datas:
        chat_doc = chatsdb.find_one({"chatid":data['last_chat_id']},{"_id": 0})
        if chat_doc:  
            arr.append(chat_doc)

    return arr

def getLatestChats(username):

    dms = getChatUsers(username)
    gms = getChatGroups(username)

    inbox = dms+gms

    datas = list(inbox)

    sorted_datas = sorted(datas, key=lambda x: x["chatid"],reverse=True)

    return sorted_datas



