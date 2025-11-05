"""Conversation and user models."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """User profile information."""

    user_id: str
    name: str
    email: Optional[str] = None
    language: str = "en"
    timezone: str = "UTC"
    preferences: Dict[str, Any] = Field(default_factory=dict)


class Message(BaseModel):
    """Message model."""

    message_id: str
    conversation_id: str
    user_id: str
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    intent: Optional[str] = None
    entities: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationContext(BaseModel):
    """Conversation context for maintaining state."""

    conversation_id: str
    user_profile: UserProfile
    messages: List[Message] = Field(default_factory=list)
    current_intent: Optional[str] = None
    entities: Dict[str, Any] = Field(default_factory=dict)
    state: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)
        self.updated_at = datetime.utcnow()

    def update_intent(self, intent: str) -> None:
        """Update current intent."""
        self.current_intent = intent
        self.updated_at = datetime.utcnow()

    def update_entities(self, entities: Dict[str, Any]) -> None:
        """Update entities."""
        self.entities.update(entities)
        self.updated_at = datetime.utcnow()

    def get_recent_messages(self, limit: int = 5) -> List[Message]:
        """Get recent messages."""
        return self.messages[-limit:]
