import argparse
from datetime import datetime, timedelta
from classes.wmGoogle import wmGSC

# Get all the options needed
parser = argparse.ArgumentParser(description='Get Google Search Console Data from the API')
parser.add_argument('--forceUpdate', action='store_true', help='Delete existing files and reprocess the query')
parser.add_argument('--siteUrl', type=str, help='If a site URL is passed only that data is gathered')
parser.add_argument('--startDate', type=str, help='The start date in format YYYY-MM-DD. If ignored this defaults to 5 days ago.')
parser.add_argument('--endDate', type=str, help='The end date in format YYYY-MM-DD. If ignored this defaults to 5 days ago.')
args = parser.parse_args()
FORCE_UPDATE = True if args.forceUpdate else False
SITE_URL = args.siteUrl if args.siteUrl else False

start = datetime.strptime(args.startDate, "%Y-%m-%d") if args.startDate else (datetime.now() - timedelta(5))
end = datetime.strptime(args.endDate, "%Y-%m-%d") if args.startDate else (datetime.now() - timedelta(5))

START_DATE = start.strftime("%Y-%m-%d")
END_DATE = max(start, end).strftime("%Y-%m-%d")


# Loop through all the google accounts in the google_accounts.txt file
accounts_filename = 'google_accounts.txt'
accounts = []
with open(accounts_filename) as f_in:
	accounts = (line.rstrip() for line in f_in) 
	accounts = list(line for line in accounts if line) # Non-blank lines in a list

# Check to make sure we have Google Credentials or request them
# Then get a list of all verified sites under that account
# De-duplicate sites across accounts
gsc = {}
verified_sites = {}
for account in accounts:
	print("CHECKING CREDENTIALS FOR "+account)
	gsc[account] = wmGSC(account)
	for site in gsc[account].get_verified_sites():
		if not SITE_URL or site == SITE_URL:
			verified_sites[site] = account

# Alert how many sites data will be gathered for based on the settings
print('')
if SITE_URL and len(verified_sites) == 0:
	print('ERROR: '+SITE_URL+' is not a verified site. Ensure it is written exactly correct including protocol and trailing slash.')
else:
	print('STARTING SCRIPT FOR '+str(len(verified_sites))+' SITES. BETWEEN '+START_DATE+' and '+END_DATE+' inclusive.')
print('')


# Start gathering the data and storing
for site_url in verified_sites:
	print('STARTING: '+site_url)
	gsc[verified_sites[site_url]].get_gsc_data(START_DATE, END_DATE, site_url, FORCE_UPDATE)
	print('')