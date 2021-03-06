#!/usr/bin/python
#coding=utf-8

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .query import Query

class CanteenQuery(Query):
    __tablename__ = 'canteen'

    id = Column(Integer, primary_key = True)
    name = Column(String)
    fullname = Column(String)
    address = Column(String)
    city = Column(String)
    detail = Column(String)
    opentimes = Column(String)
    contact = Column(String)
    logourl = Column(String)
    meals = relationship("MealQuery", back_populates="canteen")
    mealdate = relationship("MealDateQuery", back_populates="canteen")

    def __init__(self, canteen_id):
        self.id = canteen_id

    def doQuery(self):
        return self.query(CanteenQuery).filter_by(id=self.id).all()

    def __str__(self):
        return "Canteen<{0}, \"{1}\">".format(self.id, self.name)
