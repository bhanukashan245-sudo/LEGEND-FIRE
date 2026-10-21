(pc)
pyinstaller --onefile --noconsole main.py
pip install pyinstaller
pyinstaller --onefile --noconsole --icon=logo.ico my_ai.py
pyinstaller --onefile --noconsole --clean --icon=logo.ico my_ai.py
pyinstaller --onefile --clean --icon=logo.ico my_ai.py
pyinstaller --noconsole --onefile --clean --collect-all customtkinter --icon=logo.ico my_ai_gui.py
pyinstaller --noconsole --onefile --clean --collect-data customtkinter --icon=logo.ico my_ai_gui.py
pip install pyinstaller
pyinstaller --noconsole --onefile --add-data "scary.jpg;." main.py
pyinstaller --noconsole --onefile --icon="icon.ico" --add-data "scary.jpg;." main.py

(android)
pip install buildozer
buildozer -v android debug