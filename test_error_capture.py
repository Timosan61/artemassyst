#!/usr/bin/env python3
"""
Test script to capture the error message and identify its source
"""
import os
import sys
import asyncio
import logging
from datetime import datetime

# Set up logging to capture errors
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test_error.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Test the memory service directly
async def test_memory_service():
    """Test the memory service to see if errors occur"""
    try:
        from bot.memory.memory_service import MemoryService
        from bot.memory.session_manager import session_manager

        logger.info("🧪 Testing memory service...")

        # Test with a sample ZEP API key
        zep_api_key = os.getenv('ZEP_API_KEY', 'test_key')
        memory_service = MemoryService(zep_api_key, enable_memory=True)

        # Test session creation
        test_user_id = "test_user_123"
        test_chat_id = "test_chat_456"
        test_message = "Привет! Хочу купить дом в Сочи"

        logger.info(f"Testing with user_id: {test_user_id}, chat_id: {test_chat_id}")

        # Process a message
        result = await memory_service.process_message(
            user_id=test_user_id,
            message_text=test_message,
            message_type="user",
            chat_id=test_chat_id
        )

        logger.info(f"✅ Memory service result: {result.get('success', False)}")
        logger.info(f"📊 Current state: {result.get('current_state', 'unknown')}")
        logger.info(f"❓ Recommended questions: {result.get('recommendations', {}).get('next_questions', [])}")

        return result

    except Exception as e:
        logger.error(f"❌ Error in memory service test: {e}")
        logger.error(f"Traceback:", exc_info=True)
        return {'success': False, 'error': str(e)}

# Test the agent directly
async def test_agent():
    """Test the AI agent to see if errors occur"""
    try:
        from bot.agent import agent

        logger.info("🤖 Testing AI agent...")

        test_session_id = "test_session_123"
        test_message = "Хочу купить квартиру в Сочи до 3 миллионов"
        test_user_name = "Тестовый Пользователь"

        logger.info(f"Testing with session_id: {test_session_id}")

        # Test agent response generation
        response = await agent.generate_response(
            user_message=test_message,
            session_id=test_session_id,
            user_name=test_user_name
        )

        logger.info(f"✅ Agent response generated: {response[:100]}...")
        return response

    except Exception as e:
        logger.error(f"❌ Error in agent test: {e}")
        logger.error(f"Traceback:", exc_info=True)
        return f"Error: {str(e)}"

# Test the fallback error message
async def test_fallback_error():
    """Test where the fallback error message comes from"""
    try:
        logger.info("🔍 Testing fallback error scenarios...")

        # Test the exact error message
        error_message = "Извините, произошла непредвиденная ошибка. Попробуйте написать снова."

        # Check if this comes from webhook.py
        with open('webhook.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if error_message in content:
                logger.info(f"✅ Found error message in webhook.py")
                # Find the line number
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if error_message in line:
                        logger.info(f"📍 Line {i+1}: {line.strip()}")
                        break

        # Check if it comes from bot/agent.py
        with open('bot/agent.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if error_message in content:
                logger.info(f"✅ Found error message in bot/agent.py")
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if error_message in line:
                        logger.info(f"📍 Line {i+1}: {line.strip()}")
                        break

        # Check if it comes from bot/memory/
        import glob
        for file_path in glob.glob('bot/memory/*.py'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if error_message in content:
                    logger.info(f"✅ Found error message in {file_path}")
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if error_message in line:
                            logger.info(f"📍 Line {i+1}: {line.strip()}")
                            break

    except Exception as e:
        logger.error(f"❌ Error in fallback error test: {e}")
        logger.error(f"Traceback:", exc_info=True)

async def main():
    """Main test function"""
    logger.info("🚀 Starting error capture test...")
    logger.info(f"📅 Current time: {datetime.now()}")

    # Test 1: Memory service
    logger.info("\n" + "="*50)
    await test_memory_service()

    # Test 2: Agent
    logger.info("\n" + "="*50)
    await test_agent()

    # Test 3: Find error message source
    logger.info("\n" + "="*50)
    await test_fallback_error()

    logger.info("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())