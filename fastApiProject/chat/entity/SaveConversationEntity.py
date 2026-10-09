from pydantic import BaseModel,Field

class SaveConversationEntity(BaseModel):
    question: str = Field(...,description="问题")
    answer: str = Field(...,description="回答")
    currentId: int = Field(...,description="当前会话id")