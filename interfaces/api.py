import subprocess
import json
from flask import request
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
    return 'block-chain apis'

@app.route('/insert')
def insert():
    username = request.args.get('username')
    print(username)
    fin = open("cmd1.sh", "rt")
    fout = open("cmd1_out.sh", "w+")
    for line in fin:
        line = line.replace('VAR_NIK','1234')
        print(line)
        fout.write(line)
    fin.close()
    fout.close()
    subprocess.run ( [ "sh", "cmd1_out.sh"] )
    return username

if __name__ == '__main__':
    app.run(host="0.0.0.0",  port=8000, debug=True)
