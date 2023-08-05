from sqlalchemy import Column
from sqlalchemy.types import Boolean, DateTime, Float, String
from sqlalchemy.ext.declarative import declarative_base


class ODKBase(object):
    _URI = Column(String, primary_key=True)
    _CREATOR_URI_USER = Column(String)
    _IS_COMPLETE = Column(Boolean)


class MetaData(object):
    START = Column(DateTime)
    END = Column(DateTime)
    DEVICEID = Column(String)
    PHONENUMBER = Column(String)


class GPSMetaData(MetaData):
    GPS_LAT = Column(Float)
    GPS_LNG = Column(Float)
    GPS_ALT = Column(Float)
    GPS_ACC = Column(Float)


Base = declarative_base(cls=ODKBase)
