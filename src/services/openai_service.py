"""Azure OpenAI service for natural language processing."""

from typing import List, Dict, Any, Optional
from openai import AsyncAzureOpenAI

from src.config.settings import settings
from src.utils.logger import get_logger
from src.models.conversation import ConversationContext, Message

logger = get_logger(__name__)


class OpenAIService:
    """Service for Azure OpenAI GPT-4 integration."""

    def __init__(self):
        """Initialize OpenAI service."""
        self.client = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )
        self.deployment_name = settings.azure_openai_deployment_name
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the bot."""
        return """You are an intelligent assistant for SAP Ariba procurement system integrated with Microsoft Teams.

Your capabilities:
- Answer questions about purchase orders, requisitions, suppliers, contracts, and invoices
- Help users search and retrieve information from SAP Ariba
- Provide status updates on procurement processes
- Assist with creating and managing procurement documents
- Offer guidance on procurement workflows and best practices

Guidelines:
- Be professional, concise, and helpful
- If you don't have access to specific data, ask the user for clarification
- For sensitive operations, confirm with the user before proceeding
- Use structured responses when presenting data (tables, lists, cards)
- Always provide context and explanations with your answers
- If an error occurs, explain it clearly and suggest next steps

When users ask about specific documents (POs, PRs, etc.), extract the document IDs and retrieve the information.
"""

    async def generate_response(
        self,
        user_message: str,
        context: Optional[ConversationContext] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """
        Generate a response using GPT-4.

        Args:
            user_message: User's message
            context: Conversation context
            temperature: Response creativity (0-1)
            max_tokens: Maximum response length

        Returns:
            Generated response
        """
        try:
            messages = [{"role": "system", "content": self.system_prompt}]

            # Add conversation history if available
            if context:
                recent_messages = context.get_recent_messages(limit=5)
                for msg in recent_messages:
                    messages.append(
                        {
                            "role": "user" if msg.user_id else "assistant",
                            "content": msg.text,
                        }
                    )

            # Add current message
            messages.append({"role": "user", "content": user_message})

            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            generated_text = response.choices[0].message.content
            logger.info(
                f"Generated response (tokens: {response.usage.total_tokens})"
            )

            return generated_text

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    async def extract_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Extract intent and entities from user message.

        Args:
            user_message: User's message

        Returns:
            Dict with intent and entities
        """
        try:
            prompt = f"""Analyze this user message and extract:
1. Primary intent (one of: search_po, search_pr, search_supplier, get_status, create_document, general_question)
2. Entities (document IDs, dates, amounts, names, etc.)

User message: "{user_message}"

Respond in JSON format:
{{
  "intent": "intent_name",
  "confidence": 0.95,
  "entities": {{
    "document_ids": [],
    "dates": [],
    "amounts": [],
    "names": []
  }}
}}
"""

            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an intent extraction system. Always respond with valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=300,
            )

            import json

            result = json.loads(response.choices[0].message.content)
            logger.info(f"Extracted intent: {result.get('intent')}")

            return result

        except Exception as e:
            logger.error(f"Error extracting intent: {e}")
            # Return default intent
            return {
                "intent": "general_question",
                "confidence": 0.5,
                "entities": {},
            }

    async def generate_summary(
        self, data: List[Dict[str, Any]], data_type: str
    ) -> str:
        """
        Generate a natural language summary of structured data.

        Args:
            data: List of data items
            data_type: Type of data (e.g., 'purchase_orders', 'suppliers')

        Returns:
            Natural language summary
        """
        try:
            prompt = f"""Generate a concise, professional summary of these {data_type}:

{data}

Provide key insights, totals, and important highlights. Format the response in a clear, readable way."""

            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=500,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Found {len(data)} {data_type}"

    async def answer_with_context(
        self, question: str, context_data: str
    ) -> str:
        """
        Answer a question using provided context data.

        Args:
            question: User's question
            context_data: Relevant context information

        Returns:
            Answer based on context
        """
        try:
            prompt = f"""Using the following context, answer the user's question accurately and concisely.

Context:
{context_data}

Question: {question}

Provide a clear, professional answer based on the context. If the context doesn't contain enough information, say so."""

            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=800,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error answering with context: {e}")
            raise


# Global OpenAI service instance
openai_service = OpenAIService()
