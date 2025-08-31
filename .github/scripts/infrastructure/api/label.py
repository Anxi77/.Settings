"""Label operations mixin."""
from typing import Optional, Dict, Any
from gql import gql

class LabelMixin:
    """Mixin for label-related operations."""

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

    def create_label(self, repo_id: str, name: str, color: str = "0969da", description: str = "") -> Optional[Dict[str, Any]]:
        """Create a new label in the repository.

        Args:
            repo_id: Repository ID
            name: Label name
            color: Label color (hex without #)
            description: Label description

        Returns:
            Created label data or None if failed
        """
        mutation = gql("""
            mutation CreateLabel($repositoryId: ID!, $name: String!, $color: String!, $description: String) {
                createLabel(input: {
                    repositoryId: $repositoryId
                    name: $name
                    color: $color
                    description: $description
                }) {
                    label {
                        id
                        name
                        color
                        description
                        url
                    }
                }
            }
        """)

        variables = {
            "repositoryId": repo_id,
            "name": name,
            "color": color,
            "description": description
        }

        result = self._execute_with_retry(mutation, variables)
        return result.get('createLabel', {}).get('label') if result else None

    def get_or_create_label(self, repo_owner: str, repo_name: str, label_name: str, color: str = "0969da", description: str = "") -> Optional[str]:
        """Get label ID by name, create if it doesn't exist.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            label_name: Label name
            color: Label color (hex without #) for creation
            description: Label description for creation

        Returns:
            Label ID or None if failed
        """
        # First try to get existing label
        label_id = self.get_label_id_by_name(repo_owner, repo_name, label_name)
        if label_id:
            return label_id

        # Get repository ID for label creation
        repo = self.get_repository(repo_owner, repo_name)
        if not repo:
            self.logger.error(f"Repository {repo_owner}/{repo_name} not found")
            return None

        repo_id = repo.get('id')
        if not repo_id:
            self.logger.error(f"Could not get repository ID for {repo_owner}/{repo_name}")
            return None

        # Create the label
        self.logger.info(f"Creating label '{label_name}' in {repo_owner}/{repo_name}")
        created_label = self.create_label(repo_id, label_name, color, description)

        if created_label:
            self.logger.info(f"Successfully created label '{label_name}' with ID: {created_label.get('id')}")
            return created_label.get('id')
        else:
            self.logger.error(f"Failed to create label '{label_name}'")
            return None
