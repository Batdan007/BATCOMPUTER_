#!/usr/bin/env python3
"""
Basic tests for the ML Agent
Run with: python test_basic.py
"""

import sys
import os
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml_agent.config import AgentConfig, ModelConfig, TaskConfig, load_default_config
from ml_agent.utils import get_device, get_system_info


class TestMLAgentConfig(unittest.TestCase):
    """Test configuration functionality"""
    
    def test_default_config(self):
        """Test default configuration loading"""
        config = load_default_config()
        self.assertIsInstance(config, AgentConfig)
        self.assertEqual(config.agent_name, "MLAgent")
        self.assertIn("gpt2", config.models)
        self.assertIn("text_generation", config.tasks)
    
    def test_model_config(self):
        """Test model configuration"""
        model_config = ModelConfig(
            name="Test Model",
            model_type="text",
            model_path="test/path",
            device="cpu",
            precision="float32"
        )
        self.assertEqual(model_config.name, "Test Model")
        self.assertEqual(model_config.model_type, "text")
        self.assertEqual(model_config.device, "cpu")
    
    def test_task_config(self):
        """Test task configuration"""
        task_config = TaskConfig(
            name="Test Task",
            task_type="text_generation",
            model_name="test_model",
            timeout=60
        )
        self.assertEqual(task_config.name, "Test Task")
        self.assertEqual(task_config.task_type, "text_generation")
        self.assertEqual(task_config.timeout, 60)
    
    def test_config_serialization(self):
        """Test configuration serialization"""
        config = load_default_config()
        config_dict = config.to_dict()
        
        # Verify key fields are present
        self.assertIn("agent_name", config_dict)
        self.assertIn("models", config_dict)
        self.assertIn("tasks", config_dict)
        
        # Test saving and loading
        test_config_path = "test_config.yaml"
        try:
            config.save(test_config_path)
            loaded_config = AgentConfig.from_file(test_config_path)
            self.assertEqual(config.agent_name, loaded_config.agent_name)
        finally:
            if os.path.exists(test_config_path):
                os.remove(test_config_path)


class TestMLAgentUtils(unittest.TestCase):
    """Test utility functions"""
    
    def test_device_detection(self):
        """Test device detection"""
        device = get_device("auto")
        self.assertIn(device, ["cpu", "cuda", "mps"])
        
        cpu_device = get_device("cpu")
        self.assertEqual(cpu_device, "cpu")
    
    def test_system_info(self):
        """Test system information gathering"""
        info = get_system_info()
        self.assertIn("platform", info)
        self.assertIn("python_version", info)
        self.assertIn("cpu_count", info)
        self.assertIn("memory", info)
        self.assertIn("pytorch_version", info)
        self.assertIn("cuda_available", info)


class TestMLAgentIntegration(unittest.TestCase):
    """Test basic integration functionality"""
    
    def test_imports(self):
        """Test that all modules can be imported"""
        try:
            from ml_agent import MLAgent
            from ml_agent.models import ModelManager
            from ml_agent.tasks import TaskOrchestrator
            from ml_agent.api import MLAgentAPI
            self.assertTrue(True)  # If we get here, imports worked
        except ImportError as e:
            self.fail(f"Import failed: {e}")
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = load_default_config()
        
        # Verify models and tasks are properly linked
        for task_name, task_config in config.tasks.items():
            self.assertIn(task_config.model_name, config.models)
        
        # Verify model types are valid
        valid_model_types = ["text", "image", "multimodal"]
        for model_name, model_config in config.models.items():
            self.assertIn(model_config.model_type, valid_model_types)


def run_basic_tests():
    """Run basic tests"""
    print("🧪 Running ML Agent Basic Tests")
    print("=" * 40)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestMLAgentConfig))
    test_suite.addTest(unittest.makeSuite(TestMLAgentUtils))
    test_suite.addTest(unittest.makeSuite(TestMLAgentIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 40)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_basic_tests()
    sys.exit(0 if success else 1)
