"""Database models for Control Center."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Service(Base):
    """Service model for tracking managed services."""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    status = Column(String(20), default="stopped")  # stopped, running, failed
    health = Column(String(20), default="unknown")  # healthy, unhealthy, unknown
    port = Column(Integer, nullable=True)
    pid = Column(Integer, nullable=True)
    command = Column(Text, nullable=False)
    cwd = Column(String(500), nullable=True)  # working directory
    is_system = Column(Boolean, default=False)  # True if managed by system
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Agent(Base):
    """Agent model for tracking AI agents."""
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    level = Column(String(10), nullable=False)  # L1.1, L2.3, etc.
    category = Column(String(50), nullable=False)  # Foundation, Execution, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to knowledge files
    knowledge_files = relationship("KnowledgeFile", back_populates="agent", cascade="all, delete-orphan")


class KnowledgeFile(Base):
    """Knowledge file model for tracking agent knowledge base."""
    __tablename__ = "knowledge_files"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    confidence = Column(Float, default=0.0)  # 0.0 to 1.0
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to agent
    agent = relationship("Agent", back_populates="knowledge_files")


class APIUsage(Base):
    """API usage tracking for cost monitoring."""
    __tablename__ = "api_usage"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String(50), nullable=False)  # claude, openai, etc.
    cost = Column(Float, default=0.0)
    calls = Column(Integer, default=0)
    date = Column(DateTime, default=datetime.utcnow)


class JobHistory(Base):
    """Job history for tracking background tasks."""
    __tablename__ = "job_history"

    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String(100), nullable=False)  # kb_sync, service_restart, etc.
    status = Column(String(20), nullable=False)  # pending, running, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    result = Column(Text, nullable=True)


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(20), nullable=False, default="user")  # admin, user, readonly
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
