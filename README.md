# Google Search Console Downloader

This collection of scripts parses a list of accounts to download GSC data over a selected range of time.
## Installation

_Need to write install instructions, potentially create a setup.py file._

_Need to make sure I include details on how to create Google account credentials as well as explain where all the variables and samples are._

## Required Packages
- pandas
- google_auth_oauthlib
- google-api-python-client

## Usage

1. Install all required packages
2. Create a Google project with API access for GSC and Oauth credentials
   - Download the _client_id.json_ and replace **config/client-id.json.sample**
3. Update the **config/google_accounts.txt.sample** file

Then simply run the script to gather the GSC data for 5 days ago.
```bash
$ python run.py
```

There are options available to customise the scripts behaviour further:
```bash
$ python run.py -h # get a reminder of all of these options

$ python run.py --forceUpdate # if a csv file already exists with this site and date options this will delete it so it can be re-run
$ python run.py --siteUrl 'https://www.domain.com/' # limit the script to a single domain you have access to (domain needs to exactly match what is in GSC)
$ python run.py --startDate # as the name implies
$ python run.py --endDate # as the name implies
```
- If the **startDate** is later than the **endDate** then the **startDate** is used as both Start and End.
- If no **endDate** is provided but **startDate** is, it uses the largest value of 5 days ago and the Start
- If no **startDate** is provided but **endDate** is:
  - If **endDate** is more than 5 days ago this argument gets ignored and it returns to default
  - If it is less than 5 days ago then **startDate** is default (5 days ago) and **endDate** works as expected


## Notes

- _This currently only runs on CLI if you have it open due to credential requests.
If you haven't updated any accounts and know the credentials are still valid you can run it in the background. But, it may break._
- _This needs to have more features added, like the ability to run a single account rather than just a single siteUrl._
- _When running in the background, or forced, it should push to BigQuery. Otherwise should default to a CSV export._

