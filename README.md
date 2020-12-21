# mailjet_automation_tool

## How To Install
1) Python
Ensure you have Python version 3.4 or later. Kindly visit https://www.python.org/ and download Python version 3 on your system.

2) Clone or simply download the code

3) Install virtual environment package (Highly recommend but not 100% necessary)
> python -m pip install --user virtualenv
Then create an isolated virtual enviroment
> python -m virtualenv ematic_env

4) Activate the virtual enviroment (You can skip this if you don't do step 3)
> source ematic_env/bin/activate

5) Install dependencies for our program
> pip install -r requirements.txt

## How to Use

You also need to have 2 folder: input and output.

In the input folder, place the data in csv or excel format (xlsx, xls) which must have a email column. Then open the file mailjet_automation.py, change the constant NEW_DATA to the name of the new data file.

Make sure you follow these steps to prepare the script to run.
1) Go to the Mailjet account
2) Download the data from the main contact list and put the file in the input folder
3) Download the data from exclusion list and put the file in the input folder
4) Put the given file to check data in the input folder. Make sure we have an email column.
5) Open the script ``mj_automation.py`` and update name of the files to the variables namely _MJ_MainData_ and _MJ_Exclusion_ and _NEW_DATA_


Run the script with this command in your Terminal / CMD:
> python mj_automation.py

