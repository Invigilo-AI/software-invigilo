from typing import Any, Union

from fastapi import Depends, Request
import orjson
from datetime import datetime, timedelta
from copy import deepcopy
from sqlalchemy.orm import Session
from telegram import ParseMode
from telegram.error import BadRequest

from app.schemas.telegram import Update, MessageEntityType, ChatType
from app.core.config import settings
from app.api import deps
from app.crud import cam_server, incident
from app.core.notification_bot import notification_bot, IncidentCallbackData

from app.api.api_v1.router import APIRouter

router = APIRouter()


@router.post("/telegram/{secret}", dependencies=[Depends(deps.telegram_webhook_token)])
async def telegram_webhook(
    update: Update,
    db: Session = Depends(deps.get_db),
    request: Request = None
) -> Any:
    """
    Retrieve Telegram Update, process commands.
    """
    if update.callback_query:
        query = update.callback_query
        data = query.data
        message = query.message
        by_user = query.from_user.username
        chat_id = message.chat.id if hasattr(message, 'chat') else message.from_user.id
        message_id = query.message.message_id if hasattr(query, 'message') else None
        if data:
            data = IncidentCallbackData(**orjson.loads(data))
            db_incident = incident.get(db, data.incident_id)

            if not db_incident:
                return False

            if db_incident.created_at + timedelta(seconds=settings.NOTIFICATION_TIME_WINDOW) < datetime.utcnow():
                return notification_bot.answer_callback_query(query.id, text="The notification expired")
            else:
                if data.acknowledge:
                    incident.mark_acknowledged(db, data.incident_id, by_user)
                if data.inaccurate:
                    incident.mark_inaccurate(db, data.incident_id, by_user)

                return notification_bot.notification_update_incident(chat_id, message_id, query)

        return False

    if update.message:
        message = update.message
        chat_id = message.chat.id if hasattr(message, 'chat') else message.from_user.id
        text = message.text if hasattr(message, 'text') else None

        replay = {"chat_id": chat_id}

        if text:
            replay['text'] = text

        if message.entities:
            for command in message.entities:
                cmd = text[command.offset:command.length]
                cmd_attr = text[command.length + 1:]
                print(command.type, cmd, cmd_attr)
                if command.type == MessageEntityType.BOT_COMMAND:
                    if '/start' in cmd:
                        if cmd_attr:
                            server = cam_server.get_by_access_token(
                                db, access_token=cmd_attr)

                            meta = deepcopy(server.meta)
                            if not meta:
                                meta = {'telegram': []}
                            chat_instance = {'chat_id': chat_id}
                            if message.chat.type == ChatType.private:
                                chat_instance['title'] = message.chat.username
                            else:
                                chat_instance['title'] = message.chat.title
                            if not next(iter([inst for inst in meta['telegram'] if inst['chat_id'] == chat_id]), None):
                                meta['telegram'].append(chat_instance)
                                server_upd = cam_server.update(
                                    db, db_obj=server, obj_in={'meta': meta}
                                )

                                message = 'Bot will inform about incidents on server *{name}*'.format(
                                    name=notification_bot.escape(server.name))
                            else:
                                message = 'Bot is already connected to server *{name}*'.format(
                                    name=notification_bot.escape(server.name))
                        else:
                            message = 'Bot need to be started with the `access_token` of the server'

                        notification_bot.notification_message(
                            chat_id,
                            message,
                            parse_mode=ParseMode.MARKDOWN_V2
                        )
    return True
