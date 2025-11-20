import asyncio
import httpx
import os
import requests

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text


SEARCH_SHIP_URL = "https://api.shipxy.com/apicall/v3/SearchShip"

async def fetch_mmsi(api_key: str, imo: str) -> dict[str: int | None]:
    params = {
        "key": api_key,
        "keywords": imo,
        "max": 1,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(SEARCH_SHIP_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        try:
            result = {imo: data["data"][0]["mmsi"]}
        except:
            result = {imo: None}
        return result

async def fetch_all_mmsi(api_key:str, imo_list: list[str]) -> list[dict[str: int | None]]:
    tasks = [
        fetch_mmsi(api_key=api_key, imo=imo) for imo in imo_list
    ]
    result = await asyncio.gather(*tasks)
    return list(result)


async def fetch_all_mmsi_async():
    api_key = os.environ.get("SHIPXY_API_KEY")
    # imo_list = get_vessel_imo()
    imo_list = ["9972892", "9960514", "9955272"]
    mmsi = await fetch_all_mmsi(api_key=api_key, imo_list=imo_list)
    return mmsi


def get_db():
    user = os.environ.get("DBUSER")
    password = os.environ.get("DBPASS")
    host = os.environ.get("DBHOST")
    db_name = os.environ.get("DBNAME")
    port = os.environ.get("DBPORT")
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

    engine = create_engine(
        db_url,
        pool_size=10,
        max_overflow=20,
    )
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = session_local()
    print(type(db))
    return db


def get_vessel_imo() -> list[str]:
    db = get_db()
    result = db.execute(text("""
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
    """))
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
    
    values_sql = ",".join(
        f"('{imo}', '{mmsi}')"
        for imo, mmsi in rows
    )

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
