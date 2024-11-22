# src/configs/msal_config.py
from msal import ConfidentialClientApplication
from src.configs.settings import settings

# Create a global instance of the MSAL confidential client application
common_tenant = "common"
msal_app = ConfidentialClientApplication(
    client_id=settings.AZURE_AD_CLIENT_ID,
    client_credential=settings.AZURE_AD_CLIENT_SECRET,
    authority=f"https://login.microsoftonline.com/{common_tenant}"
)
