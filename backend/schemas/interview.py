from pydantic import BaseModel


class InterviewPrepOut(BaseModel):
    job_id: int
    role_pitch: str
    questions: list[str]
    weak_points: list[str]
    study_plan: list[str]
    salary_talk: str
