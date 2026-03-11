@echo off
echo 🔐 Starting FaceVault Assistant...
echo.

cd /d "%~dp0\backend"

echo 📦 Installing requirements...
pip install -r requirements.txt -q

mkdir known_faces 2>nul

echo.
echo 🚀 Starting backend server...
echo 📡 API: http://localhost:5000
echo 🌐 Open frontend\index.html in your browser
echo.
echo Press Ctrl+C to stop
echo.

python app.py
pause
