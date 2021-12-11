from flask import Flask,render_template,request, make_response
from flask import jsonify
from flask_pymongo import PyMongo
from flask_pymongo import ObjectId

application = Flask(__name__)
application.config["MONGO_URI"] = "mongodb+srv://shamal:CUzcTxAqUVRW8Xan@cluster0.4brhm.mongodb.net/loan?authSource=admin&replicaSet=atlas-zn6p9b-shard-0&w=majority&readPreference=primary&appname=MongoDB%20Compass&retryWrites=true&ssl=true"
mongodb_client = PyMongo(application)
db = mongodb_client.db

@application.route('/', methods=["GET"])
def route_home():
    tot = db.totals.find()
    currentTotal = 0;
    totId = "";
    for document in tot:
        currentTotal = document['total']
        totId = str(document['_id'])
    return render_template('index.html', total=currentTotal)

@application.route('/deposit', methods=["GET", "POST"])
def route_deposit():
    if request.method =='POST':
        name = request.form['name']
        amount = request.form['amount']
        db.users.insert_one({"name": name, "amount": int(amount)})
        tot = db.totals.find()
        currentTotal = 0;
        totId = "";
        for document in tot:
            currentTotal = document['total']
            totId = str(document['_id'])
        currentTotal = currentTotal + int(amount)
        db.totals.update_one({"_id":ObjectId(totId)}, {"$set":{"total":currentTotal}})
    return render_template('deposit.html')

@application.route('/get-loan', methods=["GET", "POST"])
def route_getLoan():
    response = []
    data = db.users.find()
    for document in data:
        document['_id'] = str(document['_id'])
        response.append(document)
    if request.method =='POST':
        name = request.form['name']
        guarantee = request.form['guarantee']
        amount = request.form['amount']
        if(name != guarantee):
            user = db.users.find_one({"_id":ObjectId(name)})
            guaranteeDetails = db.users.find_one({"_id":ObjectId(guarantee)})
            aligibalAmount = user['amount'] + guaranteeDetails['amount']
            if ("currentLoan" in user):
                print("has order")
            else:
                if(aligibalAmount >= int(amount)):
                    id = db.loans.insert_one({"user": ObjectId(name), "guarantee": ObjectId(guarantee), "amount": int(amount), "state": "active"})
                    db.users.update_one({"_id":ObjectId(name)},{"$set":{"currentLoan":ObjectId(id.inserted_id)}})
        # db.users.insert_one({"name": name, "amount": int(amount)})
    return render_template('getLoan.html', users=response)

@application.route('/pay', methods=["GET", "POST"])
def route_pay():
    response = []
    data = db.users.find()
    for document in data:
        document['_id'] = str(document['_id'])
        response.append(document)
    if request.method =='POST':
        name = request.form['name']
        amount = request.form['amount']
        user = db.users.find_one({"_id": ObjectId(name)})
        if ("currentLoan" in user):
            loan = db.loans.find_one({"_id": ObjectId(user['currentLoan'])})
            if(int(amount) >= loan['amount']):
                db.loans.update_one({"_id":ObjectId(user['currentLoan'])},{"$set":{"state":"closed"}})
                db.users.update_one({"_id":ObjectId(name)},{"$unset": {"currentLoan":""}})
    return render_template('payLoan.html', users=response)

if __name__ == '__main__':
    application.run(debug=True)