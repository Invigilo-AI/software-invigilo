from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.ai_type import AI_Type
from app.schemas.ai_type import AI_TypeCreate, AI_TypeUpdate


class CRUD_AI_Type(CRUDBase[AI_Type, AI_TypeCreate, AI_TypeUpdate]):
    def get_by_index(self, db: Session, index: int) -> AI_Type:
        return db.query(self.model).filter_by(index = index).first()

    def is_used_index(self, db: Session, index: int):
        # TODO check other models what use `type`, if isn't used, return False
        ai_type = self.get_by_index(db, index)
        if ai_type:
            return True
        else:
            return False


ai_type = CRUD_AI_Type(AI_Type)
