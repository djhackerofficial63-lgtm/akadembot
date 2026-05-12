from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import DATABASE_URL
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

# ============ MODELS ============

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    language = Column(String(10), default="uz")
    first_doc_used = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.telegram_id} - {self.first_name}>"

class Document(Base):
    """Document model"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.telegram_id"))
    doc_type = Column(String(50))  # referat, kurs, maqola, slide
    template_style = Column(String(50))  # apa, harvard, uzbek
    title = Column(String(255))
    content = Column(Text)
    file_path = Column(String(500))
    file_size = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="documents")
    
    def __repr__(self):
        return f"<Document {self.id} - {self.title}>"

class Payment(Base):
    """Payment model"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.telegram_id"))
    amount = Column(Float)
    currency = Column(String(10))  # UZS, USD
    status = Column(String(50))  # pending, success, failed, cancelled
    gateway = Column(String(50))  # click, payme
    transaction_id = Column(String(255), unique=True, nullable=True)
    merchant_trans_id = Column(String(255), nullable=True)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment {self.id} - {self.status}>"

class AdminLog(Base):
    """Admin action logs"""
    __tablename__ = "admin_logs"
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer)
    action = Column(String(255))
    target_user_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AdminLog {self.id} - {self.action}>"

# ============ DATABASE FUNCTIONS ============

def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(engine)
    logger.info("✅ Database initialized")

def get_session():
    """Get database session"""
    return SessionLocal()

def create_user(telegram_id, username=None, first_name=None, language="uz"):
    """Create new user"""
    session = get_session()
    try:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            language=language,
            created_at=datetime.utcnow()
        )
        session.add(user)
        session.commit()
        logger.info(f"✅ User created: {telegram_id}")
        return user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        session.rollback()
        return None
    finally:
        session.close()

def get_user(telegram_id):
    """Get user by telegram_id"""
    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        return user
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None
    finally:
        session.close()

def get_all_users():
    """Get all users"""
    session = get_session()
    try:
        users = session.query(User).all()
        return users
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return []
    finally:
        session.close()

def get_user_documents(user_id, limit=None):
    """Get user's documents"""
    session = get_session()
    try:
        query = session.query(Document).filter_by(user_id=user_id).order_by(Document.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        return []
    finally:
        session.close()

def save_document(user_id, doc_type, style, title, content, file_path):
    """Save document to database"""
    session = get_session()
    try:
        document = Document(
            user_id=user_id,
            doc_type=doc_type,
            template_style=style,
            title=title,
            content=content,
            file_path=file_path,
            created_at=datetime.utcnow()
        )
        session.add(document)
        session.commit()
        logger.info(f"✅ Document saved: {title}")
        return document
    except Exception as e:
        logger.error(f"Error saving document: {e}")
        session.rollback()
        return None
    finally:
        session.close()

def save_payment(user_id, amount, currency, gateway, status="pending", transaction_id=None):
    """Save payment record"""
    session = get_session()
    try:
        payment = Payment(
            user_id=user_id,
            amount=amount,
            currency=currency,
            gateway=gateway,
            status=status,
            transaction_id=transaction_id,
            created_at=datetime.utcnow()
        )
        session.add(payment)
        session.commit()
        logger.info(f"✅ Payment saved: {payment.id}")
        return payment
    except Exception as e:
        logger.error(f"Error saving payment: {e}")
        session.rollback()
        return None
    finally:
        session.close()

def update_payment_status(payment_id, status, transaction_id=None):
    """Update payment status"""
    session = get_session()
    try:
        payment = session.query(Payment).filter_by(id=payment_id).first()
        if payment:
            payment.status = status
            if transaction_id:
                payment.transaction_id = transaction_id
            if status == "success":
                payment.completed_at = datetime.utcnow()
                # Mark first doc as used for user
                user = session.query(User).filter_by(telegram_id=payment.user_id).first()
                if user:
                    user.first_doc_used = True
            session.commit()
            logger.info(f"✅ Payment updated: {payment_id} -> {status}")
            return payment
    except Exception as e:
        logger.error(f"Error updating payment: {e}")
        session.rollback()
        return None
    finally:
        session.close()

def get_user_payments(user_id):
    """Get user's payments"""
    session = get_session()
    try:
        payments = session.query(Payment).filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()
        return payments
    except Exception as e:
        logger.error(f"Error getting payments: {e}")
        return []
    finally:
        session.close()

def get_statistics():
    """Get bot statistics"""
    session = get_session()
    try:
        stats = {
            "total_users": session.query(User).count(),
            "total_documents": session.query(Document).count(),
            "total_payments": session.query(Payment).count(),
            "successful_payments": session.query(Payment).filter_by(status="success").count(),
            "total_revenue_uzs": session.query(Payment).filter_by(currency="UZS", status="success").all(),
            "total_revenue_usd": session.query(Payment).filter_by(currency="USD", status="success").all(),
        }
        return stats
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return None
    finally:
        session.close()

def block_user(user_id):
    """Block user"""
    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if user:
            user.is_blocked = True
            session.commit()
            logger.info(f"✅ User blocked: {user_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error blocking user: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def unblock_user(user_id):
    """Unblock user"""
    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if user:
            user.is_blocked = False
            session.commit()
            logger.info(f"✅ User unblocked: {user_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error unblocking user: {e}")
        session.rollback()
        return False
    finally:
        session.close()
