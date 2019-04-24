#!/usr/bin/python

import sys
import socket

def help():
    sys.stderr.write("=== SMTP Tester ===\n")
    sys.stderr.write("Usage:\n")
    sys.stderr.write(sys.argv[0]+" [SMTP_SERVER] [FROM] [TO] [SUBJECT] [BODY]\n")
    sys.stderr.write(sys.argv[0]+" [SMTP_SERVER] [FROM] [TO] - < [DATA]\n")

def error(data):
    sys.stderr.write("Unexpected response:\n")
    sys.stderr.write(data)
    sys.stderr.write("\n")
    sys.exit(2)

def request(request, expect):
    global sock
    print ">> "+request
    sock.send(request)
    response = sock.recv(4096)
    print "<< "+response
    resp = response.split(' ')
    if resp[0] != expect:
        error(response)

if len(sys.argv) < 5 or (len(sys.argv) == 5 and sys.argv[4] != "-"):
    sys.stderr.write("Wrong number of arguments!\n\n")
    help()
    sys.exit(1)

server = (sys.argv[1], 25)
fromaddr = sys.argv[2]
toaddr = sys.argv[3]

if sys.argv[4] == "-":
    subject = ""
    body = sys.stdin.read()
else:
    subject = sys.argv[4]
    body = sys.argv[5]

# Check for lines beginning with .
lines = body.split("\n")
count = len(lines)
body = ""
for l in lines:
    count-= 1
    if count == 0:
        lineend = ""
    else:
        lineend = "\n"
    if l.startswith("."):
        body += "."+l+lineend
    else:
        body += l+lineend

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.connect(server)
except:
    sys.stderr.write("Cannot connect to SMTP server at "+server[0]+"!")
    sys.exit(1)


request("", "220")
request("HELO "+socket.gethostname()+"\r\n", "250")
request("MAIL from: "+fromaddr+"\r\n", "250")
request("RCPT to: "+toaddr+"\r\n", "250")
request("DATA\r\n", "354")
request("From: "+fromaddr+"\nTo: "+toaddr+"\nSubject: "+subject+"\n"+body+"\r\n.\r\n", "250")
request("QUIT\r\n", "221")

sock.close()
print "=== Complete ===\n"
