from pydantic import BaseModel, Field, EmailStr


class RegisterRequest(BaseModel):
    tenant_name: str
    full_name: str
    email: EmailStr
    password: str
    skills: str = ""
    seniority: str = "mid"
    target_role: str = ""
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


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserMe(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    tenant_id: int
    tenant_name: str
    role: str
    skills: str
    seniority: str
    target_role: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
