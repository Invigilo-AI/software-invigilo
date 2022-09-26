from copy import deepcopy
from typing import Any, Callable, List

from fastapi import Depends, Request
from pydantic.networks import EmailStr

from app import models, schemas
from app.api import deps
from app.core.celery_app import celery_app
from app.core.notification_bot import notification_bot
from app.schemas.core import QueryParams
from app.utils import send_test_email

import asyncio
from datetime import datetime
import orjson
from sqlalchemy.orm import Session
from time import sleep
from sse_starlette import EventSourceResponse

from app.api.api_v1.router import APIRouter

router = APIRouter()


@router.post("/test-celery/", response_model=schemas.Msg, status_code=201)
def test_celery(
    msg: schemas.Msg,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test Celery worker.
    """
    celery_app.send_task("app.worker.test_celery", args=[msg.msg])
    return {"msg": "Word received"}


@router.post("/test-email/", response_model=schemas.Msg, status_code=201)
def test_email(
    email_to: EmailStr,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test emails.
    """
    send_test_email(email_to=email_to)
    return {"msg": "Test email sent"}


@router.post("/test-notification-bot/", status_code=201)
def test_telegram(
    chat_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test telegram.
    """
    return notification_bot.test(chat_id)


def event_source_response(
    db: Session, request: Request,
    pull_fn: Callable, show_fields: List[str] = None,
    stream_delay: int = 10, exclude_events: List[str] = None,
    **kwargs
):
    def response_filter(obj):
        response = deepcopy(obj)
        if exclude_events:
            for event in exclude_events:
                response.pop(event)

        return response

    async def event_publisher():

        params = QueryParams(
            skip=0,
            limit=10000
        )
        time_cursor = datetime.utcnow()
        detector_ids = []
        prev_response = None
        response = {
            "new": [],
            "updated": [],
            "removed": []
        }
        try:
            detectors = pull_fn(
                db=db,
                **kwargs,
                params=params,
                updated_before=time_cursor
            )
            detector_ids = [d.id for d in detectors]

            response["new"] = [d.to_dict(show=show_fields) for d in detectors]

            prev_response = orjson.dumps(response_filter(response))

            yield dict(data=prev_response.decode("utf-8"))

            while True:
                response = {
                    "new": [],
                    "updated": [],
                    "removed": []
                }
                disconnected = await request.is_disconnected()
                if disconnected:
                    print(f"Disconnecting client {request.client}")
                    break
                db.expire_all()
                before_detectors_count = pull_fn(
                    db=db, **kwargs, count=True, params=params, updated_before=time_cursor
                )
                after_detectors = pull_fn(
                    db=db, **kwargs, params=params, updated_after=time_cursor
                )

                if before_detectors_count != len(detector_ids):
                    detectors = pull_fn(
                        db=db, **kwargs, params=params, updated_before=time_cursor
                    )

                    response["removed"] = detector_ids.copy()
                    for d in detectors:
                        if d.id in detector_ids:
                            response["removed"].remove(d.id)

                    for removedId in response["removed"]:
                        detector_ids.remove(removedId)

                for detector in after_detectors:
                    if detector.id in detector_ids or detector.id in response["removed"]:
                        detector_ids.append(detector.id)
                        response["removed"].remove(detector.id)
                        response["updated"].append(detector.to_dict(show=show_fields))
                    else:
                        detector_ids.append(detector.id)
                        response["new"].append(detector.to_dict(show=show_fields))

                current_response = orjson.dumps(response_filter(response))

                if prev_response != current_response:
                    prev_response = current_response
                    time_cursor = datetime.utcnow()
                    if len(response["new"]) or len(response["updated"]) or len(response["removed"]):
                        yield dict(data=current_response.decode("utf-8"))
                await asyncio.sleep(stream_delay)
            print(f"Disconnected from client {request.client}")
        except asyncio.CancelledError as e:
            print(f"Disconnected from client (via refresh/close) {request.client}")
            # Do any other cleanup, if any
            # raise e

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    return EventSourceResponse(event_publisher())
