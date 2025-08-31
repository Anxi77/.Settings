#!/usr/bin/env python3
"""
Task Proposal Converter - Standalone module for converting proposals to tasks
"""
import os
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional
from github import Github
from github.Repository import Repository
from github.Issue import Issue

logger = logging.getLogger(__name__)

class ProposalData:
    """Structured proposal information"""
    
    def __init__(self, title: str, body: str, assignee: Optional[str] = None):
        self.title = title
        self.body = body
        self.assignee = assignee
        self.parsed_data = self._parse_body(body)
    
    def _parse_body(self, body: str) -> Dict:
        """Parse proposal body for structured information"""
        data = {
            'proposer': '',
            'target_date': '',
            'category': 'general',
            'objective': '',
            'requirements': [],
            'acceptance_criteria': []
        }
        
        if not body:
            return data
        
        lines = body.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Check for section headers
            if '📋 Proposal Information' in line:
                current_section = 'info'
            elif '🎯 Objective' in line:
                current_section = 'objective'
            elif '📝 Requirements' in line:
                current_section = 'requirements'
            elif '📊 Acceptance Criteria' in line:
                current_section = 'criteria'
            elif line.startswith('#'):
                current_section = None
            
            # Parse content based on current section
            elif current_section == 'info':
                if line.startswith('- Proposer:'):
                    data['proposer'] = line.replace('- Proposer:', '').strip()
                elif line.startswith('- Target Date:'):
                    data['target_date'] = line.replace('- Target Date:', '').strip()
                elif line.startswith('- Category:'):
                    data['category'] = line.replace('- Category:', '').strip()
            
            elif current_section == 'objective' and line:
                data['objective'] = line
            
            elif current_section == 'requirements' and line.startswith('- [ ]'):
                requirement = line.replace('- [ ]', '').strip()
                data['requirements'].append(requirement)
            
            elif current_section == 'criteria' and line.startswith('- [ ]'):
                criteria = line.replace('- [ ]', '').strip()
                data['acceptance_criteria'].append(criteria)
        
        return data


class TaskConverter:
    """Convert approved proposals to task issues"""
    
    PROPOSAL_LABELS = ['proposal']
    APPROVAL_LABELS = ['approved'] 
    TASK_LABELS = ['task']
    
    def __init__(self, token: str, repository: str):
        """Initialize converter with GitHub credentials
        
        Args:
            token: GitHub personal access token
            repository: Repository name in format "owner/repo"
        """
        self.github = Github(token)
        self.repo = self.github.get_repo(repository)
        self.logger = logging.getLogger(__name__)
    
    def process_proposals(self) -> List[Issue]:
        """Process all approved proposals and convert to tasks
        
        Returns:
            List of created task issues
        """
        self.logger.info("Starting proposal processing")
        created_tasks = []
        
        # Find approved proposals
        approved_proposals = self._find_approved_proposals()
        
        for proposal in approved_proposals:
            try:
                task_issue = self._convert_proposal_to_task(proposal)
                created_tasks.append(task_issue)
                self.logger.info(f"Converted proposal #{proposal.number} to task #{task_issue.number}")
                
            except Exception as e:
                self.logger.error(f"Failed to convert proposal #{proposal.number}: {str(e)}")
                self._add_error_comment(proposal, str(e))
        
        self.logger.info(f"Processed {len(approved_proposals)} proposals, created {len(created_tasks)} tasks")
        return created_tasks
    
    def _find_approved_proposals(self) -> List[Issue]:
        """Find issues that are proposals and have been approved
        
        Returns:
            List of approved proposal issues
        """
        proposals = []
        
        for issue in self.repo.get_issues(state='open'):
            labels = [label.name.lower() for label in issue.labels]
            
            # Must have proposal label and approval label
            has_proposal = any(label in labels for label in self.PROPOSAL_LABELS)
            has_approval = any(label in labels for label in self.APPROVAL_LABELS)
            
            if has_proposal and has_approval:
                proposals.append(issue)
        
        return proposals
    
    def _convert_proposal_to_task(self, proposal: Issue) -> Issue:
        """Convert a single proposal to a task issue
        
        Args:
            proposal: Proposal issue to convert
            
        Returns:
            Created task issue
        """
        # Parse proposal data
        proposal_data = ProposalData(
            title=proposal.title,
            body=proposal.body or "",
            assignee=proposal.assignee.login if proposal.assignee else None
        )
        
        # Generate task title and body
        task_title = self._generate_task_title(proposal_data)
        task_body = self._generate_task_body(proposal_data, proposal.number)
        
        # Determine task labels
        task_labels = self._generate_task_labels(proposal_data, proposal.labels)
        
        # Create task issue
        task_issue = self.repo.create_issue(
            title=task_title,
            body=task_body,
            labels=task_labels,
            assignees=[proposal_data.assignee] if proposal_data.assignee else []
        )
        
        # Link proposal to task
        self._link_proposal_to_task(proposal, task_issue)
        
        # Close the proposal
        proposal.edit(state='closed')
        
        return task_issue
    
    def _generate_task_title(self, proposal_data: ProposalData) -> str:
        """Generate task title from proposal data
        
        Args:
            proposal_data: Parsed proposal information
            
        Returns:
            Formatted task title
        """
        # Remove [Proposal] prefix if present
        title = proposal_data.title
        if title.startswith('[Proposal]'):
            title = title.replace('[Proposal]', '').strip()
        
        # Add [Task] prefix
        return f"[Task] {title}"
    
    def _generate_task_body(self, proposal_data: ProposalData, proposal_number: int) -> str:
        """Generate task body from proposal data
        
        Args:
            proposal_data: Parsed proposal information
            proposal_number: Original proposal issue number
            
        Returns:
            Formatted task body
        """
        parsed = proposal_data.parsed_data
        
        sections = [
            "# Task Details",
            "",
            "## 📋 Information",
            f"- **Created from Proposal**: #{proposal_number}",
            f"- **Proposer**: {parsed.get('proposer', 'Unknown')}",
            f"- **Target Date**: {parsed.get('target_date', 'Not specified')}",
            f"- **Category**: {parsed.get('category', 'general')}",
            "",
            "## 🎯 Objective",
            parsed.get('objective', 'No objective specified'),
            ""
        ]
        
        # Add requirements if present
        if parsed.get('requirements'):
            sections.extend([
                "## ✅ Requirements",
                ""
            ])
            for req in parsed['requirements']:
                sections.append(f"- [ ] {req}")
            sections.append("")
        
        # Add acceptance criteria if present
        if parsed.get('acceptance_criteria'):
            sections.extend([
                "## 📊 Acceptance Criteria", 
                ""
            ])
            for criteria in parsed['acceptance_criteria']:
                sections.append(f"- [ ] {criteria}")
            sections.append("")
        
        sections.extend([
            "---",
            "*This task was automatically created from an approved proposal.*"
        ])
        
        return "\n".join(sections)
    
    def _generate_task_labels(self, proposal_data: ProposalData, original_labels) -> List[str]:
        """Generate appropriate labels for the task
        
        Args:
            proposal_data: Parsed proposal information
            original_labels: Labels from original proposal
            
        Returns:
            List of labels for task issue
        """
        task_labels = self.TASK_LABELS.copy()
        
        # Add category-based labels
        category = proposal_data.parsed_data.get('category', '').lower()
        if category in ['feature', 'bug', 'enhancement', 'documentation']:
            task_labels.append(category)
        
        # Copy relevant labels from original proposal
        excluded_labels = self.PROPOSAL_LABELS + self.APPROVAL_LABELS
        for label in original_labels:
            if label.name.lower() not in excluded_labels:
                task_labels.append(label.name)
        
        return task_labels
    
    def _link_proposal_to_task(self, proposal: Issue, task: Issue):
        """Create bidirectional links between proposal and task
        
        Args:
            proposal: Original proposal issue
            task: Created task issue
        """
        # Comment on proposal
        proposal.create_comment(
            f"✅ **Proposal Approved and Converted**\n\n"
            f"This proposal has been converted to a task: #{task.number}\n\n"
            f"**Task Link**: #{task.number}\n"
            f"**Status**: Ready for implementation"
        )
        
        # Comment on task
        task.create_comment(
            f"📋 **Created from Proposal**\n\n"
            f"This task was created from proposal #{proposal.number}\n\n"
            f"**Original Proposal**: #{proposal.number}\n"
            f"**Conversion Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    
    def _add_error_comment(self, proposal: Issue, error_message: str):
        """Add error comment to proposal issue
        
        Args:
            proposal: Proposal issue that failed conversion
            error_message: Error details
        """
        proposal.create_comment(
            f"⚠️ **Conversion Failed**\n\n"
            f"Failed to convert this proposal to a task.\n\n"
            f"**Error**: {error_message}\n\n"
            f"Please check the proposal format and try again."
        )


def main():
    """Main entry point for task proposal conversion"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    # Get configuration from environment
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        logger.error("GITHUB_TOKEN environment variable not set")
        return 1
    
    repository = os.environ.get('GITHUB_REPOSITORY')
    if not repository:
        logger.error("GITHUB_REPOSITORY environment variable not set")
        return 1
    
    # Prevent recursive execution
    actor = os.environ.get('GITHUB_ACTOR', '')
    if actor == 'github-actions[bot]':
        logger.info("Skipping execution - triggered by automation")
        return 0
    
    try:
        converter = TaskConverter(token, repository)
        created_tasks = converter.process_proposals()
        
        print(f"SUCCESS: Converted {len(created_tasks)} proposals to tasks")
        return 0
        
    except Exception as e:
        logger.error(f"Task conversion failed: {str(e)}")
        return 1


if __name__ == '__main__':
    exit(main())