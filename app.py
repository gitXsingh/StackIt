from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import re
from functools import wraps
from dotenv import load_dotenv
import click

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "dev-secret-key-change-in-production"
)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///stackit.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Cache for frequently accessed data
cache = {}


# Validation utilities
class ValidationError(Exception):
    pass


def validate_email(email):
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format")
    return email


def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        raise ValidationError("Password must be at least 6 characters long")
    return password


def validate_question_data(title, description, tags):
    """Validate question data"""
    if not title or len(title.strip()) < 10:
        raise ValidationError("Title must be at least 10 characters long")
    if not description or len(description.strip()) < 20:
        raise ValidationError("Description must be at least 20 characters long")
    if not isinstance(tags, list):
        raise ValidationError("Tags must be a list")
    return True


def validate_answer_data(description):
    """Validate answer data"""
    if not description or len(description.strip()) < 10:
        raise ValidationError("Answer must be at least 10 characters long")
    return True


# Error handling decorator
def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            app.logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({"error": "An unexpected error occurred"}), 500

    return decorated_function


# Cache utilities
def get_cached_data(key, ttl=300):
    """Get data from cache with TTL"""
    if key in cache:
        data, timestamp = cache[key]
        if datetime.now() - timestamp < timedelta(seconds=ttl):
            return data
        else:
            del cache[key]
    return None


def set_cached_data(key, data):
    """Set data in cache with timestamp"""
    cache[key] = (data, datetime.now())


# Data Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")  # guest, user, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship("Question", backref="author", lazy=True)
    answers = db.relationship("Answer", backref="author", lazy=True)
    votes = db.relationship("Vote", backref="user", lazy=True)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    answers = db.relationship(
        "Answer", backref="question", lazy=True, cascade="all, delete-orphan"
    )
    tags = db.relationship(
        "QuestionTag", backref="question", lazy=True, cascade="all, delete-orphan"
    )


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    is_accepted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    votes = db.relationship(
        "Vote", backref="answer", lazy=True, cascade="all, delete-orphan"
    )


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), default="#007bff")  # Bootstrap primary color


class QuestionTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"), nullable=False)


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer_id = db.Column(db.Integer, db.ForeignKey("answer.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' or 'downvote'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("answer_id", "user_id", name="unique_user_vote"),
    )


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Utility functions for reusable components
def create_notification(user_id, message):
    """Create a notification for a user"""
    notification = Notification(user_id=user_id, message=message)
    db.session.add(notification)
    db.session.commit()
    return notification


def calculate_vote_count(answer):
    """Calculate vote count for an answer"""
    upvotes = sum(1 for vote in answer.votes if vote.vote_type == "upvote")
    downvotes = sum(1 for vote in answer.votes if vote.vote_type == "downvote")
    return upvotes - downvotes


def format_question_data(question):
    """Format question data for API response"""
    return {
        "id": question.id,
        "title": question.title,
        "description": question.description,
        "author": question.author.name,
        "created_at": question.created_at.isoformat(),
        "answers_count": len(question.answers),
        "tags": [tag.tag.name for tag in question.tags],
    }


def format_answer_data(answer):
    """Format answer data for API response"""
    return {
        "id": answer.id,
        "description": answer.description,
        "author": answer.author.name,
        "created_at": answer.created_at.isoformat(),
        "is_accepted": answer.is_accepted,
        "votes": calculate_vote_count(answer),
    }


# Role-based permission decorators
def require_role(required_role):
    """Decorator to require specific user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if required_role == 'guest':
                    return f(*args, **kwargs)
                return jsonify({'error': 'Login required'}), 401
            
            user_role = getattr(current_user, 'role', 'user')
            role_hierarchy = {'guest': 0, 'user': 1, 'admin': 2}
            
            if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 0):
                return jsonify({'error': 'Insufficient permissions'}), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def guest_access(f):
    """Allow guest access (view only)"""
    return require_role('guest')(f)

def user_access(f):
    """Require user role or higher"""
    return require_role('user')(f)

def admin_access(f):
    """Require admin role"""
    return require_role('admin')(f)


# Routes
@app.route("/")
def index():
    ensure_database_initialized()
    questions = Question.query.order_by(Question.created_at.desc()).all()
    return render_template("index.html", questions=questions)


@app.route("/register", methods=["GET", "POST"])
@handle_errors
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        # Validation
        if not name or len(name) < 2:
            raise ValidationError("Name must be at least 2 characters long")
        validate_email(email)
        validate_password(password)

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            raise ValidationError("Email already registered")

        # Check if this is the first user (make them admin)
        is_first_user = User.query.count() == 0
        user_role = "admin" if is_first_user else "user"

        # Create user
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=user_role
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
@handle_errors
def login():
    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form

        email = data.get("email", "").strip()
        password = data.get("password", "")

        if not email or not password:
            raise ValidationError("Email and password are required")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/ask", methods=["GET", "POST"])
@login_required
@handle_errors
def ask_question():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        tags = request.form.getlist("tags")
        validate_question_data(title, description, tags)
        question = Question(
            title=title, description=description, user_id=current_user.id
        )
        db.session.add(question)
        db.session.flush()
        for tag_name in tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
                db.session.flush()
            question_tag = QuestionTag(question_id=question.id, tag_id=tag.id)
            db.session.add(question_tag)
        db.session.commit()
        cache.clear()
        create_notification(1, f"New question posted: {title}")
        flash("Question posted successfully!", "success")
        return redirect(url_for("index"))
    tags = Tag.query.all()
    return render_template("ask.html", tags=tags)


@app.route("/question/<int:question_id>")
def question_detail(question_id):
    question = Question.query.get_or_404(question_id)
    answers = (
        Answer.query.filter_by(question_id=question_id)
        .order_by(Answer.created_at.asc())
        .all()
    )
    return render_template("question_detail.html", question=question, answers=answers)


# API Routes
@app.route("/api/questions", methods=["GET"])
@guest_access
@handle_errors
def get_questions():
    ensure_database_initialized()
    # Check cache first
    cache_key = f"questions_{request.args.get('tag', 'all')}"
    cached_data = get_cached_data(cache_key, ttl=60)
    if cached_data:
        return jsonify(cached_data)

    tag_filter = request.args.get("tag")
    questions_query = Question.query

    if tag_filter:
        questions_query = (
            questions_query.join(QuestionTag).join(Tag).filter(Tag.name == tag_filter)
        )

    questions = questions_query.order_by(Question.created_at.desc()).all()

    result = [format_question_data(question) for question in questions]

    # Cache the result
    set_cached_data(cache_key, result)

    return jsonify(result)


@app.route("/api/questions", methods=["POST"])
@user_access
@handle_errors
def create_question():
    data = request.get_json()

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    tags = data.get("tags", [])

    # Validation
    validate_question_data(title, description, tags)

    question = Question(title=title, description=description, user_id=current_user.id)
    db.session.add(question)
    db.session.flush()  # Get the question ID

    # Add tags
    for tag_name in tags:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
            db.session.flush()

        question_tag = QuestionTag(question_id=question.id, tag_id=tag.id)
        db.session.add(question_tag)

    db.session.commit()

    # Clear cache
    cache.clear()

    # Create notification for other users
    create_notification(1, f"New question posted: {title}")

    return jsonify({"message": "Question created successfully", "id": question.id}), 201


@app.route("/api/questions/<int:question_id>", methods=["GET"])
@handle_errors
def get_question(question_id):
    question = Question.query.get_or_404(question_id)

    question_data = {
        "id": question.id,
        "title": question.title,
        "description": question.description,
        "author": question.author.name,
        "created_at": question.created_at.isoformat(),
        "tags": [tag.tag.name for tag in question.tags],
        "answers": [format_answer_data(answer) for answer in question.answers],
    }

    return jsonify(question_data)


@app.route("/api/questions/<int:question_id>/answers", methods=["POST"])
@user_access
@handle_errors
def create_answer(question_id):
    """Create a new answer for a question"""
    question = Question.query.get_or_404(question_id)
    
    # Handle both JSON and form data
    if request.is_json:
        description = request.json.get("description", "").strip()
    else:
        description = request.form.get("description", "").strip()

    validate_answer_data(description)

    answer = Answer(
        description=description,
        question_id=question_id,
        user_id=current_user.id
    )
    db.session.add(answer)
    db.session.commit()

    # Create notification for question author
    if question.user_id != current_user.id:
        create_notification(
            question.user_id,
            f"New answer on your question: {question.title}"
        )

    return jsonify({"message": "Answer posted successfully", "answer_id": answer.id})


@app.route("/answer/<int:answer_id>/vote", methods=["POST"])
@user_access
@handle_errors
def vote_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    vote_type = request.form.get("vote_type")
    if vote_type not in ["upvote", "downvote"]:
        raise ValidationError("Invalid vote type")
    existing_vote = Vote.query.filter_by(
        answer_id=answer_id, user_id=current_user.id
    ).first()
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            db.session.delete(existing_vote)
        else:
            existing_vote.vote_type = vote_type
    else:
        vote = Vote(answer_id=answer_id, user_id=current_user.id, vote_type=vote_type)
        db.session.add(vote)
    db.session.commit()
    return redirect(request.referrer or url_for("index"))


@app.route("/api/answers/<int:answer_id>/accept", methods=["POST"])
@user_access
@handle_errors
def accept_answer(answer_id):
    question = Answer.query.get_or_404(answer_id).question

    # Only question author can accept answers
    if question.user_id != current_user.id:
        return jsonify({"error": "Only question author can accept answers"}), 403

    # Unaccept all other answers for this question
    Answer.query.filter_by(question_id=question.id).update({"is_accepted": False})

    # Accept this answer
    Answer.query.get_or_404(answer_id).is_accepted = True
    db.session.commit()

    # Create notification for answer author
    if Answer.query.get_or_404(answer_id).user_id != current_user.id:
        create_notification(
            Answer.query.get_or_404(answer_id).user_id,
            f"Your answer was accepted for: {question.title}",
        )

    return jsonify({"message": "Answer accepted successfully"})


@app.route("/api/tags", methods=["GET"])
@handle_errors
def get_tags():
    ensure_database_initialized()
    # Check cache
    cached_tags = get_cached_data("tags", ttl=300)
    if cached_tags:
        return jsonify(cached_tags)

    tags = Tag.query.all()
    result = [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in tags]

    # Cache the result
    set_cached_data("tags", result)

    return jsonify(result)


@app.route("/api/notifications", methods=["GET"])
@login_required
@handle_errors
def get_notifications():
    notifications = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(10)
        .all()
    )
    return jsonify(
        [
            {
                "id": notif.id,
                "message": notif.message,
                "is_read": notif.is_read,
                "created_at": notif.created_at.isoformat(),
            }
            for notif in notifications
        ]
    )


@app.route("/api/notifications/<int:notification_id>/read", methods=["POST"])
@login_required
@handle_errors
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    notification.is_read = True
    db.session.commit()
    return jsonify({"message": "Notification marked as read"})


@app.route("/api/notifications/mark_all_read", methods=["POST"])
@login_required
@handle_errors
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update(
        {"is_read": True}
    )
    db.session.commit()
    return jsonify({"message": "All notifications marked as read"})


# Add admin-only routes for content moderation
@app.route("/api/admin/questions/<int:question_id>/delete", methods=["DELETE"])
@admin_access
@handle_errors
def delete_question(question_id):
    """Admin: Delete a question"""
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return jsonify({"message": "Question deleted successfully"})

@app.route("/api/admin/answers/<int:answer_id>/delete", methods=["DELETE"])
@admin_access
@handle_errors
def delete_answer(answer_id):
    """Admin: Delete an answer"""
    answer = Answer.query.get_or_404(answer_id)
    db.session.delete(answer)
    db.session.commit()
    return jsonify({"message": "Answer deleted successfully"})

@app.route("/api/admin/users/<int:user_id>/role", methods=["PUT"])
@admin_access
@handle_errors
def update_user_role(user_id):
    """Admin: Update user role"""
    user = User.query.get_or_404(user_id)
    new_role = request.json.get('role')
    
    if new_role not in ['guest', 'user', 'admin']:
        raise ValidationError('Invalid role')
    
    user.role = new_role
    db.session.commit()
    return jsonify({"message": f"User role updated to {new_role}"})


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500


# Initialize database and create default tags
@app.cli.command("init-db")
def init_db():
    """Initialize the database with tables and sample data"""
    db.create_all()

    # Create sample tags if they don't exist
    default_tags = [
        {"name": "Python", "color": "#3776ab"},
        {"name": "JavaScript", "color": "#f7df1e"},
        {"name": "Flask", "color": "#000000"},
        {"name": "React", "color": "#61dafb"},
        {"name": "Database", "color": "#336791"},
        {"name": "API", "color": "#ff6b35"},
        {"name": "Frontend", "color": "#e34c26"},
        {"name": "Backend", "color": "#68217a"},
    ]

    for tag_data in default_tags:
        if not Tag.query.filter_by(name=tag_data["name"]).first():
            tag = Tag(name=tag_data["name"], color=tag_data["color"])
            db.session.add(tag)

    db.session.commit()
    print("Database initialized successfully!")


@app.cli.command("make-admin")
@click.argument("email")
def make_admin(email):
    """Make a user admin by email address"""
    user = User.query.filter_by(email=email).first()
    if not user:
        print(f"User with email {email} not found")
        return
    
    user.role = "admin"
    db.session.commit()
    print(f"User {user.name} ({email}) is now an admin!")


@app.cli.command("list-users")
def list_users():
    """List all users and their roles"""
    users = User.query.all()
    if not users:
        print("No users found")
        return
    
    print("Users:")
    for user in users:
        print(f"- {user.name} ({user.email}) - Role: {user.role}")


# Initialize database on startup
def init_database():
    """Initialize database tables and default data"""
    try:
        print("Starting database initialization...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Create default tags if they don't exist
        default_tags = [
            {"name": "Python", "color": "#3776ab"},
            {"name": "JavaScript", "color": "#f7df1e"},
            {"name": "Flask", "color": "#000000"},
            {"name": "React", "color": "#61dafb"},
            {"name": "Database", "color": "#336791"},
            {"name": "API", "color": "#ff6b35"},
            {"name": "Frontend", "color": "#e34c26"},
            {"name": "Backend", "color": "#68217a"},
        ]

        for tag_data in default_tags:
            if not Tag.query.filter_by(name=tag_data["name"]).first():
                tag = Tag(name=tag_data["name"], color=tag_data["color"])
                db.session.add(tag)
                print(f"Added tag: {tag_data['name']}")

        db.session.commit()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()

# Function to ensure database is initialized before handling requests
def ensure_database_initialized():
    """Ensure database is initialized before handling requests"""
    try:
        # Try to query a table to check if it exists
        Question.query.first()
    except Exception as e:
        print(f"Database not initialized, initializing now: {e}")
        init_database()

# Initialize database when the app starts
with app.app_context():
    init_database()

if __name__ == "__main__":
    app.run(debug=True)
