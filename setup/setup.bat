@echo off

python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Installing requirements...
pip install -r requirements.txt
echo Done installing requirements
