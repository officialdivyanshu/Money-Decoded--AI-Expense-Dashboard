# Money Decoded Dashboard - PowerShell Launcher
# Run this in PowerShell to start the dashboard

Set-Location "c:\Users\Divyanshu Shekhar\OneDrive\Desktop\MONEY, Decoded"
Write-Host "🚀 Starting Money Decoded Dashboard..." -ForegroundColor Green
Write-Host "📍 Dashboard will open at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python main.py
