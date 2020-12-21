import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from mj_formatter import mailjet
import pandas as pd 
import os
from mj_automation import clean_data, getDvScore
from pyGlade import *
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
    def __init__(self):
        self.fileMainData = None
        self.fileExclusionData = None
        self.fileNewData = None

    def onDestroy(self, *args):
        Gtk.main_quit()

    def onButtonPressed(self, button):
        # Process Data
        print(self.fileMainData, self.fileExclusionData, self.fileNewData)
        DisplayWindow = builder.get_object('DisplayWindow')
        global exportedData
        global NEW_DATA
        NEW_DATA = self.fileNewData
        writeToDirectory = os.path.split(NEW_DATA)[0]
        exportedDataPath = os.path.join(writeToDirectory, exportedData)
        
        mj = mailjet(self.fileMainData, self.fileExclusionData, exportedDataPath)

        mj.formatData()
        mj_db = pd.read_csv(exportedDataPath)    
        print("2) Crosscheck new data with Mailjet data")
        txt = clean_data(mj_db, NEW_DATA)

        self.textbuffer = DisplayWindow.get_buffer()
        self.textbuffer.set_text(txt)
        # self.textbuffer.set_text(
        #     "This is some text inside of a Gtk.TextView. "
        #     + "Select text and click one of the buttons 'bold', 'italic', "
        #     + "or 'underline' to modify the text accordingly."
        # )        

    def file_set_MainData(self, button):
        self.fileMainData = button.get_filename()
    
    def file_set_ExclusionData(self, button):
        self.fileExclusionData = button.get_filename()

    def file_set_NewData(self, button):
        self.fileNewData = button.get_filename()             

builder = Gtk.Builder()
# builder.add_from_file("./ui_main.glade")
builder.add_from_string(gladeUi)
builder.connect_signals(Handler())

window = builder.get_object("window1")
window.show_all()

Gtk.main()