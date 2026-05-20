# 💸 Money Decoded — AI Expense Dashboard
 
> **Turn your bank statements into powerful financial insights — instantly.**  
> Upload a CSV. Get AI-powered spending analysis, charts, and personalized tips in seconds.
 
---
 
## 🚀 What is this?
 
**Money Decoded** is a local AI-powered financial dashboard built with **Python (Flask)** and **HTML/CSS/JS**.  
It analyzes your personal expense data from any CSV (bank exports, UPI apps, manual logs) and gives you:
 
- 📊 **Visual breakdowns** — pie charts, monthly trends, daily spending patterns
- 🤖 **AI-generated insights** — personalized tips based on your actual spending behavior
- 🗂️ **Smart categorization** — auto-detects merchants and categories from raw data
- ⚡ **Zero cloud** — everything runs locally on your machine, your data stays with you
---
 
## 🖥️ Tech Stack
 
| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| AI / Categorization | `categorizer.py` (LLM-powered) |
| Data Processing | Pandas, CSV parsing |
| Launch Scripts | `.bat` (Windows), `.ps1` (PowerShell) |
 
---
 
## 📁 Project Structure
 
```
Money-Decoded--AI-Expense-Dashboard/
│
├── main.py                  # Flask server & API routes
├── categorizer.py           # AI-powered expense categorizer
├── index.html               # Frontend dashboard UI
├── requirements.txt         # Python dependencies
│
├── START_DASHBOARD.bat      # One-click Windows launcher
├── START_DASHBOARD.ps1      # PowerShell launcher
│
├── uploads/                 # Temporary CSV upload storage
├── HOW_TO_RUN.md            # Detailed run instructions
├── CSV_REQUIREMENTS.md      # CSV format guide
└── .gitignore
```
 
---
 
## ⚙️ Installation & Setup
 
### Prerequisites
- Python 3.8+ installed → [python.org](https://www.python.org/downloads/)
- pip (comes with Python)
### Step 1: Clone the Repository
```bash
git clone https://github.com/officialdivyanshu/Money-Decoded--AI-Expense-Dashboard.git
cd Money-Decoded--AI-Expense-Dashboard
```
 
### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```
 
### Step 3: Run the Dashboard
 
**Option A — One Click (Windows Easiest) 🎯**
```
Double-click: START_DASHBOARD.bat
```
 
**Option B — Terminal**
```bash
python main.py
```
 
**Option C — PowerShell**
```powershell
.\START_DASHBOARD.ps1
```
 
### Step 4: Open in Browser
```
http://localhost:5000
```
 
---
 
## 📊 How to Use
 
1. **Export your bank/UPI statement** as a `.csv` file (HDFC, ICICI, GPay, PhonePe, Paytm — all supported)
2. **Upload the CSV** on the dashboard
3. **Instantly see:**
   - Total expenses & income
   - Category-wise pie chart
   - Monthly spending trend
   - Daily pattern chart
   - AI-generated insights & saving tips
4. **Done!** No account, no cloud, no data sharing.
---
 
## 📋 CSV Format Guide
 
Your CSV needs at minimum a **date** and **amount** column. Here's the ideal format:
 
```csv
date,amount,merchant,category
2026-04-01,-3796.67,DMart,Groceries
2026-04-01,-1004.63,Uber,Transport
2026-04-02,-560.46,Zomato,Food & Dining
2026-04-03,5000,Salary,Income
```
 
**Supported categories:**
`Food & Dining` · `Transport` · `Shopping` · `Entertainment` · `Utilities` · `Health` · `Subscriptions` · `Travel` · `Others`
 
> 📄 See [`CSV_REQUIREMENTS.md`](./CSV_REQUIREMENTS.md) for complete format documentation, bank-specific export guides, and troubleshooting tips.
 
---
 
## 🏦 Supported Bank Exports
 
| Bank / App | Export Format | Works? |
|------------|--------------|--------|
| HDFC Bank | Date, Narration, Debit, Credit | ✅ Direct upload |
| ICICI Bank | Date, Description, Amount | ✅ Direct upload |
| Google Pay | Date, Merchant, Amount, Category | ✅ Direct upload |
| PhonePe | Date, Description, Amount | ✅ Direct upload |
| Paytm | Date, Debit, Credit, Balance | ✅ Remove Balance column |
| Manual CSV | Custom format | ✅ Auto-detected |
 
---
 
## 🛑 Stopping the Server
 
Press `Ctrl + C` in the terminal, or simply close the terminal window.
 
---
 
## 🔧 Troubleshooting
 
| Problem | Fix |
|---------|-----|
| `python` not recognized | Install Python from python.org and add to PATH |
| Port 5000 already in use | Change port in `main.py` → `app.run(port=5001)` |
| Can't open localhost:5000 | Try `http://127.0.0.1:5000` instead |
| Empty charts after upload | Check CSV has valid date + amount columns (no ₹ symbols or commas) |
| Terminal closes instantly | Use the `.bat` file which keeps the window open |
 
> 📄 Full troubleshooting guide in [`HOW_TO_RUN.md`](./HOW_TO_RUN.md)
 
---
 
## 🤝 Contributing
 
Pull requests are welcome! If you find a bug or want to suggest a feature:
 
1. Fork the repo
2. Create a new branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add: your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request 🙌
---
 
## 👨‍💻 Author
 
**Divyanshu Shekhar**  
- 🔗 [LinkedIn](https://linkedin.com/in/officialdivyanshu)
- 🐙 [GitHub](https://github.com/officialdivyanshu)
- 🌐 [Portfolio](https://officialdivyanshu.github.io)
---
 
## 📜 License
 
This project is open source and available under the [MIT License](LICENSE).
 
---
 
<div align="center">
  <strong>⭐ If this helped you, consider giving it a star on GitHub!</strong><br/>
  Made with 💛 by Divyanshu Shekhar
</div>
