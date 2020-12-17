import requests


team_id = 'XX_Team_ID_XX' 
authToken = 'Token XX_Token_XX'

# parse input data:
job_uuid = 'XX_JOB_UUID_XX'
job_base_step_id = 'XX_JOB_BASE_STEP_ID_XX'
field_title = "XX_Input_Field_XX"

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

# Build the first API call which gets the job based on the Job-ID value.
url = baseURL + "jobs"
payload = {
    "method": "fetch",
    "arguments": {
        "selectOpts": {
            "includeSteps": True,
            "includeTeam": True  # server always return team anyway
        },
        "jobIds": 'XX_Job_UUID_XX'
    }
}

response = requests.request('POST', url=url, data=None, json=payload, headers=headers)

fetchResult = response.json()['result']['success']
job = fetchResult[job_uuid]['job']


# search for the triggering step, return that step
def find_step(step_group, job_step_id):
    if step_group['jobBaseStepId'] == job_step_id:
        return step_group
    for sub_step in step_group['children']:
        step = find_step(sub_step, job_step_id)
        if step is not None:
            return step
    return None


def find_field(step, field_title):
    step_impl = step.get('impl')
    if step_impl is None:
        return None
    for field in step_impl.get('step').get('stepFields'):
        if field['key'] == field_title:
            return field
    return None


field_id = ""
step_id = ""

# Make sure job is Active & correct Team ID
if job['completedAt'] == 0 and team_id == job['team']['id']:
    # each 'stepGroup' is a template:
    for stepGroup in job['stepGroup']['children']:
        step = find_step(stepGroup, job_base_step_id)
        if step is None:
            continue
        field = find_field(step, field_title)
        if field is None:
            continue
        step_id = step['id']
        field_id = field['id']
else:
    print("Job is Completed and/or Team ID mismatched!! ")

print(input_data)

#send specified data to the input field
if field_id != "":
    payload = {
        "method": "sendExecDataWithResult",
        "arguments": {
            "jobId": job_uuid,
            "execSnippets": [
                {
                    "stepExecData": {
                        "stepId": step_id,
                        "jobBaseStepId": job_base_step_id,
                        "seqId": 0,
                        "fieldExecutionData": [
                            {
                                "fieldId": field_id,
                                "seqId": 0,
                                "execData": {
                                    "text": input_data['results']
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }
    print(payload)
    response = requests.request('POST', url=url, data=None, json=payload, headers=headers)
else:
    print("will not POST API, field_id not found")