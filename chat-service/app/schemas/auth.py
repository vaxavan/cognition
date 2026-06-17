from pydantic import BaseModel, EmailStr

class SendCodeRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyRequest(BaseModel):
    email: EmailStr
    password: str
    code: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"