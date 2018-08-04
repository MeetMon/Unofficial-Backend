from flask import Flask,jsonify,request
import json
from flask_pymongo import PyMongo
from bson import ObjectId
from bson.json_util import dumps

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://meetmon-test:1testaccount@ds249311.mlab.com:49311/meetmon"
mongo = PyMongo(app)

@app.route("/event",methods=["GET","POST"])
def events_method():
    if request.method == "GET":
        get_all()
    else:
        add_new_event()

def get_all():
    results = mongo.db.event.find({})
    return jsonify(json.loads(dumps(results)))

def add_new_event():
    data_input = {'title':request.form['title'],'description':request.form['description']}
    result = mongo.db.event.insert_one(data_input)
    return jsonify(json.loads(dumps(result)))


@app.route("/event/<ObjectId:id>",methods=["GET","PUT","DELETE"])
def event_method():
    if request.method=="GET":
        get_details(id)
    elif request.method=="PUT":
        edit_details(id)
    else:
        delete_card(id)

def get_details(id):
    results = mongo.db.event.find({"_id":id})
    return jsonify(json.loads(dumps(results)))

def edit_details(id):
    data_input = {'title':request.form['title'],'description':request.form['description']}
    condition = {'_id':id}
    result = mongo.db.event.update_one(condition,{'$inc':data_input})
    return jsonify(json.loads(dumps(result)))

def delete_card(id):
    condition = {'_id':id}
    result = mongo.db.event.delete_one(condition)
    return jsonify(json.loads(dumps(result)))