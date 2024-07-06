from datetime import datetime, time
from typing import List, Tuple

from app.models.experiment import (
    Experiment,
    ExperimentData,
    RoutineStepData,
    Timing,
)


timing_to_hour_mapping = {
    Timing.MORNING: 8,
    Timing.NOON: 12,
    Timing.AFTERNOON: 16,
    Timing.NIGHT: 20,
}

hour_to_timing_mapping = {
    8: Timing.MORNING,
    12: Timing.NOON,
    16: Timing.AFTERNOON,
    20: Timing.NIGHT,
}


def timing_and_order_to_timestamp(timing: Timing, order: int) -> time:
    """Convert timing and step_order attributes to the timestamp stored in the db.
    The timestamp is currently only used for clustering and ordering the routine steps
    i.e. 8am -> morning, 12pm -> noon, 4pm -> afternoon, 8pm -> night and nth second -> nth step
    """
    time_str = f"{timing_to_hour_mapping[timing]}:0:{order}"
    timestamp = datetime.strptime(time_str, "%H:%M:%S").time()
    return timestamp


def timestamp_to_timing_and_order(timestamp: time) -> Tuple[Timing, int]:
    timing = hour_to_timing_mapping[timestamp.hour]
    order = timestamp.second
    return timing, order


def set_experiment_end_date(experiment_record: Experiment) -> Experiment:
    experiment_record.date_ended = datetime.today().strftime("%Y-%m-%d")
    return experiment_record


def joined_records_to_experiment_data(joined_records: List) -> ExperimentData:
    experiment_record = joined_records[0][0]

    experiment_data = {}
    experiment_data["experiment_name"] = experiment_record.name
    experiment_data["routine_steps"] = []

    for joined_record in joined_records:
        routinestep_record = joined_record[1]
        object_record = joined_record[2]
        action_record = joined_record[3]

        routinestep_data = {}
        routinestep_data["object_name"] = object_record.name
        routinestep_data["action_name"] = action_record.name
        (
            routinestep_data["timing"],
            routinestep_data["step_order"],
        ) = timestamp_to_timing_and_order(routinestep_record.timestamp)

        experiment_data["routine_steps"].append(RoutineStepData(**routinestep_data))

    return ExperimentData(**experiment_data)
