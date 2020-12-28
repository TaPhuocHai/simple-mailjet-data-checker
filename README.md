# mailjet_automation_tool

## How To Install
Go to the release page: https://github.com/phatvo2015/simple-mailjet-data-checker/releases/tag/2 and download the specific build version.
There is no requirements to run the application.

## How to Use

You also need to have 2 folder: input and output.

In the input folder, place the data in csv or excel format (xlsx, xls) which must have a email column. Then open the file mailjet_automation.py, change the constant NEW_DATA to the name of the new data file.

Make sure you follow these steps to prepare the script to run.
1) Go to the Mailjet account
2) Download the data from the main contact list and put the file in the input folder
3) Download the data from exclusion list and put the file in the input folder
4) Open the application (release for respective OS platforms can be found [here](https://github.com/phatvo2015/simple-mailjet-data-checker/releases/tag/2))
5) From the application, choose exported data from Mailjet and choose the new data (data to crosscheck with Mailjet database)
6) Click the Check Data button to proceed
7) You should see the data checking result from the UI and from the console as well.

