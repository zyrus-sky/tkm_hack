##ETHIndia hacathon 
# 🎓 TKM Data Analysis & Admin Dashboard

A powerful, modular **Streamlit + Web3** powered dashboard application for managing and analyzing college, hospital, and student data. This system integrates blockchain data, local CSV-based analytics, and role-specific dashboards.

---

## 📁 Project Structure

```bash
.
├── college_admin.py            # College administrator dashboard
├── college_analyst_report.py   # Detailed analytics and reports
├── hospital_admin.py           # Hospital administrator dashboard
├── stu.py                      # Student dashboard
├── students.csv                # Student information dataset
├── faculty.csv                 # Faculty details
├── staff.csv                   # Staff members
├── grades.csv                  # Grades data
├── salary.csv                  # Salary information
├── reports.csv                 # Academic and hospital reports
├── departments.csv             # Department data
├── scholarships.csv            # Scholarship info
├── points.csv                  # Points / scoring data
├── ethers.js                   # Frontend Web3 interactions
├── hardhat.config.js           # Blockchain smart contract config
├── package.json                # JavaScript dependencies
├── venv/                       # Python virtual environment
└── home.py                     # Main entry point (dashboard navigator)
````

---

## 🚀 Features

* 🔐 **Role-based dashboards**: College admin, hospital admin, student view.
* 📊 **Advanced analytics**: Grades, scholarships, salaries, and department insights.
* 🏥 **Hospital management**: Staff, faculty, and hospital-specific reports.
* 🧠 **AI-ready & modular**: Easily integrate machine learning, charts, or LLM-based analysis.
* 🌐 **Web3 Integration**: Uses `ethers.js` and Hardhat for blockchain interaction.
* 📂 **CSV data driven**: Easily replaceable and scalable datasets.
* 🔄 **Single page navigation**: Seamless transitions via `home.py`.

---

## 📦 Dependencies

```bash
pip install streamlit pandas web3
npm install ethers hardhat
```

---

## ▶️ How to Run

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/tkm-dashboard.git
cd tkm-dashboard
```

### 2. Start the Python Streamlit app

```bash
streamlit run home.py
```

> All other modules (`college_admin.py`, `hospital_admin.py`, etc.) will be accessible from the main navigation page.

---

## 📸 Screenshots

> Add screenshots of:

* Main dashboard
* Analytics page
* Admin views
* Web3 interaction sample (optional)

---

## 🧩 Modules in Detail

| File                        | Description                                  |
| --------------------------- | -------------------------------------------- |
| `home.py`                   | Main router for all dashboard modules        |
| `college_admin.py`          | Admin panel for academic data                |
| `college_analyst_report.py` | Advanced charting and data reporting         |
| `hospital_admin.py`         | Hospital data dashboard                      |
| `stu.py`                    | Student portal / view                        |
| `ethers.js`                 | JavaScript connector for Ethereum blockchain |
| `hardhat.config.js`         | Smart contract configuration                 |

---

## 📄 License

This project is licensed under the MIT License — feel free to use, modify, and distribute.

---

## 🤝 Contributing

Pull requests, issues, and feature requests are welcome. Feel free to check the [issues page](https://github.com/yourusername/tkm-dashboard/issues).

---

## ✨ Acknowledgements

* [Streamlit](https://streamlit.io/)
* [Ethers.js](https://docs.ethers.org/)
* [Hardhat](https://hardhat.org/)
* TKM Institute community ❤️

```


