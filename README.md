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

Run the script with this command in your Terminal / CMD:
> python mailjet_automation.py

