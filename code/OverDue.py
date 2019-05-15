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
    h1_get_all_triaged_prod = dict['h1_get_all_triaged_prod']
    h1_get_report = dict['h1_get_report']
    h1_api_name = dict['h1_api_name']
    h1_api_key = dict['h1_api_key']
    sev_critical = dict['sev_critical']
    sev_high = dict['sev_high']
    sev_medium = dict['sev_medium']
    sev_low = dict['sev_low']

    past_due_report = "\n\n---------------PAST DUE REPORTS---------------\n"

    #counter
    past_due_count = 0

    #fetches 2 pages (200) reports (if they exist)
    a = 1
    while a <= 3:
        #convert number to string
        page_number = str(a)

        #get new reports
        r = requests.get(h1_get_all_triaged_prod + page_number, auth=(h1_api_name, h1_api_key))
        h1_data = json.loads(r.text)

        for item in h1_data['data']:
            #grab the h1_asset_id type
            h1_asset_id = item['relationships']['structured_scope']['data']['attributes']['asset_identifier']

            #reports that are websites
            if h1_asset_id == 'IBM Websites':

                #ignore reports that are not assignee
                if 'assignee' in item['relationships']:

                    #verify it isn't assigned to a username
                    if 'username' not in item['relationships']['assignee']['data']['attributes']:

                        r = requests.get(h1_get_report + item['id'], auth=(h1_api_name, h1_api_key))
                        h1_data2 = json.loads(r.text)

                        found_activity = 0
                        b = 0
                        while found_activity == 0:
                            if h1_data2['data']['relationships']['activities']['data'][b]['type'] == 'activity-group-assigned-to-bug':

                                h1_owner = h1_data2['data']['relationships']['activities']['data'][b]['relationships']['actor']['data']['attributes']['username']

                                #putting report create date into string
                                h1_comment_year_created = (h1_data2['data']['relationships']['activities']['data'][b]['attributes']['created_at'])[0:4]
                                h1_comment_month_created = (h1_data2['data']['relationships']['activities']['data'][b]['attributes']['created_at'])[5:7]
                                h1_comment_day_created = (h1_data2['data']['relationships']['activities']['data'][b]['attributes']['created_at'])[8:10]

                                #converting string to int
                                h1_comment_year_created = int(h1_comment_year_created)
                                h1_comment_month_created = int(h1_comment_month_created)
                                h1_comment_day_created = int(h1_comment_day_created)

                                #calculate today's date
                                todays_date = date.today()
                                h1_date_created = date(h1_comment_year_created,h1_comment_month_created,h1_comment_day_created)
                                todays_date = date(todays_date.year,todays_date.month,todays_date.day)

                                #getting days_elapsed between created and today's date, excluding weekends
                                day_generator = (h1_date_created + timedelta(x + 1) for x in range((todays_date - h1_date_created).days))
                                days_elapsed = sum(1 for day in day_generator if day.weekday() < 5)
                                h1_report_severity = h1_data2['data']['relationships']['severity']['data']['attributes']['rating']

                                #grab last activity date
                                last_activity_date = (h1_data2['data']['relationships']['activities']['data'][0]['attributes']['created_at'])[0:10]

                                if h1_report_severity == "critical" and days_elapsed >= sev_critical:
                                    missed_days = days_elapsed - sev_critical
                                    missed_days = str(missed_days)
                                    past_due_report = past_due_report + "\nReport: https://hackerone.com/reports/" + h1_data2['data']['id'] + "\nMissed Days: " + missed_days + "\nSeverity: " + h1_report_severity + "\nLast Activity on: " + last_activity_date + "\nOwner: " + h1_owner + "\n"
                                    past_due_count = 1
                                elif h1_report_severity == "high" and days_elapsed >= sev_high:
                                    missed_days = days_elapsed - sev_high
                                    missed_days = str(missed_days)
                                    past_due_report = past_due_report + "\nReport: https://hackerone.com/reports/" + h1_data2['data']['id'] + "\nMissed Days: " + missed_days + "\nSeverity: " + h1_report_severity + "\nLast Activity on: " + last_activity_date + "\nOwner: " + h1_owner + "\n"
                                    past_due_count = 1
                                elif h1_report_severity == "medium" and days_elapsed >= sev_medium:
                                    missed_days = days_elapsed - sev_medium
                                    missed_days = str(missed_days)
                                    past_due_report = past_due_report + "\nReport: https://hackerone.com/reports/" + h1_data2['data']['id'] + "\nMissed Days: " + missed_days + "\nSeverity: " + h1_report_severity + "\nLast Activity on: " + last_activity_date + "\nOwner: " + h1_owner + "\n"
                                    past_due_count = 1
                                elif h1_report_severity == "low" and days_elapsed >= sev_low:
                                    missed_days = days_elapsed - sev_low
                                    missed_days = str(missed_days)
                                    past_due_report = past_due_report + "\nReport: https://hackerone.com/reports/" + h1_data2['data']['id'] + "\nMissed Days: " + missed_days + "\nSeverity: " + h1_report_severity + "\nLast Activity on: " + last_activity_date + "\nOwner: " + h1_owner + "\n"
                                    past_due_count = 1
                                else:
                                    break;
                                found_activity = 1
                            else:
                                b += 1

        a += 1
    if r.status_code != 200:
        return {
            'statusCode': r.status_code,
            'headers': { 'Content-Type': 'application/json'},
            'body': {'message': 'Error processing your request'}
        }
    else:
        return {
            'text': past_due_report
        }
