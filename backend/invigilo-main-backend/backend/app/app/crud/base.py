from inspect import signature
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
# from fastapi_pagination import Page, paginate

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Integer
from sqlalchemy_utils import cast_if

from app.db.base_class import Base
from app.schemas.core import QueryParams

from sqlalchemy.sql import visitors, operators
from sqlalchemy import func, types
from contextlib import suppress

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    # inspired by https://github.com/juliotrigo/sqlalchemy-filters
    OPERATORS = {
        'is_null': lambda f: f.is_(None),
        'is_not_null': lambda f: f.isnot(None),
        '==': lambda f, a: f == a,
        'eq': lambda f, a: f == a,
        '!=': lambda f, a: f != a,
        'ne': lambda f, a: f != a,
        '>': lambda f, a: f > a,
        'gt': lambda f, a: f > a,
        '<': lambda f, a: f < a,
        'lt': lambda f, a: f < a,
        '>=': lambda f, a: f >= a,
        'ge': lambda f, a: f >= a,
        '<=': lambda f, a: f <= a,
        'le': lambda f, a: f <= a,
        'like': lambda f, a: f.like(a),
        'ilike': lambda f, a: f.ilike(a),
        'not_ilike': lambda f, a: ~f.ilike(a),
        'in': lambda f, a: f.in_(a),
        'not_in': lambda f, a: ~f.in_(a),
        'any': lambda f, a: f.any(a),
        'not_any': lambda f, a: func.not_(f.any(a)),
        'string_array_contains': lambda f, a: func.string_to_array(f, ',').operate(operators.custom_op("@>", precedence=5), a, result_type=types.Boolean),
    }

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(
        self, db: Session,
        id: Any,
        filters: dict = None,
        special_fields: Dict[str, Any] = None
    ) -> Optional[ModelType]:
        query = (db
                 .query(self.model)
                 .filter_by(id=id)
                 )
        query = self.query_filters(query, filters, special_fields=special_fields)

        return query.first()

    def get_multi(
        self, db: Session,
        *,
        params: QueryParams = None,
        filters: dict = None,
        special_fields: Dict[str, Any] = None
    ) -> List[ModelType]:
        query = db.query(self.model)

        query = self.query_filters(query, filters, special_fields=special_fields)
        query = self.query_order_by(query, params, special_fields=special_fields)
        query = self.query_limit(query, params)

        return query.all()

    def get_multi_count(
        self, db: Session,
        *,
        filters: dict = None,
        special_fields: Dict[str, Any] = None,
        as_query: bool = False
    ) -> List[ModelType]:
        query = db.query(self.model)
        query = self.query_filters(query, filters, special_fields)

        if as_query:
            return query
        return query.count()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in, exclude_defaults=True)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        if db_obj.deleted:
            return None
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        obj.deleted = True
        # db.delete(obj)
        db.commit()
        return obj

    def query_filters(self, query, filters, special_fields: Dict[str, Any] = None, with_deleted: bool = False):
        if not with_deleted:
            query = query.filter(self.model.deleted==False)
        if filters:
            if type(filters) != dict:
                filters = filters.dict()
            for (key, values) in filters.items():
                if special_fields and key in special_fields:
                    field = special_fields[key]
                else:
                    model = self.model
                    if not getattr(model, key, None) and '__' in key:
                        model_field, model_field_key = key.split('__')
                        field = getattr(model, model_field)
                        if field and field.property.mapper.class_:
                            model = field.property.mapper.class_
                            key = model_field_key
                    field = getattr(model, key, None)
                if not isinstance(values, list):
                    values = [values]
                for value in values:
                    if field and isinstance(value, tuple):
                        if len(value) == 2:
                            operator, value = value
                        else:
                            operator = value[0]
                        if operator not in self.OPERATORS:
                            raise Exception('Operator `{}` not valid.'.format(operator))
                        else:
                            operator_function = self.OPERATORS[operator]
                        if len(signature(operator_function).parameters) == 2:
                            query = query.filter(operator_function(field, value))
                        else:
                            query = query.filter(operator_function(field))
                    elif field and value is not None:
                        if model:
                            query = self.unique_join(query, model)
                        if isinstance(field.type, UUID):
                            query = query.filter(
                                cast_if(field, String).ilike(f'%{value}%'))
                        elif isinstance(field.type, String):
                            query = query.filter(field.ilike(f'%{value}%'))
                        elif isinstance(field.type, Integer):
                            query = query.filter(field == value)
                        else:
                            query = query.filter(field == value)
        return query

    def query_order_by(
        self, query,
        params: Union[QueryParams, Dict[str, Any]] = None,
        order_by: str = None,
        special_fields: Dict[str, Any] = None
    ):
        if not order_by and params and hasattr(params, 'order_by'):
            order_by = params.order_by
        if order_by:
            for order in order_by.split(','):
                desc = order.startswith('-')
                key = order[(1 if desc else 0):]
                if special_fields and key in special_fields:
                    field = special_fields[key]
                else:
                    model = self.model
                    if not getattr(model, key, None) and '__' in key:
                        model_field, model_field_key = key.split('__')
                        field = getattr(model, model_field)
                        if field and field.property.mapper.class_:
                            model = field.property.mapper.class_
                            key = model_field_key
                    field = getattr(model, key, None)
                if field:
                    if model:
                        query = self.unique_join(query, model)
                    if desc:
                        query = query.order_by(field.desc())
                    else:
                        query = query.order_by(field.asc())
        return query

    def query_limit(self, query, params: QueryParams = None):
        if params:
            query = query.offset(params.skip).limit(params.limit)
        return query

    def _has_entity(self, query, model) -> bool:
        for visitor in visitors.iterate(query.statement):
            # Checking for `.join(Parent.child)` clauses
            if visitor.__visit_name__ == 'binary':
                for vis in visitors.iterate(visitor):
                    # Visitor might not have table attribute
                    with suppress(AttributeError):
                        # Verify if already present based on table name
                        if model.__table__.fullname == vis.table.fullname:
                            return True
            # Checking for `.join(Child)` clauses
            if visitor.__visit_name__ == 'table':
                # Visitor might be of ColumnCollection or so,
                # which cannot be compared to model
                with suppress(TypeError):
                    if model == visitor.entity_namespace:
                        return True
            # Checking for `Model.column` clauses
            if visitor.__visit_name__ == "column":
                with suppress(AttributeError):
                    if model.__table__.fullname == visitor.table.fullname:
                        return True
        return False

    def unique_join(self, query, model, *args, **kwargs):
        """Join if given model not yet in query"""
        if not self._has_entity(query, model):
            return query.join(model, *args, **kwargs)
        return query
