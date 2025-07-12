# **StackIt – Minimalistic Q\&A Platform**

A backend-centric, lightweight Q\&A application designed to foster structured, community-driven knowledge sharing. Developed as part of **Odoo Hackathon 2025**.

---

## 🚀 **Key Features**

### ✅ **Core Functionality**

* **User Authentication** – Secure registration and login with bcrypt-based password hashing
* **Question Management** – Post, view, and manage questions with rich-text formatting
* **Answer System** – Provide answers using a modern WYSIWYG editor (Quill.js)
* **Voting Mechanism** – Upvote/downvote answers to promote helpful content
* **Tagging Support** – Categorize and filter questions with color-coded tags
* **Answer Acceptance** – Mark the most helpful answer as accepted
* **Notifications** – (Optional) Real-time updates for user interactions

---

## ⚙️ **Technology Stack**

* **Backend**: Flask (Python)
* **Database**: SQLite + SQLAlchemy ORM
* **Frontend**: HTML, CSS, Bootstrap 5, JavaScript
* **Rich Text Editor**: Quill.js
* **Authentication**: Flask-Login + bcrypt
* **Icons & UI**: Bootstrap Icons + responsive layouts

---

## 🛠️ **Setup & Installation**

### Prerequisites

* Python 3.8+
* pip package manager

### Quick Start

```bash
# Clone the repository
git clone https://github.com/gitXsingh/StackIt.git
cd StackIt

# Install dependencies
pip install -r requirements.txt

# Initialize database and run app
python app.py
```

Visit: `http://localhost:5000` in your browser.

---

## 📚 **Database Schema**

```sql
User(id, name, email, password_hash, role, created_at)
Question(id, title, description, user_id, created_at, updated_at)
Answer(id, question_id, user_id, description, is_accepted, created_at, updated_at)
Tag(id, name, color)
QuestionTag(id, question_id, tag_id)
Vote(id, answer_id, user_id, vote_type, created_at)
Notification(id, user_id, message, is_read, created_at)
```

---

## 🔌 **API Overview**

### **Authentication**

* `POST /register` – Register a new user
* `POST /login` – Log in with credentials
* `GET /logout` – Log out current session

### **Questions**

* `GET /api/questions` – Retrieve all questions (filterable by tag)
* `POST /api/questions` – Create a new question
* `GET /api/questions/<id>` – View specific question with answers

### **Answers**

* `POST /api/questions/<id>/answers` – Add answer to question
* `POST /api/answers/<id>/vote` – Vote (up/down) on an answer
* `POST /api/answers/<id>/accept` – Mark answer as accepted

### **Tags & Notifications**

* `GET /api/tags` – List all tags
* `GET /api/notifications` – Retrieve user notifications
* `POST /api/notifications/<id>/read` – Mark a notification as read

---

## 🎨 **UI/UX Highlights**

* **Responsive Design** – Optimized for desktop, tablet, and mobile
* **Interactive UI** – Smooth animations, transitions, and modal dialogs
* **Tag System** – Color-coded tags for intuitive navigation
* **Search & Filter** – Quickly locate questions by keywords or tags
* **Notification Bell** – Dropdown with real-time alerts
* **Rich Text Input** – Quill.js editor for both questions and answers

---

## 🔐 **Security Features**

* **Secure Password Storage** – bcrypt-based hashing
* **Form Validation** – Client-side and server-side validation
* **CSRF Protection** – Native Flask integration
* **Session Management** – Powered by Flask-Login
* **SQL Injection Defense** – SQLAlchemy ORM encapsulation

---

## 🏁 **Hackathon Readiness Checklist**

* ✅ Fully functional backend (no static JSON)
* ✅ Responsive and accessible UI
* ✅ REST API integration with DB modeling
* ✅ Robust input validations
* ✅ Source controlled via GitHub
* ✅ No third-party BaaS (Firebase/Supabase)
* ✅ Complete working demo and video

---

## 🚀 **Deployment Instructions**

### For Local Development

```bash
python app.py
```

### For Production

```bash
# Set environment variables
export SECRET_KEY="your-secret-key"
export FLASK_ENV="production"

# Start with Gunicorn (production-ready server)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📁 **Project Structure**

```
StackIt/
├── app.py               # Main Flask application
├── requirements.txt     # Dependency file
├── README.md            # Project documentation
├── templates/           # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   └── register.html
└── stackit.db           # SQLite DB (auto-generated)
```

---

## 🤝 **Contributing**

Interested in contributing? Follow these steps:

1. Fork the repository
2. Create a new feature branch
3. Commit and push your changes
4. Submit a pull request

---

## 📜 **License**

This project is open-source and developed solely for academic and hackathon purposes during Odoo Hackathon 2025.

---

## 🙏 **Acknowledgments**

* **Odoo Hackathon 2025** – For fostering innovation
* **Flask & Python Community** – For a powerful development stack
* **Bootstrap** – For responsive UI design
* **Quill.js** – For enabling rich text interactions

---

**Built with ❤️ for the Odoo Hackathon 2025** 
