=> SMS  - Student Management System
_____________________________________________________________________________________________________________________________________________________________________

A professional, full-stack Academic Resource Planning (ERP) system designed for educational institutions. This platform streamlines student management, attendance tracking, academic performance monitoring, and fee management through a modern, glassmorphism-inspired interface.

=> Key Features
_____________________________________________________________________________________________________________________________________________________________________

*   Secure Administration: JWT-based authentication with role-based access control.
*   Comprehensive Student Management: Complete CRUD functionality for student profiles.
*   Attendance Tracking: Dynamic attendance marking with automated date handling and history viewing.
*   Academic Performance (Marks): Track labels and scores across multiple examinations (Mid-term, Final, etc.) with visual progress indicators.
*   Financial Management (Fees): Record tuition payments, track balances, and monitor financial status (Fully Paid vs. Partial).
*   Modern Reports: Generate on-demand data previews for students.
*   Premium UI: Fully responsive, glassmorphism-based design with smooth transitions and high readability.

=> Technology Stack
_______________________________________________________________________________________________________________________________________________________________________

*   Frontend: JavaScript, HTML5, CSS3.
*   Backend: Python
*   Database: MySQL.
  
 Project Structure
________________________________________________________________________________________________________________________________________________________________________
```text
SMS_PROJECT/
├── backend/            # Python Flask API & Configuration
│   ├── app.py          # Main application entry point
│   ├── auth.py         # Authentication logic (Login/Register)
│   ├── config.py       # Database connection handler (Env-ready)
│   ├── init_db.py      # Database schema initialization script
│   └── requirements.txt # Python dependencies
├── frontend/           # Vanilla JS/HTML/CSS Assets
│   ├── attendance.html # Attendance management UI
│   ├── marks.html      # Academic performance UI
│   ├── fees.html       # Financial management UI
│   ├── dashboard.html  # Main admin control panel
│   └── style.css       # Core design system
├── vercel.json         # Deployment config for Vercel
└── README.md           # Project documentation
```

 =>Local Installation

1. Prerequisite
- Python 3.8+ installed.
- MySQL Server installed and running.

2. Clone the repository
```bash
git clone <your-repo-url>
cd SMS_PROJECT
```

 3. Setup Database
Create a database named `student_management` in your MySQL server.
Then, run the initialization script:
```bash
python backend/init_db.py
```

 4. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

 5. Run the Application
```bash
python backend/app.py
```
Visit `http://127.0.0.1:5000` in your browser.

 Deployment
_________________________________________________________________________________________________________________________________________________________________________________
The project is prepared for deployment on modern cloud platforms:
- **Render + Free Cloud MySQL (TiDB / Aiven)**: Complete step-by-step instructions available in [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).
- **PythonAnywhere**: Recommended for integrated MySQL hosting.
- **Vercel**: Using serverless functions (configured via `vercel.json`).
- **Heroku**: Fully compatible with `Procfile` and Gunicorn.

#   S t u d e n t - M a n a g e m e n t - S y s t e m  