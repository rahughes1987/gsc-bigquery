import pickle
import pandas as pd
import re
import os

from datetime import datetime, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from apiclient.discovery import build

class wmGSC:

	def __init__(self, account_email):
		ACCOUNT = account_email

		# Redirect URI for installed apps
		REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

		# There are only two OAuth Scopes for the Google Search Console API
		# For the most part, all you will need is `.readonly` but if you want to modify data in Google Search Console,
		# you will need the second scope listed below
		# Read more: https://developers.google.com/webmaster-tools/search-console-api-original/v3/
		OAUTH_SCOPE = ('https://www.googleapis.com/auth/webmasters.readonly', 'https://www.googleapis.com/auth/webmasters')

		# This is auth flow walks you through the Web auth flow the first time you run the script and stores the credentials in a file
		# Every subsequent time you run the script, the script will use the "pickled" credentials stored in config/credentials.pickle
		try:
		    credentials = pickle.load(open("config/credentials-"+ACCOUNT+".pickle", "rb"))
		except (OSError, IOError) as e:
			flow = InstalledAppFlow.from_client_secrets_file("client-id.json", scopes=OAUTH_SCOPE)
			credentials = flow.run_console()
			pickle.dump(credentials, open("config/credentials-"+ACCOUNT+".pickle", "wb"))

		# Connect to Search Console Service using the credentials
		self.webmasters_service = build('webmasters', 'v3', credentials=credentials)


	def get_verified_sites(self):
		site_list = self.webmasters_service.sites().list().execute()
		verified_sites_urls = [s['siteUrl'] for s in site_list['siteEntry']
								if s['permissionLevel'] != 'siteUnverifiedUser'
									and s['siteUrl'][:4] == 'http'];

		return verified_sites_urls


	def date_range(self, start_date, end_date, delta=timedelta(days=1)):
		"""
		The range is inclusive, so both start_date and end_date will be returned
		Args:
			start_date: The datetime object representing the first day in the range.
			end_date: The datetime object representing the second day in the range.
			delta: A datetime.timedelta instance, specifying the step interval. Defaults to one day.
		Yields:
			Each datetime object in the range.
		"""
		current_date = start_date
		while current_date <= end_date:
			yield current_date
			current_date += delta


	def get_gsc_data(self, start_date, end_date, site_url, force_update):
		maxRows = 25000
		start_date = datetime.strptime(start_date, "%Y-%m-%d") # YYYY-MM-DD
		end_date = datetime.strptime(end_date, "%Y-%m-%d") # YYYY-MM-DD
		filename = "data/gsc_output-"+re.sub(r'\W+', '', site_url)+"_"+start_date.strftime('%Y%m%d')+"-"+end_date.strftime('%Y%m%d')+".csv"

		if os.path.exists(filename) and not force_update:
			print(" - End: Already processed")
			return True
		elif os.path.exists(filename) and force_update:
			print(" - Processed file deleted with force_update")
			os.remove(filename)

		for date in self.date_range(start_date, end_date):
			date = date.strftime("%Y-%m-%d")
			print(' '+date)
			i = 0
			while True:
				request = {
					'startDate' : date,
					'endDate' : date,
					'dimensions' : ["query","page","country","device"],
					"searchType": "Web",
					'rowLimit' : maxRows,
					'startRow' : i * maxRows
				}

				response = self.webmasters_service.searchanalytics().query(siteUrl = site_url, body=request).execute()
				if response is None:
					print(" - Error: there is no response")
					break
				if 'rows' not in response:
					if i == 0: print(" - End: no data")
					break
				else:
					if i == 0: print(' - Gathering data')
					if i >= 1: print(' - Loop '+str(i+1))
					df = pd.DataFrame(columns=['site_url','date','query','page', 'country', 'device', 'clicks', 'impressions', 'ctr', 'avg_position'])
					for row in response['rows']:
						keyword = row['keys'][0]
						page = row['keys'][1]
						country = row['keys'][2]
						device = row['keys'][3]
						df = df.append({'site_url':site_url, 'date':date, 'query':keyword, 'page':page, 'country':country, 'device':device, 'clicks':row['clicks'], 'impressions':row['impressions'], 'ctr':row['ctr'], 'avg_position': row['position']}, ignore_index=True)

					with open(filename, 'a') as f:
						df.to_csv(f, header=f.tell()==0)
					df.iloc[0:0]
					i = i + 1