from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import date, datetime


## factory pattern to get the instance of different kind of integration class
## we can have many integration


class BaseFitnessProvider(ABC):
    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.client = None

    @abstractmethod
    def authenticate(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        pass

    @abstractmethod
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh expired access token"""
        pass

    @abstractmethod
    def get_daily_data(self, access_token: str, target_date: date) -> Dict[str, Any]:
        """Get daily fitness data for specific date"""
        pass

    @abstractmethod
    def test_connection(self, access_token: str) -> bool:
        """Test if connection is still valid"""
        pass