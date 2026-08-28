py -m PyInstaller --noconfirm --onefile --windowed --icon=logo.ico --hidden-import=locales --add-data "locales.py;." --add-data "logo.ico;." --add-data "logo.png;." AjaSchedule.py
pause