@echo off
echo [INFO] Starting deployment to Streamlit Cloud...

echo [1/3] Adding all changes...
git add .

echo [2/3] Committing changes (Update navigation buttons)...
git commit -m "Update navigation: List button and Chatbot button"

echo [3/3] Pushing to GitHub...
git push origin main

echo.
echo ========================================================
echo [SUCCESS] Changes have been pushed to GitHub!
echo Streamlit Cloud will recognize the update and redeploy.
echo.
echo Please wait about 1-2 minutes, then REFRESH your browser.
echo Address: https://lotte-ai-app.streamlit.app/
echo ========================================================
pause
