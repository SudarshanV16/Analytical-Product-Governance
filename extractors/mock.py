"""
Mock BI Extractor using Faker.
Generates deterministic, relational synthetic metadata for local development.
"""
import logging
import random
import uuid
from typing import List, Dict, Any
from faker import Faker

from .base import BaseBIExtractor

# Configure logging for standard output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockBIExtractor(BaseBIExtractor):
    """
    Generates synthetic, relational BI metadata for local testing.
    Maintains foreign key relationships (e.g., app.workspace_id -> workspace.id).
    """

    def __init__(self, platform: str = "Power BI", seed: int = 42):
        """
        Initializes the Mock Extractor.
        
        Args:
            platform (str): The BI platform to simulate ('Power BI', 'Qlik', etc.).
            seed (int): Random seed for reproducible mock data generation.
        """
        # Call super with dummy credentials to satisfy the Base class contract
        super().__init__(tenant_url="http://localhost.mock", api_key="mock_key")
        
        self.platform = platform
        self.fake = Faker()
        Faker.seed(seed)
        random.seed(seed)
        
        # Internal state to maintain relational integrity between generation steps
        self._workspaces: List[Dict[str, Any]] = []
        self._users: List[Dict[str, Any]] = []

    def get_workspaces(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generates mock workspaces or spaces."""
        logger.info(f"Generating {count} mock workspaces for {self.platform}...")
        workspaces = []
        space_types = ["Shared", "Managed", "Personal"] if self.platform == "Qlik" else ["Workspace", "Premium Workspace"]
        
        for _ in range(count):
            ws = {
                "workspace_id": str(uuid.uuid4()),
                "workspace_name": f"[{self.fake.word().upper()}] {self.fake.catch_phrase()} Analytics",
                "workspace_type": random.choice(space_types),
                "platform": self.platform
            }
            workspaces.append(ws)
        
        self._workspaces = workspaces
        return workspaces

    def get_apps(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generates mock dashboards assigned to previously generated workspaces."""
        if not self._workspaces:
            self.get_workspaces()

        logger.info(f"Generating {count} mock apps for {self.platform}...")
        apps = []
        for _ in range(count):
            workspace = random.choice(self._workspaces)
            apps.append({
                "app_id": str(uuid.uuid4()),
                "app_name": f"{self.fake.job()} Dashboard",
                "workspace_id": workspace["workspace_id"],
                "owner_name": self.fake.name(),
                "created_at": self.fake.date_time_this_year().isoformat(),
                "platform": self.platform
            })
        return apps

    def get_users(self, count: int = 15) -> List[Dict[str, Any]]:
        """Generates mock users for the directory."""
        logger.info(f"Generating {count} mock users...")
        users = []
        for _ in range(count):
            users.append({
                "user_id": str(uuid.uuid4()),
                "user_name": self.fake.name(),
                "email": self.fake.company_email()
            })
        self._users = users
        return users

    def get_user_access(self, num_assignments: int = 30) -> List[Dict[str, Any]]:
        """Generates mock access assignments mapping users to workspaces."""
        if not self._users or not self._workspaces:
            logger.error("Must generate users and workspaces before generating access.")
            return []

        logger.info(f"Generating {num_assignments} mock access assignments...")
        assignments = []
        roles = ["Viewer", "Contributor", "Admin", "Data Steward"]
        
        for _ in range(num_assignments):
            assignments.append({
                "assignment_id": str(uuid.uuid4()),
                "workspace_id": random.choice(self._workspaces)["workspace_id"],
                "user_id": random.choice(self._users)["user_id"],
                "role": random.choice(roles),
                "granted_at": self.fake.date_time_this_month().isoformat()
            })
        return assignments