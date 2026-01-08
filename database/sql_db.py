from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Create SQLite database
DATABASE_URL = "sqlite:///./data/ecommerce.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Base class for models
Base = declarative_base()

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ===== MODELS (Tables) =====

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    
    # Relationship: One user can have many orders
    orders = relationship("Order", back_populates="user")


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)  # e.g., "Shipped", "Delivered"
    total_amount = Column(Float, nullable=False)
    tracking_number = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_name = Column(String, nullable=False)
    product_id = Column(String, nullable=False)  # Links to vector DB
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    
    # Relationship
    order = relationship("Order", back_populates="items")


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False, index=True)
    user_email = Column(String, nullable=True)  # Optional for future auth
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(String, nullable=False)
    intent = Column(String, nullable=True)  # Store detected intent
    data_source = Column(String, nullable=True)  # SQL, VECTOR, HYBRID
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    conversation = relationship("Conversation", back_populates="messages")


# ===== DATABASE FUNCTIONS =====

def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created!")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def populate_sample_data():
    """Insert sample data for testing"""
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(User).count() > 0:
        print("⚠️ Sample data already exists!")
        db.close()
        return
    
    # Create sample users
    user1 = User(name="John Doe", email="john@example.com", phone="+1234567890")
    user2 = User(name="Jane Smith", email="jane@example.com", phone="+0987654321")
    
    db.add_all([user1, user2])
    db.commit()
    
    # Create sample orders
    order1 = Order(
        user_id=user1.id,
        order_date=datetime(2024, 11, 15),
        status="Delivered",
        total_amount=1299.99,
        tracking_number="TRACK123456"
    )
    
    order2 = Order(
        user_id=user1.id,
        order_date=datetime(2024, 12, 10),
        status="Shipped",
        total_amount=899.99,
        tracking_number="TRACK789012"
    )
    
    order3 = Order(
        user_id=user2.id,
        order_date=datetime(2024, 12, 5),
        status="Processing",
        total_amount=599.99,
        tracking_number="TRACK345678"
    )
    
    db.add_all([order1, order2, order3])
    db.commit()
    
    # Create order items
    item1 = OrderItem(
        order_id=order1.id,
        product_name="Samsung Galaxy S23 Ultra",
        product_id="PROD001",
        quantity=1,
        price=1199.99
    )
    
    item2 = OrderItem(
        order_id=order2.id,
        product_name="Sony WH-1000XM5 Headphones",
        product_id="PROD003",
        quantity=1,
        price=399.99
    )
    
    item3 = OrderItem(
        order_id=order2.id,
        product_name="Apple iPad Pro 12.9-inch (M2)",
        product_id="PROD005",
        quantity=1,
        price=1099.99
    )
    
    item4 = OrderItem(
        order_id=order3.id,
        product_name="Dell XPS 15",
        product_id="PROD008",
        quantity=1,
        price=1799.99
    )
    
    db.add_all([item1, item2, item3, item4])
    db.commit()
    
    print("✅ Sample data inserted!")
    db.close()


# ===== QUERY FUNCTIONS =====

def get_user_orders(user_email: str):
    """Get all orders for a user"""
    from sqlalchemy.orm import joinedload
    
    db = SessionLocal()
    user = db.query(User).filter(User.email == user_email).first()
    
    if not user:
        db.close()
        return None
    
    orders = db.query(Order)\
               .options(joinedload(Order.items))\
               .filter(Order.user_id == user.id)\
               .all()
    
    # Access items to load them into memory
    for order in orders:
        _ = order.items
    
    db.close()
    return orders


def get_order_by_tracking(tracking_number: str):
    """Get order details by tracking number"""
    from sqlalchemy.orm import joinedload
    
    db = SessionLocal()
    order = db.query(Order)\
              .options(joinedload(Order.items))\
              .filter(Order.tracking_number == tracking_number)\
              .first()
    
    if order:
        # Access items while session is still open
        _ = order.items  # This loads the items
    
    db.close()
    return order


def get_recent_order_products(user_email: str):
    """Get product IDs from user's recent orders"""
    db = SessionLocal()
    user = db.query(User).filter(User.email == user_email).first()
    
    if not user:
        db.close()
        return []
    
    # Get user's most recent order
    recent_order = db.query(Order).filter(Order.user_id == user.id)\
                                   .order_by(Order.order_date.desc())\
                                   .first()
    
    if not recent_order:
        db.close()
        return []
    
    # Get all items from that order
    items = db.query(OrderItem).filter(OrderItem.order_id == recent_order.id).all()
    
    product_ids = [item.product_id for item in items]
    db.close()
    return product_ids


# ===== CONVERSATION MANAGEMENT =====

def create_conversation(session_id: str, user_email: str = None):
    """Create a new conversation session"""
    db = SessionLocal()
    
    # Check if session already exists
    existing = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    if existing:
        db.close()
        return existing
    
    conversation = Conversation(
        session_id=session_id,
        user_email=user_email
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    db.close()
    return conversation


def get_conversation(session_id: str):
    """Get conversation by session ID"""
    db = SessionLocal()
    conversation = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    
    if conversation:
        # Load messages eagerly
        _ = conversation.messages
    
    db.close()
    return conversation


def add_message(session_id: str, role: str, content: str, intent: str = None, data_source: str = None):
    """Add a message to conversation"""
    db = SessionLocal()
    
    # Get or create conversation
    conversation = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    if not conversation:
        conversation = Conversation(session_id=session_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Create message
    message = Message(
        conversation_id=conversation.id,
        role=role,
        content=content,
        intent=intent,
        data_source=data_source
    )
    db.add(message)
    
    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    
    db.commit()
    db.close()
    return message


def get_conversation_history(session_id: str, limit: int = 10):
    """
    Get recent messages from conversation.
    Returns list of messages ordered by time (oldest first).
    """
    from sqlalchemy.orm import joinedload
    
    db = SessionLocal()
    conversation = db.query(Conversation)\
                    .options(joinedload(Conversation.messages))\
                    .filter(Conversation.session_id == session_id)\
                    .first()
    
    if not conversation:
        db.close()
        return []
    
    # Get recent messages (ordered by created_at)
    messages = db.query(Message)\
                 .filter(Message.conversation_id == conversation.id)\
                 .order_by(Message.created_at.desc())\
                 .limit(limit)\
                 .all()
    
    # Reverse to get chronological order (oldest first)
    messages = list(reversed(messages))
    
    # Access message content while session is open
    result = []
    for msg in messages:
        result.append({
            "role": msg.role,
            "content": msg.content,
            "intent": msg.intent,
            "data_source": msg.data_source,
            "created_at": msg.created_at
        })
    
    db.close()
    return result


def delete_conversation(session_id: str):
    """Delete a conversation and all its messages"""
    db = SessionLocal()
    conversation = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    
    if conversation:
        db.delete(conversation)
        db.commit()
    
    db.close()
    return True