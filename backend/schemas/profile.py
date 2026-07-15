from datetime import datetime
from pydantic import BaseModel, Field


class UserProfileUpdate(BaseModel):
    full_name: str = ""
    professional_title: str = ""
    summary: str = ""
    location: str = ""
    work_preferences: str = ""
    job_country: str = "Brasil"
    job_state: str = "São Paulo"
    job_state_code: str = "SP"
    job_cities: list[str] = Field(default_factory=list)
    job_all_cities: bool = False
    job_remote_preference: str = "any"
    job_city_code: str = "5211323"
    education_level: str = "Superior completo"
    english_level: str = "Intermediário"
    spanish_level: str = "Nenhum"
    salary_expectation: float = 0
    phone: str = ""
    email: str = ""


class SkillCreate(BaseModel):
    name: str
    level: str = "intermediate"
    category: str = "technical"


class ExperienceCreate(BaseModel):
    company: str
    role: str
    start_date: str = ""
    end_date: str = ""
    description: str = ""
    achievements: str = ""


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    technologies: str = ""
    url: str = ""


class EducationCreate(BaseModel):
    institution: str
    course: str
    start_date: str = ""
    end_date: str = ""
    description: str = ""


class SkillOut(SkillCreate):
    id: int
    class Config:
        from_attributes = True


class ExperienceOut(ExperienceCreate):
    id: int
    class Config:
        from_attributes = True


class ProjectOut(ProjectCreate):
    id: int
    class Config:
        from_attributes = True


class EducationOut(EducationCreate):
    id: int
    class Config:
        from_attributes = True


class UserProfileOut(BaseModel):
    id: int | None = None
    tenant_id: int
    user_id: int
    full_name: str = ""
    professional_title: str = ""
    summary: str = ""
    location: str = ""
    work_preferences: str = ""
    job_country: str = "Brasil"
    job_state: str = "São Paulo"
    job_state_code: str = "SP"
    job_cities: list[str] = Field(default_factory=list)
    job_all_cities: bool = False
    job_remote_preference: str = "any"
    job_city_code: str = "5211323"
    education_level: str = "Superior completo"
    english_level: str = "Intermediário"
    spanish_level: str = "Nenhum"
    salary_expectation: float = 0
    phone: str = ""
    email: str = ""
    resume_text: str = ""
    completeness: float = 0
    skills: list[SkillOut] = []
    experiences: list[ExperienceOut] = []
    projects: list[ProjectOut] = []
    education: list[EducationOut] = []


class ResumeUploadOut(BaseModel):
    id: int
    filename: str
    content_type: str
    extracted_text: str
    parsed_data: dict
    created_at: datetime


class ParseResumeResponse(BaseModel):
    upload_id: int | None = None
    extracted_text: str
    parsed_data: dict
    profile: UserProfileOut
