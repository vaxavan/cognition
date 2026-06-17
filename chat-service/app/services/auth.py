import os
import random
import string
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.utils.security import hash_password, verify_password

load_dotenv()

codes_store = {}

def _generate_code() -> str:
    return ''.join(random.choices(string.digits, k=6))

def _store_code(email: str, code: str):
    codes_store[email] = (code, datetime.now() + timedelta(minutes=5))

def _send_email(email: str, code: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_user or not smtp_password:
        print(f"[DEV] Code for {email}: {code}")
        return
    
    msg = MIMEText(f"""
    <h2>Код подтверждения Cognition</h2>
    <p>Ваш код: <strong>{code}</strong></p>
    <p>Действителен 5 минут.</p>
    """, "html")
    
    msg["Subject"] = "Код подтверждения Cognition"
    msg["From"] = smtp_user
    msg["To"] = email
    
    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        print(f"[EMAIL] Code sent to {email}")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        print(f"[DEV] Code for {email}: {code}")

def send_verification_code(email: str) -> str:
    code = _generate_code()
    _send_email(email, code)
    _store_code(email, code)
    return code

def verify_code(email: str, code: str) -> bool:
    stored = codes_store.get(email)
    if not stored:
        return False
    stored_code, expires = stored
    if datetime.now() > expires:
        del codes_store[email]
        return False
    if stored_code != code:
        return False
    del codes_store[email]
    return True

async def get_or_create_user(db: AsyncSession, email: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if user:
        if not verify_password(password, user.hashed_password):
            return None
        return user
    else:
        user = User(email=email, hashed_password=hash_password(password))
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user