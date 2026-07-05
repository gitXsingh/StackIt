# StackIt - Minimal Q\&A Forum

A backend-first, lightweight Q\&A platform built during the Odoo Hackathon 2025. StackIt enables structured community-based learning by allowing users to ask and answer questions, vote on the best responses, and explore topics using tags — all through a clean, responsive UI and a custom backend.
Demonstration video : https://drive.google.com/file/d/16dIEGNnsE3SxQT64p0MbIwnqbskGrBE6/view?usp=drivesdk
<img width="1522" height="834" alt="image" src="https://github.com/user-attachments/assets/37621e7e-36d4-4856-af17-85239ed170f2" />
<img width="1920" height="975" alt="image" src="https://github.com/user-attachments/assets/4fcb8c7d-26a7-4d0a-bbbf-b34731acf5eb" />
<img width="3898" height="1893" alt="image" src="https://github.com/user-attachments/assets/5be7c296-abc5-4fa6-b418-d60054da7bca" />


---

## 🚀 Features

* **User Authentication** – Secure login and registration with hashed passwords
* **Question Posting** – Ask questions using a rich text editor and categorize them using tags
* **Answer System** – Post formatted answers, mark accepted responses
* **Voting** – Upvote/downvote answers to promote community consensus
* **Tag-Based Filtering** – Filter questions by topics/tags
* **Search Support** – Search through questions by title and content
* **Notifications** – Bell-style dropdown for recent activity (mocked)

---

## 🛠️ Tech Stack

* **Backend**: Flask (Python)
* **Database**: SQLite with SQLAlchemy ORM
* **Frontend**: HTML, CSS, Bootstrap 5, JavaScript
* **Editor**: Quill.js for rich text
* **Authentication**: Flask-Login, bcrypt for secure password hashing

---

## 📦 Installation

### Prerequisites

* Python 3.8+
* pip (Python package installer)

### Steps

```bash
# Clone and navigate
$ git clone https://github.com/gitXsingh/StackIt.git
$ cd StackIt

# Install dependencies
$ pip install -r requirements.txt

# Run the app
$ python app.py

# Open in browser
http://localhost:5000
```

---

## 🧩 Database Schema

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

## 🔌 API Overview

### Authentication

* `POST /register` – Create new user account
* `POST /login` – User login
* `GET /logout` – Logout user

### Questions

* `GET /api/questions` – List questions (optional tag or search filter)
* `POST /api/questions` – Create a question
* `GET /api/questions/<id>` – Retrieve question with answers

### Answers

* `POST /api/questions/<id>/answers` – Submit an answer
* `POST /api/answers/<id>/vote` – Upvote/downvote an answer
* `POST /api/answers/<id>/accept` – Accept an answer (owner only)

### Tags & Notifications

* `GET /api/tags` – Get all available tags
* `GET /api/notifications` – Retrieve user notifications
* `POST /api/notifications/<id>/read` – Mark notification as read

---

## 🎨 UI Highlights

* **Fully Responsive** – Built with Bootstrap for all screen sizes
* **Intuitive Layout** – Simple navbar, search bar, and tagging system
* **Rich Text Support** – Ask and answer with Quill-based formatting
* **Visual Tags** – Colored tags for better content discovery
* **Minimal Design** – Clean spacing, hover effects, and navigation

---

## 🔐 Security Features

* Password hashing with bcrypt
* CSRF protection via Flask-WTF
* Server-side and client-side input validation
* SQL Injection protection with SQLAlchemy ORM
* Session management using Flask-Login

---

## 📁 Project Structure

```
StackIt/
├── app.py               # Main application
├── requirements.txt     # Python dependencies
├── templates/           # HTML files
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   └── register.html
└── stackit.db           # Auto-generated SQLite database
```

---

## 🤝 Contributing

We welcome contributions!

1. Fork this repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request

---

## 📄 License

This project is open-sourced under the MIT License. Created for learning purposes and submission to Odoo Hackathon 2025.

---

**Built with ❤️ during the Odoo Hackathon 2025**
