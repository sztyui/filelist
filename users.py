import os
import sys
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy_utils import PasswordType
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Users(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(128), nullable=False)
	password = Column(PasswordType(schemes=['pbkdf2_sha256', 'md5_crypt'], deprecated=['md5_crypt']))
	created_at = Column(DateTime, default=func.now())
	last_login = Column(DateTime)

	def __repr__(self):
		return "#ID: {id}, #Name: {name}, #Password: {password}, #Created_at: {created_at}, #Last_login: {last_login}".format(**self.__dict__)

__engine_place = 'sqlite:///{0}'.format(os.path.join(os.path.dirname(os.path.realpath(__file__)), "databases", "server_users.sqlite"))
print(__engine_place)
engine = create_engine(__engine_place)
Session = sessionmaker(autoflush=True)
Session.configure(bind=engine)
Base.metadata.create_all(engine)

# For adding user:
# user = Users(name="valami", password="valami", last_login=datetime.datetime.now())
# sess = Session()
# sess.add(user)
# sess.commit()
