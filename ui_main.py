import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from mj_formatter import mailjet
import pandas as pd 
import requests
import os
from mj_automation import clean_data, getDvScore
from pyGlade import *

import time
# 
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
# exportedData = OUTPUT_DIR_NAME + 'exported.csv' # no need to change, this is formatted DB data
exportedData ='processedDB.csv' # no need to change, this is formatted DB data

# 

class Handler:
    def file_set_MainData(self, button):
        self.fileMainData = button.get_filename()
    
    def file_set_ExclusionData(self, button):
        self.fileExclusionData = button.get_filename()

    def file_set_NewData(self, button):
        self.fileNewData = button.get_filename()    

    def __init__(self):
        self.fileMainData = None
        self.fileExclusionData = None
        self.fileNewData = None

    def onDestroy(self, *args):
        Gtk.main_quit()

    def onButtonPressed(self, button):
        # Process Data
        print(self.fileMainData, self.fileExclusionData, self.fileNewData)
        DisplayWindow = builder.get_object('DisplayWindow1')
        global exportedData
        global NEW_DATA
        NEW_DATA = self.fileNewData
        writeToDirectory = os.path.split(NEW_DATA)[0]
        exportedDataPath = os.path.join(writeToDirectory, exportedData)
        
        mj = mailjet(self.fileMainData, self.fileExclusionData, exportedDataPath)
        mj.formatData()
        mj_db = pd.read_csv(exportedDataPath)    
        # # print("2) Crosscheck new data with Mailjet data")
        # txt = '' #clean_data(mj_db, NEW_DATA)
        self.textbuffer = DisplayWindow.get_buffer()
        cleanTxt  = clean_data(mj_db, NEW_DATA)
        
        self.textbuffer.set_text(cleanTxt)
        DisplayWindowDV = builder.get_object('DisplayWindowDV')
        self.textbufferDV = DisplayWindowDV.get_buffer()
        #   -------------------------------------------------------- #        
        txt = 'Checking DV Score\n'
        self.progresBar = builder.get_object('progressBar')
        valueProgressBar = 0.01        
        self.progresBar.set_fraction(valueProgressBar)
        GLib.idle_add(self.getDV)


    def getDV(self):
        DisplayWindowDV = builder.get_object('DisplayWindowDV')
        self.textbufferDV = DisplayWindowDV.get_buffer()
        #   -------------------------------------------------------- #        
        txt = 'Checking DV Score\n'
        self.progresBar = builder.get_object('progressBar')
        while Gtk.events_pending():
            Gtk.main_iteration()        
        self.textbufferDV.set_text(txt)
        file_name = os.path.splitext(NEW_DATA)[0]
        file = file_name + "_to_hyatt.csv"
        url = 'https://dv3.datavalidation.com/api/v2/user/me/list/create_upload_url/'
        params = '?name=' + file + '&email_column_index=0&has_header=0&start_validation=false'
        DV_API_KEY = '' # Data validation API KEY
        headers = {'Authorization': 'Bearer ' + DV_API_KEY}
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount("https://", a)
        res = s.get(url+params, headers=headers)
        upload_csv_url = res.json()
        files = {
            'file': open(file, 'rb')
        }
        list_id = s.post(upload_csv_url, headers=headers, files=files)
        dv_result_url = 'https://dv3.datavalidation.com/api/v2/user/me/list/' + list_id.json()
        dv_result = s.get(dv_result_url, headers=headers).json()
        def percent(count): return round((count / dv_result['subscriber_count']), 2) * 100

        while dv_result['status_value'] == 'PRE_VALIDATING':
            dv_result = requests.get(dv_result_url, headers=headers).json()
            txt += "Status percent complete: " + str(dv_result['status_percent_complete']) + "\n"
            self.textbufferDV.set_text(txt)        
            self.progresBar.set_fraction(dv_result['status_percent_complete'] / 100)
            while Gtk.events_pending():
                Gtk.main_iteration()            
            time.sleep(5)  # sleep 5 seconds

        try:
            
            txt +=  "Done checking dv score\n"
            txt += "The grade summary is: \n" 
            score = ""
            self.textbufferDV.set_text(txt)

            for score_name, score_value in dv_result['grade_summary'].items():
                score += '%-3s : ' % (score_name) + str(percent(score_value)) +"\n"                

            txt += score + "\n"
            self.textbufferDV.set_text(txt)        

        except:
            if (dv_result['subscriber_count'] == 0):
                txt +=  '''
                        Empty list of emails were sent for dv validation!
                        Perhaps no new email to check dv?
                        Program terminated
                        '''
                self.textbufferDV.set_text(txt)            
        #   ---------------------------------------------------------#
        print(txt)
        return False
         
    def updateProgress(self, score):
        self.progresBar.set_fraction(score)
        if score == 1:
            return False


builder = Gtk.Builder()
# builder.add_from_file("./ui_main.glade")
builder.add_from_string(gladeUi)
builder.connect_signals(Handler())

window = builder.get_object("window1")
window.show_all()

Gtk.main()