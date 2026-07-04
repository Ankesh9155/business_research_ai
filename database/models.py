from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime
)

from datetime import datetime

from database.postgres import Base


# Research Job
class ResearchJob(Base):

    __tablename__ = "research_jobs"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    status = Column(
        String(50),
        default="PROCESSING"
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# Lead Table
class LeadRecord(Base):

    __tablename__ = "leads"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    first_name = Column(String(100))

    last_name = Column(String(100))

    job_title = Column(String(255))

    linkedin_url = Column(Text)

    email = Column(String(255))

    email_verified = Column(Boolean)


    company_name = Column(String(255))

    domain = Column(String(255))

    industry = Column(String(255))

    employee_size = Column(String(50))

    revenue = Column(String(100))


    phone = Column(String(50))

    address = Column(Text)

    city = Column(String(100))

    state = Column(String(100))

    postal_code = Column(String(20))

    country = Column(String(100))


    confidence_score = Column(Integer)

    review_status = Column(
        String(50),
        default="PENDING"
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# Agent Logs
class AgentLog(Base):

    __tablename__ = "agent_logs"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    agent_name = Column(
        String(100)
    )


    message = Column(
        Text
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
