import requests
import pandas as pd
from typing import List, Dict, Iterator, Tuple

try:
    from src.config import settings
except ImportError:
    settings = None

# Mapping endpoint names to the database table names
ENDPOINT_TO_TABLE_MAP = {
    "aries_daily_capacities": "stg_aries__daily_capacities",
    "procount_completiondailytb": "stg_pro_count__completiondailytb",
    "wellview_job": "stg_wellview__job",
    "wellview_jobreport": "stg_wellview__jobreport",
    "wellview_surveypoint": "stg_wellview__surveypoint",
    "wellview_wellheader": "stg_wellview__wellheader",
    "wiserock_note": "stg_wiserock__note",
    "wiserock_user": "stg_wiserock__user",
    "eia_oil_price": "stg_eia__oil_price",
}

# Define the explicit, correct loading order for API endpoints
# This is critical to ensure foreign key constraints are met.
API_LOAD_ORDER = [
    "stg_wellview__wellheader",     # Parent to job, jobreport, surveypoint
    "stg_wiserock__user",           # Parent to note
    "stg_wellview__job",            # Parent to jobreport
    "stg_wellview__jobreport",
    "stg_wellview__surveypoint",
    "stg_wiserock__note",           # Depends on user
    "stg_aries__daily_capacities",
    "stg_pro_count__completiondailytb",
    "stg_eia__oil_price"
]


class ApiExtractor:
    """
    Extracts paginated data from Supabase API endpoints in a specific order.
    """
    def __init__(self, api_key: str, email: str, password: str):
        self.base_url = "https://qlqetcqgadxcicwfzxpw.supabase.co"
        self.api_key = api_key
        self.email = email
        self.password = password
        self.access_token = None
        self.session = requests.Session()

    def _get_access_token(self) -> str:
        if self.access_token:
            return self.access_token
        print("--> Authenticating with API to get access token...")
        auth_url = f"{self.base_url}/auth/v1/token?grant_type=password"
        headers = {"apikey": self.api_key, "Content-Type": "application/json"}
        payload = {"email": self.email.strip(), "password": self.password.strip()}
        try:
            response = self.session.post(auth_url, headers=headers, json=payload)
            response.raise_for_status()
            self.access_token = response.json()["access_token"]
            print("--> Successfully authenticated.")
            return self.access_token
        except requests.exceptions.RequestException as e:
            print(f"FATAL: API authentication error: {e}")
            raise

    def _fetch_all_from_endpoint(self, endpoint_name: str) -> List[Dict]:
        access_token = self._get_access_token()
        headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {access_token}",
            "Prefer": "count=exact"
        }
        url = f"{self.base_url}/rest/v1/{endpoint_name}"
        all_records = []
        offset = 0
        page_size = 1000
        print(f"\n--> Fetching data from endpoint: {endpoint_name}")
        while True:
            headers["Range"] = f"{offset}-{offset + page_size - 1}"
            try:
                response = self.session.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                if not data:
                    break
                all_records.extend(data)
                content_range = response.headers.get("Content-Range")
                if content_range and "/" in content_range:
                    total = int(content_range.split("/")[1])
                    print(f"    > Fetched {len(all_records)} / {total} records...")
                    if len(all_records) >= total:
                        break
                else:
                    break
                offset += page_size
            except requests.exceptions.RequestException as e:
                print(f"    > Error fetching from {endpoint_name}: {e}")
                break
        print(f"--> Finished fetching {endpoint_name}. Total records: {len(all_records)}")
        return all_records

    def extract_all(self) -> Dict[str, pd.DataFrame]:
        """
        Fetches data from all endpoints and returns a dictionary mapping
        table names to their DataFrames. This allows the orchestrator (main.py)
        to control the load order.
        """
        data_map = {}
        # Get the endpoint name from the table name for the request
        endpoint_map = {v: k for k, v in ENDPOINT_TO_TABLE_MAP.items()}
        for table_name in API_LOAD_ORDER:
            endpoint = endpoint_map[table_name]
            records = self._fetch_all_from_endpoint(endpoint)
            if records:
                data_map[table_name] = pd.DataFrame(records)
        return data_map

if settings:
    api_extractor = ApiExtractor(
        api_key=settings.API_KEY,
        email=settings.API_EMAIL,
        password=settings.API_PASSWORD
    )
else:
    api_extractor = None
