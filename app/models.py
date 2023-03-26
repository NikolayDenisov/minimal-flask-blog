#!/usr/bin/python3

from datetime import datetime, timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from flask_login import UserMixin
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash

# JWT settings
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


from app import db


class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    username = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Posts', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Posts(db.Model):
    __tablename__ = 'posts'
    PER_PAGE = 5
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=1)
    tags = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f'<Post {self.body}>'


# User model
class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool = False

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

# Login form model
class Login(BaseModel):
    username: str
    password: str

# Authenticate user
def authenticate_user(username: str, password: str):
    if username not in users_db:
        return False
    user = users_db[username]
    if not pwd_context.verify(password, user["hashed_password"]):
        return False
    return User(**user)

# Create access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency to get current user from JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = users_db.get(username)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return User(**user)

# Login route
@app.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, token_type="bearer")


from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()

security = HTTPBearer()

@app.get('/protected')
async def protected_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # В этом месте можно проверить токен доступа и вернуть данные для аутентифицированного пользователя
    return {"message": "Hello, authenticated user!"}

