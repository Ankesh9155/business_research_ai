from sqlalchemy.orm import Session

from database.models import (
    ResearchJob,
    LeadRecord,
    AgentLog
)


class DatabaseService:


    def create_job(
        self,
        db: Session
    ):

        job = ResearchJob()

        db.add(job)

        db.commit()

        db.refresh(job)

        return job


    def save_lead(
        self,
        db: Session,
        data: dict
    ):

        lead = LeadRecord(
            **data
        )

        db.add(lead)

        db.commit()

        db.refresh(lead)

        return lead


    def get_leads(
        self,
        db: Session,
        status: str = None
    ):

        query = db.query(LeadRecord)

        if status:
            query = query.filter(
                LeadRecord.review_status == status.upper()
            )

        return query.order_by(LeadRecord.id.desc()).all()


    def update_review_status(
        self,
        db: Session,
        lead_id: int,
        status: str
    ):

        lead = (
            db.query(LeadRecord)
            .filter(
                LeadRecord.id == lead_id
            )
            .first()
        )


        if lead:

            lead.review_status = status

            db.commit()

        return lead


    def log_agent(
        self,
        db: Session,
        agent_name: str,
        message: str
    ):

        log = AgentLog(
            agent_name=agent_name,
            message=message
        )

        db.add(log)

        db.commit()