import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from zoneinfo import ZoneInfo
import json

def authenticate_google_sheets():
    # authentication to google APIs
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials_json = json.loads(os.environ['GOOGLE_CREDENTIALS'])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, scope)
    client = gspread.authorize(credentials)
    spreadsheet = client.open("SWDA-XMME_periodic_rebalancing")
    return spreadsheet


def update_spreadsheet_with_allocation(optimal_weights, balanced_portfolio, comparison_df):
    try:
        sheet = authenticate_google_sheets().sheet1
    except Exception as e:
        print(f"Error authenticating with Google Sheets: {e}")

    try:
        # Clear old data before writing
        sheet.batch_clear(["D2:F1000"])

        # Update optimal weights in the sheet
        sheet.update_acell('A2', optimal_weights[0])
        sheet.update_acell('B2', optimal_weights[1])

        # Update geographical allocations in the sheet
        comparison_df = comparison_df.sort_values(by = 'VWCE', ascending=False)
        N = comparison_df.shape[0]

        country_list = comparison_df.index.tolist()
        country_list = [[x] for x in country_list]

        balanced_portfolio = comparison_df['SWDA+XMME'].values.tolist()
        balanced_portfolio = [[x] for x in balanced_portfolio]

        target_portfolio = comparison_df['VWCE'].values.tolist()
        target_portfolio = [[x] for x in target_portfolio]


        cell_interval = 'D2:D' + str(N+3)
        sheet.update(country_list, cell_interval)

        cell_interval = 'E2:E' + str(N+3)
        sheet.update(balanced_portfolio, cell_interval)

        cell_interval = 'F2:F' + str(N+3)
        sheet.update(target_portfolio, cell_interval)

        italy_timezone = datetime.now(ZoneInfo("Europe/Rome"))

        timestamp = italy_timezone.strftime("%Y-%m-%d %H:%M:%S")
        sheet.update_acell('H2', timestamp)
        
    except Exception as e:
        print(f"Error updating the spreadsheet: {e}")
    
    return