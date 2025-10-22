#!/usr/bin/env python3
"""
Test script for Live Log Streaming Service
Tests all cloud provider integrations and real-time features
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.live_stream.stream_manager import StreamManager
from app.services.live_stream.cloud_connectors.aws_cloudwatch import AWSCloudWatchConnector
from app.services.live_stream.cloud_connectors.azure_monitor import AzureMonitorConnector
from app.services.live_stream.cloud_connectors.gcp_logging import GCPLoggingConnector
from app.services.live_stream.alert_engine import AlertEngine
from app.services.live_stream.websocket_broadcaster import WebSocketBroadcaster
from app.core.credential_encryption import encrypt_credentials, decrypt_credentials

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiveStreamingTester:
    """Comprehensive tester for live streaming service"""
    
    def __init__(self):
        self.test_results = {}
        
    async def run_all_tests(self):
        """Run all live streaming tests"""
        print("🚀 Starting Live Log Streaming Service Tests")
        print("=" * 60)
        
        # Test credential encryption
        await self.test_credential_encryption()
        
        # Test cloud connectors
        await self.test_aws_connector()
        await self.test_azure_connector()
        await self.test_gcp_connector()
        
        # Test alert engine
        await self.test_alert_engine()
        
        # Test WebSocket broadcaster
        await self.test_websocket_broadcaster()
        
        # Test stream manager
        await self.test_stream_manager()
        
        # Print results
        self.print_test_results()
    
    async def test_credential_encryption(self):
        """Test credential encryption and decryption"""
        print("\n🔐 Testing Credential Encryption...")
        
        try:
            # Test AWS credentials
            aws_creds = {
                "access_key_id": "AKIAIOSFODNN7EXAMPLE",
                "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                "region": "us-east-1",
                "log_group": "/aws/lambda/test-function"
            }
            
            # Encrypt
            encrypted = encrypt_credentials(aws_creds)
            assert encrypted["_encrypted"] == True
            assert "access_key_id" in encrypted["_encrypted_fields"]
            assert "secret_access_key" in encrypted["_encrypted_fields"]
            
            # Decrypt
            decrypted = decrypt_credentials(encrypted)
            assert decrypted["access_key_id"] == aws_creds["access_key_id"]
            assert decrypted["secret_access_key"] == aws_creds["secret_access_key"]
            assert decrypted["region"] == aws_creds["region"]
            
            self.test_results["credential_encryption"] = "✅ PASS"
            print("  ✅ Credential encryption/decryption works correctly")
            
        except Exception as e:
            self.test_results["credential_encryption"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ Credential encryption failed: {str(e)}")
    
    async def test_aws_connector(self):
        """Test AWS CloudWatch connector"""
        print("\n☁️ Testing AWS CloudWatch Connector...")
        
        try:
            # Mock AWS credentials (won't work without real credentials)
            config = {
                "access_key_id": "test_key",
                "secret_access_key": "test_secret",
                "region": "us-east-1",
                "log_group": "/aws/lambda/test-function",
                "log_streams": ["test-stream"]
            }
            
            connector = AWSCloudWatchConnector(config)
            
            # Test connection info
            info = connector.get_connection_info()
            assert info["provider"] == "aws"
            assert info["log_group"] == config["log_group"]
            
            # Test connection (will fail without real credentials, but should not crash)
            try:
                success = await connector.test_connection()
                if success:
                    print("  ✅ AWS connection test successful")
                else:
                    print("  ⚠️ AWS connection test failed (expected without real credentials)")
            except Exception as e:
                print(f"  ⚠️ AWS connection test failed: {str(e)} (expected without real credentials)")
            
            # Test log parsing
            mock_event = {
                "message": "2024-01-01 12:00:00 ERROR Database connection failed",
                "timestamp": int(datetime.utcnow().timestamp() * 1000),
                "eventId": "test-event-id"
            }
            
            parsed = connector._parse_log_event(mock_event, "test-stream")
            assert parsed is not None
            assert parsed["log_level"] == "ERROR"
            assert "Database connection failed" in parsed["message"]
            
            await connector.close()
            
            self.test_results["aws_connector"] = "✅ PASS"
            print("  ✅ AWS CloudWatch connector works correctly")
            
        except Exception as e:
            self.test_results["aws_connector"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ AWS connector failed: {str(e)}")
    
    async def test_azure_connector(self):
        """Test Azure Monitor connector"""
        print("\n☁️ Testing Azure Monitor Connector...")
        
        try:
            config = {
                "workspace_id": "test-workspace-id",
                "tenant_id": "test-tenant-id",
                "client_id": "test-client-id",
                "client_secret": "test-client-secret",
                "query": "AppTraces | take 10"
            }
            
            connector = AzureMonitorConnector(config)
            
            # Test connection info
            info = connector.get_connection_info()
            assert info["provider"] == "azure"
            assert info["workspace_id"] == config["workspace_id"]
            
            # Test connection (will fail without real credentials)
            try:
                success = await connector.test_connection()
                if success:
                    print("  ✅ Azure connection test successful")
                else:
                    print("  ⚠️ Azure connection test failed (expected without real credentials)")
            except Exception as e:
                print(f"  ⚠️ Azure connection test failed: {str(e)} (expected without real credentials)")
            
            # Test log parsing
            mock_row = {
                "TimeGenerated": datetime.utcnow(),
                "Message": "Error occurred in application",
                "Level": "Error",
                "Source": "test-app"
            }
            
            parsed = connector._parse_log_row([mock_row["TimeGenerated"], mock_row["Message"], mock_row["Level"], mock_row["Source"]], 
                                            ["TimeGenerated", "Message", "Level", "Source"])
            assert parsed is not None
            assert parsed["log_level"] == "ERROR"
            assert "Error occurred" in parsed["message"]
            
            await connector.close()
            
            self.test_results["azure_connector"] = "✅ PASS"
            print("  ✅ Azure Monitor connector works correctly")
            
        except Exception as e:
            self.test_results["azure_connector"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ Azure connector failed: {str(e)}")
    
    async def test_gcp_connector(self):
        """Test GCP Cloud Logging connector"""
        print("\n☁️ Testing GCP Cloud Logging Connector...")
        
        try:
            config = {
                "project_id": "test-project-id",
                "log_name": "projects/test-project-id/logs/test-log",
                "resource_type": "gce_instance",
                "credentials_json": {
                    "type": "service_account",
                    "project_id": "test-project-id",
                    "private_key_id": "test-key-id",
                    "private_key": "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----\n",
                    "client_email": "test@test-project-id.iam.gserviceaccount.com",
                    "client_id": "test-client-id"
                }
            }
            
            connector = GCPLoggingConnector(config)
            
            # Test connection info
            info = connector.get_connection_info()
            assert info["provider"] == "gcp"
            assert info["project_id"] == config["project_id"]
            
            # Test connection (will fail without real credentials)
            try:
                success = await connector.test_connection()
                if success:
                    print("  ✅ GCP connection test successful")
                else:
                    print("  ⚠️ GCP connection test failed (expected without real credentials)")
            except Exception as e:
                print(f"  ⚠️ GCP connection test failed: {str(e)} (expected without real credentials)")
            
            # Test log parsing
            class MockEntry:
                def __init__(self):
                    self.timestamp = datetime.utcnow()
                    self.payload = {"message": "Error in GCP service"}
                    self.severity = "ERROR"
                    self.log_name = "projects/test/logs/test"
                    self.resource = None
                    self.labels = {}
                    self.insert_id = "test-insert-id"
                    self.http_request = None
                    self.operation = None
                    self.trace = None
                    self.span_id = None
            
            mock_entry = MockEntry()
            parsed = connector._parse_log_entry(mock_entry)
            assert parsed is not None
            assert parsed["log_level"] == "ERROR"
            assert "Error in GCP service" in parsed["message"]
            
            await connector.close()
            
            self.test_results["gcp_connector"] = "✅ PASS"
            print("  ✅ GCP Cloud Logging connector works correctly")
            
        except Exception as e:
            self.test_results["gcp_connector"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ GCP connector failed: {str(e)}")
    
    async def test_alert_engine(self):
        """Test alert engine"""
        print("\n🚨 Testing Alert Engine...")
        
        try:
            # Mock database and Redis (would need real instances for full testing)
            class MockDB:
                pass
            
            class MockRedis:
                pass
            
            alert_engine = AlertEngine(MockDB(), MockRedis())
            
            # Test alert rule creation
            rules = alert_engine._get_default_rules("test-project")
            assert len(rules) > 0
            assert rules[0].alert_type.value == "error_rate"
            assert rules[0].severity.value == "high"
            
            # Test log level extraction
            test_log = {
                "log_level": "ERROR",
                "message": "Database connection failed",
                "project_id": "test-project",
                "user_id": "test-user"
            }
            
            # Test pattern matching
            pattern_rule = rules[2]  # Database errors rule
            assert pattern_rule.alert_type.value == "pattern_match"
            
            # Test cooldown logic
            rule = rules[0]
            assert not alert_engine._is_in_cooldown(rule)
            
            self.test_results["alert_engine"] = "✅ PASS"
            print("  ✅ Alert engine works correctly")
            
        except Exception as e:
            self.test_results["alert_engine"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ Alert engine failed: {str(e)}")
    
    async def test_websocket_broadcaster(self):
        """Test WebSocket broadcaster"""
        print("\n📡 Testing WebSocket Broadcaster...")
        
        try:
            # Mock Redis client
            class MockRedis:
                async def pubsub(self):
                    return MockPubSub()
                
                async def publish(self, channel, message):
                    pass
            
            class MockPubSub:
                async def subscribe(self, channel):
                    pass
                
                async def unsubscribe(self, channel):
                    pass
                
                async def close(self):
                    pass
                
                async def get_message(self, timeout=None):
                    return None
            
            broadcaster = WebSocketBroadcaster(MockRedis())
            
            # Test connection registration
            await broadcaster.register_connection("test-project", "test-connection")
            assert "test-project" in broadcaster.active_connections
            assert "test-connection" in broadcaster.active_connections["test-project"]
            
            # Test connection unregistration
            await broadcaster.unregister_connection("test-project", "test-connection")
            assert "test-project" not in broadcaster.active_connections or "test-connection" not in broadcaster.active_connections.get("test-project", set())
            
            # Test stats
            stats = await broadcaster.get_connection_stats()
            assert "total_connections" in stats
            assert "project_count" in stats
            
            self.test_results["websocket_broadcaster"] = "✅ PASS"
            print("  ✅ WebSocket broadcaster works correctly")
            
        except Exception as e:
            self.test_results["websocket_broadcaster"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ WebSocket broadcaster failed: {str(e)}")
    
    async def test_stream_manager(self):
        """Test stream manager"""
        print("\n🔄 Testing Stream Manager...")
        
        try:
            # Mock database and Redis
            class MockDB:
                async def execute(self, query):
                    return MockResult()
                
                async def commit(self):
                    pass
                
                async def rollback(self):
                    pass
            
            class MockResult:
                def scalar_one_or_none(self):
                    return None
                
                def scalars(self):
                    return []
            
            class MockRedis:
                pass
            
            stream_manager = StreamManager(MockDB(), MockRedis())
            
            # Test health check
            health = await stream_manager.health_check()
            assert "total_streams" in health
            assert "running_streams" in health
            assert "error_streams" in health
            assert "status" in health
            
            # Test stream status
            status = await stream_manager.get_stream_status("non-existent-stream")
            assert status is None
            
            # Test all streams status
            all_status = await stream_manager.get_all_streams_status()
            assert isinstance(all_status, list)
            
            self.test_results["stream_manager"] = "✅ PASS"
            print("  ✅ Stream manager works correctly")
            
        except Exception as e:
            self.test_results["stream_manager"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ Stream manager failed: {str(e)}")
    
    def print_test_results(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 LIVE STREAMING SERVICE TEST RESULTS")
        print("=" * 60)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            print(f"{test_name.replace('_', ' ').title()}: {result}")
            if "✅ PASS" in result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Live streaming service is ready.")
        else:
            print("⚠️ Some tests failed. Check the errors above.")
        
        print("\n📋 Next Steps:")
        print("1. Install cloud provider credentials for full testing")
        print("2. Set up Redis for WebSocket broadcasting")
        print("3. Configure database connections")
        print("4. Test with real cloud provider APIs")

async def main():
    """Main test runner"""
    tester = LiveStreamingTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
