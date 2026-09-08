# 🚀 Complete Deployment Guide: Student Management System

This guide walks you through deploying your **Student Management System** to **Render** (free Python Web Service) connected to **TiDB Cloud Serverless** (free MySQL-compatible database).

---

## 📋 Architecture Overview

| Component | Platform | Plan | Cost |
| :--- | :--- | :--- | :--- |
| **Backend & Frontend** | [Render](https://render.com) Web Service | Free Tier | **$0 / month** |
| **MySQL Database** | [TiDB Cloud](https://tidbcloud.com) Serverless | Free (25 GB free forever) | **$0 / month** (No credit card required) |

---

## 🛠️ Step 1: Create Your Free MySQL Database (TiDB Cloud)

> [!TIP]
> TiDB Cloud Serverless is 100% MySQL-compatible, provides 25GB free forever, supports TLS/SSL, and does not require a credit card.

1. Go to **[https://tidbcloud.com](https://tidbcloud.com)** and sign up (or sign in with Google/GitHub).
2. On your dashboard, click **Create Cluster** (or **Create Database**).
3. Select **Serverless** (Free plan).
4. Leave region as default or choose the region closest to you, then click **Create**.
5. Once created, click **Connect**:
   - Choose connection method: **General** or **PyMySQL / Python**.
   - Note down the connection parameters:
     - **Host**: `gateway01.us-east-1.prod.aws.tidbcloud.com` (or similar)
     - **Port**: `4000`
     - **User**: `<prefix>.root`
     - **Password**: Your generated cluster password
     - **Database**: `test` (default database provided by TiDB)

---

## 🐙 Step 2: Push Project to GitHub

If you already have this code on GitHub, skip to **Step 3**. Otherwise:

### Option A: Using Git CLI
Open PowerShell in the project root:
```powershell
git init
git add .
git commit -m "Deploy Student Management System to Render"
git branch -M main
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>.git
git push -u origin main
```

### Option B: Using GitHub Desktop
1. Open **GitHub Desktop** → Click **Add Existing Repository** → Select this folder.
2. Publish repository to your GitHub account.

---

## 🌐 Step 3: Deploy to Render

1. Go to **[https://render.com](https://render.com)** and sign in with GitHub.
2. In the top right, click **New +** → select **Web Service**.
3. Under **Connect a repository**, select your `Student-Management-System` repository.
4. Fill in the service configuration:
   - **Name**: `student-management-system` (or your choice)
   - **Language / Environment**: `Python 3`
   - **Branch**: `main`
   - **Region**: Oregon (US West) or Frankfurt (choose nearest)
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     gunicorn index:handler --bind 0.0.0.0:$PORT
     ```
   - **Instance Type**: Select **Free** ($0/mo)

5. Scroll down to **Environment Variables** and click **Add Environment Variable** for each:

| Key | Example Value | Description |
| :--- | :--- | :--- |
| `DB_HOST` | `gateway01.us-east-1.prod.aws.tidbcloud.com` | Your TiDB Cloud host |
| `DB_PORT` | `4000` | Port (TiDB uses `4000`, standard MySQL uses `3306`) |
| `DB_USER` | `xxxx.root` | Your TiDB username |
| `DB_PASSWORD` | `your_tidb_password` | Your TiDB password |
| `DB_NAME` | `test` | Database name (e.g. `test` or `student_management`) |
| `DB_SSL` | `true` | Enables secure SSL/TLS connection |
| `AUTO_INIT_DB` | `true` | Auto-creates all tables and default admin on startup |
| `JWT_SECRET_KEY` | `super_secure_random_key_abc123` | Secret key for JWT session tokens |

6. Click **Deploy Web Service**.

---

## ⚡ Step 4: Verification & Login

1. Render will build and deploy your service (takes about 1–2 minutes).
2. Once the log says `Your service is live 🎉`, click the URL at the top (e.g., `https://student-management-system-xxxx.onrender.com`).
3. **Database Health Check**:
   - Visit `https://<your-app>.onrender.com/health` to confirm the database is connected (`"database_connected": true`).
   - If tables need to be re-initialized at any time, open `https://<your-app>.onrender.com/api/setup-db`.
4. **Log In**:
   - Navigate to the root URL: `https://<your-app>.onrender.com`
   - **Email**: `admin@gmail.com`
   - **Password**: `admin123`
5. You're live! You can now manage students, track attendance, add marks, and log fee payments directly from the web.

---

## ❓ Frequently Asked Questions & Troubleshooting

### Why is the initial page load slow on Render Free Tier?
Render's free tier spins down inactive instances after 15 minutes of inactivity. When a new visitor arrives, it takes around 30–50 seconds to "wake up". Subsequent requests will be fast.

### Can I use Aiven MySQL or Railway instead of TiDB Cloud?
**Yes!** The application supports any MySQL provider:
- **Aiven**: Set `DB_HOST`, `DB_PORT` (typically 10000+), `DB_USER` (`avnadmin`), `DB_PASSWORD`, `DB_NAME` (`defaultdb`), and `DB_SSL=true`.
- **Railway**: You can also use `DATABASE_URL` or `MYSQL_URL` as a single connection string variable.
