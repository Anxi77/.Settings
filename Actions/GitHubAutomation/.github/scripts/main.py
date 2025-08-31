#!/usr/bin/env python3
"""Simplified GitHub automation system - Core functionality only."""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Add automation directory to Python path
automation_dir = Path(__file__).parent
sys.path.insert(0, str(automation_dir))

import yaml
from core.api_client import APIClient
from core.commit_parser import CommitParser
from core.daily_reporter import DailyReporter
from core.project_sync import BoardSync

class GitHubAutomation:
    """Simplified GitHub automation system - Core functionality only."""
    
    def __init__(self, config_path: Optional[str] = None, dry_run: bool = False):
        """Initialize automation system.
        
        Args:
            config_path: Path to configuration file
            dry_run: If True, don't make actual changes
        """
        self.config_path = config_path or (automation_dir / "config.yaml")
        self.config = self._load_config()
        self.dry_run = dry_run
        self._setup_logging()
        
        self.logger = logging.getLogger(__name__)
        self.api_client = None
        
        # Core components
        self.commit_parser = CommitParser()
        self.daily_reporter = None
        self.board_sync = None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Apply environment-specific overrides
            env = os.environ.get('AUTOMATION_ENV', 'production')
            if 'environments' in config and env in config['environments']:
                env_config = config['environments'][env]
                self._merge_config(config, env_config)
            
            return config
            
        except FileNotFoundError:
            print(f"Configuration file not found: {self.config_path}")
            return self._get_default_config()
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {e}")
            return self._get_default_config()
    
    def _merge_config(self, base_config: Dict[str, Any], override_config: Dict[str, Any]):
        """Merge override configuration into base configuration."""
        for key, value in override_config.items():
            if isinstance(value, dict) and key in base_config and isinstance(base_config[key], dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'global': {
                'timezone': 'UTC',
                'project_number': 1,
                'log_level': 'INFO'
            },
            'daily_reporter': {'enabled': True},
            'board_sync': {'enabled': True},
            'github': {'max_retries': 3}
        }
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_config = self.config.get('logging', {})
        
        log_level = getattr(logging, log_config.get('level', 'INFO').upper())
        log_format = log_config.get('format', '%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        date_format = log_config.get('date_format', '%Y-%m-%d %H:%M:%S')
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            datefmt=date_format
        )
        
        # Set component-specific log levels
        loggers = log_config.get('loggers', {})
        for logger_name, level in loggers.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(getattr(logging, level.upper()))
    
    def initialize(self) -> bool:
        """Initialize the automation system."""
        try:
            # Get GitHub token
            github_token = os.environ.get('GITHUB_TOKEN')
            if not github_token:
                self.logger.error("GitHub token not found in environment variables")
                return False
            
            # Initialize GitHub client
            github_config = self.config.get('github', {})
            self.api_client = APIClient(
                token=github_token,
                max_retries=github_config.get('max_retries', 3),
                base_delay=github_config.get('base_delay', 1.0)
            )
            
            # Get repository info
            repo_name = os.environ.get('GITHUB_REPOSITORY')
            if not repo_name:
                self.logger.error("GITHUB_REPOSITORY not found in environment")
                return False
            
            self.repo_name = repo_name
            self.logger.info(f"Connected to repository: {repo_name}")
            
            # Initialize core components
            if self.config.get('daily_reporter', {}).get('enabled', True):
                self.daily_reporter = DailyReporter(
                    self.api_client, 
                    self.config.get('daily_reporter', {})
                )
            
            if self.config.get('board_sync', {}).get('enabled', True):
                project_number = self.config.get('global', {}).get('project_number')
                if project_number:
                    self.board_sync = BoardSync(
                        self.api_client,
                        self.config.get('board_sync', {}),
                        project_number
                    )
            
            self.logger.info("GitHub automation system initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize automation system: {e}")
            return False
    
    def _should_skip_automation(self) -> bool:
        """Check if automation should be skipped based on actor and conditions."""
        actor = os.environ.get('GITHUB_ACTOR', '')
        excluded_actors = ['github-actions[bot]', 'dependabot[bot]', 'renovate[bot]']
        
        if actor in excluded_actors:
            self.logger.info(f"Skipping - automated actor: {actor}")
            return True
        
        # Check commit message if available
        commit_sha = os.environ.get('GITHUB_SHA')
        if commit_sha:
            try:
                repo_owner, repo_name = self.repo_name.split('/', 1)
                commit = self.api_client.get_commit(repo_owner, repo_name, commit_sha)
                message = commit.get('message', '').lower()
                
                skip_patterns = ['[automated]', '[skip ci]', '[no ci]', 'github-automation']
                if any(pattern in message for pattern in skip_patterns):
                    self.logger.info("Skipping - commit contains skip pattern")
                    return True
                    
            except Exception:
                pass  # Continue if commit check fails
        
        return False
    
    def run_workflow_tracking(self) -> Dict[str, Any]:
        """Run workflow tracking (commit-based DSR generation)."""
        if not self.daily_reporter:
            return {'error': 'Daily reporter not initialized'}
        
        try:
            self.logger.info("Starting workflow tracking")
            
            if self._should_skip_automation():
                return {'skipped': True, 'reason': 'automation_bypass'}
            
            # Generate DSR
            if self.dry_run:
                self.logger.info("DRY RUN: Would generate DSR issue")
                return {'success': True, 'dry_run': True}
            
            # Generate DSR using GraphQL API
            repo_owner, repo_name = self.repo_name.split('/', 1)
            dsr_issue = self.daily_reporter.generate_dsr(repo_owner, repo_name)
            
            if dsr_issue:
                return {
                    'success': True,
                    'dsr_issue': {
                        'number': dsr_issue.get('number'),
                        'title': dsr_issue.get('title'),
                        'url': dsr_issue.get('url')
                    }
                }
            else:
                return {'success': False, 'reason': 'no_commits_today'}
                
        except Exception as e:
            self.logger.error(f"Workflow tracking failed: {e}")
            return {'error': str(e)}
    
    def run_task_management(self) -> Dict[str, Any]:
        """Run task management (issue/project sync)."""
        if not self.board_sync:
            return {'error': 'Project sync not initialized'}
        
        try:
            self.logger.info("Starting task management")
            
            if self._should_skip_automation():
                return {'skipped': True, 'reason': 'automation_bypass'}
            
            if self.dry_run:
                self.logger.info("DRY RUN: Would sync project board")
                return {'success': True, 'dry_run': True}
            
            # Sync project board
            repo_name = os.environ.get('GITHUB_REPOSITORY')
            if not repo_name:
                return {'error': 'GITHUB_REPOSITORY not found in environment'}
            
            repo_owner, repo_name = repo_name.split('/', 1)
            sync_results = self.board_sync.sync_board(repo_owner, repo_name)
            
            return {
                'success': True,
                'board_sync': sync_results
            }
            
        except Exception as e:
            self.logger.error(f"Task management failed: {e}")
            return {'error': str(e)}
    
    def run_project_report(self) -> Dict[str, Any]:
        """Generate project status report."""
        try:
            self.logger.info("Generating project report")
            
            if self.dry_run:
                self.logger.info("DRY RUN: Would generate project report")
                return {'success': True, 'dry_run': True}
            
            # Generate comprehensive project report
            repo_name = os.environ.get('GITHUB_REPOSITORY')
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'repository': repo_name
            }
            
            # Add daily reporter stats
            if self.daily_reporter:
                dsr_stats = self.daily_reporter.get_statistics()
                report_data['dsr_statistics'] = dsr_stats
            
            # Add project sync stats  
            if self.board_sync and repo_name:
                repo_owner, repo_name_only = repo_name.split('/', 1)
                sync_stats = self.board_sync.get_project_statistics(repo_owner, repo_name_only)
                report_data['project_statistics'] = sync_stats
            
            return {
                'success': True,
                'report': report_data
            }
            
        except Exception as e:
            self.logger.error(f"Project report failed: {e}")
            return {'error': str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Perform system health check."""
        health = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'components': {}
        }
        
        try:
            # Check GitHub client
            if self.api_client:
                rate_limit = self.api_client.get_rate_limit()
                health['components']['api_client'] = {
                    'status': 'healthy',
                    'rate_limit_remaining': rate_limit['core']['remaining'],
                    'rate_limit_limit': rate_limit['core']['limit']
                }
            else:
                health['components']['api_client'] = {'status': 'not_initialized'}
            
            # Check repository access
            if hasattr(self, 'repo_name') and self.repo_name:
                health['components']['repository'] = {
                    'status': 'healthy',
                    'name': self.repo_name,
                    'configured': True
                }
            else:
                health['components']['repository'] = {'status': 'not_initialized'}
            
            # Check core components
            health['components']['daily_reporter'] = {
                'status': 'enabled' if self.daily_reporter else 'disabled'
            }
            health['components']['board_sync'] = {
                'status': 'enabled' if self.board_sync else 'disabled'
            }
            
            return health
            
        except Exception as e:
            health['overall_status'] = 'unhealthy'
            health['error'] = str(e)
            return health

def create_argument_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description='GitHub Automation System - Core functionality',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode workflow          # Process commits and generate DSR
  python main.py --mode task-management   # Sync project board
  python main.py --mode report            # Generate project report
  python main.py --health-check           # Check system health
  python main.py --dry-run --verbose      # Test without changes
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['workflow', 'task-management', 'report'],
        default='workflow',
        help='Automation mode to run'
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without making actual changes'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--health-check',
        action='store_true',
        help='Perform system health check'
    )
    
    return parser

def main():
    """Main entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Override log level if verbose
    if args.verbose:
        os.environ['AUTOMATION_LOG_LEVEL'] = 'DEBUG'
    
    # Initialize automation system
    automation = GitHubAutomation(
        config_path=args.config,
        dry_run=args.dry_run
    )
    
    if not automation.initialize():
        print("❌ Failed to initialize automation system")
        sys.exit(1)
    
    # Run health check if requested
    if args.health_check:
        health = automation.health_check()
        print("🏥 System Health Check:")
        print(f"Overall Status: {health['overall_status'].upper()}")
        
        for component, status in health['components'].items():
            print(f"  {component}: {status['status'].upper()}")
        
        if health['overall_status'] == 'unhealthy':
            print(f"Error: {health.get('error', 'Unknown error')}")
            sys.exit(1)
        
        print("✅ All systems healthy")
        return
    
    # Run automation mode
    try:
        if args.mode == 'workflow':
            results = automation.run_workflow_tracking()
        elif args.mode == 'task-management':  
            results = automation.run_task_management()
        elif args.mode == 'report':
            results = automation.run_project_report()
        else:
            print(f"❌ Unknown mode: {args.mode}")
            sys.exit(1)
        
        # Output results
        if results.get('success'):
            print("✅ Automation completed successfully")
            
            if args.mode == 'workflow' and 'dsr_issue' in results:
                dsr = results['dsr_issue']
                print(f"📅 DSR Issue: #{dsr['number']} - {dsr['title']}")
            
            elif args.mode == 'task-management' and 'board_sync' in results:
                sync = results['board_sync']
                print(f"📊 Project Sync: Updated {sync.get('updated_items', 0)} items")
            
            elif args.mode == 'report':
                print("📈 Project report generated")
                
        elif results.get('skipped'):
            print(f"⏭️ Automation skipped: {results.get('reason', 'unknown')}")
            
        elif results.get('error'):
            print(f"❌ Automation failed: {results['error']}")
            sys.exit(1)
            
        else:
            print(f"⚠️ Unexpected result: {results}")
            
    except KeyboardInterrupt:
        print("\n🛑 Automation interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        automation.logger.error(f"Unexpected error: {e}")
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()