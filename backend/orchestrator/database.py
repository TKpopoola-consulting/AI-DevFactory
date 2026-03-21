from sqlalchemy import create_engine, Column, String, JSON, Float, DateTime, LargeBinary, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/aidevfactory")

# Create engine - THIS WAS MISSING
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# For encryption (create a simple placeholder if needed)
class DataEncryptor:
    def encrypt(self, data):
        return data.encode() if isinstance(data, str) else data
    
    def decrypt(self, data):
        return data.decode() if isinstance(data, bytes) else data

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
    def __init__(self):
        self.Session = sessionmaker(bind=engine)
    
    def generate_id(self):
        import uuid
        return str(uuid.uuid4())
    
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
            job_data = {
                'job_id': job.job_id,
                'user_id': job.user_id,
                'prompt': encryptor.decrypt(job.prompt),
                'config': job.config,
                'status': job.status,
                'created_at': job.created_at,
                'updated_at': job.updated_at,
                'artifacts': job.artifacts,
                'estimated_cost': job.estimated_cost,
                'actual_cost': job.actual_cost,
                'error': job.error
            }
            return job_data
        return None
    
    def update_job(self, job_id: str, data: dict):
        session = self.Session()
        job = session.query(Job).filter(Job.job_id == job_id).first()
        if job:
            for key, value in data.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            session.commit()
        session.close()

# Initialize database
def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    init_db()
