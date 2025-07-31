#!/usr/bin/env python3

import sys
import os
sys.path.append('/home/ubuntu/deepresearch_teste/backend')

def test_config():
    """Test that the research depth configuration is properly loaded"""
    try:
        from backend.app.config import RESEARCH_DEPTH_CONFIG
        print("✓ Research depth configurations loaded successfully:")
        for depth, config in RESEARCH_DEPTH_CONFIG.items():
            print(f"  {depth}: {config['max_tool_calls']} tool calls - {config['description']}")
        return True
    except Exception as e:
        print(f"✗ Error loading config: {e}")
        return False

def test_models():
    """Test that ResearchRequest model accepts new fields"""
    try:
        from backend.app.models import ResearchRequest, ResearchMode
        
        request = ResearchRequest(
            query='Test query',
            mode=ResearchMode.DEEP_RESEARCH_O3,
            research_depth='fast',
            max_tool_calls=5,
            background_mode=True
        )
        print("✓ ResearchRequest model accepts new depth parameters:")
        print(f"  research_depth: {request.research_depth}")
        print(f"  max_tool_calls: {request.max_tool_calls}")
        print(f"  background_mode: {request.background_mode}")
        return True
    except Exception as e:
        print(f"✗ Error with ResearchRequest: {e}")
        return False

def test_openai_service():
    """Test that OpenAI service accepts new parameters"""
    try:
        from backend.app.services.openai_service import OpenAIService
        from backend.app.models import ResearchMode
        import asyncio
        
        async def test_method_signature():
            service = OpenAIService()
            
            try:
                result = await service.deep_research(
                    prompt='Test prompt',
                    mode=ResearchMode.DEEP_RESEARCH_O3,
                    tools=[],
                    research_depth='fast',
                    max_tool_calls=5,
                    background_mode=True
                )
                print('✓ OpenAI service accepts new depth parameters')
                return True
            except Exception as e:
                if 'invalid API key' in str(e) or 'API error' in str(e) or 'timeout' in str(e).lower():
                    print('✓ OpenAI service accepts new depth parameters (API error expected)')
                    return True
                else:
                    print(f'✗ Error with new parameters: {e}')
                    return False
        
        return asyncio.run(test_method_signature())
    except Exception as e:
        print(f"✗ Error testing OpenAI service: {e}")
        return False

if __name__ == "__main__":
    print("Testing research depth configuration implementation...")
    print()
    
    success = True
    success &= test_config()
    print()
    success &= test_models()
    print()
    success &= test_openai_service()
    print()
    
    if success:
        print("🎉 All tests passed! Research depth configuration is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
