from halo import Halo
from codetiming import Timer
import pandas as pd 
import time
import os
from mj_formatter import mailjet

# Default directories where input and output data located
INPUT_DIR_NAME     = 'input/'
OUTPUT_DIR_NAME    = 'output/'

DV_API_KEY         = '' # API KEY of Data validation

NEW_DATA           = '' # Name of the data with file extension (csv, xlsx)
MJ_MainData        = '' # Downloaded data from mainlist 
MJ_Exclusion       = '' # Downloaded data from exclusion


# Folder setting
mainlistData  = INPUT_DIR_NAME  + MJ_MainData
exclusionData = INPUT_DIR_NAME  + MJ_Exclusion
exportedData = OUTPUT_DIR_NAME + 'exported.csv' # no need to change, this is formatted DB data

def clean_data(current_users):
    global NEW_DATA

    file_name, file_extension = os.path.splitext(NEW_DATA)
    file_extension = file_extension[1:]    

    if file_extension == 'csv':
        new_user_data = pd.read_csv(INPUT_DIR_NAME + '/' + NEW_DATA)
    elif file_extension == 'xlsx' or file_extension == 'xls':
        new_user_data = pd.read_excel(INPUT_DIR_NAME + '/' + NEW_DATA)
    else:
        return -1, "error: file_extention is not supported: " + file_extension
    
    # check email header exist
    is_no_email_header = True
    email_header = None
    for header in list(new_user_data.columns):
        formatted_header = header.lower().strip()
        if formatted_header.find("email") != -1 or formatted_header.find("e-mail"):
            email_header = header
            is_no_email_header = False
            break
    
    if is_no_email_header is True:
        return -1, "error: no email header/column found in your file " + NEW_DATA

    new_emails = new_user_data[email_header] #E-Mail or Email
    new_emails = new_user_data.rename(columns={email_header: "Email"})['Email']
    print("Number of users in the new file: ", len(new_emails))    
    # new_emails.sort_index(inplace=True)
    new_emails = new_emails.str.lower()
    new_emails = new_emails.str.strip()
    new_emails.drop_duplicates(keep="last", inplace=True)
    print("Number of users after dedup: ", len(new_emails))
    new_emails.to_csv(OUTPUT_DIR_NAME + "/" + file_name + "_removed_dup.csv", header=True, index=False)

    """get current existing users"""
    current_users.rename(columns={'email': 'Email', 'status': 'Status'},inplace=True)
    current_users['Email'] = current_users['Email'].str.lower()
    current_users['Email'] = current_users['Email'].str.strip()
    merged = current_users.merge(new_emails, how="right", indicator=True)
    merged.to_csv(OUTPUT_DIR_NAME + "/" + file_name + "compared_with_currentdb.csv", index=False, columns=["Email", "Status"])

    new_users = merged[merged['_merge']=='right_only']
    existing_sub = merged[merged['Status']=='sub']
    existing_sub.to_csv(OUTPUT_DIR_NAME + "/" + file_name + "_existing.csv", index=False)
    existing_unsub = merged[merged['Status']=='unsub']
    suppressed = merged[merged['Status']=='excluded']

    print("Number of new users: ", len(new_users), end=", ")
    print("along with %s existing sub, %s unsub, %s cleaned users" %(len(existing_sub), len(existing_unsub), len(suppressed)))
    
    new_users = pd.DataFrame(new_users['Email'])
    new_users.to_csv(OUTPUT_DIR_NAME + "/" + file_name + "_new_users.csv", index=False)
    sample_bad_emails = pd.read_csv("bad_emails.csv")
    new_users['Domain'] = new_users['Email'].str.split('@').str[1]
    merged = sample_bad_emails.merge(new_users, how="right", indicator=True, on="Domain")
    good_emails = merged[merged['_merge']=='right_only']
    print("Number of user after remove blacklisted domain: ", len(good_emails))
    good_emails = good_emails['Email']
    good_emails.to_csv(OUTPUT_DIR_NAME + "/" + file_name + "_to_hyatt.csv", index=False, header=True)
    bad_emails  = merged[merged['_merge']=='both']
    bad_emails.to_csv(OUTPUT_DIR_NAME + "/" + file_name + "_blacklisted.csv", index=False, header=True, columns=["Email", "Domain"])



def getDvScore():
    spinner = Halo(text="Checking dv score before performing hyatt", spinner='dots', text_color="grey")
    spinner.start()
        
    file = NEW_DATA.split(".")[0] + "_to_hyatt.csv"
    url = 'https://dv3.datavalidation.com/api/v2/user/me/list/create_upload_url/'
    params = '?name=' + file + '&email_column_index=0&has_header=0&start_validation=false'     
    headers = { 'Authorization': 'Bearer ' + DV_API_KEY }
    s = requests.Session()
    a = requests.adapters.HTTPAdapter(max_retries=3)
    s.mount("https://", a)    
    res = s.get(url+params, headers=headers)
    upload_csv_url = res.json()    
    files = {
        'file': open(OUTPUT_DIR_NAME + "/" + file, 'rb')
    }
    # list_id = requests.post(upload_csv_url, headers=headers, files=files)
    list_id = s.post(upload_csv_url, headers=headers, files=files)
    dv_result_url = 'https://dv3.datavalidation.com/api/v2/user/me/list/' + list_id.json()
    # dv_result = requests.get(dv_result_url, headers=headers).json()
    dv_result = s.get(dv_result_url, headers=headers).json()
    while dv_result['status_value'] == 'PRE_VALIDATING':
        dv_result = requests.get(dv_result_url, headers=headers).json()
        spinner.info("Status percent complete: " + str(dv_result['status_percent_complete']))
        time.sleep(5) # sleep 5 seconds
    try:
        percent = lambda count: round((count / dv_result['subscriber_count']),2) * 100
        
        spinner.succeed("Done checking dv score")
        print("The grade summary is: ")
        for score_name, score_value in dv_result['grade_summary'].items():
            print('%-3s : ' %(score_name) + str(percent(score_value)))
    except:
        if (dv_result['subscriber_count'] == 0):
            print("Empty list of emails were sent for dv validation!")
            print("Perhaps no new email to check dv?")
            print("Program terminated")
            return 0



if __name__ == "__main__":
    mj = mailjet(mainlistData, exclusionData, exportedData)
    mj.formatData()
    mj_db = pd.read_csv(exportedData)    
    print("2) Crosscheck new data with Mailjet data")
    clean_data(mj_db)
