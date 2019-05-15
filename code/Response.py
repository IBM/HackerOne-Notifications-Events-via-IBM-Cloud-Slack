#© Copyright IBM Corporation [2018], [2019] [Ali Kaba]
#LICENSE: [Apache License 2.0 (Apache-2.0) http://www.apache.org/licenses/LICENSE-2.0]
import sys
import requests
import json
import datetime
from datetime import date,timedelta

def main(dict):
    #required parameters - actual secrets are entered in the IBM Function action's paremeter section. DO NOT PUT SECRETS IN CODE
    top_info = dict['top_info']
    h1_get_all_new_prod = dict['h1_get_all_new_prod']
    h1_api_name = dict['h1_api_name']
    h1_api_key = dict['h1_api_key']

    time_to_first_response_report = "\n\n----------FIRST RESPONSE REQUIRED----------\n"
    time_to_triage_report = "\n----------------TRIAGE REQUIRED----------------\n"

    #counter
    time_to_first_response_count = 0
    time_to_triage_count = 0

    #get new reports
    r = requests.get(h1_get_all_new_prod, auth=(h1_api_name, h1_api_key))
    h1_data = json.loads(r.text)

    for item in h1_data['data']:
        #putting report create date into string
        h1_report_year_created = (item['attributes']['created_at'])[0:4]
        h1_report_month_created = (item['attributes']['created_at'])[5:7]
        h1_report_day_created = (item['attributes']['created_at'])[8:10]

        #converting string to int
        h1_report_year_created = int(h1_report_year_created)
        h1_report_month_created = int(h1_report_month_created)
        h1_report_day_created = int(h1_report_day_created)

        #calculate today's date
        todays_date = date.today()
        h1_date_created = date(h1_report_year_created,h1_report_month_created,h1_report_day_created)
        todays_date = date(todays_date.year,todays_date.month,todays_date.day)

        #getting days_elapsed between created and today's date, excluding weekends
        day_generator = (h1_date_created + timedelta(x + 1) for x in range((todays_date - h1_date_created).days))
        days_elapsed = sum(1 for day in day_generator if day.weekday() < 5)

        #get reports that are 3 days old
        if days_elapsed >= 3:

            #get the number of days
            h1_report_life = str(days_elapsed)

            if 'structured_scope' in item['relationships']:
                #grab the h1_asset_id type
                h1_asset_id = item['relationships']['structured_scope']['data']['attributes']['asset_identifier']
            else:
                h1_asset_id = "No Asset Selected"

            #did not respond
            if item['attributes']['first_program_activity_at'] is None:
                time_to_first_response_report = time_to_first_response_report + "Asset: " + h1_asset_id +"\nReport: https://hackerone.com/reports/" + item['id'] + "\nLife (in days): " + h1_report_life + "\n"
                time_to_first_response_count = 1

        #get reports that are 8 or more days old (includes weekends)
        if days_elapsed >= 8:
            time_to_triage_report = time_to_triage_report + "Asset: " + h1_asset_id +"\nReport: https://hackerone.com/reports/" + item['id'] + "\nLife (in days): " + h1_report_life + "\n"
            time_to_triage_count = 1

    #check if either have no results,  don't send anything
    if time_to_first_response_count == 0:
        time_to_first_response_report = time_to_first_response_report + "\n No Reports"
    if time_to_triage_count == 0:
        time_to_triage_report = time_to_triage_report + "\n No Reports"

    if r.status_code != 200:
        return {
            'statusCode': r.status_code,
            'headers': { 'Content-Type': 'application/json'},
            'body': {'message': 'Error processing your request'}
        }
    else:
        return {
            'text': top_info + time_to_first_response_report + time_to_triage_report
        }
