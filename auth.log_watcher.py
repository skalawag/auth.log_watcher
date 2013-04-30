#! /usr/bin/python

import re, os, time

def get_time_stamp(string):
    return time.mktime(time.strptime(string[:15] + " 2013", '%b %d %H:%M:%S %Y'))


match_1 = re.compile(r"sshd.*Accepted")
match_2 = re.compile(r"/dev/hvc0")

# modify this as needed:
auth_path = "/var/log/auth.log"

# you must create this file:
last_date = "/tmp/auth.date"

# get going....
f = open(auth_path)
g = open(last_date, 'r')

try:
    last_time = float(g.readline().strip())
except:
    last_time = time.time() - 6000
g.close()

mail = ""
stamp = ""
for line in f.readlines()[-40:]: # captures last 20 lines
    if get_time_stamp(line) > last_time:
        if match_1.search(line) or match_2.search(line):
            mail += line + "\n"
            stamp = str(get_time_stamp(line))
print mail
# uncomment this and delete the previous line to send the result as a message

if len(mail) > 1:
    os.system('echo "%s" | mailx -s auth.log markscala@gmail.com' % mail)

g = open(last_date, 'w')
g.write(stamp)
g.flush(); g.close()
f.close()
