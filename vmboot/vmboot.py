import __future__
import os
import sys
import requests
import shutil
import subprocess
import json
import pprint
import urllib3
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

zsbuname = raw_input("Please enter a Business Unit name: ")
username = raw_input("Please enter a Business Unit Admin name: ")
password = raw_input("Please enter the admin password, CAUTION: This is in plain text: ")
email = raw_input("Please enter the BU admin email: ")
#imagename = raw_input("Please enter a valid OS image name from your image library: ")

auth_username = os.getenv('OS_USERNAME',None)
auth_password = os.getenv('OS_PASSWORD',None)
auth_url = os.getenv('OS_AUTH_URL',None)
project_name = os.getenv('OS_PROJECT_NAME',None)
user_domain_name = os.getenv('OS_USER_DOMAIN_NAME',None)
project_domain_name = os.getenv('OS_PROJECT_DOMAIN_NAME',None)
cacert = os.getenv('OS_CACERT',None)
user_region = os.getenv('OS_REGION',None)

if(auth_username == None or auth_password == None or auth_url == None or \
   project_name == None or user_region == None or user_domain_name == None or \
   project_domain_name == None or cacert == None):
    print "Export the Zerostack RC file, or explicitly define authentication environment variables."
    sys.exit(1)

if(user_region == None):
    print "Add user region variable OS_REGION to the Zerostack rc file and re-export, or export OS_REGION as an environment variable."
    sys.exit(1)

#get the region ID
regionsplit = auth_url.split('/')
region_id = regionsplit[6]

#get the base url
baseurl = auth_url[:-12]

#get the login token
try:
    body = '{"auth":{"identity":{"methods":["password"],"password":{"user":{"domain":{"name":"%s"},"name":"%s","password":"%s"}}},"scope":{"domain":{"name":"%s"}}}}' \
           %(project_domain_name,auth_username,auth_password,project_domain_name)
    #headers={"content-type":"application/json"}
    token_url = auth_url+'/auth/tokens'
    trequest = requests.post(token_url,verify = False,data = body,headers={"content-type":"application/json"})
    jtoken = json.loads(trequest.text)
    admin_user_id = jtoken['token']['user']['id']
    token = trequest.headers.get('X-Subject-Token')
except Exception as e:
    print e
    sys.exit(1)

print "Looking for the default image"
image_id = None
try:
    send_url = baseurl + '/glance/v2/images?visibility=public'
    r = requests.get(send_url,verify = False,headers={"content-type":"application/json","X-Auth-Token":token})
    images = json.loads(r.text)
    count = 0
    im = []
    for image in images['images']:
        im.append({'count':count,'imagename':image['name'],'imageid':image['id']})
        count += 1
except Exception as e:
    print e
    sys.exit(1)

for i in im:
    print "ID: %s   Name: %s"%(i['count'],i['imagename'])

try:
    imid = raw_input('Enter the ID of the image to use: ')
    for i in im:
        if(i['count'] == int(imid)):
            image_id = i['imageid']
            break
except Exception as e:
    print e
    sys.exit(1)

