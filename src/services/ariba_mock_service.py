"""Mock SAP Ariba service for development and testing."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
import random

from src.models.ariba_models import (
    AribaResponse,
    PurchaseOrder,
    PurchaseRequisition,
    Supplier,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AribaMockService:
    """Mock implementation of Ariba service for development."""

    def __init__(self):
        """Initialize mock Ariba service with sample data."""
        self._init_mock_data()

    def _init_mock_data(self):
        """Initialize mock data."""
        # Mock Suppliers
        self.mock_suppliers = [
            {
                "supplier_id": "SUP-001",
                "name": "Acme Corporation",
                "status": "Active",
                "country": "España",
                "city": "Madrid",
                "contact_email": "contact@acme.com",
                "contact_phone": "+34 91 123 4567",
                "rating": 4.5,
                "created_date": datetime.now() - timedelta(days=365),
                "metadata": {"industry": "Technology"},
            },
            {
                "supplier_id": "SUP-002",
                "name": "Global Tech Solutions",
                "status": "Active",
                "country": "España",
                "city": "Barcelona",
                "contact_email": "info@globaltech.com",
                "contact_phone": "+34 93 987 6543",
                "rating": 4.8,
                "created_date": datetime.now() - timedelta(days=200),
                "metadata": {"industry": "IT Services"},
            },
            {
                "supplier_id": "SUP-003",
                "name": "Office Supplies Pro",
                "status": "Active",
                "country": "España",
                "city": "Valencia",
                "contact_email": "ventas@officesupplies.es",
                "contact_phone": "+34 96 555 1234",
                "rating": 4.2,
                "created_date": datetime.now() - timedelta(days=180),
                "metadata": {"industry": "Office Supplies"},
            },
        ]

        # Mock Purchase Orders
        self.mock_purchase_orders = [
            {
                "po_number": "PO-2024-001",
                "pr_number": "PR-2024-001",
                "supplier": "Acme Corporation",
                "supplier_id": "SUP-001",
                "status": "Approved",
                "created_date": datetime.now() - timedelta(days=10),
                "delivery_date": datetime.now() + timedelta(days=20),
                "total_amount": Decimal("15000.00"),
                "currency": "EUR",
                "payment_terms": "Net 30",
                "shipping_address": "Calle Principal 123, Madrid, España",
                "line_items": [
                    {
                        "line_number": 1,
                        "description": "Laptops Dell XPS 15",
                        "quantity": 10,
                        "unit_price": Decimal("1200.00"),
                        "total": Decimal("12000.00"),
                    },
                    {
                        "line_number": 2,
                        "description": "Monitores LG 27 pulgadas",
                        "quantity": 15,
                        "unit_price": Decimal("200.00"),
                        "total": Decimal("3000.00"),
                    },
                ],
                "metadata": {"project": "IT Modernization"},
            },
            {
                "po_number": "PO-2024-002",
                "pr_number": "PR-2024-002",
                "supplier": "Global Tech Solutions",
                "supplier_id": "SUP-002",
                "status": "Pending",
                "created_date": datetime.now() - timedelta(days=5),
                "delivery_date": datetime.now() + timedelta(days=15),
                "total_amount": Decimal("8500.00"),
                "currency": "EUR",
                "payment_terms": "Net 45",
                "shipping_address": "Avenida Diagonal 456, Barcelona, España",
                "line_items": [
                    {
                        "line_number": 1,
                        "description": "Licencias Microsoft 365",
                        "quantity": 50,
                        "unit_price": Decimal("120.00"),
                        "total": Decimal("6000.00"),
                    },
                    {
                        "line_number": 2,
                        "description": "Soporte técnico anual",
                        "quantity": 1,
                        "unit_price": Decimal("2500.00"),
                        "total": Decimal("2500.00"),
                    },
                ],
                "metadata": {"project": "Software Renewal"},
            },
            {
                "po_number": "PO-2024-003",
                "supplier": "Office Supplies Pro",
                "supplier_id": "SUP-003",
                "status": "Delivered",
                "created_date": datetime.now() - timedelta(days=30),
                "delivery_date": datetime.now() - timedelta(days=5),
                "total_amount": Decimal("1200.00"),
                "currency": "EUR",
                "payment_terms": "Net 15",
                "shipping_address": "Calle Valencia 789, Valencia, España",
                "line_items": [
                    {
                        "line_number": 1,
                        "description": "Papel A4 (100 paquetes)",
                        "quantity": 100,
                        "unit_price": Decimal("5.00"),
                        "total": Decimal("500.00"),
                    },
                    {
                        "line_number": 2,
                        "description": "Bolígrafos (50 cajas)",
                        "quantity": 50,
                        "unit_price": Decimal("10.00"),
                        "total": Decimal("500.00"),
                    },
                    {
                        "line_number": 3,
                        "description": "Carpetas archivadoras",
                        "quantity": 20,
                        "unit_price": Decimal("10.00"),
                        "total": Decimal("200.00"),
                    },
                ],
                "metadata": {"department": "Administration"},
            },
        ]

        # Mock Purchase Requisitions
        self.mock_purchase_requisitions = [
            {
                "pr_number": "PR-2024-001",
                "title": "Equipamiento IT Q1 2024",
                "requester": "Juan García",
                "status": "Approved",
                "created_date": datetime.now() - timedelta(days=15),
                "total_amount": Decimal("15000.00"),
                "currency": "EUR",
                "urgency": "High",
                "department": "IT",
                "cost_center": "CC-IT-001",
                "description": "Renovación de equipos informáticos para el equipo de desarrollo",
                "line_items": [
                    {
                        "line_number": 1,
                        "description": "Laptops Dell XPS 15",
                        "quantity": 10,
                        "estimated_unit_price": Decimal("1200.00"),
                        "estimated_total": Decimal("12000.00"),
                    },
                    {
                        "line_number": 2,
                        "description": "Monitores LG 27 pulgadas",
                        "quantity": 15,
                        "estimated_unit_price": Decimal("200.00"),
                        "estimated_total": Decimal("3000.00"),
                    },
                ],
                "approvers": ["María López", "Carlos Rodríguez"],
                "metadata": {"project_code": "PROJ-2024-IT"},
            },
            {
                "pr_number": "PR-2024-002",
                "title": "Licencias Software 2024",
                "requester": "Ana Martínez",
                "status": "Pending Approval",
                "created_date": datetime.now() - timedelta(days=7),
                "total_amount": Decimal("8500.00"),
                "currency": "EUR",
                "urgency": "Medium",
                "department": "IT",
                "cost_center": "CC-IT-001",
                "description": "Renovación de licencias Microsoft 365 y soporte",
                "line_items": [
                    {
                        "line_number": 1,
                        "description": "Licencias Microsoft 365",
                        "quantity": 50,
                        "estimated_unit_price": Decimal("120.00"),
                        "estimated_total": Decimal("6000.00"),
                    },
                    {
                        "line_number": 2,
                        "description": "Soporte técnico anual",
                        "quantity": 1,
                        "estimated_unit_price": Decimal("2500.00"),
                        "estimated_total": Decimal("2500.00"),
                    },
                ],
                "approvers": ["María López"],
                "metadata": {"project_code": "PROJ-2024-SOFT"},
            },
            {
                "pr_number": "PR-2024-003",
                "title": "Material de oficina Q1",
                "requester": "Pedro Sánchez",
                "status": "Draft",
                "created_date": datetime.now() - timedelta(days=2),
                "total_amount": Decimal("500.00"),
                "currency": "EUR",
                "urgency": "Low",
                "department": "Administration",
                "cost_center": "CC-ADMIN-001",
                "description": "Material de oficina estándar para el trimestre",
                "line_items": [
                    {
                        "line_number": 1,
                        "description": "Papel, bolígrafos y material variado",
                        "quantity": 1,
                        "estimated_unit_price": Decimal("500.00"),
                        "estimated_total": Decimal("500.00"),
                    },
                ],
                "approvers": ["Laura Fernández"],
                "metadata": {"recurring": "quarterly"},
            },
        ]

    async def get_purchase_orders(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 20,
        use_cache: bool = True,
    ) -> AribaResponse:
        """
        Get mock purchase orders.

        Args:
            filters: Filter criteria (e.g., status, supplier)
            page: Page number
            page_size: Items per page
            use_cache: Ignored in mock

        Returns:
            AribaResponse with purchase orders
        """
        logger.info("🎭 Using MOCK Ariba service - get_purchase_orders")

        # Apply filters
        filtered_pos = self.mock_purchase_orders.copy()

        if filters:
            if "status" in filters:
                filtered_pos = [
                    po for po in filtered_pos if po["status"] == filters["status"]
                ]
            if "supplier_id" in filters:
                filtered_pos = [
                    po
                    for po in filtered_pos
                    if po["supplier_id"] == filters["supplier_id"]
                ]

        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_pos = filtered_pos[start_idx:end_idx]

        response = AribaResponse(
            records=paginated_pos,
            total_count=len(filtered_pos),
            page=page,
            page_size=page_size,
        )

        logger.info(f"Returning {len(paginated_pos)} mock purchase orders")
        return response

    async def get_purchase_order_by_id(
        self, po_number: str, use_cache: bool = True
    ) -> Optional[PurchaseOrder]:
        """
        Get a specific mock purchase order by ID.

        Args:
            po_number: Purchase order number
            use_cache: Ignored in mock

        Returns:
            PurchaseOrder or None
        """
        logger.info(f"🎭 Using MOCK Ariba service - get_purchase_order: {po_number}")

        # Find PO by number
        for po_data in self.mock_purchase_orders:
            if po_data["po_number"] == po_number:
                # Convert to PurchaseOrder model
                po = PurchaseOrder(**po_data)
                logger.info(f"Found mock PO: {po_number}")
                return po

        logger.warning(f"Mock PO not found: {po_number}")
        return None

    async def get_purchase_requisitions(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 20,
        use_cache: bool = True,
    ) -> AribaResponse:
        """
        Get mock purchase requisitions.

        Args:
            filters: Filter criteria
            page: Page number
            page_size: Items per page
            use_cache: Ignored in mock

        Returns:
            AribaResponse with purchase requisitions
        """
        logger.info("🎭 Using MOCK Ariba service - get_purchase_requisitions")

        # Apply filters
        filtered_prs = self.mock_purchase_requisitions.copy()

        if filters:
            if "status" in filters:
                filtered_prs = [
                    pr for pr in filtered_prs if pr["status"] == filters["status"]
                ]
            if "requester" in filters:
                filtered_prs = [
                    pr for pr in filtered_prs if pr["requester"] == filters["requester"]
                ]

        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_prs = filtered_prs[start_idx:end_idx]

        response = AribaResponse(
            records=paginated_prs,
            total_count=len(filtered_prs),
            page=page,
            page_size=page_size,
        )

        logger.info(f"Returning {len(paginated_prs)} mock purchase requisitions")
        return response

    async def get_suppliers(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 20,
        use_cache: bool = True,
    ) -> AribaResponse:
        """
        Get mock suppliers.

        Args:
            filters: Filter criteria
            page: Page number
            page_size: Items per page
            use_cache: Ignored in mock

        Returns:
            AribaResponse with suppliers
        """
        logger.info("🎭 Using MOCK Ariba service - get_suppliers")

        # Apply filters
        filtered_suppliers = self.mock_suppliers.copy()

        if filters:
            if "status" in filters:
                filtered_suppliers = [
                    s for s in filtered_suppliers if s["status"] == filters["status"]
                ]
            if "country" in filters:
                filtered_suppliers = [
                    s for s in filtered_suppliers if s["country"] == filters["country"]
                ]

        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_suppliers = filtered_suppliers[start_idx:end_idx]

        response = AribaResponse(
            records=paginated_suppliers,
            total_count=len(filtered_suppliers),
            page=page,
            page_size=page_size,
        )

        logger.info(f"Returning {len(paginated_suppliers)} mock suppliers")
        return response

    async def search_documents(
        self, query: str, document_type: str = "all", use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for mock documents.

        Args:
            query: Search query
            document_type: Type of documents to search
            use_cache: Ignored in mock

        Returns:
            List of matching documents
        """
        logger.info(
            f"🎭 Using MOCK Ariba service - search_documents: '{query}' (type: {document_type})"
        )

        results = []
        query_lower = query.lower()

        # Search in purchase orders
        if document_type in ["all", "po", "purchase_order"]:
            for po in self.mock_purchase_orders:
                if (
                    query_lower in po["po_number"].lower()
                    or query_lower in po["supplier"].lower()
                    or any(
                        query_lower in item["description"].lower()
                        for item in po["line_items"]
                    )
                ):
                    results.append(
                        {
                            "type": "purchase_order",
                            "id": po["po_number"],
                            "title": f"PO {po['po_number']} - {po['supplier']}",
                            "data": po,
                        }
                    )

        # Search in purchase requisitions
        if document_type in ["all", "pr", "purchase_requisition"]:
            for pr in self.mock_purchase_requisitions:
                if (
                    query_lower in pr["pr_number"].lower()
                    or query_lower in pr["title"].lower()
                    or query_lower in (pr.get("description") or "").lower()
                ):
                    results.append(
                        {
                            "type": "purchase_requisition",
                            "id": pr["pr_number"],
                            "title": f"PR {pr['pr_number']} - {pr['title']}",
                            "data": pr,
                        }
                    )

        # Search in suppliers
        if document_type in ["all", "supplier"]:
            for supplier in self.mock_suppliers:
                if query_lower in supplier["name"].lower() or query_lower in supplier[
                    "supplier_id"
                ].lower():
                    results.append(
                        {
                            "type": "supplier",
                            "id": supplier["supplier_id"],
                            "title": f"Supplier {supplier['name']}",
                            "data": supplier,
                        }
                    )

        logger.info(f"Search returned {len(results)} mock results")
        return results

    async def create_purchase_requisition(
        self, requisition_data: Dict[str, Any]
    ) -> PurchaseRequisition:
        """
        Create a mock purchase requisition.

        Args:
            requisition_data: PR data

        Returns:
            Created PurchaseRequisition
        """
        logger.info("🎭 Using MOCK Ariba service - create_purchase_requisition")

        # Generate mock PR number
        pr_number = f"PR-2024-{len(self.mock_purchase_requisitions) + 1:03d}"

        # Create PR data
        pr_data = {
            "pr_number": pr_number,
            "title": requisition_data.get("title", "New Purchase Requisition"),
            "requester": requisition_data.get("requester", "Mock User"),
            "status": "Draft",
            "created_date": datetime.now(),
            "total_amount": Decimal(str(requisition_data.get("total_amount", 0))),
            "currency": requisition_data.get("currency", "EUR"),
            "urgency": requisition_data.get("urgency", "Medium"),
            "department": requisition_data.get("department", "General"),
            "cost_center": requisition_data.get("cost_center", "CC-GEN-001"),
            "description": requisition_data.get("description", ""),
            "line_items": requisition_data.get("line_items", []),
            "approvers": requisition_data.get("approvers", []),
            "metadata": requisition_data.get("metadata", {}),
        }

        # Add to mock data
        self.mock_purchase_requisitions.append(pr_data)

        pr = PurchaseRequisition(**pr_data)
        logger.info(f"Created mock PR: {pr_number}")
        return pr

    async def get_document_status(
        self, document_id: str, document_type: str
    ) -> Dict[str, Any]:
        """
        Get mock status of a document.

        Args:
            document_id: Document ID
            document_type: Type of document

        Returns:
            Status information
        """
        logger.info(
            f"🎭 Using MOCK Ariba service - get_document_status: {document_type} {document_id}"
        )

        # Mock status responses
        statuses = {
            "po": {
                "document_id": document_id,
                "status": "Approved",
                "workflow_state": "Completed",
                "approval_date": datetime.now() - timedelta(days=5),
                "approvers": [
                    {"name": "María López", "status": "Approved", "date": datetime.now() - timedelta(days=6)},
                    {"name": "Carlos Rodríguez", "status": "Approved", "date": datetime.now() - timedelta(days=5)},
                ],
            },
            "pr": {
                "document_id": document_id,
                "status": "Pending Approval",
                "workflow_state": "In Progress",
                "submitted_date": datetime.now() - timedelta(days=3),
                "approvers": [
                    {"name": "María López", "status": "Pending", "date": None},
                ],
            },
        }

        doc_type = document_type.lower()
        if doc_type in statuses:
            return statuses[doc_type]

        return {
            "document_id": document_id,
            "status": "Unknown",
            "message": "Document type not supported in mock",
        }


# Global mock Ariba service instance
ariba_mock_service = AribaMockService()
