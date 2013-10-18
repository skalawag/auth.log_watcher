#! /usr/bin/python

""" auth.log_watcher.py:  Watch for logins and report by email.
"""

import re, os, time

# FIXME: the year is hard-coded!
def get_time_stamp(string):
    return time.mktime(time.strptime(string[:15] + " 2013", '%b %d %H:%M:%S %Y'))

# modify as needed
match_1 = re.compile(r"sshd.*Accepted")
match_2 = re.compile(r"su\[.*\]: pam_unix\(su:session\)")

# target to write to.
auth_path = "/tmp/journ_out"

# command
COMMAND = 'journalctl > %s' % auth_path

# your email address
email = "YOUREMAIL@WHATEVER.COM"

# you must create this file:
os.system('touch /tmp/auth.date')
last_date = "/tmp/auth.date"
last_time = time.time() - 6000

if __name__ == '__main__':
    # get going....
    while True:
        try:
            os.system(COMMAND)
            f = open(auth_path)

            g = open(last_date, 'r')
            last_time = float(g.readline())
            g.close()
            mail = ""
            stamp = ""
            for line in f.readlines()[-100:]:
                if get_time_stamp(line) > last_time:
                    if match_1.search(line) or match_2.search(line):
                        mail += line + "\n"
                        stamp = str(get_time_stamp(line))
            if mail:
                mail = "From: " + email + "\n" + "Subject: Auth Log Update\n\n" + mail
                m = open('/tmp/mail', 'w')
                m.write(mail); m.flush(); m.close()
                os.system("cat /tmp/mail | msmtp -a default %s" % email)
            g = open(last_date, 'w')
            if stamp:
                g.write(stamp)
            else:
                g.write(str(time.time()))
            g.flush(); g.close()
            f.flush(); f.close()
            try:
                os.system('rm /tmp/journ_out')
                os.system('rm /tmp/mail')
            except: pass
            time.sleep(20)
        except:
            mail = "From: " + email + "\n" + "Subject: ERROR: Auth Log Update\n\n We have a problem, NASA..."
            try:
                m = open('/tmp/mail', 'w')
                m.writeline(mail)
                m.close()
                os.system("cat /tmp/mail | msmtp -a default %s" % email)
                os.system('rm /tmp/mail')
                break
            except:
                print "I'm broken."
                break
