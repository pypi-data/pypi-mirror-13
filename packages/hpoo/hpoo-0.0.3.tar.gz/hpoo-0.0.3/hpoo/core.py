import requests
import time
import base64
import json

requests.packages.urllib3.disable_warnings()

__all__=['HPOO']

def str2base64str(string):
    return base64.b64encode(string.encode('ascii')).decode('utf-8')

class HPOO(object):
    def __init__(self, url, user, password, verify_ssl=False):
        self.verify = verify_ssl
        self.authorization = "%s:%s"%(user,password)
        self.authorization = "Basic %s"%(str2base64str(self.authorization))
        self.headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': self.authorization
        }
        self.url=url
        
    def start_flow(self, uuid, run_name, inputs={}):
        data = {
            "uuid": uuid,
            "runName": run_name,
            "logLevel": "DEBUG",
            "inputs": inputs
        }
        
        r = requests.post(url="%s/oo/rest/executions"%(self.url),
                          headers=self.headers,
                          data=json.dumps(data),
                          verify=self.verify) 
        
        if r.status_code == 201:
            return json.loads(r.text)
        
        if r.status_code == 400:
            raise Exception("ERROR %d : Missing parameters or "
                            "invalid parameters for the flow"%(r.status_code))
        
        raise Exception("ERROR %d : %s"%(r.status_code,r.text))
       
    def flow_status(self, runid):
        r = requests.get(url="%s/oo/rest/executions/%s/summary"%(self.url,runid),
                         headers=self.headers, verify=self.verify)
        
        if r.status_code != 200:
            raise Exception("Error %d : %s"%(r.status_code,r.text))
        
        return json.loads(r.text)[0].get('status')
       
    def wait_for_flow_to_finish(self, runid, poll_interval=5):
        status='RUNNING'
        while True:
            status = self.flow_status(runid=runid)
            if status in ('COMPLETED', 'SYSTEM_FAILURE', 'CANCELLED'):
                return status
            else:
                time.sleep(poll_interval)

    def get_flow_executionlog(self, runid):
        r = requests.get(url="%s/oo/rest/executions/%s/execution-log"%(self.url,runid),
                         headers=self.headers,
                         verify=self.verify)
        if r.status_code != 200:
            raise Exception("ERROR %d : %s"%(r.status_code, r.text))
        return json.loads(r.text)