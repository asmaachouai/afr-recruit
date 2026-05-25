"""
Development seed script — creates test users and sample data.
Run with: python -m app.db.seed
Never run in production.
"""

import asyncio
import sys
import uuid

import bcrypt

from app.db.session import AsyncSessionLocal
from app.db.models import User, Candidate, Recruiter, Job
from app.db.models.user import UserRole, UserStatus
from app.db.models.job import JobStatus, JobType

# Fix Windows Python 3.13 asyncio event loop issue
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def hash_password(password: str) -> str:
    """Hash a password using bcrypt directly — no passlib dependency."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        # Admin user
        admin = User(
            id=uuid.uuid4(),
            email="admin@afr-recruit.com",
            hashed_password=hash_password("admin123"),
            full_name="Platform Admin",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_verified=True,
        )
        db.add(admin)

        # Recruiter user
        recruiter_user = User(
            id=uuid.uuid4(),
            email="recruiter@nexoria.ma",
            hashed_password=hash_password("recruiter123"),
            full_name="Sara Benali",
            role=UserRole.RECRUITER,
            status=UserStatus.ACTIVE,
            is_verified=True,
            preferred_language="fr",
        )
        db.add(recruiter_user)
        await db.flush()

        recruiter = Recruiter(
            user_id=recruiter_user.id,
            company_name="Nexoria Morocco",
            company_website="https://nexoria.ma",
            industry="Technology",
            company_size="50-200",
            city="Casablanca",
            country="Morocco",
        )
        db.add(recruiter)
        await db.flush()

        # Sample job posting
        job = Job(
            recruiter_id=recruiter.id,
            title="Developpeur Full Stack Python/React",
            description=(
                "Nous recherchons un developpeur Full Stack experimente "
                "pour rejoindre notre equipe tech a Casablanca."
            ),
            requirements="Python, React, PostgreSQL, 3+ ans d'experience",
            location="Casablanca, Maroc",
            job_type=JobType.FULL_TIME,
            status=JobStatus.PUBLISHED,
            required_skills=["Python", "React", "PostgreSQL", "FastAPI"],
            required_languages=["fr", "en"],
            experience_years_min=3,
            is_remote=True,
            language="fr",
        )
        db.add(job)

        # Candidate user
        candidate_user = User(
            id=uuid.uuid4(),
            email="candidate@gmail.com",
            hashed_password=hash_password("candidate123"),
            full_name="Youssef El Amrani",
            role=UserRole.CANDIDATE,
            status=UserStatus.ACTIVE,
            is_verified=True,
            preferred_language="ar",
        )
        db.add(candidate_user)
        await db.flush()

        candidate = Candidate(
            user_id=candidate_user.id,
            city="Marrakech",
            country="Morocco",
            skills=["Python", "Django", "React", "SQL"],
            languages_spoken=["ar", "fr", "en"],
            years_of_experience=4,
            education_level="Licence",
            current_title="Developpeur Backend",
        )
        db.add(candidate)

        await db.commit()
        print("Seed data created successfully.")
        print("Admin:     admin@afr-recruit.com / admin123")
        print("Recruiter: recruiter@nexoria.ma / recruiter123")
        print("Candidate: candidate@gmail.com / candidate123")


if __name__ == "__main__":
    asyncio.run(seed())