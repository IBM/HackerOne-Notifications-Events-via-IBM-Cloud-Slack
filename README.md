# HackerOne Notifications/Events via IBM Cloud+Slack

The purpose of this project is to do 3 things.

- (1) [Response.py](code/Response.py) will notify you via Slack when:
  - a new report hasn't had any activity over 3 business days and when
  - a new report hasn't been triaged over 8 days
- (2) [RoundRobin.py](code/RoundRobin.py) will automatically assign new reports in a round robin fashion
- (3) [OverDue.py](code/OverDue.py) will notify you via Slack when a report is past due based on severity timeline

# Technologies used
- Python 3.7 (1)(2)(3)
- Node.js 6 (1)(2)(3)
- [HackerOne API](https://api.hackerone.com) (1)(2)(3)
  - The data that needs to be processed.
- [IBM Cloud](https://cloud.ibm.com/)
  - [Functions](https://www.ibm.com/cloud/functions) is used to manipulate and process the data and trigger all events.
  - [Cloudant](https://www.ibm.com/cloud/cloudant) is only used for [RoundRobin.py](code/RoundRobin.py) to store who went last.  I rotate between 2 users, so I store the value one or two in the db.
- Slack
  - The processed data is posted in a Slack channel.

# Contributions and Maintenance
This project is no longer being maintained.
