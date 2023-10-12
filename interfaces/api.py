import subprocess
import json
import hashlib
import random
import string
import datetime
import uuid

from datetime import datetime
from flask import request
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return 'block-chain apis'

@app.route('/insert', methods = ['POST'])
def insert():
    uid = request.args.get('uid')
    uid_destination = request.args.get('uid_destination')
    transaction_id = request.args.get('transaction_id')
    transaction_type = request.args.get('transaction_type')
    transaction_amount = request.args.get('transaction_amount')

    now = datetime.now()
    transaction_date_time = now.strftime("%d/%m/%Y %H:%M:%S")
    filename = "logs/"+str(uuid.uuid4())+".sh"

    fin = open("InsertQuery.sh", "rt")
    fout = open(filename, "w+")
    for line in fin:
        line = line.replace('VAR_UID', uid)
        line = line.replace('VAR_DESTINATION', uid_destination)
        line = line.replace('VAR_TRANSACTION_ID', transaction_id)
        line = line.replace('VAR_TRANSACTION_TYPE', transaction_type)
        line = line.replace('VAR_TRANSACTION_AMOUNT', transaction_amount)
        line = line.replace('VAR_TRANSACTION_DATETIME', transaction_date_time)
        fout.write(line)
    fin.close()
    fout.close()
    subprocess.run ( [ "sh", filename] )
    return transaction_id

if __name__ == '__main__':
    app.run(host="0.0.0.0",  port=8000, debug=True)
