import os


stream = os.popen("./cmd1.sh")
output = stream.read()
output

