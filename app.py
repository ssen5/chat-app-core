import a
from flask_cors import CORS
from flask import Flask,jsonify,request

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/createaccount', methods=['POST'])
def createaccount():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    
    name = data.get("name")

    values = a.createAccount(username,password,name)

    return jsonify(values)

@app.route('/sendmessage', methods=['POST'])
def sendmessage():
    data = request.get_json()

    snd = data.get("snd")
    rcv = data.get("rcv")
    msg = data.get("msg")

    if a.getID(snd)['status'] and a.getID(rcv)['status']:
        values = a.sendMessage(snd,rcv,msg)
        return jsonify(values)
    else:
        return jsonify({"status":0,"msg":"One of users not found"})

@app.route('/creategroup',methods=['POST'])
def creategroup():
    data = request.get_json()

    username = data.get("username")
    group_name = data.get("group_name")
    
    if a.getID(username)['status']:
        values = a.createGroup(username,group_name)
        return jsonify(values)
    else:
        return jsonify({"status":0,"msg":"User dosent exists"})

@app.route('/sendgroupmessage',methods=['POST'])
def sendgroupmessage():
    data = request.get_json()
    username = data.get("username")
    group_id = data.get("group_id")
    message = data.get("message")

    if a.getID(username)['status']:
        values = a.sendGroupMessage(username,group_id,message)
        return jsonify(values)
    else:
        return jsonify({"status":0,"msg":"User not found"})

@app.route("/addusertogroup",methods=['POST'])
def addusertogroup():
    data = request.get_json()
    username = data.get("username")  
    friend = data.get("friend")
    group_id = data.get("group_id")

    if a.getID(username)['status'] and a.getID(friend)['status']:
        values = a.addUserToGroup(username,friend,group_id)
        return jsonify(values)
    else:
        return jsonify({"status":0,"msg":"One of the users dont exists"})

@app.route('/login',methods=['POST'])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    value = a.login(username,password)

    return jsonify(value)

@app.route('/getmessages', methods=['POST'])
def gm():
    data = request.get_json()

    snd = data.get("snd")
    rcv = data.get("rcv")

    if a.getID(snd)['status'] and a.getID(rcv)['status']:
        values = a.getMessages(snd, rcv)  
        return jsonify(values)
    else:
        return jsonify({"status":0,"msg":"One of users not found"})
    
@app.route("/getgroupmessages",methods=['POST'])
def getgroupmessages():
    data = request.get_json()

    group_id = data.get("group_id")

    values = a.getGroupMessages(group_id)

    return jsonify(values)

@app.route('/getlatestchats',methods=['POST'])
def getlatestchats():
    data = request.get_json()

    username = data.get("username")

    if a.getID(username)['status']:
        values = a.getLatestChats(username)
        return jsonify(values)
    else:
        return jsonify({"status":0,"msg":"Username dosent exists"})

if __name__ == '__main__':
    app.run(debug=True)