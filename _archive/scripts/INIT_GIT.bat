@echo off
REM Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo Git is not installed. Please install Git first.
    pause
    exit /b
)

echo Initializing Git repository...
git init
git add .
git commit -m "Initial commit of Lotte AI Sales App"

echo.
echo ========================================================
echo Git repository initialized and changes committed.
echo Now you need to create a repository on GitHub.
echo.
echo 1. Go to https://github.com/new
echo 2. Name your repository (e.g., lotte-ai-app)
echo 3. Create repository
echo 4. Copy the URL (e.g., https://github.com/peace0191/lotte-ai-app.git)
echo.
echo Then run the following commands manually:
echo git remote add origin <YOUR_REPO_URL>
echo git push -u origin main
echo ========================================================
pause
