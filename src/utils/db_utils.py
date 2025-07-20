from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from src.utils.time_utils import get_current_ist_time

DATABASE_URL = "sqlite:///database/trading_service.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class LoginSession(Base):
    __tablename__ = 'login_sessions'
    api_key = Column(String, primary_key=True)
    access_token = Column(String, nullable=False)
    created_at = Column(DateTime, default=get_current_ist_time)


Base.metadata.create_all(engine)


def save_access_token(api_key, access_token):
    session = SessionLocal()
    login_entry = session.query(LoginSession).filter_by(api_key=api_key).first()
    if login_entry:
        login_entry.access_token = access_token
        login_entry.created_at = get_current_ist_time()
    else:
        login_entry = LoginSession(api_key=api_key, access_token=access_token)
        session.add(login_entry)
    session.commit()
    session.close()


def get_latest_access_token(api_key):
    session = SessionLocal()
    login_entry = session.query(LoginSession).filter_by(api_key=api_key).first()
    session.close()
    if login_entry:
        return login_entry.access_token
    return None
