"""SAP Ariba integration service with OAuth2 and caching."""

from typing import List, Dict, Any, Optional
from decimal import Decimal
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.config.settings import settings
from src.utils.logger import get_logger
from src.services.cache_service import cache_service
from src.services.auth_service import auth_service
from src.models.ariba_models import (
    AribaRequest,
    AribaResponse,
    PurchaseOrder,
    PurchaseRequisition,
    Supplier,
)

logger = get_logger(__name__)


class AribaService:
    """Service for SAP Ariba API integration."""

    def __init__(self):
        """Initialize Ariba service."""
        self.base_url = settings.ariba_api_base_url
        self.realm = settings.ariba_realm
        self.api_key = settings.ariba_api_key

    async def _get_headers(self) -> Dict[str, str]:
        """
        Get headers with OAuth2 token.

        Returns:
            Headers dict with authorization
        """
        token = await auth_service.get_ariba_token()
        return {
            "Authorization": f"Bearer {token}",
            "X-ARIBA-Network-Id": self.realm,
            "apiKey": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Ariba API with retry logic.

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON payload

        Returns:
            Response data

        Raises:
            httpx.HTTPStatusError: On HTTP errors after retries
        """
        url = f"{self.base_url}{endpoint}"
        headers = await self._get_headers()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
            )

            # Handle token expiration
            if response.status_code == 401:
                logger.warning("Token expired, refreshing...")
                token = await auth_service.get_ariba_token(force_refresh=True)
                headers["Authorization"] = f"Bearer {token}"

                # Retry request with new token
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                )

            response.raise_for_status()
            return response.json()

    async def get_purchase_orders(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 20,
        use_cache: bool = True,
    ) -> AribaResponse:
        """
        Get purchase orders from Ariba.

        Args:
            filters: Filter criteria
            page: Page number
            page_size: Items per page
            use_cache: Whether to use cache

        Returns:
            AribaResponse with purchase orders
        """
        try:
            cache_key = cache_service._generate_key(
                "ariba:po", filters=filters, page=page, page_size=page_size
            )

            if use_cache:
                cached_data = await cache_service.get(cache_key)
                if cached_data:
                    logger.info("Returning cached purchase orders")
                    return AribaResponse(**cached_data)

            # Make API request
            params = {
                "realm": self.realm,
                "page": page,
                "pageSize": page_size,
            }
            if filters:
                params.update(filters)

            data = await self._make_request(
                "GET", "/api/purchase-orders", params=params
            )

            response = AribaResponse(
                records=data.get("records", []),
                total_count=data.get("totalCount", 0),
                page=page,
                page_size=page_size,
            )

            # Cache results
            if use_cache:
                await cache_service.set(
                    cache_key, response.model_dump(), ttl=settings.cache_ttl_seconds
                )

            logger.info(
                f"Retrieved {len(response.records)} purchase orders from Ariba"
            )
            return response

        except Exception as e:
            logger.error(f"Error getting purchase orders: {e}")
            raise

    async def get_purchase_order_by_id(
        self, po_number: str, use_cache: bool = True
    ) -> Optional[PurchaseOrder]:
        """
        Get a specific purchase order by ID.

        Args:
            po_number: Purchase order number
            use_cache: Whether to use cache

        Returns:
            PurchaseOrder or None
        """
        try:
            cache_key = f"ariba:po:{po_number}"

            if use_cache:
                cached_data = await cache_service.get(cache_key)
                if cached_data:
                    logger.info(f"Returning cached PO: {po_number}")
                    return PurchaseOrder(**cached_data)

            data = await self._make_request(
                "GET", f"/api/purchase-orders/{po_number}"
            )

            po = PurchaseOrder(
                po_number=data["poNumber"],
                supplier=data["supplier"]["name"],
                supplier_id=data["supplier"]["id"],
                status=data["status"],
                created_date=data["createdDate"],
                total_amount=Decimal(str(data["totalAmount"])),
                currency=data["currency"],
                line_items=data.get("lineItems", []),
                metadata=data.get("metadata", {}),
            )

            if use_cache:
                await cache_service.set(cache_key, po.model_dump(), ttl=3600)

            logger.info(f"Retrieved PO: {po_number}")
            return po

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Purchase order not found: {po_number}")
                return None
            raise
        except Exception as e:
            logger.error(f"Error getting purchase order {po_number}: {e}")
            raise

    async def get_purchase_requisitions(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 20,
        use_cache: bool = True,
    ) -> AribaResponse:
        """
        Get purchase requisitions from Ariba.

        Args:
            filters: Filter criteria
            page: Page number
            page_size: Items per page
            use_cache: Whether to use cache

        Returns:
            AribaResponse with purchase requisitions
        """
        try:
            cache_key = cache_service._generate_key(
                "ariba:pr", filters=filters, page=page, page_size=page_size
            )

            if use_cache:
                cached_data = await cache_service.get(cache_key)
                if cached_data:
                    return AribaResponse(**cached_data)

            params = {
                "realm": self.realm,
                "page": page,
                "pageSize": page_size,
            }
            if filters:
                params.update(filters)

            data = await self._make_request(
                "GET", "/api/purchase-requisitions", params=params
            )

            response = AribaResponse(
                records=data.get("records", []),
                total_count=data.get("totalCount", 0),
                page=page,
                page_size=page_size,
            )

            if use_cache:
                await cache_service.set(cache_key, response.model_dump(), ttl=1800)

            logger.info(
                f"Retrieved {len(response.records)} purchase requisitions from Ariba"
            )
            return response

        except Exception as e:
            logger.error(f"Error getting purchase requisitions: {e}")
            raise

    async def get_suppliers(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 20,
        use_cache: bool = True,
    ) -> AribaResponse:
        """
        Get suppliers from Ariba.

        Args:
            filters: Filter criteria
            page: Page number
            page_size: Items per page
            use_cache: Whether to use cache

        Returns:
            AribaResponse with suppliers
        """
        try:
            cache_key = cache_service._generate_key(
                "ariba:suppliers", filters=filters, page=page, page_size=page_size
            )

            if use_cache:
                cached_data = await cache_service.get(cache_key)
                if cached_data:
                    return AribaResponse(**cached_data)

            params = {
                "realm": self.realm,
                "page": page,
                "pageSize": page_size,
            }
            if filters:
                params.update(filters)

            data = await self._make_request("GET", "/api/suppliers", params=params)

            response = AribaResponse(
                records=data.get("records", []),
                total_count=data.get("totalCount", 0),
                page=page,
                page_size=page_size,
            )

            if use_cache:
                await cache_service.set(cache_key, response.model_dump(), ttl=7200)

            logger.info(f"Retrieved {len(response.records)} suppliers from Ariba")
            return response

        except Exception as e:
            logger.error(f"Error getting suppliers: {e}")
            raise

    async def search_documents(
        self, query: str, document_type: str = "all", use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for documents across Ariba.

        Args:
            query: Search query
            document_type: Type of documents to search
            use_cache: Whether to use cache

        Returns:
            List of matching documents
        """
        try:
            cache_key = cache_service._generate_key(
                "ariba:search", query=query, doc_type=document_type
            )

            if use_cache:
                cached_results = await cache_service.get(cache_key)
                if cached_results:
                    return cached_results

            params = {
                "realm": self.realm,
                "query": query,
                "type": document_type,
            }

            data = await self._make_request("GET", "/api/search", params=params)
            results = data.get("results", [])

            if use_cache:
                await cache_service.set(cache_key, results, ttl=600)

            logger.info(
                f"Search returned {len(results)} results for query: {query}"
            )
            return results

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

    async def create_purchase_requisition(
        self, requisition_data: Dict[str, Any]
    ) -> PurchaseRequisition:
        """
        Create a new purchase requisition.

        Args:
            requisition_data: PR data

        Returns:
            Created PurchaseRequisition
        """
        try:
            data = await self._make_request(
                "POST",
                "/api/purchase-requisitions",
                json_data=requisition_data,
            )

            pr = PurchaseRequisition(
                pr_number=data["prNumber"],
                title=data["title"],
                requester=data["requester"],
                status=data["status"],
                created_date=data["createdDate"],
                total_amount=Decimal(str(data["totalAmount"])),
                currency=data["currency"],
                line_items=data.get("lineItems", []),
            )

            logger.info(f"Created purchase requisition: {pr.pr_number}")
            return pr

        except Exception as e:
            logger.error(f"Error creating purchase requisition: {e}")
            raise

    async def get_document_status(
        self, document_id: str, document_type: str
    ) -> Dict[str, Any]:
        """
        Get status of a document.

        Args:
            document_id: Document ID
            document_type: Type of document (po, pr, invoice, etc.)

        Returns:
            Status information
        """
        try:
            endpoint_map = {
                "po": "/api/purchase-orders",
                "pr": "/api/purchase-requisitions",
                "invoice": "/api/invoices",
                "contract": "/api/contracts",
            }

            endpoint = endpoint_map.get(document_type.lower())
            if not endpoint:
                raise ValueError(f"Unknown document type: {document_type}")

            data = await self._make_request("GET", f"{endpoint}/{document_id}/status")

            logger.info(f"Retrieved status for {document_type}: {document_id}")
            return data

        except Exception as e:
            logger.error(
                f"Error getting status for {document_type} {document_id}: {e}"
            )
            raise


# Global Ariba service instance
ariba_service = AribaService()
