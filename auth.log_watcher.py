#! /usr/bin/python

"""You have to do some things to make this work:

1. You need to install msmtp, create a config file for the root
account, and chmod it to 600.  Here's an example:

---- Example msmtp for use with gmail -------
defaults
auth             on
tls              on
tls_trust_file   /usr/share/ca-certificates/mozilla/Thawte_Premium_Server_CA.crt

#  gmail address
account        gmail
host           smtp.gmail.com
port           587
from           YOUREMAIL@gmail.com
user           YOUREMAIL@gmail.com
password       YOUR PASSWORD
tls_trust_file /etc/ssl/certs/ca-certificates.crt

# Set a default account
account default : gmail
----- END EXAMLE --------------------------

2. You may want to modify the regexes below.

3. Since this was designed for Arch using systemd, you should modify
auth_path below to point at your auth.log, probably /var/log/auth.log

4. The main loop will sleep for 10 minutes. Change that to fit your
needs. This is not designed to run as a chron job.

5. Insert your own email address (or wherever you want the log info sent).

"""

import re, os, time

def get_time_stamp(string):
    return time.mktime(time.strptime(string[:15] + " 2013", '%b %d %H:%M:%S %Y'))

# modify as needed
match_1 = re.compile(r"sshd.*Accepted")
match_2 = re.compile(r"su\[.*\]: pam_unix\(su:session\)")

# modify this as needed (this is for Arch Linux):
auth_path = "/tmp/journ_out"

# your email address
email = "markscala@gmail.com"

# you must create this file:
os.system('touch /tmp/auth.date')
last_date = "/tmp/auth.date"
last_time = time.time() - 6000

if __name__ == '__main__':
    # get going....
    while True:
        try:
            os.system('journalctl > /tmp/journ_out')
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
                

