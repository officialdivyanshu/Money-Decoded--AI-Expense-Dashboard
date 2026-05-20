# How to Run Money Decoded Dashboard

## ✅ OPTION 1: ONE-CLICK START (EASIEST) 🎯

### **For Windows Users:**
1. Navigate to: `c:\Users\Divyanshu Shekhar\OneDrive\Desktop\MONEY, Decoded`
2. Double-click: **`START_DASHBOARD.bat`**
3. Black terminal window opens
4. Go to browser: **http://localhost:5000**
5. Dashboard loads! ✓

---

## ✅ OPTION 2: PowerShell Start

### **Step 1: Open PowerShell**
- Press `Win + X` → Select **PowerShell**
- Or type `PowerShell` in Windows search

### **Step 2: Run the Script**
```powershell
c:\Users\Divyanshu Shekhar\OneDrive\Desktop\MONEY,\ Decoded\START_DASHBOARD.ps1
```

### **Step 3: Open Browser**
- Go to: http://localhost:5000

---

## ✅ OPTION 3: Manual Terminal Start

### **Using Command Prompt (CMD):**
```cmd
cd c:\Users\Divyanshu Shekhar\OneDrive\Desktop\MONEY, Decoded
python main.py
```

### **Using PowerShell:**
```powershell
cd "c:\Users\Divyanshu Shekhar\OneDrive\Desktop\MONEY, Decoded"
python main.py
```

---

## ✅ OPTION 4: Create Desktop Shortcut

### **Step 1: Right-click Desktop**
- Select: **New** → **Shortcut**

### **Step 2: Enter Target**
```
cmd /k "cd /d c:\Users\Divyanshu Shekhar\OneDrive\Desktop\MONEY, Decoded && python main.py"
```

### **Step 3: Name It**
- Type: `Money Decoded Dashboard`
- Click: **Finish**

### **Step 4: Use It**
- Double-click the shortcut anytime to start!

---

## ✅ OPTION 5: Batch File with Auto-Browser

Create a fancier batch file that opens browser automatically:

### **File: `START_DASHBOARD_AUTO.bat`**
```batch
@echo off
cd /d "c:\Users\Divyanshu Shekhar\OneDrive\Desktop\MONEY, Decoded"
title Money Decoded Dashboard
color 0A
echo.
echo ===============================================
echo   MONEY DECODED - AI Financial Dashboard
echo ===============================================
echo.
echo Starting server...
echo Opening browser...
echo.
timeout /t 2 /nobreak
start http://localhost:5000
python main.py
pause
```

---

## 🔧 WHAT HAPPENS AFTER YOU START?

✅ Terminal shows:
```
🚀 Starting Money Decoded Flask Server
📍 Open: http://localhost:5000
🔌 CORS enabled for local development
* Running on http://127.0.0.1:5000
```

✅ Browser automatically opens dashboard

✅ Upload your CSV and analyze!

---

## ⛔ STOPPING THE SERVER

### **Method 1: Press in Terminal**
```
Ctrl + C
```

### **Method 2: Close Terminal Window**
- Simply close the black terminal window

### **Method 3: End Task**
- Press `Ctrl + Alt + Delete`
- Select Task Manager
- Find "Python" or "cmd"
- Click "End Task"

---

## 🚀 RECOMMENDED WORKFLOW

**Every time you want to use the dashboard:**

1. Double-click: **`START_DASHBOARD.bat`** ← EASIEST!
2. Wait for terminal to show "Running on http://127.0.0.1:5000"
3. Go to browser: **http://localhost:5000**
4. Upload your CSV
5. Analyze your spending!

**To stop:**
- Press `Ctrl + C` in terminal or close window

---

## 🎯 QUICK SUMMARY

| Method | Difficulty | Speed | Permanence |
|--------|-----------|-------|-----------|
| Double-click `.bat` | ⭐ Easiest | ⚡⚡⚡ Fastest | Per session |
| Desktop Shortcut | ⭐ Easy | ⚡⚡⚡ Fastest | Permanent |
| PowerShell | ⭐⭐ Medium | ⚡⚡ Fast | Per session |
| Terminal | ⭐⭐ Medium | ⚡⚡ Fast | Per session |

---

## 💡 PRO TIP

**Set the batch file to run on startup:**
1. Press `Win + R`
2. Type: `shell:startup`
3. Drag `START_DASHBOARD.bat` into that folder
4. Dashboard will start automatically when you boot your PC!

---

## ❓ TROUBLESHOOTING

**Q: Python is not installed?**
A: Run in PowerShell: `python --version`
   If error, install Python from python.org

**Q: Port 5000 already in use?**
A: Change port in `main.py` line ~490:
   ```python
   app.run(host='0.0.0.0', port=5001)  # Change 5000 to 5001
   ```

**Q: Can't access http://localhost:5000?**
A: Try http://127.0.0.1:5000 instead

**Q: Terminal closes immediately?**
A: Check your Python path or use `.bat` file (has `pause` to keep it open)

---

## 🎉 YOU'RE ALL SET!

Pick any method above and you're good to go. Recommended for most users: **Double-click `START_DASHBOARD.bat`**

No need to ask the AI anymore - just run the file! 🚀
