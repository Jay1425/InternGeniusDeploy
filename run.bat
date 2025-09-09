@echo off
echo Starting InternGenius Application...
echo.
echo Please wait while we set up the environment...

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo Starting the application...
python simple_app.py

echo.
pause
