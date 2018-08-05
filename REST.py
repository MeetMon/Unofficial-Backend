from flask import Flask,jsonify,request
import json
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin
from bson import ObjectId
from bson.json_util import dumps
from datetime import datetime

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["MONGO_URI"] = "mongodb://meetmon-test:1testaccount@ds249311.mlab.com:49311/meetmon"
mongo = PyMongo(app)

@app.route("/event/",methods=["GET","POST"])
@cross_origin()
def events_method():
    result = None
    if request.method == "GET":
        result = get_all()
    else:
        result = add_new_event()
    return result

def get_all():
    results = mongo.db.event.find({})
    return jsonify(json.loads(dumps(results)))

def add_new_event():
    data_input = {'title':request.form['title'],'description':request.form['description'],'timestamp':datetime.now()}
    result = mongo.db.event.insert_one(data_input)
    return jsonify({'_id':str(result.inserted_id)})


@app.route("/event/<ObjectId:id>",methods=["GET","PUT","DELETE"])
@cross_origin()
def event_method(id):
    result = None
    if request.method=="GET":
        result = get_details(id)
    elif request.method=="PUT":
        result = edit_details(id)
    else:
        result = delete_card(id)
    return result

def get_details(id):
    results = mongo.db.event.find({"_id":id})
    return jsonify(json.loads(dumps(results)))

def edit_details(id):
    data_input = {'title':request.form['title'],'description':request.form['description']}
    condition = {'_id':id}
    result = mongo.db.event.replace_one(condition,data_input)
    return jsonify({'_id':str(id)})

def delete_card(id):
    condition = {'_id':id}
    result = mongo.db.event.delete_one(condition)
    return jsonify({'count':result.deleted_count})