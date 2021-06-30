import requests
import os
from os.path import expanduser
import logging
import time

os.chdir('E:')
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
		
		# List of templates. [Lip Print Template]
		self.template_id_list = ["a2faf77a-5734-4089-97a2-aae584f2ac91"]

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

		os.chdir('E:')
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
		beforeJob = time.time()
		# Check to see if job is already downloaded
		if not os.path.exists(os.path.join(self.photo_dest, jobObject["lookupId"])):
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
		afterJob = time.time()
		logging.info(jobObject["lookupId"] + " - Already Downloaded")

	def get_all_document_ids(self, jobData, jobLookupId):
		"""
		Get all document IDs inside of this job

		Parameters:
			jobLookupId (string): Look up ID of the specific job. I.e. Job-xxxxx
			jobData (Object): Job data object that includes all collected data from job.

		Returns:
			Document List: A list of tuples that contain (jobLookupId, documentId, fieldId)
		"""

		#List of Tuples that contain (jobLookupId, documentId, fieldId)
		document_list = []

		# GRAB ALL IMAGE IDs IN JOB
		# Loop through all templates in the job
		for template in jobData["snippets"]:
			# Make sure it is a regular step
			# TODO: Add else if statements if needd for StepGroup
			if "stepExecData" in template:
				# Loop through all regular steps in the template, excluding 
				for step in template["stepExecData"]["fieldExecutionData"]:
					# CHECK to see if it is an image input
					if "documents" in step:
						# Grab the first image ID in the image list
						imageId = step["documents"][0]["id"]
						# Tuple that contains (jobLookupId, documentId, fieldId)
						documentTuple = (jobLookupId, imageId, step["fieldId"])
						# Append document Tuple to the document list
						document_list.append(documentTuple)
						# Download Image
						# Call can be moved outside of this function. Only here to speed things up.
						self.download_document(documentTuple)
					# CHECK to see if it is an signature input
					elif "document" in step:
						# Grab Signature ID
						signatureId = step["document"]["id"]
						# Tuple that contains (jobLookupId, documentId, fieldId)
						documentTuple = (jobLookupId, signatureId, step["fieldId"])
						# Append document Tuple to the document list
						document_list.append(documentTuple)
						# Download Signature
						# Call can be moved outside of this function. Only here to speed things up.
						self.download_document(documentTuple)
					else:
						logging.info("Not an image.")
		return document_list

	def download_document(self, documentInfo):
		"""
		Download document based on the ID.

		Parameters:
			documentInfo (Tuple): Tuple that contains (jobLookupId, documentId, fieldId).
		"""
		# If folder doen't exist create it then download image else download image to existng folder
		if not os.path.exists(os.path.join(self.photo_dest, documentInfo[0])):
			# Create folder to hold all images related to this job
			os.mkdir(os.path.join(self.photo_dest, documentInfo[0]))

		# Image request URL
		documentUrl = self.baseURL + "documents/" + documentInfo[1]

		# GET image from request
		document_response = requests.request('GET', url=documentUrl, data=None, json=None, headers=self.headers)

		# Save image from json response
		# Download image from requests
		if document_response.status_code == 200:
			# Save image with name: JobID_FieldID.jpeg in JobID folder
			destinationName = self.photo_dest + documentInfo[0] + "/" + documentInfo[0] + "_" + documentInfo[2] + ".jpeg"
			
			# w - write and b - binary (images)
			with open(destinationName, "wb") as x:
				x.write(document_response.content)
		else:
			logging.error(response.status_code + " - Image GET Request Unsuccessful!")

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
			# Get a list of all document IDs in job
			document_id_list = parsable.get_all_document_ids(job_data, job["lookupId"])
	else:
		logging.info("Empty Job List")

	after_download = time.time()
	logging.info("Download Finished: " + str(after_download - before_download) + " seconds")
except Exception as e:
	logging.exception("Exception occurred")
