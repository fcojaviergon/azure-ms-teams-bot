#!/usr/bin/env python
"""Script para probar la conectividad de los servicios."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.services.cache_service import cache_service
from src.services.auth_service import auth_service
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def test_redis():
    """Test Redis connection."""
    print("\n🔍 Testing Redis connection...")
    try:
        await cache_service.connect()
        if cache_service.client:
            await cache_service.client.ping()
            print("✅ Redis: Connected")

            # Test set/get
            await cache_service.set("test_key", {"test": "value"}, ttl=10)
            value = await cache_service.get("test_key")
            if value:
                print("✅ Redis: Set/Get works")

            await cache_service.delete("test_key")
            await cache_service.disconnect()
            return True
        else:
            print("❌ Redis: Not connected")
            return False
    except Exception as e:
        print(f"❌ Redis: Error - {e}")
        return False


async def test_ariba_auth():
    """Test Ariba authentication."""
    print("\n🔍 Testing SAP Ariba authentication...")
    try:
        token = await auth_service.get_ariba_token()
        if token:
            print("✅ Ariba: OAuth2 token obtained")

            # Validate token
            is_valid = await auth_service.validate_token(token)
            if is_valid:
                print("✅ Ariba: Token is valid")
            return True
        else:
            print("❌ Ariba: Failed to get token")
            return False
    except Exception as e:
        print(f"❌ Ariba: Error - {e}")
        return False


async def test_openai():
    """Test OpenAI connection."""
    print("\n🔍 Testing Azure OpenAI...")
    try:
        from src.services.openai_service import openai_service

        # Simple test
        response = await openai_service.generate_response(
            "Hello, this is a test",
            temperature=0.3,
            max_tokens=50
        )

        if response:
            print("✅ OpenAI: Connected and responding")
            print(f"   Sample response: {response[:100]}...")
            return True
        else:
            print("❌ OpenAI: No response")
            return False
    except Exception as e:
        print(f"❌ OpenAI: Error - {e}")
        return False


async def test_search():
    """Test Cognitive Search."""
    print("\n🔍 Testing Azure Cognitive Search...")
    try:
        from src.services.search_service import search_service

        # Try a simple search
        results = await search_service.search("test", top=1, use_cache=False)

        print("✅ Cognitive Search: Connected")
        print(f"   Search returned {len(results)} results")
        return True
    except Exception as e:
        print(f"❌ Cognitive Search: Error - {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("🔧 Azure Teams Bot - Service Connectivity Test")
    print("=" * 60)

    print(f"\n📋 Configuration:")
    print(f"   Environment: {settings.environment}")
    print(f"   OpenAI Endpoint: {settings.azure_openai_endpoint}")
    print(f"   Search Endpoint: {settings.azure_search_endpoint}")
    print(f"   Redis Host: {settings.redis_host}")
    print(f"   Ariba API: {settings.ariba_api_base_url}")

    results = {}

    # Test each service
    results["redis"] = await test_redis()
    results["ariba"] = await test_ariba_auth()
    results["openai"] = await test_openai()
    results["search"] = await test_search()

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for service, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {service.upper()}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All services are working correctly!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} service(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
