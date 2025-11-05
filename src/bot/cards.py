"""Adaptive Cards for Microsoft Teams."""

from typing import List, Dict, Any, Optional
from datetime import datetime


class AdaptiveCardBuilder:
    """Builder for Adaptive Cards."""

    @staticmethod
    def create_welcome_card() -> Dict[str, Any]:
        """Create welcome card for new users."""
        return {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "👋 ¡Bienvenido al Bot de SAP Ariba!",
                    "size": "Large",
                    "weight": "Bolder",
                    "color": "Accent",
                },
                {
                    "type": "TextBlock",
                    "text": "Soy tu asistente inteligente para consultas de procurement en SAP Ariba.",
                    "wrap": True,
                    "spacing": "Medium",
                },
                {
                    "type": "TextBlock",
                    "text": "**¿Qué puedo hacer por ti?**",
                    "weight": "Bolder",
                    "spacing": "Medium",
                },
                {
                    "type": "TextBlock",
                    "text": "• Consultar Purchase Orders (PO)\n• Consultar Purchase Requisitions (PR)\n• Buscar proveedores\n• Obtener estados de documentos\n• Búsquedas generales en Ariba",
                    "wrap": True,
                },
                {
                    "type": "TextBlock",
                    "text": "**Ejemplos de preguntas:**",
                    "weight": "Bolder",
                    "spacing": "Medium",
                },
                {
                    "type": "TextBlock",
                    "text": "• \"Muéstrame el PO PO1234567\"\n• \"Lista las últimas requisiciones\"\n• \"Busca proveedores activos\"\n• \"¿Cuál es el estado del PR7654321?\"",
                    "wrap": True,
                },
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Ver últimos POs",
                    "data": {"action": "list_pos"},
                },
                {
                    "type": "Action.Submit",
                    "title": "Ver últimas PRs",
                    "data": {"action": "list_prs"},
                },
            ],
        }

    @staticmethod
    def create_purchase_order_card(po_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create card for displaying purchase order."""
        return {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": f"📋 Purchase Order: {po_data.get('po_number', 'N/A')}",
                    "size": "Large",
                    "weight": "Bolder",
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {
                            "title": "Estado:",
                            "value": po_data.get("status", "N/A"),
                        },
                        {
                            "title": "Proveedor:",
                            "value": po_data.get("supplier", "N/A"),
                        },
                        {
                            "title": "Total:",
                            "value": f"{po_data.get('total_amount', 0)} {po_data.get('currency', 'USD')}",
                        },
                        {
                            "title": "Fecha:",
                            "value": str(po_data.get("created_date", "N/A")),
                        },
                    ],
                },
                {
                    "type": "TextBlock",
                    "text": "**Líneas de pedido:**",
                    "weight": "Bolder",
                    "spacing": "Medium",
                },
                {
                    "type": "TextBlock",
                    "text": AdaptiveCardBuilder._format_line_items(
                        po_data.get("line_items", [])
                    ),
                    "wrap": True,
                },
            ],
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "Ver en Ariba",
                    "url": f"https://ariba.com/po/{po_data.get('po_number', '')}",
                }
            ],
        }

    @staticmethod
    def create_purchase_requisition_card(pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create card for displaying purchase requisition."""
        return {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": f"📝 Purchase Requisition: {pr_data.get('pr_number', 'N/A')}",
                    "size": "Large",
                    "weight": "Bolder",
                },
                {
                    "type": "TextBlock",
                    "text": pr_data.get("title", ""),
                    "wrap": True,
                    "weight": "Bolder",
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {
                            "title": "Estado:",
                            "value": pr_data.get("status", "N/A"),
                        },
                        {
                            "title": "Solicitante:",
                            "value": pr_data.get("requester", "N/A"),
                        },
                        {
                            "title": "Total:",
                            "value": f"{pr_data.get('total_amount', 0)} {pr_data.get('currency', 'USD')}",
                        },
                        {
                            "title": "Urgencia:",
                            "value": pr_data.get("urgency", "Normal"),
                        },
                        {
                            "title": "Departamento:",
                            "value": pr_data.get("department", "N/A"),
                        },
                    ],
                },
            ],
        }

    @staticmethod
    def create_supplier_card(supplier_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create card for displaying supplier information."""
        rating_stars = "⭐" * int(supplier_data.get("rating", 0))

        return {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": f"🏢 {supplier_data.get('name', 'N/A')}",
                    "size": "Large",
                    "weight": "Bolder",
                },
                {
                    "type": "TextBlock",
                    "text": f"Rating: {rating_stars} ({supplier_data.get('rating', 0)}/5)",
                    "spacing": "Small",
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {
                            "title": "ID:",
                            "value": supplier_data.get("supplier_id", "N/A"),
                        },
                        {
                            "title": "Estado:",
                            "value": supplier_data.get("status", "N/A"),
                        },
                        {
                            "title": "País:",
                            "value": supplier_data.get("country", "N/A"),
                        },
                        {
                            "title": "Ciudad:",
                            "value": supplier_data.get("city", "N/A"),
                        },
                        {
                            "title": "Email:",
                            "value": supplier_data.get("contact_email", "N/A"),
                        },
                    ],
                },
            ],
        }

    @staticmethod
    def create_list_card(
        title: str, items: List[Dict[str, Any]], item_type: str = "po"
    ) -> Dict[str, Any]:
        """Create card for displaying list of items."""
        body = [
            {
                "type": "TextBlock",
                "text": title,
                "size": "Large",
                "weight": "Bolder",
            }
        ]

        for item in items[:10]:  # Limit to 10 items
            if item_type == "po":
                text = f"**{item.get('po_number', 'N/A')}** - {item.get('supplier', 'N/A')} - {item.get('total_amount', 0)} {item.get('currency', 'USD')} - *{item.get('status', 'N/A')}*"
            elif item_type == "pr":
                text = f"**{item.get('pr_number', 'N/A')}** - {item.get('title', 'N/A')} - {item.get('total_amount', 0)} {item.get('currency', 'USD')} - *{item.get('status', 'N/A')}*"
            elif item_type == "supplier":
                text = f"**{item.get('name', 'N/A')}** - {item.get('country', 'N/A')} - *{item.get('status', 'N/A')}*"
            else:
                text = str(item)

            body.append({"type": "TextBlock", "text": text, "wrap": True})

        if len(items) > 10:
            body.append(
                {
                    "type": "TextBlock",
                    "text": f"... y {len(items) - 10} más",
                    "isSubtle": True,
                }
            )

        return {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": body,
        }

    @staticmethod
    def create_error_card(error_message: str) -> Dict[str, Any]:
        """Create error card."""
        return {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "❌ Error",
                    "size": "Large",
                    "weight": "Bolder",
                    "color": "Attention",
                },
                {
                    "type": "TextBlock",
                    "text": error_message,
                    "wrap": True,
                },
                {
                    "type": "TextBlock",
                    "text": "Por favor, intenta de nuevo o contacta a soporte si el problema persiste.",
                    "wrap": True,
                    "isSubtle": True,
                    "spacing": "Medium",
                },
            ],
        }

    @staticmethod
    def create_loading_card() -> Dict[str, Any]:
        """Create loading card."""
        return {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "⏳ Procesando tu solicitud...",
                    "size": "Medium",
                    "horizontalAlignment": "Center",
                },
                {
                    "type": "TextBlock",
                    "text": "Esto puede tomar unos segundos.",
                    "isSubtle": True,
                    "horizontalAlignment": "Center",
                },
            ],
        }

    @staticmethod
    def _format_line_items(line_items: List[Dict[str, Any]]) -> str:
        """Format line items as text."""
        if not line_items:
            return "No hay líneas de pedido disponibles."

        formatted = []
        for i, item in enumerate(line_items[:5], 1):
            formatted.append(
                f"{i}. {item.get('description', 'N/A')} - {item.get('quantity', 0)} unidades - {item.get('unit_price', 0)} c/u"
            )

        if len(line_items) > 5:
            formatted.append(f"... y {len(line_items) - 5} líneas más")

        return "\n".join(formatted)
