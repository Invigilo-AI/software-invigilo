from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


class CRUDCompany(CRUDBase[Company, CompanyCreate, CompanyUpdate]):
    def get_by_owner(self, db: Session, *, owner_id: int) -> Company:
        return (
            db.query(self.model)
            .filter(Company.owner_id == owner_id)
            .first()
        )


company = CRUDCompany(Company)
