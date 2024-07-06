from datetime import date, time, datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field
from enum import Enum


class Experiment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    name: str
    date_started: date = datetime.today().strftime("%Y-%m-%d")
    date_ended: Optional[date] = None
    deleted: bool = False


class RoutineStep(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    experiment_id: Optional[int] = Field(default=None, foreign_key="experiment.id")
    action_id: Optional[int] = Field(default=None, foreign_key="action.id")
    object_id: Optional[int] = Field(default=None, foreign_key="object.id")

    # the timestamp is currently only used for clustering and ordering the routine steps
    # i.e. 8am -> morning, 12pm -> noon, 4pm -> afternoon, 8pm -> night
    # nth second -> nth step
    timestamp: time


class Object(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class Action(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class Timing(str, Enum):
    MORNING = "morning"
    NOON = "noon"
    AFTERNOON = "afternoon"
    NIGHT = "night"


class RoutineStepData(SQLModel):
    timing: Timing
    step_order: int
    object_name: str
    action_name: str


class ExperimentData(SQLModel):
    experiment_name: str
    routine_steps: List[RoutineStepData]

    class Config:
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "experiment_name": "basic",
                "routine_steps": [
                    {
                        "timing": "morning",
                        "step_order": 1,
                        "action_name": "wash",
                        "object_name": "water",
                    }
                ],
            }
        }

    def to_routine_steps(self):
        pass
