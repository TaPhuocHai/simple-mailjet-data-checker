# MacOS 
sudo pyinstaller --add-data 'ui_main.glade:.' ui_main-dev.py -F --clean

# Windows (Cannot bundle into a single exe file)
pyinstaller  ui_main-dev.py  --clean



 