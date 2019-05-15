#© Copyright IBM Corporation [2018], [2019] [Ali Kaba]
#LICENSE: [Apache License 2.0 (Apache-2.0) http://www.apache.org/licenses/LICENSE-2.0]
import sys
import requests
import json
from cloudant.client import Cloudant
from cloudant import cloudant
from cloudant.document import Document

def main(dict):
    #required parameters - actual secrets are entered in the IBM Function action's paremeter section. DO NOT PUT SECRETS IN CODE
    h1_get_all_new_prod = dict['h1_get_all_new_prod']
    h1_get_report = dict['h1_get_report']
    h1_api_name = dict['h1_api_name']
    h1_api_key = dict['h1_api_key']
    cloudant_api_name = dict['cloudant_api_name']
    cloudant_api_key = dict['cloudant_api_key']
    person_one_id = dict['person_one_id']
    person_two_id = dict['person_two_id']

    #get new reports
    r = requests.get(h1_get_all_new_prod, auth=(h1_api_name, h1_api_key))
    h1_data = json.loads(r.text)

    for item in h1_data['data']:

        if 'structured_scope' in item['relationships']:
            #grab the h1_asset_id type
            h1_asset_id = item['relationships']['structured_scope']['data']['attributes']['asset_identifier']

            #check if report is already assigned
            if 'assignee' not in item['relationships']:

                #https://console.bluemix.net/docs/services/Cloudant/getting-started.html#appendix-complete-python-code-listing
                #IAM Authentication (uncomment if needed, and comment out IBM Cloudant Legacy authentication section above)
                client = Cloudant.iam(cloudant_api_name, cloudant_api_key, connect=True)

                #retrieve db
                my_database = client['h1']

                # Upon entry into the document context, fetches the document from the
                # remote database, if it exists. Upon exit from the context, saves the
                # document to the remote database with changes made within the context.
                with Document(my_database, 'roundrobin') as my_document:
                    my_last = my_document['last']

                    if my_last == 0:
                        #assigns report to redstapler
                        my_payload = {'data': {'id': person_one_id,'type': 'user','attributes': {'message': 'A report has been assigned automatically to you.'}}}
                        r = requests.put(h1_get_report + item['id'] + '/assignee', json=my_payload, auth=(h1_api_name, h1_api_key))

                        #return value to db
                        my_document['last'] = 1

                    else:
                        #assigns report to bluescreen
                        my_payload = {'data': {'id': person_two_id,'type': 'user','attributes': {'message': 'A report has been assigned automatically to you.'}}}
                        r = requests.put(h1_get_report + item['id'] + '/assignee', json=my_payload, auth=(h1_api_name, h1_api_key))

                        #return value to db
                        my_document['last'] = 0

                    #save db new value
                    my_document.save()
                    #close db connection
                    client.disconnect()

        else:
            print("failed")
            continue

    if r.status_code != 200:
        return {
            'statusCode': r.status_code,
            'headers': { 'Content-Type': 'application/json'},
            'body': {'message': 'Error processing your request'}
        }
    else:
        return {
            'text': print()
        }
