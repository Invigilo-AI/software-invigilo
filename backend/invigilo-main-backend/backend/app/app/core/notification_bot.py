from copy import deepcopy
import json
from typing import Any, Optional
import orjson
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.core.config import settings
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, CallbackQuery
from telegram.error import Unauthorized, BadRequest

from app.models.cam_server import Cam_Server
from app.crud.crud_cam_server import cam_server
from app.schemas.incident import Incident


class IncidentCallbackData(BaseModel):
    incident_id: int
    acknowledge: Optional[bool] = None
    inaccurate: Optional[bool] = None


class NotificationBot:
    '''
    Interface for Chat Notification bot
    '''

    def test(self, chat_id: int):
        pass

    def escape(self, text: str):
        pass

    def notification_incident(self, chat_id: int, incident: Incident):
        pass

    def notification_update_incident(self, chat_id: int, message_id: int, query: CallbackQuery) -> bool:
        pass

    def notification_message(self, chat_id: int, message: str = None):
        pass

    def server_notification_chats(self, server: Cam_Server):
        pass

    def server_notification_incident(self, server: Cam_Server, incident: Incident):
        pass

    def server_notification_chat_id_remove(self, server: Cam_Server, chat_id: int):
        pass


class TelegramBot(Bot, NotificationBot):
    def __init__(
        self, token: str,
        base_url: str = None, base_file_url: str = None,
        request: 'Request' = None,
        private_key: bytes = None, private_key_password: bytes = None,
        defaults: 'Defaults' = None
    ):
        super().__init__(token, base_url, base_file_url, request,
                         private_key, private_key_password, defaults)

    def escape(self, text: str):
        chars = ('_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!')
        for char in chars:
            text = text.replace(char, f'\\{char}')
        return text

    def test(self, chat_id):
        return self.send_message(chat_id, 'This is test telegram message')

    def notification_message(self, chat_id, message, **kwargs):
        return self.send_message(chat_id, message, **kwargs)

    def notification_incident(self, chat_id: int, incident: Incident, **kwargs):
        incident_schema = Incident(**jsonable_encoder(incident))
        incident_id = incident.id
        keyboard = [
            [
                InlineKeyboardButton("✅ Acknowledge", callback_data=json.dumps(
                    {'incident_id': incident_id, 'acknowledge': True})),
                InlineKeyboardButton("❌ Inaccurate", callback_data=json.dumps(
                    {'incident_id': incident_id, 'inaccurate': True}))
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        frame = incident_schema.frame_url
        caption = 'Incident *{ai_mapping_name}* detected by _{camera_name}_\nLocation: *{location}* at *{server_location}*'.format(
            ai_mapping_name=self.escape(incident.ai_mapping.name),
            camera_name=self.escape(incident.camera.name),
            location=self.escape(incident.location),
            server_location=self.escape(incident.camera.cam_server.location)
        )

        try:
            return self.send_photo(
                chat_id,
                frame,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=reply_markup,
                **kwargs
            )
        except:
            return None

    def server_notification_chats(self, server: Cam_Server):
        if server.meta and 'telegram' in server.meta:
            return [chat['chat_id'] for chat in server.meta['telegram'] if not chat.get('disabled', False)]
        return []

    def server_notification_chat_id_remove(self, server: Cam_Server, chat_id: int, db: Session = None):
        if server.meta and 'telegram' in server.meta:
            meta = deepcopy(server.meta)
            meta['telegram'] = [chat for chat in server.meta['telegram']
                                if chat['chat_id'] != chat_id]
            return cam_server.update(db, db_obj=server, obj_in={'meta': meta})
        return None

    def server_notification_incident(self, server: Cam_Server, incident: Any, db: Session = None):
        chat_ids = self.server_notification_chats(server)

        if chat_ids:
            for chat_id in chat_ids:
                try:
                    response = self.notification_incident(chat_id, incident)
                except Unauthorized as e:
                    print('Bot kicked', e)
                    server_upd = self.server_notification_chat_id_remove(
                        server, chat_id, db=db
                    )

            return True

        return False

    def notification_update_incident(self, chat_id: int, message_id: int, query: CallbackQuery) -> bool:
        data = query.data
        by_user = query.from_user.username
        if data:
            data = IncidentCallbackData(**orjson.loads(data))
        else:
            return False

        if data.acknowledge:
            mark_as = f'✅ Acknowledged'

        if data.inaccurate:
            mark_as = f'❌ Marked as inaccurate'
        mark_as = "{mark_as} by {by_user}".format(mark_as=mark_as, by_user=by_user)

        keyboard = [
            [
                InlineKeyboardButton(
                    mark_as,
                    callback_data=json.dumps({'incident_id': data.incident_id})
                )
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            self.answer_callback_query(query.id, text=mark_as)
        except BadRequest as e:
            print('Cant answer', e)

        response = self.edit_message_reply_markup(
            chat_id=chat_id, message_id=message_id, reply_markup=reply_markup
        )
        return response


notification_bot: NotificationBot = TelegramBot(settings.TELEGRAM_ACCESS_TOKEN)
