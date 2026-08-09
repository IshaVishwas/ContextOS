from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)

def seed_db():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "dev@contextos.ai").first()
        if not user:
            # We map username to full_name since username is not in the schema
            user = User(
                email="dev@contextos.ai",
                full_name="developer",
                hashed_password=get_password_hash("dev"),
                is_active=True
            )
            db.add(user)
            db.commit()
            logger.info("Development user seeded successfully.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()
