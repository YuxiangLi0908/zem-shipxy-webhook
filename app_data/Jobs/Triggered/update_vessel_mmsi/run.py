import sys

UTIL_ROOT = "/home/site/wwwroot"
PYTHON_ROOT = "/home/site/wwwroot/.venv/lib/python3.13/site-packages"
if UTIL_ROOT not in sys.path:
    sys.path.insert(0, UTIL_ROOT)
if PYTHON_ROOT not in sys.path:
    sys.path.insert(0, PYTHON_ROOT)

import asyncio
import os
from datetime import datetime

import httpx
from sqlalchemy import text

from utils.db_conn import get_db

SEARCH_SHIP_URL = os.environ.get("SHIPXY_SEARCH_SHIP_URL")


async def fetch_mmsi(api_key: str, imo: str) -> dict[str : int | None]:
    params = {
        "key": api_key,
        "keywords": imo,
        "max": 20,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(SEARCH_SHIP_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        try:
            records = data["data"]
            latest = max(records, key=lambda r: r["last_time_utc"])
            result = {imo: latest["mmsi"]}
        except:
            result = {imo: None}
        return result


async def fetch_all_mmsi(
    api_key: str, imo_list: list[str]
) -> list[dict[str : int | None]]:
    tasks = [fetch_mmsi(api_key=api_key, imo=imo) for imo in imo_list]
    result = await asyncio.gather(*tasks)
    return list(result)


async def fetch_all_mmsi_async() -> list[dict[str : int | None]]:
    api_key = os.environ.get("SHIPXY_API_KEY")
    imo_list = get_vessel_imo()
    mmsi = await fetch_all_mmsi(api_key=api_key, imo_list=imo_list)
    return mmsi


def get_vessel_imo() -> list[str]:
    db = get_db()
    result = db.execute(
        text(
            """
        SELECT distinct vessel_imo
        FROM warehouse_vessel a
        JOIN warehouse_order b
            ON a.id = b.vessel_id_id
        JOIN warehouse_retrieval c
            ON c.id = b.retrieval_id_id
        WHERE
            temp_t49_pod_arrive_at is null
            AND target_retrieval_timestamp is null
            AND vessel_mmsi is null
            AND vessel_imo is not null
            AND NOT cancel_notification
    """
        )
    )
    db.close()
    result = result.mappings().all()
    result = [d["vessel_imo"] for d in result]
    return result


def main():
    print(f"Job starts running at {datetime.now()}")
    imo_to_mmsi = asyncio.run(fetch_all_mmsi_async())
    print(imo_to_mmsi)

    rows = []
    for item in imo_to_mmsi:
        for imo, mmsi in item.items():
            rows.append((imo, str(mmsi)))

    if len(rows) == 0:
        print("No vessel to search!")
        return 0

    values_sql = ",".join(f"('{imo}', '{mmsi}')" for imo, mmsi in rows)

    sql = f"""
        UPDATE warehouse_vessel AS v
        SET vessel_mmsi = vals.mmsi
        FROM (
            VALUES {values_sql}
        ) AS vals(imo, mmsi)
        WHERE v.vessel_imo = vals.imo;
    """
    db = get_db()
    db.execute(text(sql))
    db.commit()
    db.close()
    print(f"{len(rows)} vessel mmsi updated.")


if __name__ == "__main__":
    main()
