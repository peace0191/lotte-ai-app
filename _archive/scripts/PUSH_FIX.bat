@echo off
echo ========================================================
echo [Update] Adding Missing Libraries (Plotly, Pydeck)...
echo ========================================================
git add requirements.txt

echo.
echo ========================================================
echo [Commit] Saving changes...
echo ========================================================
git commit -m "Fix: Add missing dependencies (plotly, pydeck)"

echo.
echo ========================================================
echo [Push] Uploading fix to GitHub...
echo ========================================================
git push origin main
pause
