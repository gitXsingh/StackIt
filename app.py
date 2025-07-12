from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stackit.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Data Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # guest, user, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    questions = db.relationship('Question', backref='author', lazy=True)
    answers = db.relationship('Answer', backref='author', lazy=True)
    votes = db.relationship('Vote', backref='user', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    answers = db.relationship('Answer', backref='question', lazy=True, cascade='all, delete-orphan')
    tags = db.relationship('QuestionTag', backref='question', lazy=True, cascade='all, delete-orphan')

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_accepted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    votes = db.relationship('Vote', backref='answer', lazy=True, cascade='all, delete-orphan')

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#007bff')  # Bootstrap primary color

class QuestionTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' or 'downvote'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('answer_id', 'user_id', name='unique_user_vote'),)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    questions = Question.query.order_by(Question.created_at.desc()).all()
    return render_template('index.html', questions=questions)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        if not all([name, email, password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return jsonify({'message': 'Registration successful'}), 201
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# API Routes
@app.route('/api/questions', methods=['GET'])
def get_questions():
    tag_filter = request.args.get('tag')
    questions_query = Question.query
    
    if tag_filter:
        questions_query = questions_query.join(QuestionTag).join(Tag).filter(Tag.name == tag_filter)
    
    questions = questions_query.order_by(Question.created_at.desc()).all()
    
    result = []
    for question in questions:
        question_data = {
            'id': question.id,
            'title': question.title,
            'description': question.description,
            'author': question.author.name,
            'created_at': question.created_at.isoformat(),
            'answers_count': len(question.answers),
            'tags': [tag.tag.name for tag in question.tags]
        }
        result.append(question_data)
    
    return jsonify(result)

@app.route('/api/questions', methods=['POST'])
@login_required
def create_question():
    data = request.get_json()
    
    title = data.get('title')
    description = data.get('description')
    tags = data.get('tags', [])
    
    if not title or not description:
        return jsonify({'error': 'Title and description are required'}), 400
    
    question = Question(
        title=title,
        description=description,
        user_id=current_user.id
    )
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
    return jsonify({'message': 'Question created successfully', 'id': question.id}), 201

@app.route('/api/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    question_data = {
        'id': question.id,
        'title': question.title,
        'description': question.description,
        'author': question.author.name,
        'created_at': question.created_at.isoformat(),
        'tags': [tag.tag.name for tag in question.tags],
        'answers': []
    }
    
    for answer in question.answers:
        votes_count = sum(1 for vote in answer.votes if vote.vote_type == 'upvote') - \
                     sum(1 for vote in answer.votes if vote.vote_type == 'downvote')
        
        answer_data = {
            'id': answer.id,
            'description': answer.description,
            'author': answer.author.name,
            'created_at': answer.created_at.isoformat(),
            'is_accepted': answer.is_accepted,
            'votes': votes_count
        }
        question_data['answers'].append(answer_data)
    
    return jsonify(question_data)

@app.route('/api/questions/<int:question_id>/answers', methods=['POST'])
@login_required
def create_answer(question_id):
    question = Question.query.get_or_404(question_id)
    data = request.get_json()
    
    description = data.get('description')
    if not description:
        return jsonify({'error': 'Answer description is required'}), 400
    
    answer = Answer(
        description=description,
        question_id=question_id,
        user_id=current_user.id
    )
    db.session.add(answer)
    db.session.commit()
    
    return jsonify({'message': 'Answer created successfully', 'id': answer.id}), 201

@app.route('/api/answers/<int:answer_id>/vote', methods=['POST'])
@login_required
def vote_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    data = request.get_json()
    
    vote_type = data.get('vote_type')  # 'upvote' or 'downvote'
    if vote_type not in ['upvote', 'downvote']:
        return jsonify({'error': 'Invalid vote type'}), 400
    
    # Check if user already voted
    existing_vote = Vote.query.filter_by(
        answer_id=answer_id, 
        user_id=current_user.id
    ).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # Remove vote if clicking same button
            db.session.delete(existing_vote)
        else:
            # Change vote type
            existing_vote.vote_type = vote_type
    else:
        # Create new vote
        vote = Vote(
            answer_id=answer_id,
            user_id=current_user.id,
            vote_type=vote_type
        )
        db.session.add(vote)
    
    db.session.commit()
    
    # Calculate new vote count
    votes_count = sum(1 for vote in answer.votes if vote.vote_type == 'upvote') - \
                 sum(1 for vote in answer.votes if vote.vote_type == 'downvote')
    
    return jsonify({'votes': votes_count})

@app.route('/api/answers/<int:answer_id>/accept', methods=['POST'])
@login_required
def accept_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    question = answer.question
    
    # Only question author can accept answers
    if question.user_id != current_user.id:
        return jsonify({'error': 'Only question author can accept answers'}), 403
    
    # Unaccept all other answers for this question
    Answer.query.filter_by(question_id=question.id).update({'is_accepted': False})
    
    # Accept this answer
    answer.is_accepted = True
    db.session.commit()
    
    return jsonify({'message': 'Answer accepted successfully'})

@app.route('/api/tags', methods=['GET'])
def get_tags():
    tags = Tag.query.all()
    return jsonify([{'id': tag.id, 'name': tag.name, 'color': tag.color} for tag in tags])

@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(10).all()
    return jsonify([{
        'id': notif.id,
        'message': notif.message,
        'is_read': notif.is_read,
        'created_at': notif.created_at.isoformat()
    } for notif in notifications])

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification.is_read = True
    db.session.commit()
    return jsonify({'message': 'Notification marked as read'})

# Initialize database and create default tags
@app.cli.command('init-db')
def init_db():
    db.create_all()
    
    # Create default tags
    default_tags = [
        'Python', 'JavaScript', 'Flask', 'React', 'Database', 
        'API', 'Frontend', 'Backend', 'DevOps', 'Testing'
    ]
    
    for tag_name in default_tags:
        if not Tag.query.filter_by(name=tag_name).first():
            tag = Tag(name=tag_name)
            db.session.add(tag)
    
    db.session.commit()
    print('Database initialized with default tags!')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 