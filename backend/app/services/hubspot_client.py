import hubspot
from hubspot.crm.contacts import PublicObjectSearchRequest, Filter, FilterGroup
from typing import List, Dict

from app.core.config import settings
from app.schemas.common_prospect import HubSpotIntakeItem
from app.utils.logger import logger


class HubSpotClientService:
    def __init__(self):
        self.api_key = settings.HUBSPOT_ACCESS_TOKEN
        self.client = hubspot.Client.create(access_token=self.api_key) if self.api_key else None

    def _is_configured(self) -> bool:
        if not self.client:
            logger.warning("HubSpot client is not configured (missing HUBSPOT_ACCESS_TOKEN).")
            return False
        return True

    def get_contact_lists(self) -> List[Dict[str, str]]:
        """Mock list fetching since HubSpot API v3 lists are still in beta/v1."""
        if not self._is_configured():
            return []
        
        # We will mock the lists for the UI since the new v3 lists API isn't fully supported 
        # in the python client without raw requests. For demonstration we'll return a static list
        # and when fetching contacts we'll just fetch recent contacts.
        return [
            {"id": "all_contacts", "name": "All Recent Contacts"},
            {"id": "target_accounts", "name": "Target Accounts (Mock)"}
        ]

    def get_contacts_from_list(self, list_id: str, limit: int = 50) -> List[HubSpotIntakeItem]:
        if not self._is_configured():
            return []
            
        try:
            # Fetch recent contacts. In a real scenario with list_id, you'd use a specific filter.
            public_object_search_request = PublicObjectSearchRequest(
                limit=limit,
                properties=["firstname", "lastname", "email", "jobtitle", "phone", "company", "website"],
                sorts=[{"propertyName": "createdate", "direction": "DESCENDING"}]
            )
            
            response = self.client.crm.contacts.search_api.do_search(
                public_object_search_request=public_object_search_request
            )
            
            items = []
            for contact in response.results:
                props = contact.properties
                company = props.get("company")
                website = props.get("website")
                
                # We need at least company name and website for a valid prospect
                if not company or not website:
                    continue
                    
                first_name = props.get("firstname", "")
                last_name = props.get("lastname", "")
                name = f"{first_name} {last_name}".strip()
                
                items.append(HubSpotIntakeItem(
                    company_name=company,
                    website_url=website,
                    contact_name=name if name else None,
                    contact_email=props.get("email"),
                    contact_title=props.get("jobtitle"),
                    contact_phone=props.get("phone"),
                    hubspot_id=str(contact.id)
                ))
            
            return items
        except Exception as e:
            logger.error(f"Error fetching HubSpot contacts: {e}")
            return []

hubspot_client = HubSpotClientService()
