"""Azure Cognitive Search service for knowledge base queries."""

from typing import List, Dict, Any, Optional
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential

from src.config.settings import settings
from src.utils.logger import get_logger
from src.services.cache_service import cache_service

logger = get_logger(__name__)


class SearchService:
    """Service for Azure Cognitive Search integration."""

    def __init__(self):
        """Initialize search service."""
        self.client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index_name,
            credential=AzureKeyCredential(settings.azure_search_api_key),
        )

    async def search(
        self,
        query: str,
        filters: Optional[str] = None,
        top: int = 10,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base.

        Args:
            query: Search query
            filters: OData filter expression
            top: Number of results to return
            use_cache: Whether to use cache

        Returns:
            List of search results
        """
        try:
            # Generate cache key
            cache_key = cache_service._generate_key(
                "search", query=query, filters=filters, top=top
            )

            # Check cache
            if use_cache:
                cached_results = await cache_service.get(cache_key)
                if cached_results:
                    logger.info(f"Returning cached search results for: {query}")
                    return cached_results

            # Perform search
            results = []
            search_results = await self.client.search(
                search_text=query,
                filter=filters,
                top=top,
                include_total_count=True,
            )

            async for result in search_results:
                results.append(
                    {
                        "score": result.get("@search.score"),
                        "content": result.get("content"),
                        "title": result.get("title"),
                        "category": result.get("category"),
                        "metadata": result.get("metadata", {}),
                    }
                )

            logger.info(f"Search returned {len(results)} results for: {query}")

            # Cache results
            if use_cache and results:
                await cache_service.set(cache_key, results, ttl=1800)  # 30 minutes

            return results

        except Exception as e:
            logger.error(f"Search error: {e}")
            raise

    async def semantic_search(
        self,
        query: str,
        top: int = 5,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search for more contextual results.

        Args:
            query: Search query
            top: Number of results to return
            use_cache: Whether to use cache

        Returns:
            List of semantic search results
        """
        try:
            cache_key = cache_service._generate_key(
                "semantic_search", query=query, top=top
            )

            if use_cache:
                cached_results = await cache_service.get(cache_key)
                if cached_results:
                    return cached_results

            results = []
            search_results = await self.client.search(
                search_text=query,
                query_type="semantic",
                top=top,
                include_total_count=True,
            )

            async for result in search_results:
                results.append(
                    {
                        "score": result.get("@search.score"),
                        "reranker_score": result.get("@search.reranker_score"),
                        "content": result.get("content"),
                        "title": result.get("title"),
                        "captions": result.get("@search.captions", []),
                    }
                )

            logger.info(
                f"Semantic search returned {len(results)} results for: {query}"
            )

            if use_cache and results:
                await cache_service.set(cache_key, results, ttl=1800)

            return results

        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return await self.search(query, top=top, use_cache=use_cache)

    async def suggest(
        self, query: str, suggester_name: str = "sg", top: int = 5
    ) -> List[str]:
        """
        Get search suggestions.

        Args:
            query: Partial query
            suggester_name: Name of the suggester
            top: Number of suggestions

        Returns:
            List of suggestions
        """
        try:
            suggestions = []
            suggest_results = await self.client.suggest(
                search_text=query, suggester_name=suggester_name, top=top
            )

            async for suggestion in suggest_results:
                suggestions.append(suggestion.get("text"))

            logger.debug(f"Generated {len(suggestions)} suggestions for: {query}")
            return suggestions

        except Exception as e:
            logger.error(f"Suggestion error: {e}")
            return []

    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document data or None
        """
        try:
            document = await self.client.get_document(key=document_id)
            return document
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {e}")
            return None

    async def search_with_facets(
        self,
        query: str,
        facets: List[str],
        filters: Optional[str] = None,
        top: int = 10,
    ) -> Dict[str, Any]:
        """
        Search with faceted navigation.

        Args:
            query: Search query
            facets: List of fields to facet on
            filters: OData filter expression
            top: Number of results

        Returns:
            Dict with results and facets
        """
        try:
            results = []
            facet_results = {}

            search_results = await self.client.search(
                search_text=query,
                filter=filters,
                facets=facets,
                top=top,
                include_total_count=True,
            )

            async for result in search_results:
                results.append(result)

            # Get facets if available
            if hasattr(search_results, "get_facets"):
                facet_results = await search_results.get_facets()

            return {
                "results": results,
                "facets": facet_results,
                "count": len(results),
            }

        except Exception as e:
            logger.error(f"Faceted search error: {e}")
            raise


# Global search service instance
search_service = SearchService()
