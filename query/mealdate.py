#!/usr/bin/python
#coding=utf-8

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from .catering import CateringQuery
from .query import Query

Base = declarative_base()
class MealDateQuery(Query):
    __tablename__ = 'date'

    date_id = Column(Integer)
    text = Column(String)
    catering_id = Column(Integer, ForeignKey("catering.id"))
    catering = relationship(CateringQuery, back_populates="mealdate")
    meals = relationship("MealQuery", back_populates="mealdate")

    __table_args__ = (
        PrimaryKeyConstraint('catering_id', 'date_id'),
    )

    def __init__(self, catering_id):
        self.catering_id = catering_id

    def doQuery(self):
        return self.query(MealDateQuery).filter_by(catering_id=self.catering_id).all()

    def __str__(self):
        return "MealDate<{0}, {1}, {2}>".format(self.date_id, self.catering.name, self.text)
