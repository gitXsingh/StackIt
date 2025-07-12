import pytest
import json
from app import app, db, User, Question, Answer, Tag, Vote, Notification
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def test_user():
    user = User(
        name='Test User',
        email='test@example.com',
        password_hash=generate_password_hash('password123')
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_tag():
    tag = Tag(name='Python', color='#007bff')
    db.session.add(tag)
    db.session.commit()
    return tag

def test_home_page(client):
    """Test home page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'StackIt' in response.data

def test_register_page(client):
    """Test registration page loads"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Join StackIt' in response.data

def test_login_page(client):
    """Test login page loads"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Welcome Back' in response.data

def test_user_registration(client):
    """Test user registration"""
    data = {
        'name': 'New User',
        'email': 'newuser@example.com',
        'password': 'password123'
    }
    response = client.post('/register', 
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 201
    
    # Check user was created
    user = User.query.filter_by(email='newuser@example.com').first()
    assert user is not None
    assert user.name == 'New User'

def test_user_login(client, test_user):
    """Test user login"""
    data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    response = client.post('/login',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 200

def test_invalid_login(client):
    """Test invalid login credentials"""
    data = {
        'email': 'wrong@example.com',
        'password': 'wrongpassword'
    }
    response = client.post('/login',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 401

def test_get_questions_api(client):
    """Test questions API endpoint"""
    response = client.get('/api/questions')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_get_tags_api(client, test_tag):
    """Test tags API endpoint"""
    response = client.get('/api/tags')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0

def test_create_question_unauthorized(client):
    """Test creating question without authentication"""
    data = {
        'title': 'Test Question',
        'description': 'Test question description',
        'tags': ['Python']
    }
    response = client.post('/api/questions',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 401

def test_validation_errors(client):
    """Test input validation"""
    # Test invalid email
    data = {
        'name': 'Test',
        'email': 'invalid-email',
        'password': 'password123'
    }
    response = client.post('/register',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 400
    
    # Test short password
    data = {
        'name': 'Test',
        'email': 'test@example.com',
        'password': '123'
    }
    response = client.post('/register',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 400

def test_error_handlers(client):
    """Test error handlers"""
    # Test 404
    response = client.get('/nonexistent')
    assert response.status_code == 404
    
    # Test invalid question ID
    response = client.get('/api/questions/999999')
    assert response.status_code == 404

def test_cache_functionality():
    """Test cache utilities"""
    from app import get_cached_data, set_cached_data
    
    # Test setting and getting cache
    set_cached_data('test_key', 'test_value')
    cached_value = get_cached_data('test_key')
    assert cached_value == 'test_value'
    
    # Test cache expiration
    cached_value = get_cached_data('test_key', ttl=0)
    assert cached_value is None

def test_validation_functions():
    """Test validation utility functions"""
    from app import validate_email, validate_password, ValidationError
    
    # Test valid email
    assert validate_email('test@example.com') == 'test@example.com'
    
    # Test invalid email
    with pytest.raises(ValidationError):
        validate_email('invalid-email')
    
    # Test valid password
    assert validate_password('password123') == 'password123'
    
    # Test short password
    with pytest.raises(ValidationError):
        validate_password('123')

def test_format_functions(test_user, test_tag):
    """Test data formatting functions"""
    from app import format_question_data, format_answer_data
    
    # Create test question
    question = Question(
        title='Test Question',
        description='Test description',
        user_id=test_user.id
    )
    db.session.add(question)
    db.session.commit()
    
    # Test question formatting
    formatted = format_question_data(question)
    assert 'id' in formatted
    assert 'title' in formatted
    assert 'author' in formatted
    assert formatted['title'] == 'Test Question'
    
    # Create test answer
    answer = Answer(
        description='Test answer',
        question_id=question.id,
        user_id=test_user.id
    )
    db.session.add(answer)
    db.session.commit()
    
    # Test answer formatting
    formatted = format_answer_data(answer)
    assert 'id' in formatted
    assert 'description' in formatted
    assert 'author' in formatted
    assert formatted['description'] == 'Test answer'

if __name__ == '__main__':
    pytest.main([__file__]) 