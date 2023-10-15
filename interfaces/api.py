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
from flask import jsonify, make_response

import psycopg2
from datetime import datetime
token_security = "cbdcitb"

cbdcID = "e702e3530f81e19b73ce331173638c00"
bankBalance = "a50493399674fb1c80eaa6f5c0bfc339"

insert_query = """
    INSERT INTO transaction.logs (uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
"""

try:
    conn = psycopg2.connect(
        dbname='cbdc',
        user='cbdc',
        password='cbdcS3cret',
        host='localhost',
        port='5432'
    )
except Exception as e:
    print(f"Error: Unable to connect to the database: {e}")
    exit()

cursor = conn.cursor()
app = Flask(__name__)

@app.route('/')
def home():
    return 'block-chain apis'

def TrxCBDC(uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time):
    try:
        cursor.execute(
            insert_query,
            (uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
        )
        transaction_id = cursor.fetchone()[0]
        conn.commit()
        print("Data has been inserted successfully")
    except Exception as e:
        print(f"Error: Unable to insert data: {e}")
        conn.rollback()

def convertCBDC(uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time):
    try:
        cursor.execute(
            insert_query,
            (uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
        )
        transaction_id = cursor.fetchone()[0]
        conn.commit()
        print("Data has been inserted successfully")
    except Exception as e:
        print(f"Error: Unable to insert data: {e}")
        conn.rollback()

def convertCBDCApprove(uid, destination_uid, transaction_amount):
    query = f"SELECT * FROM transaction.logs WHERE transaction_type = 'balance' AND uid = '{cbdcID}' order by id desc LIMIT 1"
    cursor.execute(query)
    rows = cursor.fetchall()
    if rows:
        balance_cbdc = rows[0][4]
    else:
        balance_cbdc = 0

    query = f"SELECT * FROM transaction.logs WHERE transaction_type = 'convert' AND uid = '{bankBalance}' order by id desc LIMIT 1"
    cursor.execute(query)
    rows = cursor.fetchall()
    if rows:
        balance_convert = rows[0][4]
    else:
        balance_convert = 0

    balance_cbdc = int(balance_cbdc)
    
    if int(balance_convert) >= int(transaction_amount):
        balance_approve = int(transaction_amount)
        balance_bank = int(balance_convert) - int(transaction_amount)
        balance_cbdc = int(balance_cbdc) + int(balance_approve)

    store_uid = uid
    store_destination_uid = destination_uid
    store_destination_type = "central"
    store_transaction_type = "approve-convert"
    store_transaction_amount = transaction_amount
    store_transaction_date_time = datetime.now()

    try:
        cursor.execute(
            insert_query,
            (store_uid, store_destination_uid, store_destination_type, store_transaction_type, store_transaction_amount, store_transaction_date_time)
        )
        transaction_id = cursor.fetchone()[0]
        conn.commit()
        print("Data has been inserted successfully")
    except Exception as e:
        print(f"Error: Unable to insert data: {e}")
        conn.rollback()

    store_uid = bankBalance
    store_destination_uid = bankBalance
    store_destination_type = "system"
    store_transaction_type = "balance"
    store_transaction_amount = balance_bank
    store_transaction_date_time = datetime.now()

    try:
        cursor.execute(
            insert_query,
            (store_uid, store_destination_uid, store_destination_type, store_transaction_type, store_transaction_amount, store_transaction_date_time)
        )
        transaction_id = cursor.fetchone()[0]
        conn.commit()
        print("Data has been inserted successfully")
    except Exception as e:
        print(f"Error: Unable to insert data: {e}")
        conn.rollback()

    store_uid = cbdcID
    store_destination_uid = cbdcID
    store_destination_type = "system"
    store_transaction_type = "balance"
    store_transaction_amount = balance_cbdc
    store_transaction_date_time = datetime.now()

    try:
        cursor.execute(
            insert_query,
            (store_uid, store_destination_uid, store_destination_type, store_transaction_type, store_transaction_amount, store_transaction_date_time)
        )
        transaction_id = cursor.fetchone()[0]
        conn.commit()
        print("Data has been inserted successfully")
    except Exception as e:
        print(f"Error: Unable to insert data: {e}")
        conn.rollback()



def approveIssue(uid, destination_uid, transaction_amount):
    query = f"SELECT * FROM transaction.logs WHERE transaction_type = 'balance' AND uid = '{cbdcID}' order by id desc LIMIT 1"
    cursor.execute(query)
    rows = cursor.fetchall()
    if rows:
        balance_cbdc = rows[0][4]
    else:
        balance_cbdc = 0
    
    query = f"SELECT * FROM transaction.logs WHERE transaction_type = 'balance' AND uid = '{destination_uid}' order by id desc LIMIT 1"
    cursor.execute(query)
    rows = cursor.fetchall()
    if rows:
        balance_user = rows[0][4]
    else:
        balance_user = 0

    balance_cbdc = int(balance_cbdc) - int(transaction_amount)
    balance_user = int(balance_user) + int(transaction_amount)

    store_uid = uid
    store_destination_uid = destination_uid
    store_destination_type = "central"
    store_transaction_type = "approve"
    store_transaction_amount = transaction_amount
    store_transaction_date_time = datetime.now()

    try:
        cursor.execute(
            insert_query,
            (store_uid, store_destination_uid, store_destination_type, store_transaction_type, store_transaction_amount, store_transaction_date_time)
        )
        transaction_id = cursor.fetchone()[0]
        conn.commit()
        print("Data has been inserted successfully")
    except Exception as e:
        print(f"Error: Unable to insert data: {e}")
        conn.rollback()

    store_uid = destination_uid
    store_destination_uid = destination_uid
    store_destination_type = "system"
    store_transaction_type = "balance"
    store_transaction_amount = balance_user
    store_transaction_date_time = datetime.now()

    try:
        cursor.execute(
            insert_query,
            (store_uid, store_destination_uid, store_destination_type, store_transaction_type, store_transaction_amount, store_transaction_date_time)
        )
        transaction_id = cursor.fetchone()[0]
        conn.commit()
        print("Data has been inserted successfully")
    except Exception as e:
        print(f"Error: Unable to insert data: {e}")
        conn.rollback()

    store_uid = cbdcID
    store_destination_uid = cbdcID
    store_destination_type = "system"
    store_transaction_type = "balance"
    store_transaction_amount = balance_cbdc
    store_transaction_date_time = datetime.now()

    try:
        cursor.execute(
            insert_query,
            (store_uid, store_destination_uid, store_destination_type, store_transaction_type, store_transaction_amount, store_transaction_date_time)
        )
        transaction_id = cursor.fetchone()[0]
        conn.commit()
        print("Data has been inserted successfully")
    except Exception as e:
        print(f"Error: Unable to insert data: {e}")
        conn.rollback()

def blockchainStore(store_uid, store_destination_uid, store_destination_type, store_transaction_type, store_transaction_amount, store_transaction_date_time):
    now = datetime.now()
    transaction_date_time = now.strftime("%d/%m/%Y %H:%M:%S")
    filename = "logs/"+str(uuid.uuid4())+".sh"

    fin = open("InsertQuery.sh", "rt")
    fout = open(filename, "w+")
    for line in fin:
        line = line.replace('VAR_UID', uid)
        line = line.replace('VAR_DESTINATION', destination_uid)
        line = line.replace('VAR_TRANSACTION_ID', transaction_id)
        line = line.replace('VAR_TRANSACTION_TYPE', transaction_type)
        line = line.replace('VAR_TRANSACTION_AMOUNT', transaction_amount)
        line = line.replace('VAR_TRANSACTION_DATETIME', transaction_date_time)
        fout.write(line)
    fin.close()
    fout.close()
    subprocess.run ( [ "sh", filename] )
    

@app.route('/insert', methods = ['POST'])
def insert():
    txid = ""
    transaction_id = ""

    token = request.args.get('token')
    if(token != token_security):
        return jsonify(status=0, message="invalid token")

    uid = request.args.get('uid')
    destination_uid = request.args.get('destination_uid')
    destination_type = request.args.get('destination_type')
    transaction_type = request.args.get('transaction_type')
    transaction_amount = request.args.get('transaction_amount')
    transaction_date_time = datetime.now()

    if transaction_type == "approve":
        approveIssue(uid, destination_uid, transaction_amount)
    elif transaction_type == "approve-convert":
        convertCBDCApprove(uid, destination_uid, transaction_amount)
    elif transaction_type == "convert":
        convertCBDC(uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
    else:
        TrxCBDC(uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)

    # blockchainStore(store_uid, store_destination_uid, store_destination_type, store_transaction_type, store_transaction_amount, store_transaction_date_time)
    
    return jsonify(status=1, message="successfully", transaction_id=transaction_id)

if __name__ == '__main__':
    app.run(host="0.0.0.0",  port=8000, debug=True)
