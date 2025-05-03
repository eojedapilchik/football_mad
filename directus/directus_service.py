import json
import os
from typing import Any, Optional

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()


class DirectusQueryParams(BaseModel):
    entity: str
    filter: Optional[dict[str, Any]] = None
    limit: Optional[int] = None
    sort: Optional[str] = None
    fields: Optional[str] = None
    aggregation_type: Optional[str] = None
    aggregation_field: Optional[str] = None
    group_by: Optional[str] = None


class DirectusService:
    def __init__(self, base_url: Optional[str] = None,
                 token: Optional[str] = None):
        if not token:
            token = os.getenv("DIRECTUS_TOKEN")
        if not base_url:
            base_url = os.getenv("DIRECTUS_BASE_URL")
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def get_items(self, params: DirectusQueryParams) -> list:
        url = f"{self.base_url}/items/{params.entity}"
        query = {}

        if params.filter:
            query["filter"] = json.dumps(
                params.filter)  # ✅ Proper stringified JSON
        if params.limit:
            query["limit"] = params.limit
        if params.sort:
            query["sort"] = params.sort
        if params.fields:
            query["fields"] = params.fields
        if params.aggregation_type and params.aggregation_field:
            query[
                f"aggregate[{params.aggregation_type}]"] = params.aggregation_field
        if params.group_by:
            query["groupBy[]"] = params.group_by

        response = httpx.get(url, headers=self.headers, params=query)
        response.raise_for_status()
        return response.json()["data"]

    def get_event_qualifier_by_opta_id(self, opta_id: int) -> Optional[
        dict[str, Any]]:
        params = DirectusQueryParams(
            entity="opta_event_qualifiers",
            filter={"opta_id": {"_eq": opta_id}},
            limit=1,
        )
        results = self.get_items(params)
        return results[0] if results else None


if __name__ == "__main__":
    opta_id_to_test = 21
    service = DirectusService()

    print(
        f"🔍 Looking for Opta ID {opta_id_to_test} in 'opta_event_qualifiers'...")
    result = service.get_event_qualifier_by_opta_id(opta_id_to_test)

    if result:
        print("✅ Found qualifier:")
        print(result)
    else:
        print("❌ No qualifier found for that Opta ID.")
