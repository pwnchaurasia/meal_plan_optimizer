from typing import List, Dict, Any

from integrations.base_fitness_provider import BaseFitnessProvider
from integrations.fitbit import FitbitProvider
from integrations.google_fit import GoogleFitProvider
from utils.enums import FitnessProvider
from datetime import date, datetime


class FitnessAppConnectionFactory:
    """Factory class to create appropriate fitness provider instances"""

    # Registry of available providers
    _providers = {
        FitnessProvider.GOOGLE_FIT: GoogleFitProvider,
        FitnessProvider.FITBIT: FitbitProvider,
    }

    # Provider-specific credentials/config
    # urls and everything should get loaded from .env file or some other creds storage because
    # it would be different for dev, sit, and prod
    _credentials = {
        FitnessProvider.GOOGLE_FIT: {
            "client_id": "your_google_client_id",
            "client_secret": "your_google_client_secret",
            "redirect_uri": "https://yourapp.com/auth/google/callback"
        },
        FitnessProvider.FITBIT: {
            "client_id": "your_fitbit_client_id",
            "client_secret": "your_fitbit_client_secret",
            "redirect_uri": "https://yourapp.com/auth/fitbit/callback"
        },
        FitnessProvider.APPLE_HEALTH: {
            "app_id": "your_ios_app_id"
        }
    }

    @classmethod
    def create_provider(cls, provider_type: FitnessProvider) -> BaseFitnessProvider:

        if provider_type not in cls._providers:
            raise ValueError(f"Unsupported fitness provider: {provider_type}")

        provider_class = cls._providers[provider_type]
        credentials = cls._credentials[provider_type]

        return provider_class(credentials)

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of supported fitness providers"""
        return list(cls._providers.keys())

    @classmethod
    def is_provider_supported(cls, provider_type: str) -> bool:
        """Check if provider is supported"""
        try:
            return FitnessProvider(provider_type) in cls._providers
        except ValueError:
            return False


class FitnessConnectionService:
    """High-level service for managing fitness connections"""

    def connect_user_to_provider(self, user_id: int, provider_type: str, authorization_code: str) -> Dict[str, Any]:
        try:
            # Create provider using factory
            provider = FitnessAppConnectionFactory.create_provider(FitnessProvider(provider_type))

            # Authenticate with provider
            auth_result = provider.authenticate(authorization_code)

            # Store tokens in database (UserFitnessConnection model)
            # This would save to your database

            return {
                "status": "success",
                "provider": provider_type,
                "connected_at": datetime.utcnow(),
                "message": f"Successfully connected to {provider_type}"
            }

        except ValueError as e:
            return {
                "status": "error",
                "message": f"Unsupported provider: {provider_type}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}"
            }

    def sync_user_data(self, user_id: int, provider_type: str, access_token: str, target_date: date) -> Dict[str, Any]:
        try:
            # Create provider
            provider = FitnessAppConnectionFactory.create_provider(FitnessProvider(provider_type))

            # Get daily data
            fitness_data = provider.get_daily_data(access_token, target_date)

            # Store in database (DailyFitnessData model)
            # This would save to your database

            return {
                "status": "success",
                "user_id": user_id,
                "provider": provider_type,
                "date": target_date,
                "data": fitness_data
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Sync failed: {str(e)}"
            }