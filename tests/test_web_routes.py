import pytest
import os
from unittest.mock import patch, AsyncMock, MagicMock
from flask import Flask, session
from werkzeug.security import generate_password_hash
from app.web.routes.auth import auth_bp
from app.web.routes.dialogs import dialogs_bp
from app.database.models import Manager, User, Dialog

@pytest.fixture
def app():
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'web', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'web', 'static'))
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['TESTING'] = True
    app.register_blueprint(auth_bp)
    app.register_blueprint(dialogs_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_login_page_get(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_login_success(client):
    mock_manager = Manager(
        id=1,
        username='admin',
        password_hash=generate_password_hash('password123')
    )
    
    with patch('app.web.routes.auth.get_manager_by_username', return_value=mock_manager):
        with patch('app.web.routes.auth.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            response = client.post('/login', data={
                'username': 'admin',
                'password': 'password123'
            }, follow_redirects=False)
            
            assert response.status_code == 302
            assert '/login' not in response.location

def test_login_failure(client):
    with patch('app.web.routes.auth.get_manager_by_username', return_value=None):
        with patch('app.web.routes.auth.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            response = client.post('/login', data={
                'username': 'admin',
                'password': 'wrongpassword'
            })
            
            assert response.status_code == 200
            assert 'Неверные учетные данные' in response.data.decode()

def test_logout(client):
    with client.session_transaction() as sess:
        sess['manager'] = 'admin'
    
    response = client.get('/logout', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location

def test_dashboard_requires_login(client):
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location

def test_dashboard_with_login(client):
    mock_dialogs = []
    
    with patch('app.web.routes.dialogs.get_all_dialogs', return_value=mock_dialogs):
        with patch('app.web.routes.dialogs.async_session_maker') as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            with client.session_transaction() as sess:
                sess['manager'] = 'admin'
            
            response = client.get('/')
            assert response.status_code == 200

def test_dialog_view_requires_login(client):
    response = client.get('/dialog/1', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location

def test_send_reply_requires_login(client):
    response = client.post('/dialog/1/reply', 
                          json={'text': 'Test reply'},
                          follow_redirects=False)
    assert response.status_code == 302

def test_change_status_requires_login(client):
    response = client.post('/dialog/1/status',
                          json={'status': 'закрыто'},
                          follow_redirects=False)
    assert response.status_code == 302