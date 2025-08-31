"""Enhanced API client with GraphQL implementation."""
import time
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


@dataclass
class FieldInfo:
    """Field information."""
    field_id: str
    name: str
    data_type: str
    options: Optional[List[Dict[str, Any]]] = None


@dataclass 
class BoardItem:
    """Board item with content and field values."""
    item_id: str
    content_id: Optional[str] = None
    content_type: Optional[str] = None
    content_number: Optional[int] = None
    content_title: Optional[str] = None
    field_values: Optional[Dict[str, Any]] = None


class APIClient:
    """GraphQL API client with retry logic and comprehensive error handling."""
    
    def __init__(self, token: str, max_retries: int = 3, base_delay: float = 1.0):
        """Initialize API client.
        
        Args:
            token: Personal access token
            max_retries: Maximum retry attempts for rate limiting
            base_delay: Base delay for exponential backoff
        """
        self.token = token
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.logger = logging.getLogger(__name__)
        
        # Initialize GraphQL transport
        transport = RequestsHTTPTransport(
            url="https://api.github.com/graphql",
            headers={"Authorization": f"Bearer {token}"},
            retries=max_retries
        )
        
        self.client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Cache for field mappings
        self._field_cache: Dict[str, Dict[str, FieldInfo]] = {}
    
    def get_repository(self, owner: str, repo_name: str) -> Dict[str, Any]:
        """Get repository information.
        
        Args:
            owner: Repository owner
            repo_name: Repository name
            
        Returns:
            Repository data dictionary
        """
        query = gql("""
            query GetRepository($owner: String!, $name: String!) {
              repository(owner: $owner, name: $name) {
                id
                name
                fullName
                private
                url
              }
            }
        """)
        
        variables = {"owner": owner, "name": repo_name}
        result = self._execute_with_retry(query, variables)
        return result.get('repository') if result else None
    
    def get_issues(self, repo_owner: str, repo_name: str, state: str = 'OPEN', 
                  labels: Optional[List[str]] = None, first: int = 100) -> List[Dict[str, Any]]:
        """Get repository issues.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            state: Issue state ('OPEN', 'CLOSED')
            labels: List of label names to filter by
            first: Maximum number of issues to fetch
            
        Returns:
            List of issue data dictionaries
        """
        query = gql("""
            query GetIssues($owner: String!, $name: String!, $states: [IssueState!], $labels: [String!], $first: Int!) {
              repository(owner: $owner, name: $name) {
                issues(states: $states, labels: $labels, first: $first, orderBy: {field: CREATED_AT, direction: DESC}) {
                  nodes {
                    id
                    number
                    title
                    body
                    state
                    labels(first: 10) {
                      nodes {
                        name
                      }
                    }
                    assignees(first: 5) {
                      nodes {
                        login
                      }
                    }
                    createdAt
                    updatedAt
                  }
                }
              }
            }
        """)
        
        variables = {
            "owner": repo_owner,
            "name": repo_name,
            "states": [state],
            "labels": labels or [],
            "first": first
        }
        
        result = self._execute_with_retry(query, variables)
        return result.get('repository', {}).get('issues', {}).get('nodes', []) if result else []
    
    def create_issue(self, repo_id: str, title: str, body: str = '', 
                    labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create new issue.
        
        Args:
            repo_id: Repository node ID
            title: Issue title
            body: Issue body content
            labels: List of label IDs
            
        Returns:
            Created issue data dictionary
        """
        mutation = gql("""
            mutation CreateIssue($repositoryId: ID!, $title: String!, $body: String, $labelIds: [ID!]) {
              createIssue(input: {
                repositoryId: $repositoryId
                title: $title
                body: $body
                labelIds: $labelIds
              }) {
                issue {
                  id
                  number
                  title
                  url
                }
              }
            }
        """)
        
        variables = {
            "repositoryId": repo_id,
            "title": title,
            "body": body,
            "labelIds": labels or []
        }
        
        result = self._execute_with_retry(mutation, variables)
        return result.get('createIssue', {}).get('issue') if result else None
    
    def update_issue(self, issue_id: str, title: Optional[str] = None,
                    body: Optional[str] = None, state: Optional[str] = None) -> Dict[str, Any]:
        """Update existing issue.
        
        Args:
            issue_id: Issue node ID
            title: New title (optional)
            body: New body content (optional)
            state: New state ('OPEN' or 'CLOSED')
            
        Returns:
            Updated issue data dictionary
        """
        mutation = gql("""
            mutation UpdateIssue($issueId: ID!, $title: String, $body: String, $state: IssueState) {
              updateIssue(input: {
                id: $issueId
                title: $title
                body: $body
                state: $state
              }) {
                issue {
                  id
                  number
                  title
                  state
                }
              }
            }
        """)
        
        variables = {"issueId": issue_id}
        if title is not None:
            variables["title"] = title
        if body is not None:
            variables["body"] = body
        if state is not None:
            variables["state"] = state.upper()
        
        result = self._execute_with_retry(mutation, variables)
        return result.get('updateIssue', {}).get('issue') if result else None
    
    def get_board_with_items(self, owner: str, board_number: int, 
                            first: int = 100) -> Dict[str, Any]:
        """Get board with all items and issues in single query.
        
        Args:
            owner: Organization/user login
            board_number: Board number
            first: Maximum items to fetch
            
        Returns:
            Complete board data with items and content
        """
        query = gql("""
            query GetBoard($owner: String!, $number: Int!, $first: Int!) {
              organization(login: $owner) {
                projectV2(number: $number) {
                  id
                  title
                  url
                  fields(first: 20) {
                    nodes {
                      ... on ProjectV2Field {
                        id
                        name
                        dataType
                      }
                      ... on ProjectV2SingleSelectField {
                        id
                        name
                        dataType
                        options {
                          id
                          name
                        }
                      }
                    }
                  }
                  items(first: $first) {
                    nodes {
                      id
                      content {
                        ... on Issue {
                          id
                          number
                          title
                          state
                          labels(first: 10) {
                            nodes {
                              name
                            }
                          }
                          assignees(first: 5) {
                            nodes {
                              login
                            }
                          }
                        }
                      }
                      fieldValues(first: 10) {
                        nodes {
                          ... on ProjectV2ItemFieldTextValue {
                            field {
                              ... on ProjectV2Field {
                                name
                              }
                            }
                            text
                          }
                          ... on ProjectV2ItemFieldSingleSelectValue {
                            field {
                              ... on ProjectV2SingleSelectField {
                                name
                              }
                            }
                            optionId
                            name
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
        """)
        
        variables = {
            "owner": owner,
            "number": board_number,
            "first": first
        }
        
        result = self._execute_with_retry(query, variables)
        
        # Cache field information
        if result and 'organization' in result and result['organization']:
            board_data = result['organization']['projectV2']
            if board_data:
                self._cache_fields(f"{owner}:{board_number}", board_data['fields']['nodes'])
        
        return result
    
    def add_item_to_board(self, board_id: str, content_id: str) -> Dict[str, Any]:
        """Add issue to board.
        
        Args:
            board_id: Board ID
            content_id: Issue node ID
            
        Returns:
            Mutation result
        """
        mutation = gql("""
            mutation AddItem($boardId: ID!, $contentId: ID!) {
              addProjectV2ItemById(input: {
                projectId: $boardId
                contentId: $contentId
              }) {
                item {
                  id
                  content {
                    ... on Issue {
                      number
                      title
                    }
                  }
                }
              }
            }
        """)
        
        variables = {
            "boardId": board_id,
            "contentId": content_id
        }
        
        return self._execute_with_retry(mutation, variables)
    
    def update_item_field(self, board_id: str, item_id: str, 
                         field_id: str, value: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Update board item field value.
        
        Args:
            board_id: Board ID
            item_id: Item ID
            field_id: Field ID to update
            value: New field value (text or single select option)
            
        Returns:
            Mutation result
        """
        # Handle different field value types
        if isinstance(value, dict) and 'singleSelectOptionId' in value:
            # Single select field
            mutation = gql("""
                mutation UpdateField($boardId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
                  updateProjectV2ItemFieldValue(input: {
                    projectId: $boardId
                    itemId: $itemId
                    fieldId: $fieldId
                    value: $value
                  }) {
                    projectV2Item {
                      id
                    }
                  }
                }
            """)
            
            field_value = {
                "singleSelectOptionId": value['singleSelectOptionId']
            }
        else:
            # Text field
            mutation = gql("""
                mutation UpdateField($boardId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
                  updateProjectV2ItemFieldValue(input: {
                    projectId: $boardId
                    itemId: $itemId
                    fieldId: $fieldId
                    value: $value
                  }) {
                    projectV2Item {
                      id
                    }
                  }
                }
            """)
            
            field_value = {
                "text": str(value)
            }
        
        variables = {
            "boardId": board_id,
            "itemId": item_id,
            "fieldId": field_id,
            "value": field_value
        }
        
        return self._execute_with_retry(mutation, variables)
    
    def batch_update_items(self, updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch update multiple board items efficiently.
        
        Args:
            updates: List of update operations with keys:
                    - board_id, item_id, field_id, value
                    
        Returns:
            List of mutation results
        """
        results = []
        
        # Group updates by board for efficiency
        board_groups = {}
        for update in updates:
            board_id = update['board_id']
            if board_id not in board_groups:
                board_groups[board_id] = []
            board_groups[board_id].append(update)
        
        # Execute updates in batches
        for board_id, board_updates in board_groups.items():
            for update in board_updates:
                result = self.update_item_field(
                    update['board_id'],
                    update['item_id'], 
                    update['field_id'],
                    update['value']
                )
                results.append(result)
                
                # Small delay between mutations to avoid rate limiting
                time.sleep(0.1)
        
        return results
    
    def get_field_id_by_name(self, owner: str, board_number: int, field_name: str) -> Optional[str]:
        """Get field ID by name using cached field information.
        
        Args:
            owner: Organization/user login
            board_number: Board number
            field_name: Field name to find
            
        Returns:
            Field ID or None if not found
        """
        board_key = f"{owner}:{board_number}"
        
        # Load fields if not cached
        if board_key not in self._field_cache:
            board_data = self.get_board_with_items(owner, board_number, first=1)
            if not board_data or not board_data.get('organization', {}).get('projectV2'):
                return None
        
        # Search cached fields
        fields_cache = self._field_cache.get(board_key, {})
        field_info = fields_cache.get(field_name)
        return field_info.field_id if field_info else None
    
    def get_select_option_id(self, owner: str, board_number: int, 
                           field_name: str, option_name: str) -> Optional[str]:
        """Get single select option ID for field value updates.
        
        Args:
            owner: Organization/user login  
            board_number: Board number
            field_name: Field name
            option_name: Option name to find
            
        Returns:
            Option ID or None if not found
        """
        board_key = f"{owner}:{board_number}"
        fields_cache = self._field_cache.get(board_key, {})
        field_info = fields_cache.get(field_name)
        
        if not field_info or not field_info.options:
            return None
        
        for option in field_info.options:
            if option['name'] == option_name:
                return option['id']
        
        return None
    
    def get_board_items(self, board_data: Dict[str, Any]) -> List[BoardItem]:
        """Parse board items from board data.
        
        Args:
            board_data: Board data dictionary from API
            
        Returns:
            List of BoardItem objects
        """
        if not isinstance(board_data, dict) or 'items' not in board_data:
            return []
        
        items_data = board_data['items']['nodes']
        board_items = []
        
        for item_data in items_data:
            # Parse field values
            field_values = {}
            for field_value in item_data.get('fieldValues', {}).get('nodes', []):
                if 'field' in field_value and 'name' in field_value['field']:
                    field_name = field_value['field']['name']
                    if 'text' in field_value:
                        field_values[field_name] = field_value['text']
                    elif 'name' in field_value:  # Single select
                        field_values[field_name] = field_value['name']
            
            # Extract content info
            content = item_data.get('content', {})
            board_item = BoardItem(
                item_id=item_data['id'],
                content_id=content.get('id'),
                content_type='Issue' if 'number' in content else None,
                content_number=content.get('number'),
                content_title=content.get('title'),
                field_values=field_values
            )
            
            board_items.append(board_item)
        
        return board_items
    
    def get_commits(self, repo_owner: str, repo_name: str, since: Optional[str] = None, 
                   until: Optional[str] = None, branch: str = "main", first: int = 100) -> List[Dict[str, Any]]:
        """Get repository commits.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            since: Only commits after this date (ISO format)
            until: Only commits before this date (ISO format)
            branch: Branch name to query
            first: Maximum number of commits to fetch
            
        Returns:
            List of commit data dictionaries
        """
        query = gql("""
            query GetCommits($owner: String!, $name: String!, $ref: String!, $since: GitTimestamp, $until: GitTimestamp, $first: Int!) {
              repository(owner: $owner, name: $name) {
                ref(qualifiedName: $ref) {
                  target {
                    ... on Commit {
                      history(since: $since, until: $until, first: $first) {
                        nodes {
                          oid
                          message
                          committedDate
                          author {
                            name
                            email
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
        """)
        
        variables = {
            "owner": repo_owner,
            "name": repo_name,
            "ref": f"refs/heads/{branch}",
            "first": first
        }
        
        if since:
            variables["since"] = since
        if until:
            variables["until"] = until
        
        result = self._execute_with_retry(query, variables)
        history = result.get('repository', {}).get('ref', {}).get('target', {}).get('history', {})
        return history.get('nodes', []) if history else []
    
    def get_commit(self, repo_owner: str, repo_name: str, commit_sha: str) -> Dict[str, Any]:
        """Get a single commit by SHA.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            commit_sha: Commit SHA
            
        Returns:
            Commit data dictionary
        """
        query = gql("""
            query GetCommit($owner: String!, $name: String!, $oid: GitObjectID!) {
              repository(owner: $owner, name: $name) {
                object(oid: $oid) {
                  ... on Commit {
                    oid
                    message
                    committedDate
                    author {
                      name
                      email
                    }
                  }
                }
              }
            }
        """)
        
        variables = {
            "owner": repo_owner,
            "name": repo_name,
            "oid": commit_sha
        }
        
        result = self._execute_with_retry(query, variables)
        return result.get('repository', {}).get('object', {}) if result else {}
    
    def get_rate_limit(self) -> Dict[str, Any]:
        """Get current rate limit status.
        
        Returns:
            Dictionary with rate limit information
        """
        query = gql("""
            query GetRateLimit {
              rateLimit {
                limit
                remaining
                resetAt
                used
              }
            }
        """)
        
        result = self._execute_with_retry(query, {})
        rate_limit = result.get('rateLimit', {}) if result else {}
        
        return {
            'limit': rate_limit.get('limit', 0),
            'remaining': rate_limit.get('remaining', 0),
            'reset': rate_limit.get('resetAt'),
            'used': rate_limit.get('used', 0)
        }
    
    def _cache_fields(self, board_key: str, fields_data: List[Dict[str, Any]]):
        """Cache board field information for efficient lookups."""
        fields_cache = {}
        
        for field in fields_data:
            field_info = FieldInfo(
                field_id=field['id'],
                name=field['name'],
                data_type=field['dataType'],
                options=field.get('options', []) if 'options' in field else None
            )
            fields_cache[field['name']] = field_info
        
        self._field_cache[board_key] = fields_cache
    
    
    def _execute_with_retry(self, query_or_mutation, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Execute operation with retry logic for rate limiting."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = self.client.execute(query_or_mutation, variable_values=variables)
                return result
                
            except Exception as e:
                last_exception = e
                error_str = str(e).lower()
                
                # Handle rate limiting
                if 'rate limit' in error_str or 'abuse detection' in error_str:
                    if attempt < self.max_retries:
                        delay = self.base_delay * (2 ** attempt)
                        self.logger.warning(
                            f"Rate limited, retrying in {delay}s (attempt {attempt + 1}/{self.max_retries + 1})"
                        )
                        time.sleep(delay)
                        continue
                
                # Handle secondary rate limits  
                elif 'secondary rate limit' in error_str:
                    if attempt < self.max_retries:
                        delay = 60  # Wait 1 minute
                        self.logger.warning(
                            f"Secondary rate limit, waiting {delay}s"
                        )
                        time.sleep(delay)
                        continue
                
                # For other errors, don't retry
                raise
        
        # All retries exhausted
        raise last_exception
    
    def get_repository_labels(self, repo_owner: str, repo_name: str) -> List[Dict[str, Any]]:
        """Get all repository labels.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            
        Returns:
            List of label dictionaries with id, name, color
        """
        query = gql("""
            query GetLabels($owner: String!, $name: String!) {
              repository(owner: $owner, name: $name) {
                labels(first: 100) {
                  nodes {
                    id
                    name
                    color
                    description
                  }
                }
              }
            }
        """)
        
        variables = {"owner": repo_owner, "name": repo_name}
        result = self._execute_with_retry(query, variables)
        return result.get('repository', {}).get('labels', {}).get('nodes', []) if result else []
    
    def add_labels_to_issue(self, issue_id: str, label_ids: List[str]) -> Dict[str, Any]:
        """Add labels to an issue.
        
        Args:
            issue_id: Issue node ID
            label_ids: List of label node IDs to add
            
        Returns:
            Mutation result
        """
        mutation = gql("""
            mutation AddLabelsToIssue($issueId: ID!, $labelIds: [ID!]!) {
              addLabelsToLabelable(input: {
                labelableId: $issueId
                labelIds: $labelIds
              }) {
                labelable {
                  ... on Issue {
                    id
                    labels(first: 10) {
                      nodes {
                        name
                      }
                    }
                  }
                }
              }
            }
        """)
        
        variables = {
            "issueId": issue_id,
            "labelIds": label_ids
        }
        
        return self._execute_with_retry(mutation, variables)
    
    def remove_labels_from_issue(self, issue_id: str, label_ids: List[str]) -> Dict[str, Any]:
        """Remove labels from an issue.
        
        Args:
            issue_id: Issue node ID
            label_ids: List of label node IDs to remove
            
        Returns:
            Mutation result
        """
        mutation = gql("""
            mutation RemoveLabelsFromIssue($issueId: ID!, $labelIds: [ID!]!) {
              removeLabelsFromLabelable(input: {
                labelableId: $issueId
                labelIds: $labelIds
              }) {
                labelable {
                  ... on Issue {
                    id
                    labels(first: 10) {
                      nodes {
                        name
                      }
                    }
                  }
                }
              }
            }
        """)
        
        variables = {
            "issueId": issue_id,
            "labelIds": label_ids
        }
        
        return self._execute_with_retry(mutation, variables)
    
    def get_label_id_by_name(self, repo_owner: str, repo_name: str, label_name: str) -> Optional[str]:
        """Get label ID by name.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            label_name: Label name to find
            
        Returns:
            Label ID or None if not found
        """
        labels = self.get_repository_labels(repo_owner, repo_name)
        for label in labels:
            if label.get('name') == label_name:
                return label.get('id')
        return None

    def close(self):
        """Close the API client connection."""
        if hasattr(self.client.transport, 'close'):
            self.client.transport.close()