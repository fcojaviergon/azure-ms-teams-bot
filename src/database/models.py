"""SQLAlchemy models for PostgreSQL with pgvector."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from src.database.session import Base


class Conversation(Base):
    """Conversation model - stores chat sessions."""

    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    user_name = Column(String(255))
    channel_id = Column(String(100))  # 'msteams', 'webchat', etc.
    conversation_id = Column(String(500), unique=True, index=True)  # Bot Framework conversation ID
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSONB, default=dict)  # Additional flexible data

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id='{self.user_id}', started_at='{self.started_at}')>"


class Message(Base):
    """Message model - stores individual messages with embeddings."""

    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # OpenAI ada-002 embedding (1536 dimensions)
    intent = Column(String(100))  # Detected intent
    entities = Column(JSONB, default=dict)  # Extracted entities
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    metadata = Column(JSONB, default=dict)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    # Index for vector similarity search
    __table_args__ = (
        Index('idx_message_embedding_cosine', 'embedding', postgresql_using='hnsw', postgresql_ops={'embedding': 'vector_cosine_ops'}),
    )

    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', content='{self.content[:30]}...')>"


class UserSettings(Base):
    """User settings and preferences."""

    __tablename__ = 'user_settings'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255))
    email = Column(String(255))
    department = Column(String(100))
    role = Column(String(100))  # 'admin', 'manager', 'buyer', 'finance', 'viewer'
    preferences = Column(JSONB, default=dict)  # Language, timezone, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserSettings(user_id='{self.user_id}', role='{self.role}')>"


class Alert(Base):
    """Alert configuration model."""

    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), ForeignKey('user_settings.user_id', ondelete='CASCADE'), nullable=False, index=True)
    alert_type = Column(String(100), nullable=False)  # 'po_approval', 'contract_expiry', etc.
    title = Column(String(500))
    condition = Column(JSONB, nullable=False)  # Alert condition configuration
    channels = Column(JSONB, default=list)  # ['teams', 'email']
    frequency = Column(String(50), default='daily')  # 'realtime', 'daily', 'weekly'
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserSettings", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, type='{self.alert_type}', user_id='{self.user_id}')>"


class KnowledgeBase(Base):
    """Knowledge base model - stores documents with embeddings for semantic search."""

    __tablename__ = 'knowledge_base'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # OpenAI embedding
    source = Column(String(255))  # 'manual', 'faq', 'policy', etc.
    category = Column(String(100), index=True)
    tags = Column(JSONB, default=list)
    metadata = Column(JSONB, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Index for vector similarity search
    __table_args__ = (
        Index('idx_kb_embedding_cosine', 'embedding', postgresql_using='hnsw', postgresql_ops={'embedding': 'vector_cosine_ops'}),
    )

    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, title='{self.title}')>"


class AuditLog(Base):
    """Audit log for tracking user actions and system events."""

    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True)
    action = Column(String(100), nullable=False, index=True)  # 'query', 'export', 'config_change', etc.
    entity_type = Column(String(100))  # 'po', 'pr', 'invoice', 'alert', etc.
    entity_id = Column(String(255))
    details = Column(JSONB, default=dict)
    ip_address = Column(String(50))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id='{self.user_id}')>"


class CachedQuery(Base):
    """Cache for frequent queries - reduce load on external systems."""

    __tablename__ = 'cached_queries'

    id = Column(Integer, primary_key=True, index=True)
    query_key = Column(String(255), unique=True, nullable=False, index=True)  # Hash of query parameters
    query_type = Column(String(100), nullable=False)  # 'po', 'pr', 'supplier', etc.
    result_data = Column(JSONB, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    hit_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CachedQuery(id={self.id}, type='{self.query_type}', key='{self.query_key[:20]}...')>"
