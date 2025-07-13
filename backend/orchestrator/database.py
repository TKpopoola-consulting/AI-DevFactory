from sqlalchemy import create_engine, Column, String, JSON, Float, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from utils.security import DataEncryptor

Base = declarative_base()
encryptor = DataEncryptor()

class Job(Base):
    __tablename__ = 'jobs'
    
    job_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    prompt = Column(LargeBinary, nullable=False)  # Encrypted
    config = Column(JSON, nullable=False)
    status = Column(String, default='created')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)
    artifacts = Column(JSON)
    estimated_cost = Column(Float)
    actual_cost = Column(Float)
    error = Column(String)

class JobDB:
    # ... existing methods ...
    
    def create_job(self, user_id: str, prompt: str, config: dict) -> str:
        session = self.Session()
        job_id = self.generate_id()
        
        # Encrypt sensitive data
        encrypted_prompt = encryptor.encrypt(prompt)
        
        job = Job(
            job_id=job_id,
            user_id=user_id,
            prompt=encrypted_prompt,
            config=config
        )
        session.add(job)
        session.commit()
        session.close()
        return job_id
    
    def get_job(self, job_id: str) -> dict:
        session = self.Session()
        job = session.query(Job).filter(Job.job_id == job_id).first()
        session.close()
        
        if job:
            job_data = job.__dict__
            # Decrypt sensitive data
            job_data["prompt"] = encryptor.decrypt(job_data["prompt"])
            return job_data
        return None