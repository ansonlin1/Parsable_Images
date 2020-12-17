import requests
import os
from os.path import expanduser
import logging
import time

logFile = expanduser("~") + "/Desktop/PythonImages/" + "LogFile.log"
logging.basicConfig(level = logging.DEBUG, filename = logFile, format='%(asctime)s - %(levelname)s - %(message)s')



production_team_id = "f0b1ad0a-e589-413e-bf9d-3fdaf7590df8"
sandbox_team_id = "7bd5118a-9e55-44e7-992d-ba30854e31ef" 

# Permanent Production Auth Token
# TODO: MUST FILL IN
authToken = 

# TODO: Get all jobs with a specific template
lip_print_template_id = "9babcbd6-b34f-433c-a78f-ff0f976d354c"
# Job-653962
job_uuid = "3bafd9c4-07dd-498c-a201-4393e9d5ba70"

# API base URL
baseURL = "https://api.parsable.net/api/"
##baseURL = "http://localhost:8080/api/"

# API Headers
headers = {
    "accept": "application/json",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "Authorization": authToken
}

def download_image(imageId):
	# Image request URL
	imageUrl = baseURL + "documents/" + imageId
	beforeImage = time.time()
	# GET image from request
	image_response = requests.request('GET', url=imageUrl, data=None, json=None, headers=headers)
	
	# Save image from json response
	# Download image from requests
	if image_response.status_code == 200:
		# Save image with name: JobUUID_FieldID.jpeg in JobUUID folder
		destinationName = expanduser("~") + "/Desktop/PythonImages/" + job_uuid + "/" + job_uuid + "_" + step["fieldId"] + ".jpeg"
		
		# w - write and b - binary (images)
		with open(destinationName, "wb") as x:
			x.write(image_response.content)
			afterImage = time.time()
			logging.info("Image Created: " + str(afterImage - beforeImage) + " seconds")
	else:
		logging.error(response.status_code + " - Image GET Request Unsuccessful!")

try:
	# Build the first API call which gets the job data based on the JobUUID value.
	url = baseURL + "jobs#getData"
	payload = {
	    "method": "getData",
	    "arguments": {
	        "jobId": job_uuid,
	        "seqId": 1,
	        "options": {
	        	"canHandlePendingDocuments": True
	        }
	    }
	}

	# Get job data Request
	job_data_response = requests.request('POST', url=url, data=None, json=payload, headers=headers)

	# Make sure request was successful
	if job_data_response.status_code == 200:
		# Get JSON response object
		jsonRespose = job_data_response.json()

		# Make sure JSON object is good
		if not ("err" in jsonRespose['result']) and not ("exception" in jsonRespose):
			# Create folder to hold all images related to this job
			os.mkdir(expanduser("~") + "/Desktop/PythonImages/" + job_uuid)

			# Grab job data from json response
			fetchResult = jsonRespose['result']['success']

			beforeJob = time.time()
			# GRAB ALL IMAGES IN JOB
			# Loop through all templates in the job
			for template in fetchResult["snippets"]:
				# Make sure it is a regular step
				# Add else if statements if needd for StepGroup
				if "stepExecData" in template:
					# Loop through all steps in the template
					for step in template["stepExecData"]["fieldExecutionData"]:
						# CHECK to see if it is an image input
						if "documents" in step:
							# Grab image ID
							imageId = step["documents"][0]["id"]
							#Download Image
							download_image(imageId)
						elif "document" in step:
							# Grab image ID
							imageId = step["document"]["id"]
							#Download Image
							download_image(imageId)
						else:
							logging.info("Not an image.")
				else: 
					print ("Step Group")
			afterJob = time.time()
			logging.info("Job Finished: " + str(afterJob - beforeJob) + " seconds")
		else:
			logging.error(str(jsonRespose["result"]["err"]["errorCode"]) + " - JSON Object Error!")
	else:
		logging.error(str(response.status_code) + " - GetData POST Request Unsuccessful!")
except Exception as e:
  logging.exception("Exception occurred")


# Resizing an image
# image = Image.open(r"C:\Users\jnq136\Desktop\pythonImage.jpeg")
# width, height = image.size
# newSize = (width*12, height*12)
# image = image.resize(newSize)
# image.show()