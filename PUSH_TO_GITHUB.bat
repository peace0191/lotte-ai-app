@echo off
echo ========================================================
echo [1/2] Connecting to GitHub repository...
echo ========================================================

git remote remove origin 2>nul
git remote add origin https://github.com/peace0191/lotte-ai-app.git

echo.
echo ========================================================
echo [2/2] Pushing code to GitHub...
echo ========================================================
git branch -M main
git push -u origin main

echo.
echo ========================================================
echo SUCCESS! Code successfully uploaded to GitHub.
echo.
echo Now, follow these final steps to get your public link:
echo.
echo 1. Go to: https://share.streamlit.io/
echo 2. Login with GitHub
echo 3. Click 'New app'
echo 4. Select Repository: peace0191/lotte-ai-app
echo 5. Main file path: app.py
echo 6. Click 'Deploy!'
echo ========================================================
pause
