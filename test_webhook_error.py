#!/usr/bin/env python3
"""
Test webhook error handling
"""
import asyncio
import json
import time
from datetime import datetime

# Create a test webhook payload that will trigger the error handling
test_payload = {
    "update_id": 123456789,
    "message": {
        "message_id": 1,
        "from": {
            "id": 123456789,
            "is_bot": False,
            "first_name": "Тест",
            "username": "test_user"
        },
        "chat": {
            "id": 123456789,
            "first_name": "Тест",
            "username": "test_user",
            "type": "private"
        },
        "date": int(time.time()),
        "text": "Привет! Хочу купить дом в Сочи до 5 миллионов"
    }
}

async def test_webhook_error_handling():
    """Test webhook error handling"""
    import aiohttp

    print("🧪 Testing webhook error handling...")

    # Test with local webhook endpoint
    webhook_url = "http://localhost:8000/webhook"

    headers = {
        "Content-Type": "application/json",
        "X-Telegram-Bot-Api-Secret-Token": "ikXktYv3Sd_h87wMYvcp1sHsQaSiIjxS_wQOCy7GGrY"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=test_payload, headers=headers) as response:
                print(f"📊 Response status: {response.status}")
                result = await response.json()
                print(f"📋 Response body: {result}")
                return result
    except Exception as e:
        print(f"❌ Webhook test error: {e}")
        return None

def test_webhook_locally():
    """Test webhook processing locally"""
    print("🧪 Testing webhook processing locally...")

    try:
        # Import the webhook processing function
        import sys
        sys.path.append('/home/coder/projects/bot_cloning_digital_ocean/clones/artemmyassyst')

        from webhook import process_webhook
        from fastapi import Request

        # Create mock request
        class MockRequest:
            def __init__(self, json_data):
                self._json_data = json.dumps(json_data).encode('utf-8')
                self.headers = {
                    "X-Telegram-Bot-Api-Secret-Token": "ikXktYv3Sd_h87wMYvcp1sHsQaSiIjxS_wQOCy7GGrY"
                }

            async def body(self):
                return self._json_data

        # Test the webhook processing
        mock_request = MockRequest(test_payload)

        # Run the async function
        import asyncio
        result = asyncio.run(process_webhook(mock_request))

        print(f"✅ Local webhook test result: {result}")
        return result

    except Exception as e:
        print(f"❌ Local webhook test error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🚀 Testing webhook error handling...")
    print(f"📅 Current time: {datetime.now()}")

    # Test local processing first
    result = test_webhook_locally()

    if result:
        print("✅ Webhook error handling test completed successfully!")
    else:
        print("❌ Webhook error handling test failed!")

    print("\n🏁 Test completed!")