import json
import os
from flask import Flask,jsonify,request
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin
from bson import ObjectId
from bson.json_util import dumps
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["MONGO_URI"] = "mongodb://meetmon-test:1testaccount@ds249311.mlab.com:49311/meetmon"
mongo = PyMongo(app)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = 'static'

def convert_result(mongo_result):
    mongo_result = list(mongo_result)
    result = []
    for item in mongo_result:
        current_result = {}
        current_result['_id'] = str(item['_id'])
        current_result['title'] = item['title']
        current_result['description'] = item['description']
        current_result['filename'] = item['filename']
        current_result['timestamp'] = item['timestamp']
        result.append(current_result)
    return jsonify(result)

@app.route("/event",methods=["GET","POST"])
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
    return convert_result(results)

def add_new_event():
    data_input = {'title':request.form['title'],'description':request.form['description'],'timestamp':datetime.now(),'filename':request.form['filename']}
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
    return convert_result(results)

def edit_details(id):
    data_input = {'title':request.form['title'],'description':request.form['description']}
    condition = {'_id':id}
    result = mongo.db.event.replace_one(condition,data_input)
    return jsonify({'_id':str(id)})

def delete_card(id):
    condition = {'_id':id}
    result = mongo.db.event.delete_one(condition)
    return jsonify({'count':result.deleted_count})

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload',methods=["POST"])
@cross_origin()
def upload_file():
    file = request.files['image']
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return filename