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
    data = request.args.get('data')
    print(data)
    fin = open("cmd1.sh", "rt")
    fout = open("cmd1_out.sh", "w+")
    for line in fin:
        JsonDump = json.dumps('{"Args":["Store", "1234", "{asdad:1234}"]}')
        # JsonDump = json.dumps('{"Args":["Query", "default-asset"]}')
        line = line.replace('PARAMETER', JsonDump)
        line = line.replace('"{','{')
        line = line.replace('}"','}')
        print(line)
        fout.write(line)
    fin.close()
    fout.close()
    subprocess.run ( [ "sh", "cmd1_out.sh"] )
    return data

if __name__ == '__main__':
    app.run(host="0.0.0.0",  port=8000, debug=True)
