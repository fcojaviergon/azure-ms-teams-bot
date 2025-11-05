"""SAP Ariba data models."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AribaRequest(BaseModel):
    """Base model for Ariba API requests."""

    realm: str
    user_id: str
    filters: Optional[Dict[str, Any]] = None
    fields: Optional[List[str]] = None
    page: int = 1
    page_size: int = 20


class AribaResponse(BaseModel):
    """Base model for Ariba API responses."""

    records: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Supplier(BaseModel):
    """Supplier information."""

    supplier_id: str
    name: str
    status: str
    country: Optional[str] = None
    city: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    rating: Optional[float] = None
    created_date: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PurchaseRequisition(BaseModel):
    """Purchase Requisition model."""

    pr_number: str
    title: str
    requester: str
    status: str
    created_date: datetime
    total_amount: Decimal
    currency: str
    urgency: Optional[str] = None
    department: Optional[str] = None
    cost_center: Optional[str] = None
    description: Optional[str] = None
    line_items: List[Dict[str, Any]] = Field(default_factory=list)
    approvers: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PurchaseOrder(BaseModel):
    """Purchase Order model."""

    po_number: str
    pr_number: Optional[str] = None
    supplier: str
    supplier_id: str
    status: str
    created_date: datetime
    delivery_date: Optional[datetime] = None
    total_amount: Decimal
    currency: str
    payment_terms: Optional[str] = None
    shipping_address: Optional[str] = None
    line_items: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Invoice(BaseModel):
    """Invoice model."""

    invoice_number: str
    po_number: str
    supplier: str
    status: str
    invoice_date: datetime
    due_date: Optional[datetime] = None
    total_amount: Decimal
    currency: str
    payment_status: str
    line_items: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Contract(BaseModel):
    """Contract model."""

    contract_id: str
    title: str
    supplier: str
    status: str
    start_date: datetime
    end_date: datetime
    contract_value: Decimal
    currency: str
    contract_type: str
    owner: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
