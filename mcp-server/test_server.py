#!/usr/bin/env python3
"""Test script for FleetPulse MCP Server.

This script tests the MCP server functionality by importing and calling
the tool functions directly, without going through the MCP protocol.
"""

import asyncio
import sys
import os

# Add the current directory to Python path to import server modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import FleetPulseAPI, format_fleet_overview, format_vehicles_list


async def test_api_connection():
    """Test basic API connectivity."""
    print("🔗 Testing FleetPulse API connection...")
    
    api_client = FleetPulseAPI("http://localhost:8080/api")
    
    try:
        # Test health endpoint
        health = api_client._make_request("/health")
        print(f"✅ API Health: {health}")
        return True
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        print("   Make sure the FleetPulse backend is running at http://localhost:8080")
        return False


async def test_fleet_overview():
    """Test fleet overview functionality."""
    print("\n📊 Testing fleet overview...")
    
    api_client = FleetPulseAPI("http://localhost:8080/api")
    
    try:
        data = api_client.get_fleet_overview()
        print(f"✅ Raw data: {data}")
        
        formatted = format_fleet_overview(data)
        print(f"✅ Formatted output:\n{formatted}")
        return True
    except Exception as e:
        print(f"❌ Fleet overview test failed: {e}")
        return False


async def test_vehicles_list():
    """Test vehicles list functionality."""
    print("\n🚗 Testing vehicles list...")
    
    api_client = FleetPulseAPI("http://localhost:8080/api")
    
    try:
        data = api_client.get_vehicles()
        print(f"✅ Found {len(data)} vehicles")
        
        formatted = format_vehicles_list(data)
        print(f"✅ Formatted output:\n{formatted[:500]}...")  # Truncate for readability
        return True
    except Exception as e:
        print(f"❌ Vehicles list test failed: {e}")
        return False


async def test_natural_language_query():
    """Test natural language query functionality."""
    print("\n🤖 Testing natural language query...")
    
    api_client = FleetPulseAPI("http://localhost:8080/api")
    
    try:
        test_question = "Which location has the best safety scores?"
        data = api_client.query_fleet(test_question)
        print(f"✅ Query: '{test_question}'")
        print(f"✅ Response: {data.get('response', 'No response')}")
        
        if data.get('insights'):
            print("✅ Insights found:")
            for insight in data['insights'][:3]:
                print(f"   • {insight}")
        
        return True
    except Exception as e:
        print(f"❌ Natural language query test failed: {e}")
        return False


async def test_safety_scores():
    """Test safety scores functionality."""
    print("\n🛡️ Testing safety scores...")
    
    api_client = FleetPulseAPI("http://localhost:8080/api")
    
    try:
        data = api_client.get_safety_scores()
        print(f"✅ Found safety data for {len(data)} drivers/vehicles")
        
        if data:
            best_score = max(data, key=lambda x: x.get('score', 0))
            print(f"✅ Best performer: {best_score.get('vehicle_name', 'Unknown')} with {best_score.get('score', 0):.1f}%")
        
        return True
    except Exception as e:
        print(f"❌ Safety scores test failed: {e}")
        return False


async def test_recommendations():
    """Test AI recommendations functionality."""
    print("\n💡 Testing AI recommendations...")
    
    api_client = FleetPulseAPI("http://localhost:8080/api")
    
    try:
        data = api_client.get_recommendations()
        print(f"✅ Found {len(data)} recommendations")
        
        if data:
            for rec in data[:2]:  # Show first 2
                print(f"   • {rec.get('title', 'Untitled')} ({rec.get('priority', 'medium')} priority)")
        
        return True
    except Exception as e:
        print(f"❌ Recommendations test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 FleetPulse MCP Server Test Suite")
    print("=" * 50)
    
    tests = [
        ("API Connection", test_api_connection),
        ("Fleet Overview", test_fleet_overview),
        ("Vehicles List", test_vehicles_list),
        ("Natural Language Query", test_natural_language_query),
        ("Safety Scores", test_safety_scores),
        ("AI Recommendations", test_recommendations)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📋 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The MCP server is working correctly.")
        print("\n📋 Next steps:")
        print("1. Copy the configuration to Claude Desktop:")
        print("   ~/.config/claude-desktop/config.json (Linux)")
        print("   ~/Library/Application Support/Claude/config.json (macOS)")
        print("2. Restart Claude Desktop")
        print("3. Look for 'FleetPulse' in the MCP servers list")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Check the FleetPulse backend.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)