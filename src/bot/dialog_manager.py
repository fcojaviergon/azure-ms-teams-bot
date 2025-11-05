"""Dialog manager for conversation context and state management."""

from typing import Dict, Optional
from datetime import datetime, timedelta

from src.models.conversation import ConversationContext, Message, UserProfile
from src.services.cache_service import cache_service
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DialogManager:
    """Manager for conversation dialogs and context."""

    def __init__(self):
        """Initialize dialog manager."""
        self.context_ttl = 3600  # 1 hour

    async def get_context(
        self, conversation_id: str, user_id: str, user_name: str = "User"
    ) -> ConversationContext:
        """
        Get or create conversation context.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            user_name: User name

        Returns:
            ConversationContext
        """
        cache_key = f"conversation:{conversation_id}"

        # Try to get from cache
        cached_context = await cache_service.get(cache_key)

        if cached_context:
            logger.debug(f"Retrieved context from cache: {conversation_id}")
            return ConversationContext(**cached_context)

        # Create new context
        logger.info(f"Creating new conversation context: {conversation_id}")

        user_profile = UserProfile(
            user_id=user_id,
            name=user_name,
        )

        context = ConversationContext(
            conversation_id=conversation_id,
            user_profile=user_profile,
        )

        # Save to cache
        await self.save_context(context)

        return context

    async def save_context(self, context: ConversationContext) -> bool:
        """
        Save conversation context to cache.

        Args:
            context: ConversationContext to save

        Returns:
            True if successful
        """
        try:
            cache_key = f"conversation:{context.conversation_id}"
            context.updated_at = datetime.utcnow()

            await cache_service.set(
                cache_key,
                context.model_dump(),
                ttl=self.context_ttl,
            )

            logger.debug(f"Saved context: {context.conversation_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving context: {e}")
            return False

    async def add_message(
        self,
        context: ConversationContext,
        text: str,
        user_id: str,
        intent: Optional[str] = None,
        entities: Optional[Dict] = None,
    ) -> None:
        """
        Add a message to the conversation context.

        Args:
            context: ConversationContext
            text: Message text
            user_id: User ID
            intent: Detected intent
            entities: Extracted entities
        """
        message = Message(
            message_id=f"{context.conversation_id}_{len(context.messages)}",
            conversation_id=context.conversation_id,
            user_id=user_id,
            text=text,
            intent=intent,
            entities=entities or {},
        )

        context.add_message(message)

        if intent:
            context.update_intent(intent)

        if entities:
            context.update_entities(entities)

        await self.save_context(context)

    async def clear_context(self, conversation_id: str) -> bool:
        """
        Clear conversation context.

        Args:
            conversation_id: Conversation ID

        Returns:
            True if successful
        """
        try:
            cache_key = f"conversation:{conversation_id}"
            await cache_service.delete(cache_key)
            logger.info(f"Cleared context: {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing context: {e}")
            return False

    async def cleanup_old_contexts(self, max_age_hours: int = 24) -> int:
        """
        Cleanup old conversation contexts.

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            Number of contexts cleaned up
        """
        # This would require scanning all conversation keys
        # For now, Redis TTL handles cleanup automatically
        logger.info("Old contexts are automatically cleaned by Redis TTL")
        return 0

    def is_context_expired(self, context: ConversationContext) -> bool:
        """
        Check if context is expired.

        Args:
            context: ConversationContext

        Returns:
            True if expired
        """
        expiry_time = context.updated_at + timedelta(seconds=self.context_ttl)
        return datetime.utcnow() > expiry_time
