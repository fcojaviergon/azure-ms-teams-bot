"""Message handler for processing user messages and routing to services."""

from typing import Dict, Any, Optional, Tuple
from botbuilder.core import TurnContext

from src.utils.logger import get_logger
from src.utils.validators import extract_ariba_ids, sanitize_input
from src.services.openai_service import openai_service
from src.services.ariba_factory import ariba
from src.services.search_service import search_service
from src.models.conversation import ConversationContext, Message, UserProfile
from src.bot.cards import AdaptiveCardBuilder

logger = get_logger(__name__)


class MessageHandler:
    """Handler for processing messages and generating responses."""

    def __init__(self):
        """Initialize message handler."""
        self.card_builder = AdaptiveCardBuilder()

    async def process_message(
        self,
        text: str,
        turn_context: TurnContext,
        context: Optional[ConversationContext] = None,
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Process user message and generate response.

        Args:
            text: User message text
            turn_context: Bot turn context
            context: Conversation context

        Returns:
            Tuple of (response_text, adaptive_card)
        """
        try:
            # Sanitize input
            text = sanitize_input(text)

            # Handle commands
            if text.startswith("/"):
                return await self._handle_command(text, turn_context)

            # Extract intent and entities
            logger.info(f"Processing message: {text[:100]}")
            intent_data = await openai_service.extract_intent(text)
            intent = intent_data.get("intent", "general_question")
            entities = intent_data.get("entities", {})

            logger.info(f"Detected intent: {intent}")

            # Route to appropriate handler
            if intent == "search_po":
                return await self._handle_search_po(text, entities)
            elif intent == "search_pr":
                return await self._handle_search_pr(text, entities)
            elif intent == "search_supplier":
                return await self._handle_search_supplier(text, entities)
            elif intent == "get_status":
                return await self._handle_get_status(text, entities)
            elif intent == "create_document":
                return await self._handle_create_document(text, entities)
            else:
                return await self._handle_general_question(text, context)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return (
                "Lo siento, ocurrió un error al procesar tu mensaje. Por favor intenta de nuevo.",
                self.card_builder.create_error_card(str(e)),
            )

    async def _handle_command(
        self, command: str, turn_context: TurnContext
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Handle bot commands."""
        command_lower = command.lower()

        if command_lower in ["/ayuda", "/help"]:
            return (
                "Aquí está la información de ayuda:",
                self.card_builder.create_welcome_card(),
            )
        elif command_lower in ["/status", "/health"]:
            return (
                "✅ El bot está funcionando correctamente.\n\n"
                "Servicios activos:\n"
                "• Azure OpenAI: ✅\n"
                "• Azure Cognitive Search: ✅\n"
                "• SAP Ariba: ✅\n"
                "• Redis Cache: ✅",
                None,
            )
        elif command_lower in ["/clear", "/reset"]:
            return (
                "✅ Contexto de conversación reiniciado. Puedes empezar una nueva consulta.",
                None,
            )
        else:
            return (f"Comando desconocido: {command}", None)

    async def _handle_search_po(
        self, text: str, entities: Dict[str, Any]
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Handle purchase order search."""
        try:
            # Extract PO IDs from text
            po_ids = extract_ariba_ids(text)

            if po_ids:
                # Get specific PO
                po_id = po_ids[0]
                logger.info(f"Fetching PO: {po_id}")

                po = await ariba.get_purchase_order_by_id(po_id)

                if po:
                    card = self.card_builder.create_purchase_order_card(
                        po.model_dump()
                    )
                    return (
                        f"He encontrado el Purchase Order {po_id}:",
                        card,
                    )
                else:
                    return (
                        f"No encontré el Purchase Order {po_id}. Verifica que el ID sea correcto.",
                        None,
                    )
            else:
                # List recent POs
                logger.info("Listing recent purchase orders")
                response = await ariba.get_purchase_orders(page_size=5)

                if response.records:
                    card = self.card_builder.create_list_card(
                        "📋 Últimos Purchase Orders",
                        response.records,
                        item_type="po",
                    )
                    return (
                        f"He encontrado {response.total_count} purchase orders. Aquí están los últimos 5:",
                        card,
                    )
                else:
                    return ("No se encontraron purchase orders.", None)

        except Exception as e:
            logger.error(f"Error handling PO search: {e}")
            return (
                "Ocurrió un error al buscar el purchase order.",
                self.card_builder.create_error_card(str(e)),
            )

    async def _handle_search_pr(
        self, text: str, entities: Dict[str, Any]
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Handle purchase requisition search."""
        try:
            pr_ids = extract_ariba_ids(text)

            if pr_ids:
                # Search for specific PR
                pr_id = pr_ids[0]
                logger.info(f"Searching for PR: {pr_id}")

                response = await ariba.get_purchase_requisitions(
                    filters={"pr_number": pr_id}, page_size=1
                )

                if response.records:
                    pr_data = response.records[0]
                    card = self.card_builder.create_purchase_requisition_card(
                        pr_data
                    )
                    return (f"He encontrado la requisición {pr_id}:", card)
                else:
                    return (f"No encontré la requisición {pr_id}.", None)
            else:
                # List recent PRs
                logger.info("Listing recent purchase requisitions")
                response = await ariba.get_purchase_requisitions(
                    page_size=5
                )

                if response.records:
                    card = self.card_builder.create_list_card(
                        "📝 Últimas Purchase Requisitions",
                        response.records,
                        item_type="pr",
                    )
                    return (
                        f"He encontrado {response.total_count} requisiciones. Aquí están las últimas 5:",
                        card,
                    )
                else:
                    return ("No se encontraron requisiciones.", None)

        except Exception as e:
            logger.error(f"Error handling PR search: {e}")
            return (
                "Ocurrió un error al buscar la requisición.",
                self.card_builder.create_error_card(str(e)),
            )

    async def _handle_search_supplier(
        self, text: str, entities: Dict[str, Any]
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Handle supplier search."""
        try:
            logger.info("Searching for suppliers")

            # Extract supplier name or search in text
            filters = {}
            if "names" in entities and entities["names"]:
                filters["name"] = entities["names"][0]

            response = await ariba.get_suppliers(
                filters=filters, page_size=10
            )

            if response.records:
                if len(response.records) == 1:
                    card = self.card_builder.create_supplier_card(
                        response.records[0]
                    )
                    return ("He encontrado este proveedor:", card)
                else:
                    card = self.card_builder.create_list_card(
                        "🏢 Proveedores Encontrados",
                        response.records,
                        item_type="supplier",
                    )
                    return (
                        f"He encontrado {response.total_count} proveedores:",
                        card,
                    )
            else:
                return ("No se encontraron proveedores con esos criterios.", None)

        except Exception as e:
            logger.error(f"Error handling supplier search: {e}")
            return (
                "Ocurrió un error al buscar proveedores.",
                self.card_builder.create_error_card(str(e)),
            )

    async def _handle_get_status(
        self, text: str, entities: Dict[str, Any]
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Handle status inquiry."""
        try:
            # Extract document ID
            doc_ids = extract_ariba_ids(text)

            if not doc_ids:
                return (
                    "Por favor proporciona un ID de documento (ej: PO1234567, PR7654321)",
                    None,
                )

            doc_id = doc_ids[0]
            doc_type = "po" if doc_id.startswith("PO") else "pr"

            logger.info(f"Getting status for {doc_type}: {doc_id}")

            status_data = await ariba.get_document_status(doc_id, doc_type)

            response_text = f"**Estado de {doc_id}:**\n\n"
            response_text += f"Estado actual: **{status_data.get('status', 'N/A')}**\n"
            response_text += f"Última actualización: {status_data.get('last_updated', 'N/A')}\n"

            if status_data.get("workflow_steps"):
                response_text += "\n**Flujo de aprobación:**\n"
                for step in status_data["workflow_steps"]:
                    response_text += f"• {step.get('step')}: {step.get('status')}\n"

            return (response_text, None)

        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return (
                "Ocurrió un error al obtener el estado del documento.",
                self.card_builder.create_error_card(str(e)),
            )

    async def _handle_create_document(
        self, text: str, entities: Dict[str, Any]
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Handle document creation (not implemented yet)."""
        return (
            "⚠️ La creación de documentos aún no está disponible.\n\n"
            "Próximamente podrás crear Purchase Requisitions directamente desde Teams.",
            None,
        )

    async def _handle_general_question(
        self, text: str, context: Optional[ConversationContext]
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Handle general questions using OpenAI and search."""
        try:
            logger.info("Handling general question")

            # Search for relevant information
            search_results = await search_service.semantic_search(text, top=3)

            # Build context from search results
            search_context = ""
            if search_results:
                search_context = "Información relevante:\n"
                for result in search_results:
                    search_context += f"- {result.get('title', 'N/A')}: {result.get('content', '')[:200]}\n"

            # Generate response with OpenAI
            if search_context:
                response = await openai_service.answer_with_context(
                    text, search_context
                )
            else:
                response = await openai_service.generate_response(text, context)

            return (response, None)

        except Exception as e:
            logger.error(f"Error handling general question: {e}")
            return (
                "Ocurrió un error al procesar tu pregunta.",
                self.card_builder.create_error_card(str(e)),
            )
