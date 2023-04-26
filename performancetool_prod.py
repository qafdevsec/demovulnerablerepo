import json
import requests
import yaml
from collections import OrderedDict
import docker
import os
import time
import csv
import sys
import time

create_apps=90
fdevsec_dashboard_ip='10.34.160.80'
file_name = 'fdevsec.yaml'
perf_list = [];
fields = ['AP Count', 'Response Time (secs)']
filename="fdevsec_perf_report.csv"
r4=None
headers_details=None
org_id=None
org_api_id=None

payload = {'username':'fortidevsecqa0007@qatest.com','password':'Fortinet01!'}
r4 = requests.post('https://fortidevsec.forticloud.com/api/v1/login/access-token', verify=False,data=payload)
#print (r4.json())
#print("status_code-",r4.status_code)

if(r4.status_code == requests.codes.ok):
    print("status code True, for API call /api/v1/login/access-token\n")
else:
    print("status code is False, for API call /api/v1/login/access-token\n")

print("Headers-",r4.headers)

r4_data = json.loads(r4.text)
print("r4_data --> ",r4_data)
print("json_data-",r4_data['access_token']);

headers_details={'Authorization': r4_data['token_type'] + ' ' + r4_data['access_token'],'accept':r4.headers['Content-Type']}
print("headers_details",headers_details)
r5 = requests.get('https://fortidevsec.forticloud.com/api/v1/dashboard/get_orgs',headers=headers_details,verify=False)
#print (r5.json())
r5_data = json.loads(r5.text)
print("r5_data --> ",r5_data)

params_data  = {'org_id': r5_data[0]['id']}
print("payload-->",payload)
org_id=r5_data[0]['id'];
org_api_id=r5_data[0]['api_id'];
print(org_id)
print(org_api_id)

headers_details={'Authorization': r4_data['token_type'] + ' ' + r4_data['access_token'],'accept':r4.headers['Content-Type']}

for x in range(create_apps):
    try:
        print("Creating the Application:","apptest"+str(x))
        params_data  = {'app_name':"app_test"+str(x),'org_id': org_id}
        r7 = requests.post('https://fortidevsec.forticloud.com/api/v1/dashboard/create_app', headers=headers_details, params = params_data, verify=False)
        print (r7.json())
        r7_data = json.loads(r7.text)
        print("r7_data --> ",r7_data)
        print ("app_uuid:", r7_data['app_uuid'])
    
        appid=r7_data['app_uuid']

        with open(file_name, "r") as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
            print(type(data))
            data['id']['org']=org_api_id
            data['id']['app']=appid
            print("Read successful")
            print(data)
            yamlfile.close()

        with open(file_name, 'w') as yamlfile:
            data1 = yaml.dump(data, yamlfile,sort_keys=False)
            print(data)
            print("Write successful")
            yamlfile.close()

        pwd = os.getcwd()
        client = docker.from_env()
        client.images.pull('registry.fortidevsec.forticloud.com/fdevsec_sast:latest')
        for x in range(9):
            container=client.containers.run('registry.fortidevsec.forticloud.com/fdevsec_sast:latest',remove=True,extra_hosts={'fortidevsec.forticloud.com':fdevsec_dashboard_ip},volumes={pwd : {'bind': '/scan', 'mode': 'rw'}},detach=True)
            time.sleep(90)
        #str1=container.logs();
        #print(str1)
        for line in container.logs(stdout=True,stderr=True,follow=True,stream=True):
             line=line.decode("utf-8")
             print(line.strip())
         #print(container.attrs)

        container.stop()
        container.remove(force=True)

        headers_details={'Authorization': r4_data['token_type'] + ' ' + r4_data['access_token'],'accept':r4.headers['Content-Type']}
        r6 = requests.get('https://fortidevsec.forticloud.com/api/v1/dashboard/get_apps', headers=headers_details, params = {'org_id': org_id}, verify=False)
        #print (r6.json())
        item_dict = json.loads(r6.text)
        appCount=len(item_dict['apps'])
        elapsedTime=r6.elapsed.total_seconds()

        print("No.of Apps",appCount)
        print("Elapsed Time:",elapsedTime)

        perf_list.append([appCount,elapsedTime])
    except:
        time.sleep(5)
        print("Some Exeception..Reconnect/ReAuth.")  
        payload = {'username':'fortidevsecqa0007@qatest.com','password':'Fortinet01!'}
        r4 = requests.post('https://fortidevsec.forticloud.com/api/v1/login/access-token', verify=False,data=payload)
        headers_details={'Authorization': r4_data['token_type'] + ' ' + r4_data['access_token'],'accept':r4.headers['Content-Type']}
        continue
    else:
        continue
    finally:
        pass

with open(filename, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    csvwriter.writerows(perf_list)

