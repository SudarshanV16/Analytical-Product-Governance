"""
Abstract Base Class for BI Metadata Extractors.
Defines the standard contract for all BI tool integrations.
"""
import abc
from typing import List, Dict, Any

class BaseBIExtractor(abc.ABC):
    """
    Abstract Base Class defining the contract for all BI Metadata Extractors.
    Any new BI tool added to the governance hub must implement these methods.
    """
    
    def __init__(self, tenant_url: str, api_key: str):
        self.tenant_url = tenant_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    @abc.abstractmethod
    def get_workspaces(self, count: int = 5) -> List[Dict[str, Any]]:
        """Fetch all workspaces/spaces."""
        pass

    @abc.abstractmethod
    def get_apps(self, count: int = 20) -> List[Dict[str, Any]]:
        """Fetch all dashboards/apps/reports."""
        pass

    @abc.abstractmethod
    def get_users(self, count: int = 15) -> List[Dict[str, Any]]:
        """Fetch user directory."""
        pass

    @abc.abstractmethod
    def get_user_access(self, num_assignments: int = 30) -> List[Dict[str, Any]]:
        """Fetch user assignments and access rights."""
        pass