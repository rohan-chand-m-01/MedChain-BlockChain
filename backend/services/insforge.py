import os
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Load from root .env file
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / '.env')

INSFORGE_BASE_URL = os.getenv("INSFORGE_BASE_URL", "")
INSFORGE_SERVICE_KEY = os.getenv("INSFORGE_SERVICE_KEY", "")


def _headers():
    return {
        "apikey": INSFORGE_SERVICE_KEY,
        "Authorization": f"Bearer {INSFORGE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


async def db_insert(table: str, payload: dict) -> dict:
    """Insert a row into an InsForge (PostgREST) table and return the created record."""
    import logging
    logger = logging.getLogger(__name__)
    
    url = f"{INSFORGE_BASE_URL}/api/database/records/{table}"
    # InsForge requires the payload to be an array even for single inserts
    payload_list = [payload]
    
    # We must add Prefer: return=representation if not already present
    headers = _headers()
    headers["Prefer"] = "return=representation"

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload_list, headers=headers)
        
        if not resp.is_success:
            logger.error(f"[DB_INSERT] Failed with status {resp.status_code}")
            logger.error(f"[DB_INSERT] Response body: {resp.text}")
            logger.error(f"[DB_INSERT] Payload sent: {payload}")
        
        resp.raise_for_status()
        data = resp.json()
        return data[0] if getattr(data, '__iter__', False) and len(data) > 0 else data


async def db_select(table: str, filters: dict = None, order: str = None, limit: int = None, select: str = "*") -> list:
    """Select rows from an InsForge (PostgREST) table."""
    import logging
    logger = logging.getLogger(__name__)
    
    url = f"{INSFORGE_BASE_URL}/api/database/records/{table}"
    params = {"select": select}
    if filters:
        params.update({f"{k}": f"eq.{v}" for k, v in filters.items()})
    if order:
        params["order"] = order
    
    # PostgREST uses Range header for pagination
    headers = _headers()
    if limit:
        headers["Range"] = f"0-{limit-1}"  # Request rows 0 to limit-1
    else:
        # Request a large range to get all records (up to 10000)
        headers["Range"] = "0-9999"  # Get up to 10000 records
    
    logger.info(f"[DB_SELECT] Querying {table} with params: {params}")
    logger.info(f"[DB_SELECT] Using Range header: {headers.get('Range')}")

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        
        # Log Content-Range if present (shows total available rows)
        content_range = resp.headers.get('Content-Range')
        if content_range:
            logger.info(f"[DB_SELECT] Content-Range from API: {content_range}")
        
        logger.info(f"[DB_SELECT] Received {len(data) if isinstance(data, list) else 'non-list'} records from database")
        return data


async def db_select_single(table: str, filters: dict = None, select: str = "*", order: str = None) -> dict | None:
    """Select a single row. Returns None if not found."""
    rows = await db_select(table, filters=filters, order=order, limit=1, select=select)
    return rows[0] if rows else None


async def db_update(table: str, row_id: str, payload: dict) -> dict:
    """Update a row by id in an InsForge (PostgREST) table."""
    url = f"{INSFORGE_BASE_URL}/api/database/records/{table}"
    params = {"id": f"eq.{row_id}"}
    
    headers = _headers()
    headers["Prefer"] = "return=representation"

    async with httpx.AsyncClient() as client:
        resp = await client.patch(url, json=payload, params=params, headers=headers)
        if not resp.is_success:
            raise Exception(f"Database update failed with {resp.status_code}: {resp.text}")
        data = resp.json()
        # the response should be an array according to the docs
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        return data


async def db_delete(table: str, row_id: str) -> None:
    """Delete a row by id from an InsForge (PostgREST) table."""
    url = f"{INSFORGE_BASE_URL}/api/database/records/{table}"
    params = {"id": f"eq.{row_id}"}
    async with httpx.AsyncClient() as client:
        resp = await client.delete(url, params=params, headers=_headers())
        resp.raise_for_status()
