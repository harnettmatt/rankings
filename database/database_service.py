"""Module containing all database setup"""
from typing import Type

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from persistable.models import Persistable


class DatabaseService:
    """
    Service that interacts with the db layer
    """

    session: Session

    def __init__(self, session: Session):
        self.session = session

    def get(self, id: int, model_type: Type[Persistable]):
        """
        Gets instance from db for a given model and id
        """
        return self.session.query(model_type).filter_by(id=id).first()

    def all(self, model_type: Type[Persistable], skip: int = 0, limit: int = 100):
        """
        Gets all instances from db for a given model and optional limiting
        """
        return self.session.query(model_type).offset(skip).limit(limit).all()

    def create(self, input_schema: BaseModel, model_type: Type[Persistable]):
        """
        Creates instance in db for a given pydantic input schema and model
        """
        model_instance = model_type(**jsonable_encoder(input_schema))
        self.session.add(model_instance)
        self.session.commit()
        self.session.refresh(model_instance)
        return model_instance

    def delete(self, id: int, model_type: Type[Persistable]):
        """
        Deletes instance from db for a given model and id
        """
        model_instance = self.get(id=id, model_type=model_type)
        self.session.delete(model_instance)
        self.session.commit()
        return model_instance

    def update(self, id: int, input_schema: BaseModel, model_type: Type[Persistable]):
        """
        Gets instance from db, merges input_schema with db instance, update db instance
        """
        update_dict = input_schema.dict(exclude_none=True)

        model_instance = self.get(id=id, model_type=model_type)
        model_instance_dict = jsonable_encoder(model_instance)
        for key, val in update_dict.items():
            if key in model_instance_dict:
                setattr(model_instance, key, val)

        self.session.add(model_instance)
        self.session.commit()
        self.session.refresh(model_instance)
        return model_instance
