from pydantic import BaseModel


class GoalCreate(BaseModel):
    title: str
    description: str | None = None
    category: str


class GoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None


class GoalResponse(BaseModel):
    id: str
    title: str
    description: str | None
    category: str
    status: str

    class Config:
        from_attributes = True


class ProgressCreate(BaseModel):
    note: str | None = None
    mood: str | None = None


class MessageCreate(BaseModel):
    content: str


class ConversationResponse(BaseModel):
    id: str
    title: str | None

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
