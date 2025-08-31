#!/usr/bin/env python3
"""Validation script for GitHub automation system implementation."""
import sys
import os
import traceback
from pathlib import Path

# Add the scripts directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("🧪 Testing module imports...")
    
    try:
        # Test core imports
        from core.api_client import APIClient
        from core.commit_parser import CommitParser, CommitData
        from core.daily_reporter import DailyReporter
        from core.project_sync import BoardSync, TaskStatus, TaskPriority
        
        # Test main module
        from main import GitHubAutomation
        
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration loading."""
    print("\n🧪 Testing configuration loading...")
    
    try:
        import yaml
        config_path = Path(__file__).parent / "config.yaml"
        
        if not config_path.exists():
            print("❌ config.yaml not found")
            return False
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # Validate required config sections
        required_sections = ['global', 'daily_reporter', 'project_sync', 'github']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing config section: {section}")
                return False
                
        print("✅ Configuration valid")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_commit_parser():
    """Test commit parser functionality."""
    print("\n🧪 Testing commit parser...")
    
    try:
        from core.commit_parser import CommitParser
        
        parser = CommitParser()
        
        # Test valid commit message
        test_message = """[feat] add new feature

[Body]
- Added user authentication
- Improved error handling

[Todo]
@enhancement
- Add unit tests
- Update documentation

[Footer]
Closes #123
"""
        
        commit_data = parser.parse(test_message)
        
        if commit_data.type != 'feat':
            print(f"❌ Wrong commit type: {commit_data.type}")
            return False
            
        if commit_data.title != 'add new feature':
            print(f"❌ Wrong commit title: {commit_data.title}")
            return False
            
        if len(commit_data.body) != 2:
            print(f"❌ Wrong body length: {len(commit_data.body)}")
            return False
            
        if len(commit_data.todos) != 2:
            print(f"❌ Wrong todos length: {len(commit_data.todos)}")
            return False
            
        print("✅ Commit parser working correctly")
        return True
    except Exception as e:
        print(f"❌ Commit parser error: {e}")
        traceback.print_exc()
        return False

def test_class_instantiation():
    """Test that classes can be instantiated."""
    print("\n🧪 Testing class instantiation...")
    
    try:
        # Test API client (without token - just check constructor)
        from core.api_client import APIClient
        # Don't actually create APIClient without token
        
        # Test commit parser
        from core.commit_parser import CommitParser
        parser = CommitParser()
        
        # Test automation system (without full initialization)
        from main import GitHubAutomation
        config_path = Path(__file__).parent / "config.yaml"
        automation = GitHubAutomation(str(config_path), dry_run=True)
        
        print("✅ Class instantiation successful")
        return True
    except Exception as e:
        print(f"❌ Class instantiation error: {e}")
        traceback.print_exc()
        return False

def test_method_signatures():
    """Test that key methods have correct signatures."""
    print("\n🧪 Testing method signatures...")
    
    try:
        from core.api_client import APIClient
        from core.daily_reporter import DailyReporter
        from core.project_sync import BoardSync
        
        # Check APIClient methods exist
        api_methods = [
            'get_repository', 'get_issues', 'create_issue', 'update_issue',
            'get_board_with_items', 'add_item_to_board', 'update_item_field',
            'get_commits', 'get_commit', 'get_rate_limit',
            'get_repository_labels', 'add_labels_to_issue', 'remove_labels_from_issue'
        ]
        
        for method in api_methods:
            if not hasattr(APIClient, method):
                print(f"❌ Missing APIClient method: {method}")
                return False
                
        # Check DailyReporter methods exist
        dr_methods = ['generate_dsr']
        for method in dr_methods:
            if not hasattr(DailyReporter, method):
                print(f"❌ Missing DailyReporter method: {method}")
                return False
                
        # Check BoardSync methods exist
        bs_methods = ['sync_board', 'update_task_status', 'get_project_statistics']
        for method in bs_methods:
            if not hasattr(BoardSync, method):
                print(f"❌ Missing BoardSync method: {method}")
                return False
                
        print("✅ All method signatures valid")
        return True
    except Exception as e:
        print(f"❌ Method signature error: {e}")
        return False

def main():
    """Run validation tests."""
    print("🔍 GitHub Automation System Validation")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_configuration,
        test_commit_parser,
        test_class_instantiation,
        test_method_signatures
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print("❌ Test failed, stopping validation")
            break
    
    print("\n" + "=" * 40)
    print(f"📊 Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All validations passed! Implementation is ready.")
        return 0
    else:
        print("❌ Validation failed. Please fix issues before using.")
        return 1

if __name__ == '__main__':
    sys.exit(main())