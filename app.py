from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
from bson import json_util
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
cart = db['cart']
purchased = db['purchased']

uuids.delete_many({})
cart.delete_many({})

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
    return uuids.find_one({})

# sign up
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

    if users.update({'name': data['name'], 'password':data['password'], 'email':data['email'], 'category':data['category']},data, upsert=True,): 
        return Response(data['name']+" was added to the MongoDB", mimetype='application/json'),200 # ΠΡΟΣΘΗΚΗ STATUS
    else:
        return Response("A user with the given email already exists", mimetype='application/json'),400 # ΠΡΟΣΘΗΚΗ STATUS

# login
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
        y=""
        agg_result= users.aggregate(
            [{
            "$group" : 
                {"_id" : None,
                "category": { "$first": "$category" }
                 }}
            ])
        for i in agg_result:
            y = i

        user_uuid = create_session(data['email'])
        res = {"uuid": user_uuid, "email": data['email'], "category": y}
        uuids.insert_one({'email': data['email'] ,"uuid": user_uuid, "category": y})
        return Response(json.dumps(res), mimetype='application/json'),200 # ΠΡΟΣΘΗΚΗ STATUS
    else:
        # Μήνυμα λάθους (Λάθος email ή password)
        return Response("Wrong email or password.",mimetype='application/json'),400 # ΠΡΟΣΘΗΚΗ STATUS

# προσθήκη προιόντων
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
        if products.insert_one({'_id':data['id'],'name': data['name'], 'category':data['category'], 'quantity':data['quantity'], 'description':data['description'], 'price':data['price']}): 
            return Response("product added", mimetype='application/json'),200 # ΠΡΟΣΘΗΚΗ STATUS
        else:
            return Response("A product with the given name already exists", mimetype='application/json'),400 # ΠΡΟΣΘΗΚΗ STATUS
    else:
        return Response("Log in as admin to add products",mimetype='application/json')
    

# διαγραφή προιόντος
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
    if not "id" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if uuids.find_one({'email': 'admin'}):
        if products.find_one({'_id': data['id']}):
            products.delete_one({'_id': data['id']})
            msg = "product deleted"
            return Response(msg, status=200, mimetype='application/json')
        else:
            return "No product found"
    else:
        return Response("Log in as admin to delete products",mimetype='application/json')

# ενημέρωση κατηγορίας
@app.route('/patchProductCategory', methods=['PATCH'])
def patch_product_category():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "id" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if uuids.find_one({'email': 'admin'}):
        if products.find_one({'_id': data['id']}):
            products.update({'_id': data['id']}, {'$set': {'category': data['category']}})
            msg = "product updated"
            return Response(msg, status=200, mimetype='application/json')
        else:
            return "No name found"
    else:
        return Response("Log in as admin first",mimetype='application/json') 

# ενημέρωση τιμής
@app.route('/patchProductPrice', methods=['PATCH'])
def patch_product_price():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "id" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if uuids.find_one({'email': 'admin'}):
        if products.find_one({'_id': data['id']}):
            products.update({'_id': data['id']}, {'$set': {'price': data['price']}})
            msg = "product updated"
            return Response(msg, status=200, mimetype='application/json')
        else:
            return "No name found"
    else:
        return Response("Log in as admin first",mimetype='application/json') 

# ενημέρωση ποσότητας
@app.route('/patchProductQuantity', methods=['PATCH'])
def patch_product_quantity():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "id" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if uuids.find_one({'email': 'admin'}):
        if products.find_one({'_id': data['id']}):
            products.update({'_id': data['id']}, {'$set': {'quantity': data['quantity']}})
            msg = "product updated"
            return Response(msg, status=200, mimetype='application/json')
        else:
            return "No name found"
    else:
        return Response("Log in as admin first",mimetype='application/json') 

# ενημέρωση περιγραφής
@app.route('/patchProductDescription', methods=['PATCH'])
def patch_product_description():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "id" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if uuids.find_one({'email': 'admin'}):
        if products.find_one({'_id': data['id']}):
            products.update({'_id': data['id']}, {'$set': {'description': data['description']}})
            msg = "product updated"
            return Response(msg, status=200, mimetype='application/json')
        else:
            return "No name found"
    else:
        return Response("Log in as admin first",mimetype='application/json') 


# αναζήτηση βάσει ονόματος
@app.route('/getByName', methods=['GET'])
def get_by_name():
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

    if(is_session_valid(document)):
        product = list(products.find({'name': data['name']}))
        return Response(json.dumps(product, default=json_util.default), status=200, mimetype='application/json')
    else:
        return Response("Log in first",mimetype='application/json'),400 

# αναζήτηση βάσει κατηγορίας
@app.route('/getByCat', methods=['GET'])
def get_by_cat():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "category" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if(is_session_valid(document)):
        product = list(products.find({'category': data['category']}))
        return Response(json.dumps(product, default=json_util.default), status=200, mimetype='application/json')
    else:
        return Response("Log in first",mimetype='application/json'),400 

# αναζήτηση βάσει id
@app.route('/getById', methods=['GET'])
def get_by_id():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "id" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if(is_session_valid(document)):
        product = list(products.find({'_id': data['id']}))
        return Response(json.dumps(product, default=json_util.default), status=200, mimetype='application/json')
    else:
        return Response("Log in first",mimetype='application/json'),400 


# προσθήκη προιόντων/cart
@app.route('/addToCart', methods=['POST'])
def add_to_cart():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "id" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    
    if (is_session_valid(document)):
        if products.find_one({'_id': data['id']}):
            lst = list(products.find({'_id': data['id']}))
            # print(lst)
            cart.insert_many(lst)
            return Response("product was added to the cart", mimetype='application/json'),200 # ΠΡΟΣΘΗΚΗ STATUS
        else:
            return Response("no product found",mimetype='application/json')
    else:
        return Response("Log in as admin to add products",mimetype='application/json')

hasRun=False
# εμφανιση καλαθιου
@app.route('/getCart', methods=['GET'])
def get_cart():
    global hasRun
    hasRun = True
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    
    if(is_session_valid(document)):
        agg_result= cart.aggregate(
            [{
            "$group" : 
                {"_id" : "price",
                "total": {"$sum": "$price"}
                 }}
            ])
        for i in agg_result:
            x = i
        cart.insert_one(x)
        cart1 = list(cart.find())
        return Response(json.dumps(cart1, default=json_util.default), status=200, mimetype='application/json')
    else:
        return Response("Log in first",mimetype='application/json'),400 

# αγορα
@app.route('/BuyCart', methods=['POST'])
def buy_cart():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "ccInfo" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    ccInfo = [ 
        data['ccInfo']
    ]

    if(hasRun==True):
        if(is_session_valid(document)):
            if(len(data["ccInfo"])==16):
                # purchased.insert_one({'cc':data["ccInfo"],'purchased':list(cart.find()), 'user': list(uuids.find())})
                # cart.insert({"ccInfo":ccInfo})
                users.update({'email': 'admin'},{'$addToSet':{'history': list(cart.find())}})
                purchased.insert_one({'purchased':list(cart.find()), 'user': list(uuids.find())})
                return Response("purchase completed", mimetype='application/json'),200
            else:
                return Response("credit card info needs to be 16 digits long",mimetype='application/json'),400 
        else:
            return Response("Log in first",mimetype='application/json'),400 
    else:
        return Response("run getCart first",mimetype='application/json'),400 

# εμφανιση ιστορικού
@app.route('/getHistory', methods=['GET'])
def get_history():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")


    if(is_session_valid(document)):
        history = list(purchased.find({"user.email": data["email"]}))
        return Response(json.dumps(history, default=json_util.default), status=200, mimetype='application/json')
    else:
        return Response("Log in first",mimetype='application/json'),400 


# διαγραφή προιόντος/cart
@app.route('/deleteProductCart', methods=['DELETE'])
def delete_product_cart():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "id" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if(is_session_valid(document)):
        if cart.find_one({'_id': data['id']}):
            cart.delete_one({'_id': data['id']})
            msg = "product deleted from cart"
            return Response(msg, status=200, mimetype='application/json')
        else:
            return "No product found"
    else:
        return Response("Log in first",mimetype='application/json'),400 


# διαγραφή user
@app.route('/deleteUser', methods=['DELETE'])
def delete_user():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    if(is_session_valid(document)):
        # print(uuids.find_one({"email": data['email']}))
        users.delete_one({'email': data['email']})
        msg = "user deleted"
        return Response(msg, status=200, mimetype='application/json')
    else:
        return Response("Log in first",mimetype='application/json'),400 

# Εκτέλεση flask service σε debug mode, στην port 5000. 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)