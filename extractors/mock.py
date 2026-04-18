"""
Mock BI Extractor using Faker.
Generates deterministic, relational synthetic enterprise metadata for local development.
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

# --- ENTERPRISE VOCABULARY ---
DEPARTMENTS = ["Finance", "Sales", "HR", "Marketing", "Supply Chain", "IT", "Operations", "C-Suite"]
REGIONS = ["Global", "EMEA", "NA", "APAC", "LATAM"]
ENVIRONMENTS = ["PROD", "UAT", "DEV"]
DASHBOARD_TYPES = ["Overview", "Deep Dive", "Analytics", "Scorecard", "Tracker", "Report", "Cockpit"]
METRICS = {
    "Finance": ["Revenue", "Margin", "OpEx", "EBITDA", "Cash Flow", "Forecasting"],
    "Sales": ["Pipeline", "Win/Loss", "Quota Attainment", "Churn", "Bookings", "ARR"],
    "HR": ["Headcount", "Attrition", "Diversity", "Time-to-Hire", "Compensation"],
    "Marketing": ["Campaign ROI", "Web Traffic", "Lead Gen", "Conversion", "CAC"],
    "Supply Chain": ["Inventory", "Logistics", "Vendor Performance", "Freight", "Procurement"],
    "IT": ["Server Uptime", "Helpdesk Tickets", "Cloud Spend", "Security Incidents"],
    "Operations": ["Factory Yield", "OEE", "Safety Incidents", "Utilization", "Downtime"],
    "C-Suite": ["Executive Summary", "Board KPIs", "Strategic Initiatives", "ESG"]
}

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
        """Generates realistic mock workspaces for enterprise departments."""
        logger.info(f"Generating {count} mock workspaces for {self.platform}...")
        workspaces = []
        space_types = ["Shared", "Managed", "Personal"] if self.platform == "Qlik" else ["Workspace", "Premium Workspace"]
        
        for _ in range(count):
            dept = random.choice(DEPARTMENTS)
            region = random.choice(REGIONS)
            env = random.choices(ENVIRONMENTS, weights=[70, 20, 10])[0] # Heavy weighting to PROD
            
            ws = {
                "workspace_id": str(uuid.uuid4()),
                "workspace_name": f"{dept} Analytics - {region} [{env}]",
                "workspace_type": random.choice(space_types),
                "platform": self.platform,
                "department": dept # Track this so apps can use matching metrics
            }
            workspaces.append(ws)
        
        self._workspaces = workspaces
        return workspaces

    def get_apps(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generates mock dashboards with realistic KPI names assigned to generated workspaces."""
        if not self._workspaces:
            self.get_workspaces()

        logger.info(f"Generating {count} mock apps for {self.platform}...")
        apps = []
        for _ in range(count):
            workspace = random.choice(self._workspaces)
            dept = workspace.get("department", random.choice(DEPARTMENTS))
            metric = random.choice(METRICS[dept])
            dtype = random.choice(DASHBOARD_TYPES)
            
            apps.append({
                "app_id": str(uuid.uuid4()),
                "app_name": f"{metric} {dtype}",
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
                "role": random.choices(roles, weights=[60, 20, 10, 10])[0], # Mostly viewers
                "granted_at": self.fake.date_time_this_month().isoformat()
            })
        return assignments