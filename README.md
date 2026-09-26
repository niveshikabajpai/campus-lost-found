# CampusFind 🎓

CampusFind is a campus-based Lost & Found web application that helps students report, search, and manage lost and found items in one place.

🌐 **Live Demo:** https://campus-lost-found-9js3.onrender.com

## ✨ Features

* 🔐 User registration and login
* 📌 Report lost or found items
* 🔎 Search and filter reported items
* 📷 Upload images of items
* 👤 View your own reports
* ✏️ Edit and delete your reports
* ✅ Mark items as resolved
* 📩 Contact the reporter
* 📱 Responsive user interface

## 🛠️ Tech Stack

* **Frontend:** HTML, CSS
* **Backend:** Python, Flask
* **Database:** SQLite
* **Templating:** Jinja2
* **Authentication:** Werkzeug password hashing and Flask sessions
* **Version Control:** Git & GitHub
* **Deployment:** Render

## 📂 Project Structure

```text
campus-lost-found/
│
├── app.py
├── requirements.txt
├── .gitignore
├── database.db
│
├── static/
│   ├── style.css
│   └── uploads/
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── items.html
│   ├── report.html
│   ├── my_reports.html
│   ├── item_details.html
│   └── ...
│
└── screenshots/
    ├── home.png
    ├── find-items.png
    ├── reports.png
    └── my-reports.png
```

## 🚀 How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/niveshikabajpai/campus-lost-found.git
cd campus-lost-found
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python app.py
```

### 6. Open the application

Visit:

```text
http://127.0.0.1:5000
```

## 🎯 Purpose

CampusFind was created as a beginner-friendly web development project to make reporting and finding lost items easier within a campus environment.

The project also helped me gain practical experience with Flask routing, database operations, user authentication, file uploads, CRUD operations, Git/GitHub, and web deployment.

## 📸 Screenshots

### Home Page

![CampusFind Home Page](screenshots/home.png)

### Find Items

![Find Items Page](screenshots/find-items.png)

### Report an Item

![Report Item Page](screenshots/reports.png)

### My Reports

![My Reports Page](screenshots/my-reports.png)

## 🔮 Future Improvements

* Add email notifications for reporters
* Improve image validation
* Improve database persistence for production deployment
* Add an admin dashboard for managing reports
* Add more advanced search and filtering options

## 👩‍💻 Author

**Niveshika Bajpai**

GitHub: https://github.com/niveshikabajpai
