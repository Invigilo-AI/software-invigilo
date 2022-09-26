from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

from datetime import timedelta, datetime

from app.schemas.cam_server import CamServerInfo
from app.schemas.incident import IncidentFilters

class ReportType(str, Enum):
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    CUSTOM = 'custom'

class ReportFilters(BaseModel):
    start: datetime = datetime.utcnow()
    end: datetime = None
    interval: Optional[timedelta] = timedelta(days=1)
    period: Optional[ReportType] = ReportType.MONTH
    class Config:  
        use_enum_values = True


class ReportInterventionFilters(ReportFilters, IncidentFilters):
    pass
    # class Config:
    #     fields = {'id': {'exclude': True}}


class Report(BaseModel):
    pass


class CamServerActivity(BaseModel):
    x: datetime
    y: Optional[float]


class ReportCamServerActivityTimeline(Report):
    cam_server: CamServerInfo
    interval: timedelta
    timeline: List[CamServerActivity]


class ReportServerMeter(Report):
    cam_server: CamServerInfo
    value: float


class TypeCount(BaseModel):
    index: int
    count: int

class ReportServerTypeCount(Report):
    cam_server: CamServerInfo
    values: List[TypeCount]


class ReportGaugeTendency(ReportServerMeter):
    interval: timedelta
    created: datetime
