import time
import json
import requests

VERSION = '0.1.0'
api_url = "http://api.metzoo.com"

def API(url):
  global api_url
  api_url= url

def api_call(url, body, headers = {}, debug = False):
  headers.update({"Content-Type": "application/json", "User-Agent": "Metzoo-Python-Client/"+VERSION})
  if debug:
    print "Request:"
    print "   URL    :", url
    print "   Headers:", headers
    print "   Body   :", body
  #
  response = requests.post(url, data=json.dumps(body), headers=headers)
  #
  if debug:
    print "Response:"
    print "   Status :", response.status_code
    print "   Body   :", response.text
  #
  return (response.status_code, response.text)

class Customer:
  def __init__(self, customer_key, debug = False):
    self.key= customer_key
    self.debug = debug
  #
  def create_agent(self, host_name):
    code, text= api_call(api_url + "/agents", body={"customer_key": self.key, "host_name": host_name}, debug=self.debug)
    #
    if code == 201:
      responseJSON = json.JSONDecoder().decode(text)
      return Agent(responseJSON["agentKey"], debug=self.debug)
    else:
      return False

class Agent:
  def __init__(self, agent_key, debug = False):
    self.key= agent_key
    self.debug= debug
  #
  def create_metric(self, series):
    body= []
    for serie in (series if type(series) is list else [series]):
      if type(serie) is dict:
        body.append(serie)
      else:
        name, unit= (serie+":").split(":")[0:2]
        body.append({"name": name, "unit": unit})
    #
    code, text= api_call(api_url + "/metrics", body, headers={"Agent-Key": self.key}, debug=self.debug)
    return (code == 201)
  #
  def send_data(self, data):
    body = {"t": int(time.time())}
    if type(data) is list:
      for metric in data:
        body[metric["id"]] = metric["value"]
    elif type(data) is dict:
      body.update(data)
    else:
      return False
    #
    code, text= api_call(api_url + "/metrics/data", body, headers={"Agent-Key": self.key}, debug=self.debug)
    return (code == 200)
