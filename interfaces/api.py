import subprocess
import json
import hashlib
import random
import string
import datetime
import uuid
import time

from datetime import datetime
from flask import request
from flask import Flask, render_template
from flask import jsonify, make_response
from subprocess import check_output

import psycopg2
from datetime import datetime
token_security = "cbdcitb"

cbdcID = "e702e3530f81e19b73ce331173638c00"
bankBalance = "a50493399674fb1c80eaa6f5c0bfc339"

insert_query = """
    INSERT INTO transaction.logs (uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
"""

update_query = """ UPDATE transaction.logs
                SET txid = %s
                WHERE id = %s"""

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

def blockchainStore(uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time):
    now = datetime.now()
    transaction_date_time = now.strftime("%d/%m/%Y %H:%M:%S")
    filename_insert = "logs/insert_"+str(uuid.uuid4())+".sh"
    filename_verify = "logs/verify_"+str(uuid.uuid4())+".sh"

    fin = open("InsertQuery.sh", "rt")
    fout = open(filename_insert, "w+")
    for line in fin:
        line = line.replace('VAR_TRANSACTION_ID', str(transaction_id))
        line = line.replace('VAR_UID', uid)
        line = line.replace('VAR_DestinationUID', destination_uid)
        line = line.replace('VAR_DestinationType', destination_type)
        line = line.replace('VAR_TransactionID', str(transaction_id))
        line = line.replace('VAR_TransactionType', transaction_type)
        line = line.replace('VAR_TransactionAmount', str(transaction_amount))
        line = line.replace('VAR_TransactionDateTime', transaction_date_time)
        fout.write(line)

    fin.close()
    fout.close()
    subprocess.run ( [ "sh", filename_insert] )


    fin = open("VerifyQuery.sh", "rt")
    fout = open(filename_verify, "w+")
    for line in fin:
        line = line.replace('VAR_TRANSACTION_ID', str(transaction_id))
        fout.write(line)

    fin.close()
    fout.close()
    time.sleep(1)
    out = check_output([ "sh", filename_verify])
    out_str = str(out).split('txID')
    out_txid = out_str[1].split('\\')[4].replace('"', '')
    cursor.execute(update_query, (out_txid, transaction_id))
    
def PaymentCBDC(uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time):
    try:
        cursor.execute(
            insert_query,
            (uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
        )
        transaction_id = cursor.fetchone()[0]

        blockchainStore(uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)
        print("DEBUG: PaymentCBDC", uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)

        conn.commit()
        print("Data has been inserted successfully")
    except Exception as e:
        print(f"Error: Unable to insert data: {e}")
        conn.rollback()
    
    query = f"SELECT * FROM transaction.logs WHERE transaction_type = 'balance' AND uid = '{uid}' order by id desc LIMIT 1"
    cursor.execute(query)
    rows = cursor.fetchall()
    balance_init = False

    if rows:
        balance_user = rows[0][4]
    else:
        balance_user = 0
        balance_init = True

    print("balance_user", balance_user)
    print("balance_user", transaction_amount)
    if balance_init == False and (int(balance_user) < int(transaction_amount)):
        actionIssue(uid, destination_uid, transaction_amount, "reject-payment")
    else:
        actionIssue(uid, destination_uid, transaction_amount, "approve-payment")        

def convertCBDC(uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time):
    try:
        cursor.execute(
            insert_query,
            (uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
        )
        transaction_id = cursor.fetchone()[0]

        blockchainStore(uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)
        print("DEBUG: convertCBDC", uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)

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

    uid = uid
    destination_uid = destination_uid
    destination_type = "central"
    transaction_type = "approve-convert"
    transaction_amount = transaction_amount
    transaction_date_time = datetime.now()

    try:
        cursor.execute(
            insert_query,
            (uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
        )
        transaction_id = cursor.fetchone()[0]

        blockchainStore(uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)
        print("DEBUG: convertCBDCApprove", uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)

        conn.commit()
        print("Data has been inserted successfully")
    except Exception as e:
        print(f"Error: Unable to insert data: {e}")
        conn.rollback()

    uid = bankBalance
    destination_uid = bankBalance
    destination_type = "system"
    transaction_type = "balance"
    transaction_amount = balance_bank
    transaction_date_time = datetime.now()

    try:
        cursor.execute(
            insert_query,
            (uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
        )
        transaction_id = cursor.fetchone()[0]
        
        blockchainStore(uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)
        print("DEBUG: convertCBDCApprove", uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)

        conn.commit()
        print("Data has been inserted successfully")
    except Exception as e:
        print(f"Error: Unable to insert data: {e}")
        conn.rollback()

    uid = cbdcID
    destination_uid = cbdcID
    destination_type = "system"
    transaction_type = "balance"
    transaction_amount = balance_cbdc
    transaction_date_time = datetime.now()

    try:
        cursor.execute(
            insert_query,
            (uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
        )
        transaction_id = cursor.fetchone()[0]

        blockchainStore(uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)
        print("DEBUG: convertCBDCApprove", uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)

        conn.commit()
        print("Data has been inserted successfully")
    except Exception as e:
        print(f"Error: Unable to insert data: {e}")
        conn.rollback()

def actionIssue(uid, destination_uid, transaction_amount, state):
    query = f"SELECT * FROM transaction.logs WHERE transaction_type = 'balance' AND uid = '{cbdcID}' order by id desc LIMIT 1"
    cursor.execute(query)
    rows = cursor.fetchall()
    if rows:
        balance_cbdc = rows[0][4]
    else:
        balance_cbdc = 0
    
    
    query = f"SELECT * FROM transaction.logs WHERE transaction_type = 'balance' AND uid = '{destination_uid}' order by id desc LIMIT 1"
    # print("debug", query)
    cursor.execute(query)
    rows = cursor.fetchall()
    if rows:
        balance_user = rows[0][4]
    else:
        balance_user = 0

    if state == "approve":
        balance_cbdc = int(balance_cbdc) - int(transaction_amount)
        balance_user = int(balance_user) + int(transaction_amount)
    elif state == "approve-payment":
        balance_cbdc = int(balance_cbdc)
        balance_user = int(balance_user) + int(transaction_amount)

    uid = uid
    destination_uid = destination_uid
    destination_type = "central"
    transaction_type = state
    transaction_amount = transaction_amount
    transaction_date_time = datetime.now()

    try:
        cursor.execute(
            insert_query,
            (uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
        )
        transaction_id = cursor.fetchone()[0]

        blockchainStore(uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)
        print("DEBUG: actionIssue", uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)

        conn.commit()
        print("Data has been inserted successfully")
    except Exception as e:
        print(f"Error: Unable to insert data: {e}")
        conn.rollback()

    if state == "reject-payment":
        query = f"SELECT * FROM transaction.logs WHERE transaction_type = 'balance' AND uid = '{uid}' order by id desc LIMIT 1"
        # print("debug", query)
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            balance_user_rejected = rows[0][4]
        else:
            balance_user_rejected = 0

        uid = uid
        destination_uid = uid
        destination_type = "system"
        transaction_type = "balance"
        transaction_amount = balance_user_rejected
        transaction_date_time = datetime.now()

        try:
            cursor.execute(
                insert_query,
                (uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
            )
            transaction_id = cursor.fetchone()[0]

            blockchainStore(uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)
            print("DEBUG: actionIssue", uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)

            conn.commit()
            print("Data has been inserted successfully")
        except Exception as e:
            print(f"Error: Unable to insert data: {e}")
            conn.rollback()

    if state == "approve-payment":
        query = f"SELECT * FROM transaction.logs WHERE transaction_type = 'balance' AND uid = '{uid}' order by id desc LIMIT 1"
        # print("debug", query)
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            balance_user_payee = rows[0][4]
        else:
            balance_user_payee = 0

        print("balance_user_payee", balance_user_payee)
        balance_payee = int(balance_user_payee) - int(transaction_amount)
        print("balance_payee", balance_payee)
        print("transaction_amount", transaction_amount)

        uid = uid
        destination_uid = uid
        destination_type = "system"
        transaction_type = "balance"
        transaction_amount = balance_payee
        transaction_date_time = datetime.now()

        try:
            cursor.execute(
                insert_query,
                (uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
            )
            transaction_id = cursor.fetchone()[0]

            blockchainStore(uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)
            print("DEBUG: actionIssue", uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)

            conn.commit()
            print("Data has been inserted successfully")
        except Exception as e:
            print(f"Error: Unable to insert data: {e}")
            conn.rollback()

    uid = destination_uid
    destination_uid = destination_uid
    destination_type = "system"
    transaction_type = "balance"
    transaction_amount = balance_user
    transaction_date_time = datetime.now()

    try:
        cursor.execute(
            insert_query,
            (uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
        )
        transaction_id = cursor.fetchone()[0]

        blockchainStore(uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)
        print("DEBUG: actionIssue", uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)

        conn.commit()
        print("Data has been inserted successfully")
    except Exception as e:
        print(f"Error: Unable to insert data: {e}")
        conn.rollback()

    uid = cbdcID
    destination_uid = cbdcID
    destination_type = "system"
    transaction_type = "balance"
    transaction_amount = balance_cbdc
    transaction_date_time = datetime.now()

    try:
        cursor.execute(
            insert_query,
            (uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
        )
        transaction_id = cursor.fetchone()[0]

        blockchainStore(uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)
        print("DEBUG: actionIssue", uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)

        conn.commit()
        print("Data has been inserted successfully")
    except Exception as e:
        print(f"Error: Unable to insert data: {e}")
        conn.rollback()

def TrxCBDC(uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time):
    try:
        cursor.execute(
            insert_query,
            (uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
        )
        transaction_id = cursor.fetchone()[0]
        
        blockchainStore(uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)
        print("DEBUG: actionIssue", uid, destination_uid, destination_type, transaction_id, transaction_type, transaction_amount, transaction_date_time)

        conn.commit()
        print("Data has been inserted successfully")
    except Exception as e:
        print(f"Error: Unable to insert data: {e}")
        conn.rollback()
    
    query = f"SELECT * FROM transaction.logs WHERE transaction_type = 'balance' AND uid = '{destination_uid}' order by id desc LIMIT 1"
    # print("debug", query)
    cursor.execute(query)
    rows = cursor.fetchall()
    balance_init = False

    if rows:
        balance_user = rows[0][4]
    else:
        balance_user = 0
        balance_init = True

    if balance_init == False and (int(balance_user) < int(transaction_amount)):
        actionIssue(uid, destination_uid, transaction_amount, "reject")


@app.route('/')
def home():
    return 'block-chain apis'

@app.route('/transaction', methods = ['POST'])
def transaction():
    token = request.args.get('token')
    if(token != token_security):
        return jsonify(status=0, message="invalid token")
        
    uid = request.args.get('uid')
    type = request.args.get('type')

    if type == "all":
        query = f"SELECT destination_type, destination_uid, id, transaction_amount, transaction_date_time, transaction_type, uid FROM transaction.logs WHERE uid = '{uid}' order by id desc"
    elif type == "issue":
        query = f"SELECT destination_type, destination_uid, id, transaction_amount, transaction_date_time, transaction_type, uid FROM transaction.logs WHERE transaction_type = 'issue' AND uid = '{uid}' order by id desc"
    else:
        query = f"SELECT destination_type, destination_uid, id, transaction_amount, transaction_date_time, transaction_type, uid FROM transaction.logs WHERE transaction_type = 'balance' AND uid = '{uid}' order by id desc"

    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    real_dict = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return jsonify(status=1, data=real_dict)

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
        actionIssue(uid, destination_uid, transaction_amount, 'approve')
    elif transaction_type == "approve-convert":
        convertCBDCApprove(uid, destination_uid, transaction_amount)
    elif transaction_type == "convert":
        convertCBDC(uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
    elif transaction_type == "payment":
        PaymentCBDC(uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
    else:
        TrxCBDC(uid, destination_uid, destination_type, transaction_type, transaction_amount, transaction_date_time)
    
    return jsonify(status=1, message="successfully")

if __name__ == '__main__':
    app.run(host="0.0.0.0",  port=8000, debug=True)
