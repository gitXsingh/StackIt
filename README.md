# StackIt - Minimal Q&A Forum

A backend-first, lightweight Q&A platform for structured, community-based learning. Built for the Odoo Hackathon 2025.

## 🚀 Features

### ✅ Core Features
- **Authentication System** - Register/Login with secure password hashing
- **Question Management** - Create, view, and manage questions with rich text
- **Answer System** - Post answers with rich text editor (Quill.js)
- **Voting System** - Upvote/downvote answers
- **Tag System** - Categorize questions with tags and filter by them
- **Accept Answers** - Question authors can mark answers as accepted
- **Notifications** - Real-time notification system (optional/mocked)

### 🎯 Technical Stack
- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML/CSS + Bootstrap 5 + JavaScript
- **Rich Text**: Quill.js
- **Authentication**: Flask-Login with bcrypt
- **UI/UX**: Modern, responsive design with Bootstrap icons

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/gitXsingh/StackIt.git
   cd StackIt
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python app.py
   ```
   The database will be automatically created with default tags.

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and go to `http://localhost:5000`

## 📊 Database Schema

### Core Models
```sql
User(id, name, email, password_hash, role, created_at)
Question(id, title, description, user_id, created_at, updated_at)
Answer(id, question_id, user_id, description, is_accepted, created_at, updated_at)
Tag(id, name, color)
QuestionTag(id, question_id, tag_id)
Vote(id, answer_id, user_id, vote_type, created_at)
Notification(id, user_id, message, is_read, created_at)
```

## 🔌 API Endpoints

### Authentication
- `POST /register` - Create new user account
- `POST /login` - Authenticate user
- `GET /logout` - Logout user

### Questions
- `GET /api/questions` - Get all questions (with optional tag filter)
- `POST /api/questions` - Create new question
- `GET /api/questions/<id>` - Get specific question with answers

### Answers
- `POST /api/questions/<id>/answers` - Add answer to question
- `POST /api/answers/<id>/vote` - Vote on answer (upvote/downvote)
- `POST /api/answers/<id>/accept` - Accept answer (question author only)

### Tags & Notifications
- `GET /api/tags` - Get all available tags
- `GET /api/notifications` - Get user notifications
- `POST /api/notifications/<id>/read` - Mark notification as read

## 🎨 UI/UX Features

### Modern Design
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Bootstrap 5** - Modern CSS framework with components
- **Bootstrap Icons** - Clean, consistent iconography
- **Smooth Animations** - Hover effects and transitions
- **Color-coded Tags** - Visual categorization system

### User Experience
- **Real-time Search** - Filter questions by title/description
- **Tag Filtering** - Filter questions by tags
- **Rich Text Editor** - Quill.js for questions and answers
- **Voting System** - Intuitive upvote/downvote buttons
- **Notification System** - Bell icon with dropdown
- **Modal Dialogs** - Clean question/answer forms

## 🔒 Security Features

- **Password Hashing** - bcrypt for secure password storage
- **Input Validation** - Client and server-side validation
- **CSRF Protection** - Built-in Flask security
- **Session Management** - Flask-Login for user sessions
- **SQL Injection Protection** - SQLAlchemy ORM

## 🏆 Hackathon Compliance

### ✅ Requirements Met
- ✅ **No static JSON** - Real APIs and live database
- ✅ **Clean, responsive UI** - Bootstrap with good layout & spacing
- ✅ **Backend & DB Modeling** - Custom database + REST APIs
- ✅ **Input Validation** - Client + server-side validation
- ✅ **GitHub Used Properly** - Version control ready
- ✅ **No Firebase/Supabase** - Custom backend implementation
- ✅ **Demo Video Ready** - Working app with all features

### 🎯 Demo Features
- User registration and login
- Ask questions with rich text and tags
- Answer questions with rich text editor
- Vote on answers (upvote/downvote)
- Accept answers (question author only)
- Search and filter questions
- Notification system
- Responsive design on all devices

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. Set environment variables:
   ```bash
   export SECRET_KEY="your-secret-key-here"
   export FLASK_ENV="production"
   ```

2. Use a production WSGI server:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

## 📝 Project Structure

```
StackIt/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Home page with questions
│   ├── login.html        # Login page
│   └── register.html     # Registration page
└── stackit.db           # SQLite database (created on first run)
```

## 🤝 Contributing

This project was built for the Odoo Hackathon 2025. For contributions:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is built for educational purposes and the Odoo Hackathon 2025.

## 🎉 Acknowledgments

- **Odoo Hackathon 2025** - For the opportunity to build this project
- **Flask Community** - For the excellent web framework
- **Bootstrap Team** - For the responsive CSS framework
- **Quill.js** - For the rich text editor

---

**Built with ❤️ for the Odoo Hackathon 2025** 