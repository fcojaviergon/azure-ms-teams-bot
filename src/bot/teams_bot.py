"""Microsoft Teams Bot implementation."""

from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import Activity, ActivityTypes, ChannelAccount, Attachment

from src.utils.logger import get_logger
from src.bot.message_handler import MessageHandler
from src.bot.dialog_manager import DialogManager
from src.bot.cards import AdaptiveCardBuilder

logger = get_logger(__name__)


class TeamsBot(ActivityHandler):
    """Bot for Microsoft Teams integration."""

    def __init__(self):
        """Initialize Teams bot."""
        super().__init__()
        self.message_handler = MessageHandler()
        self.dialog_manager = DialogManager()
        self.card_builder = AdaptiveCardBuilder()

    async def on_turn(self, turn_context: TurnContext):
        """
        Handle incoming activity.

        Args:
            turn_context: Turn context
        """
        try:
            await super().on_turn(turn_context)
        except Exception as e:
            logger.error(f"Error in on_turn: {e}")
            await turn_context.send_activity(
                "Lo siento, ocurrió un error. Por favor intenta de nuevo."
            )

    async def on_message_activity(self, turn_context: TurnContext):
        """
        Handle message activities.

        Args:
            turn_context: Turn context
        """
        try:
            # Get user and conversation info
            user = turn_context.activity.from_property
            conversation_id = turn_context.activity.conversation.id
            text = turn_context.activity.text

            logger.info(
                f"Received message from {user.name} ({user.id}): {text[:100]}"
            )

            # Get or create conversation context
            context = await self.dialog_manager.get_context(
                conversation_id=conversation_id,
                user_id=user.id,
                user_name=user.name,
            )

            # Show typing indicator
            await turn_context.send_activity(
                Activity(type=ActivityTypes.typing)
            )

            # Process message
            response_text, card_data = await self.message_handler.process_message(
                text, turn_context, context
            )

            # Add message to context
            await self.dialog_manager.add_message(
                context=context,
                text=text,
                user_id=user.id,
            )

            # Send response
            if card_data:
                # Send response with adaptive card
                card_attachment = self._create_adaptive_card_attachment(card_data)
                message = MessageFactory.attachment(card_attachment)
                if response_text:
                    message.text = response_text
                await turn_context.send_activity(message)
            else:
                # Send text response
                await turn_context.send_activity(response_text)

            logger.info(f"Sent response to {user.name}")

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            error_card = self.card_builder.create_error_card(
                "Ocurrió un error al procesar tu mensaje. Por favor intenta de nuevo."
            )
            await turn_context.send_activity(
                MessageFactory.attachment(
                    self._create_adaptive_card_attachment(error_card)
                )
            )

    async def on_members_added_activity(
        self, members_added: list[ChannelAccount], turn_context: TurnContext
    ):
        """
        Handle members added to conversation.

        Args:
            members_added: List of added members
            turn_context: Turn context
        """
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                logger.info(f"New member added: {member.name} ({member.id})")

                try:
                    # Send welcome message with card
                    welcome_card = self.card_builder.create_welcome_card()
                    card_attachment = self._create_adaptive_card_attachment(
                        welcome_card
                    )

                    await turn_context.send_activity(
                        MessageFactory.attachment(card_attachment)
                    )
                except Exception as e:
                    logger.error(f"Error sending welcome card: {e}")
                    # Try sending simple text message as fallback
                    try:
                        await turn_context.send_activity(
                            "¡Hola! Soy el bot de SAP Ariba. Escribe '/ayuda' para ver qué puedo hacer."
                        )
                    except Exception as fallback_error:
                        logger.error(f"Error sending fallback message: {fallback_error}")

    async def on_conversation_update_activity(
        self, turn_context: TurnContext
    ):
        """
        Handle conversation updates.

        Args:
            turn_context: Turn context
        """
        logger.info(
            f"Conversation update: {turn_context.activity.conversation.id}"
        )
        await super().on_conversation_update_activity(turn_context)

    async def on_event_activity(self, turn_context: TurnContext):
        """
        Handle event activities.

        Args:
            turn_context: Turn context
        """
        logger.info(f"Event received: {turn_context.activity.name}")
        await super().on_event_activity(turn_context)

    async def on_message_reaction_activity(self, turn_context: TurnContext):
        """
        Handle message reactions.

        Args:
            turn_context: Turn context
        """
        logger.info(f"Message reaction: {turn_context.activity.type}")

        # Track reactions for feedback
        reactions_added = turn_context.activity.reactions_added or []
        reactions_removed = turn_context.activity.reactions_removed or []

        for reaction in reactions_added:
            logger.info(f"Reaction added: {reaction.type}")

        for reaction in reactions_removed:
            logger.info(f"Reaction removed: {reaction.type}")

    async def on_teams_channel_created(self, turn_context: TurnContext):
        """Handle Teams channel created event."""
        logger.info("Teams channel created")

    async def on_teams_channel_deleted(self, turn_context: TurnContext):
        """Handle Teams channel deleted event."""
        logger.info("Teams channel deleted")

    async def on_teams_channel_renamed(self, turn_context: TurnContext):
        """Handle Teams channel renamed event."""
        logger.info("Teams channel renamed")

    async def on_teams_team_archived(self, turn_context: TurnContext):
        """Handle Teams team archived event."""
        logger.info("Teams team archived")

    async def on_teams_team_deleted(self, turn_context: TurnContext):
        """Handle Teams team deleted event."""
        logger.info("Teams team deleted")

    async def on_teams_team_hard_deleted(self, turn_context: TurnContext):
        """Handle Teams team hard deleted event."""
        logger.info("Teams team hard deleted")

    async def on_teams_team_renamed(self, turn_context: TurnContext):
        """Handle Teams team renamed event."""
        logger.info("Teams team renamed")

    async def on_teams_team_restored(self, turn_context: TurnContext):
        """Handle Teams team restored event."""
        logger.info("Teams team restored")

    async def on_teams_team_unarchived(self, turn_context: TurnContext):
        """Handle Teams team unarchived event."""
        logger.info("Teams team unarchived")

    def _create_adaptive_card_attachment(
        self, card_data: dict
    ) -> Attachment:
        """
        Create adaptive card attachment.

        Args:
            card_data: Card data dictionary

        Returns:
            Attachment
        """
        return Attachment(
            content_type="application/vnd.microsoft.card.adaptive",
            content=card_data,
        )
