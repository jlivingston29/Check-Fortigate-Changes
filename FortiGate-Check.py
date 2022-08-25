import requests
import os
import datetime
import smtplib
from email.message import EmailMessage
#Ignore selfsigned Cert
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


#API section. Grabbing the running config and saving to a file.
url = "https:/<IP HERE>/api/v2/monitor/system/config/backup"

payload={}
headers = {
  'Accept': 'application/json',
  'Authorization': 'KEY HERE'
}
params = { 'scope' : 'global' }

response = requests.request("GET", url, headers=headers, params=params, data=payload, verify=False)

Tempfile = open('/home/user/Firewall/latest-config.conf', 'w+')
Tempfile.write(response.text)
Tempfile.close()

#Compare section. Comparing running config to an approved config
temp_output = os.popen("diff -I 'set password ENC' -I '#conf_file_ver' /home/user/Firewall/backup.conf /home/user/Firewall/latest-config.conf")
output = temp_output.read()
#checking if output is empty and logging to file
today = datetime.datetime.now()
if not output:
  logfile = open("/home/user/Firewall/changes.log", "a")
  logfile.write(f"No changes on {today}\n")
  logfile.close()
else:
  logfile = open("/home/user/Firewall/changes.log", "a")
  logfile.write(f"Changes noticed on {today}\n\n")
  #logfile.write("==================\n")
  logfile.write(output)
  logfile.write("\n")
  logfile.write("==================\n")
  body = "A change has occurred on the primary firewall. Please verify if changes are autheroized. \n \n %s"%output
  msg = EmailMessage()
  msg['Subject'] = 'Fortigate Changes'
  msg['From'] = "<Email here>"
  msg['To'] = "<Email here>"
  msg.set_content(body)
  server = smtplib.SMTP('<IP HERE>')
  server.send_message(msg)
  server.quit()
  logfile.close()
