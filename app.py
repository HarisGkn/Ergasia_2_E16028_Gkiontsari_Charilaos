from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import uuid
import time

# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Choose database
db = client['DSMarkets']

# Choose collections
users = db['Users']
products = db['Products']
uuids = db['uuid']

uuids.delete_many({})

# Initiate Flask App
app = Flask(__name__)

users_sessions = {}

document = uuids.find_one({})

def create_session(username):
    user_uuid = str(uuid.uuid1())
    users_sessions[user_uuid] = (username, time.time())
    return user_uuid  

def is_session_valid(user_uuid):
    # return user_uuid in users_sessions
    return uuids.find()


@app.route('/createUser', methods=['POST'])
def create_user():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "name" in data or not "password" in data or not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if users.update({'name': data['name'], 'password':data['password'], 'email':data['email']},data, upsert=True,): 
        return Response(data['name']+" was added to the MongoDB", mimetype='application/json'),200 # ΠΡΟΣΘΗΚΗ STATUS
    else:
        return Response("A user with the given email already exists", mimetype='application/json'),400 # ΠΡΟΣΘΗΚΗ STATUS


@app.route('/login', methods=['POST'])
def login():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")


    if users.find({ "email" : data['email'], "password" : data['password']} ).count() > 0: 
        user_uuid = create_session(data['email'])
        res = {"uuid": user_uuid, "email": data['email']}
        uuids.insert_one({'email': data['email'] ,"uuid": user_uuid})
        return Response(json.dumps(res), mimetype='application/json'),200 # ΠΡΟΣΘΗΚΗ STATUS
    else:
        # Μήνυμα λάθους (Λάθος email ή password)
        return Response("Wrong email or password.",mimetype='application/json'),400 # ΠΡΟΣΘΗΚΗ STATUS


@app.route('/addProducts', methods=['POST'])
def add_product():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "name" in data or not "category" in data or not "quantity" in data or not "description" in data or not "price" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    
    if uuids.find_one({'email': 'admin'}):
        if products.insert_one({'name': data['name'], 'category':data['category'], 'quantity':data['quantity'], 'description':data['description'], 'price':data['price']}): 
            return Response(data['name']+" was added to the MongoDB", mimetype='application/json'),200 # ΠΡΟΣΘΗΚΗ STATUS
        else:
            return Response("A product with the given name already exists", mimetype='application/json'),400 # ΠΡΟΣΘΗΚΗ STATUS
    else:
        return Response("Log in as admin to add products",mimetype='application/json')
    


@app.route('/deleteProduct', methods=['DELETE'])
def delete_product():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "name" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if uuids.find_one({'email': 'admin'}):
        if products.find_one({'name': data['name']}):
            products.delete_one({'name': data['name']})
            msg = "product deleted"
            return Response(msg, status=200, mimetype='application/json')
        else:
            return "No product found"
    else:
        return Response("Log in as admin to delete products",mimetype='application/json')


# Εκτέλεση flask service σε debug mode, στην port 5000. 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)