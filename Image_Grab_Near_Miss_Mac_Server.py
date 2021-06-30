import requests
import os
from os.path import expanduser
import logging
import time

os.chdir('/Users/ansonlin/Desktop')
logFile = os.getcwd() + "/Near_Miss_Photos/" + "LogFile.log"

# If Python Images Folder doesn't exist create it
if not os.path.isdir(os.path.join(os.getcwd(), "Near_Miss_Photos")):
	os.mkdir(os.path.join(os.getcwd(), "Near_Miss_Photos"))

# Create Log File
logFile = os.path.join(os.getcwd(), "Near_Miss_Photos", "LogFile.log")
logging.basicConfig(level = logging.DEBUG, filename = logFile, format='%(asctime)s - %(levelname)s - %(message)s')

class Parsable():
	def __init__(self):
		"""Initialize all useful information"""

		self.production_team_id = "f0b1ad0a-e589-413e-bf9d-3fdaf7590df8"
		# self.sandbox_team_id = "7bd5118a-9e55-44e7-992d-ba30854e31ef" 

		#TODO: MUST ADD TOKEN
		self.authToken = 
		
		# List of templates. ["NA SAF Near Miss"]
		self.template_id_list = ["731a87e6-9b87-48d2-bde3-11fbb5e0595c"]

		# API base URL
		self.baseURL = "https://api.parsable.net/api/"
		##baseURL = "http://localhost:8080/api/"

		# API Headers
		self.headers = {
		    "accept": "application/json",
		    "cache-control": "no-cache",
		    "content-type": "application/json",
		    "Authorization": self.authToken
		}

		os.chdir('/Users/ansonlin/Desktop')
		self.photo_dest = os.path.join(os.getcwd(), "Near_Miss_Photos")

	def query_jobs(self, templateIds):
		"""
		Querys a list of job objecta that contain a jobs metadata.

		Parameters:
			templateIds (list): List of template IDs.

		Returns:
			Job Object List: A list of job objects that contain a jobs metadata.
		"""

		# Build an API call which querys a list of jobs based on the template ID value.
		url = self.baseURL + "jobs#query"
		payload = {
		    "method": "query",
		    "arguments": {
		        "selectOpts": {
		            "includeTeam": False,
		            "includeTemplate": False,
		            "includeRootHeaders": False,
		            "includeSteps": False,
		            "includeDocuments": False,
		            "includeUsers": False,
		            "includeStats": False,
		            "includeActivity": False,
		            "includeTemplates": False,
		            "includeCreator": False,
		            "includeRoles": False,
		            "includePermissions": False,
		            "includeExecSnippets": False,
		            "includeMessages": False,
		            "includeIssues": False,
		            "includeDeviationCounts": False,
		            "includeDeviations": False,
		            "includeRefMap": False,
		            "includePlannedDataSheetIds": False,
		            "includeSnapshottedDataSheetValues": False,
		            "includeAttributes": False
		        },
		        "whereOpts": {
		            "teamId": self.production_team_id,
		            "isComplete": True,
		            "sourceTemplateIds": templateIds,
		            "allSourceTemplateIds": True
		        }
		    }
		}

		# Get job data Request
		job_list_response = requests.request('POST', url=url, data=None, json=payload, headers=self.headers)
		# Make sure request was successful
		if job_list_response.status_code == 200:
			# Get JSON response object
			jsonRespose = job_list_response.json()
 			# Make sure JSON object is good
			if not ("err" in jsonRespose['result']) and not ("exception" in jsonRespose):
				# Return a job list from json response
				return jsonRespose['result']['success']["jobs"]
				
			# TODO: Fix to match if statement			
			# else:
			# 	logging.error(str(jsonRespose["result"]["err"]["errorCode"]) + " - JSON Object Error!")
		else:
			logging.error(str(job_list_response.status_code) + " - GetData POST Request Unsuccessful!")

	def get_job_data(self, jobObject):
		"""
		Get the data collected from this job.

		Parameters:
			jobObject (Object): Job metadata object used to make a request to get actual job data.

		Returns:
			Job Data (Object): Job object that contains all collected data inside of job.
		"""

		logging.info(jobObject["lookupId"] + " - Started")
		# Check to see if job is already downloaded
		if os.path.exists(os.path.join(self.photo_dest, jobObject["lookupId"])):
			logging.info(jobObject["lookupId"] + " - Already Downloaded")
		else:
			# Create folder to hold all images related to this job
			os.mkdir(os.path.join(self.photo_dest, jobObject["lookupId"]))

			# Build the first API call which gets the job data based on the JobUUID value.
			url = self.baseURL + "jobs#getData"
			payload = {
			    "method": "getData",
			    "arguments": {
			        "jobId": jobObject["id"],
			        "seqId": 1,
			        "options": {
			        	"canHandlePendingDocuments": True
			        }
			    }
			}

			# Get job data Request
			job_data_response = requests.request('POST', url=url, data=None, json=payload, headers=self.headers)

			# Make sure request was successful
			if job_data_response.status_code == 200:
				# Get JSON response object
				jsonRespose = job_data_response.json()

				# Make sure JSON object is good
				if not ("err" in jsonRespose['result']) and not ("exception" in jsonRespose):

					# Return job data from json response
					return jsonRespose['result']['success']

				# TODO: Fix to match if statement
				# else:
				# 	logging.error(str(jsonRespose["result"]["err"]["errorCode"]) + " - JSON Object Error!")
			else:
				logging.error(str(job_data_response.status_code) + " - GetData POST Request Unsuccessful!")

	def get_all_document_ids(self, jobData, jobLookupId):
		"""
		Get all document IDs inside of this job

		Parameters:
			jobLookupId (string): Look up ID of the specific job. I.e. Job-xxxxx
			jobData (Object): Job data object that includes all collected data from job.
		"""

		# GRAB ALL IMAGE IDs IN JOB
		# Loop through all steps in the job
		for job_step in jobData["snippets"]:
			# Make sure it is a regular step
			# TODO: Add else if statements if need for StepGroup
			if "stepExecData" in job_step:
				# Loop through step content (input)
				for job_input in job_step["stepExecData"]["fieldExecutionData"]:
					# CHECK to see if it is an image input
					if "documents" in job_input:
						for job_image in job_input["documents"]:
							# Grab the image ID in the image list
							imageId = job_image["id"]
							# Tuple that contains (jobLookupId, documentId)
							documentTuple = (jobLookupId, imageId)
							# Download Image
							# Call can be moved outside of this function. Only here to speed things up.
							self.download_document(documentTuple)
					# CHECK to see if it is an signature input
					elif "document" in job_input:
						# Grab Signature ID
						signatureId = job_input["document"]["id"]
						# Tuple that contains (jobLookupId, documentId)
						documentTuple = (jobLookupId, signatureId)
						# Download Signature
						# Call can be moved outside of this function. Only here to speed things up.
						self.download_document(documentTuple)
					else:
						logging.info("Not an image.")

	def download_document(self, documentInfo):
		"""
		Download document based on the ID.

		Parameters:
			documentInfo (Tuple): Tuple that contains (jobLookupId, documentId).
		"""

		# Image request URL
		documentUrl = self.baseURL + "documents/" + documentInfo[1]

		# GET image from request
		document_response = requests.request('GET', url=documentUrl, data=None, json=None, headers=self.headers)

		# Save image from json response
		# Download image from requests
		if document_response.status_code == 200:
			# Save image with name: JobID_FieldID.jpeg in JobID folder
			destinationName = self.photo_dest + "/" + documentInfo[0] + "/" + documentInfo[0] + "_" + documentInfo[1] + ".jpeg"
			
			# w - write and b - binary (images)
			with open(destinationName, "wb") as x:
				x.write(document_response.content)
		else:
			logging.error(document_response.status_code + " - Image GET Request Unsuccessful!")

if __name__ == "__main__":
	try:
		before_download = time.time()

		parsable = Parsable()
		# Query a list of jobs
		jobs_list = parsable.query_jobs(parsable.template_id_list)
		# Make sure jobs_list is not NoneType (Empty)
		if jobs_list:
			# Go through job list job by job to get job data
			for job in jobs_list:
				# Get job data call
				job_data = parsable.get_job_data(job)
				# Make sure job_data is not NoneType (Empty) (Job not already downloaded) 
				if job_data:
					# Get all document IDs in job
					parsable.get_all_document_ids(job_data, job["lookupId"])
		else:
			logging.info("Empty Job List")

		after_download = time.time()
		logging.info("Download Finished: " + str(after_download - before_download) + " seconds")
	except Exception as e:
		logging.exception("Exception occurred")
