import os
import smtplib
import requests
import json
import urllib
import logger
import sys
import re
from time import sleep

class CloudFlare(object):
	"""docstring for CloudFlare"""
	def __init__(self, email, global_key):
		super(CloudFlare, self).__init__()
		self.email = email
		self.global_key = global_key
		
	def getHeader(self):
		return {
			"X-Auth-Email": self.email,
			"X-Auth-Key": self.global_key,
			"Content-Type": "application/json"
		}

	def apiCall(self, method, type = "GET", data = None):
		apiUrl = "https://api.cloudflare.com/client/v4"
		if type == "POST":
			r = requests.post(apiUrl + method, headers = self.getHeader(), data = json.dumps(data))
		elif type == "PUT":
			r = requests.put(apiUrl + method, headers = self.getHeader(), data = json.dumps(data))
		else:
			if data == None:
				r = requests.get(apiUrl + method, headers = self.getHeader())
			else: 
				r = requests.get(apiUrl + method + '?' + urllib.urlencode(data), headers = self.getHeader())

		return json.loads(r.text)

def readProxies(filename):
	proxies = ["255.255.255.255"]
	f = open(filename)
	for px in f.readlines():
		px = px.strip()
		proxies.append(px)
	logger.info("Proxy count: " + str(len(proxies)))
	return proxies

def cFlare(hostname):
	# Initialize
	email = "r3nato@tuta.io"
	key = "109da6ce9eb354c49fff3b55ab6f152721e5a"
	ip = hostname

	cf = CloudFlare(email,key)
	pages = cf.apiCall('/zones')['result_info']['total_pages']

	for page in xrange(0,pages + 1):
		zones = cf.apiCall('/zones','GET', {'page': page})['result']
		
		for zone in zones:
			zone_id = zone['id']

			records = cf.apiCall("/zones/"+zone_id+"/dns_records","GET")['result']

			for record in records:
				if record['type'] == 'A':
					identifier = record['id']

					data = {
						'type': 'A',
						'name': record['name'],
						'content': ip,
						'proxied': record['proxied'],
						'ttl': record['ttl']
					}

					res = cf.apiCall("/zones/"+zone_id+"/dns_records/"+identifier,"PUT",data)['result']

					if res != None:
						logger.success(res['name'])
					else:
						logger.fail(record['name'])

def conspirology(subject = "Hey there!", message = "Something just happenned"):
	sender = 'johnlehah@gmx.com'
	receivers = ['lrptraffic@gmail.com']


	message = ("""From: John <johnlehah@gmx.com>\r\nTo: LrpTraffic <lrptraffic@gmail.com>\r\nSubject: %s\r\n

	%s
	""" % (subject, message)) 

	try:
	   smtpObj = smtplib.SMTP('mail.gmx.com', 587)
	   smtpObj.starttls()
	   smtpObj.login("johnlehah@gmx.com", "astadaparola1")
	   smtpObj.sendmail(sender, receivers, message)         
	   #print "Successfully sent email"
	   smtpObj.quit()
	except Exception, e:
	   logger.fail("Error: unable to send email: " + str(e))

def routine(subject = "Heartbeat", message = "Null"):
	sender = 'johnlehah@gmx.com'
	receivers = ['johnlehah@gmx.com']


	message = ("""From: Heartbeat <johnlehah@gmx.com>\r\nTo: Me <johnlehah@gmx.com>\r\nSubject: %s\r\n

	%s
	""" % (subject, message)) 

	try:
	   smtpObj = smtplib.SMTP('mail.gmx.com', 587)
	   smtpObj.starttls()
	   smtpObj.login("johnlehah@gmx.com", "astadaparola1")
	   smtpObj.sendmail(sender, receivers, message)         
	   logger.info("Successfully sent email")
	   smtpObj.quit()
	except Exception:
	   logger.fail("Error: unable to send email")

def main():
	proxies = readProxies("proxies.txt")
	currentProxy = proxies[0]
	while True:
		hostname = proxies[0]
		response = os.system("ping -c 1 -w2 " + hostname + " > /dev/null 2>&1")

		#and then check the response...
		if response == 0:
		  erMsg = hostname + ' is up!'
		  #logger.success(erMsg)
		else:
		  erMsg = hostname + ' is down! wait for 30 seconds'
		  logger.warning(erMsg)
		  #routine(hostname + " is down! wait for 30 seconds") ## Too many emails
		  sleep(30)
		  response = os.system("ping -c 1 -w2 " + hostname + " > /dev/null 2>&1")
		  if response == 0:
		  	erMsg = hostname + ' is up!'
		  	logger.success(erMsg)
		  else:
		  	#print hostname, "is down x2! checking it again"
		  	erMsg = hostname + ' is down x2! checking it again'
		  	logger.fail(erMsg)
		  	routine("WARN: " + hostname + " is down", hostname + " is down x2! checking it again") ## Something really happened
		  	conspirology("Something really happened") ## Something really happened
		  	sleep(30)
		  	response = os.system("ping -c 1 -w2 " + hostname + " > /dev/null 2>&1")
		  	if response == 0:
		  		erMsg = hostname + ' is up!'
		  		logger.success(erMsg)
		  	else:
		  		#print hostname, "is down x3! checking it again"
		  		erMsg = hostname + ' is down x3! checking it again'
		  		logger.fail(erMsg)
		  		routine("CRIT: " + hostname + " is down", hostname + " is down x3! checking it again") ## WTF??!
		  		conspirology("WTF??!")
		  		sleep(30)
		  		response = os.system("ping -c 1 -w2 " + hostname + " > /dev/null 2>&1")
		  		if response == 0:
					erMsg = hostname + ' is up!'
		  			logger.success(erMsg)
				else:
					#print hostname, "is down x4! starting cloudflare routine"
					erMsg = hostname + ' is down x4! starting cloudflare routine'
		  			logger.fail(erMsg)
					routine("PANIC: " + hostname + " is down", hostname + " is down x4! starting cf routine") ## PANIC AT THE DISCO!
					conspirology("PANIC AT THE DISCO!")
					proxies.pop(0)
					if len(proxies) == 0:
						proxies = readProxies("proxies.txt")
					cFlare(proxies[0])
		sleep(5)

logger.info("Initialized")
main()

