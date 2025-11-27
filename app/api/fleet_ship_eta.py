from datetime import datetime

from fastapi import APIRouter, Request, status

from app.data_models.db.ship_eta_received import ShipEtaReceived
from utils.db_conn import get_db

router = APIRouter()


@router.post("/shipeta", status_code=status.HTTP_201_CREATED)
async def receive_ship_added(request: Request):
    """Receive ship-added POST requests and persist them to the DB.

    - Stores request headers into `header` JSON column
    - Stores request body into `body` JSON column
    - Saves the current UTC timestamp to `received_at`
    """
    # read body and headers
    try:
        body = await request.json()
    except Exception:
        # if body isn't JSON, store raw text
        body = (await request.body()).decode("utf-8", errors="replace")

    headers = dict(request.headers)

    db = get_db()
    try:
        record = ShipEtaReceived(received_at=datetime.now(), header=headers, body=body)
        db.add(record)
        db.commit()
        db.refresh(record)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return {"id": getattr(record, "id", None), "status": "created"}
