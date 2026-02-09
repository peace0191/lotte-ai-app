@echo off
echo ========================================================
echo [FORCE UPDATE] Deploying latest changes to Streamlit Cloud...
echo ========================================================
echo [1/3] Adding changes...
git add .
if %errorlevel% neq 0 (
    echo [ERROR] Git add failed. Check your git installation or permissions.
    pause
    exit /b
)

echo.
echo [2/3] Committing changes (Timestamp update)...
git commit -m "Force Update: %date% %time%"
if %errorlevel% neq 0 (
    echo [WARNING] Nothing to commit? Continuing anyway...
)

echo.
echo [3/3] Pushing to GitHub...
git push origin main
if %errorlevel% neq 0 (
    echo [ERROR] Git push failed. Please check your internet connection or git login.
    echo Try running: git push origin main manually.
    pause
    exit /b
)

echo.
echo ========================================================
echo [SUCCESS] Changes pushed!
echo Streamlit Cloud will now detect a new commit and rebuild the app.
echo Please wait 2-3 minutes before refreshing the page.
echo Address: https://lotte-ai-app.streamlit.app/
echo ========================================================
pause
