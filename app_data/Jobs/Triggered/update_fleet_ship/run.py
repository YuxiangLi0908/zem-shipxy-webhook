import sys

UTIL_ROOT = "/home/site/wwwroot"
PYTHON_ROOT = "/home/site/wwwroot/.venv/lib/python3.13/site-packages"
if UTIL_ROOT not in sys.path:
    sys.path.insert(0, UTIL_ROOT)
if PYTHON_ROOT not in sys.path:
    sys.path.insert(0, PYTHON_ROOT)

import os
from datetime import datetime

import requests
from sqlalchemy import text, update

from app.data_models.db.ship_added import ShipAdded
from app.data_models.db.ship_deleted import ShipDeleted
from app.data_models.db.vessel import Vessel
from utils.db_conn import get_db


def get_ships_to_add() -> list[str]:
    db = get_db()
    result = db.execute(
        text(
            """
        SELECT distinct vessel_mmsi
        FROM warehouse_vessel a
        JOIN warehouse_order b
            ON a.id = b.vessel_id_id
        JOIN warehouse_retrieval c
            ON c.id = b.retrieval_id_id
        WHERE
            vessel_mmsi is not null
            AND NOT add_to_shipxy
            AND NOT cancel_notification
    """
        )
    )
    db.close()
    result = result.mappings().all()
    result = [d["vessel_mmsi"] for d in result]
    return result


def get_ships_to_remove() -> list[str]:
    db = get_db()
    result = db.execute(
        text(
            """
        SELECT distinct vessel_mmsi
        FROM warehouse_vessel a
        JOIN warehouse_order b
            ON a.id = b.vessel_id_id
        JOIN warehouse_retrieval c
            ON c.id = b.retrieval_id_id
        WHERE
            vessel_mmsi is not null
            AND add_to_shipxy
            AND (
                (cancel_notification) or
                (temp_t49_pod_arrive_at is not null) or
                (target_retrieval_timestamp is not null)
            )
    """
        )
    )
    db.close()
    result = result.mappings().all()
    result = [d["vessel_mmsi"] for d in result]
    return result


def update_add_to_shipxy(mmsi_list: list[str]) -> int:
    with get_db() as db:
        stmt = (
            update(Vessel)
            .where(Vessel.vessel_mmsi.in_(mmsi_list))
            .values(add_to_shipxy=True)
        )
        result = db.execute(stmt)
        db.commit()
    return result.rowcount


def main():
    print(f"Job starts running at {datetime.now()}")

    ADD_SHIP_URL = os.environ.get("SHIPXY_ADD_SHIP_URL")
    REMOVE_SHIP_URL = os.environ.get("SHIPXY_REMOVE_SHIP_URL")
    API_KEY = os.environ.get("SHIPXY_API_KEY")
    FLEET_ID = os.environ.get("SHIPXY_FLEET_ID")

    ships_to_add = get_ships_to_add()
    ships_to_remove = get_ships_to_remove()

    if ships_to_add:
        resp = requests.post(
            url=ADD_SHIP_URL,
            params={
                "key": API_KEY,
                "fleet_id": FLEET_ID,
                "mmsis": ",".join(ships_to_add),
            }
        )
        if resp.status_code == 200:
            with get_db() as db:
                record = ShipAdded(
                    received_at=datetime.now(), header=dict(resp.headers), body=resp.json()
                )
                db.add(record)
                db.commit()
            print(f"Adding ships successed: {len(ships_to_add)}.")
            print(ships_to_add)

            updated = update_add_to_shipxy(ships_to_add)
            print(f"Updated {updated} containers.")
        else:
            print(f"Adding ships failed: {resp.json()}.")
    else:
        print("No ships to be added.")

    if ships_to_remove:
        resp = requests.post(
            url=REMOVE_SHIP_URL,
            params={
                "key": API_KEY,
                "fleet_id": FLEET_ID,
                "mmsis": ",".join(ships_to_add),
            }
        )
        if resp.status_code == 200:
            with get_db() as db:
                record = ShipDeleted(
                    received_at=datetime.now(), header=dict(resp.headers), body=resp.json()
                )
                db.add(record)
                db.commit()
            print(f"Removing ships successed: {len(ships_to_remove)}.")
            print(ships_to_remove)
        else:
            print(f"Removing ships failed: {resp.json()}.")
    else:
        print("No ships to be removed.")


if __name__ == "__main__":
    main()
