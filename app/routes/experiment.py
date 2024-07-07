from fastapi import APIRouter, Depends, status, HTTPException

from app.auth.authenticate import authenticate_user_credentials
from app.database.connection import get_session
from app.database.querying import (
    insert_record,
    insert_records,
    get_records_by_field,
    get_records_by_fields,
    get_record,
    cross_inner_join_w_constraints,
    update_record,
)
from app.models.experiment import (
    ExperimentData,
    Experiment,
    Object,
    Action,
    RoutineStep,
)
from app.models.response import ResponseModel
from app.models.user import User
from app.routes.utils import (
    timing_and_order_to_timestamp,
    set_experiment_end_date,
    joined_records_to_experiment_data,
)


experiment_router = APIRouter(tags=["Experiments"])


@experiment_router.get("/experiment/retrieve", response_model=ResponseModel)
async def get_experiment(
    experiment_name: str,
    user_id=Depends(authenticate_user_credentials),
    session=Depends(get_session),
):
    data_models_dict = {}
    data_models_dict[Experiment] = (
        None,
        None,
        {"name": experiment_name, "user_id": user_id},
    )
    data_models_dict[RoutineStep] = (Experiment.id, RoutineStep.experiment_id, None)
    data_models_dict[Object] = (RoutineStep.object_id, Object.id, None)
    data_models_dict[Action] = (RoutineStep.action_id, Action.id, None)
    joined_records = await cross_inner_join_w_constraints(data_models_dict, session)

    if not joined_records:
        raise HTTPException(
            status_code=400,
            detail=f"No experiment with name '{experiment_name}' found.",
        )

    experiment_data = joined_records_to_experiment_data(joined_records)

    return {"message": "Experiment successfully retrieved.", "data": experiment_data}


@experiment_router.get("/experiment/retrieve-all", response_model=ResponseModel)
async def get_all_experiments_for_user(
    user_id=Depends(authenticate_user_credentials), session=Depends(get_session)
):
    data_models_dict = {}
    data_models_dict[Experiment] = (None, None, {"user_id": user_id})
    data_models_dict[RoutineStep] = (Experiment.id, RoutineStep.experiment_id, None)
    data_models_dict[Object] = (RoutineStep.object_id, Object.id, None)
    data_models_dict[Action] = (RoutineStep.action_id, Action.id, None)
    joined_records = await cross_inner_join_w_constraints(data_models_dict, session)

    if not joined_records:
        return {"message": "No experiments found for user."}

    data = {}
    experiment_ids = set([joined_record[0].id for joined_record in joined_records])
    for id in experiment_ids:
        records = [
            joined_record
            for joined_record in joined_records
            if joined_record[0].id == id
        ]
        data[id] = joined_records_to_experiment_data(records)

    return {"message": "Experiment successfully retrieved.", "data": data}


@experiment_router.post(
    "/experiment/create",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def create_experiment(
    experiment_data: ExperimentData,
    user_firebase_id: str = Depends(authenticate_user_credentials),
    session=Depends(get_session),
):

    user = await get_records_by_field(user_firebase_id, "id", User, session)
    user = user[0]

    # Check that user doesn't have experiment of the same name
    fields_dict = {"user_id": user.id, "name": experiment_data.experiment_name}
    experiments_with_same_name = await get_records_by_fields(
        fields_dict, Experiment, session
    )
    if experiments_with_same_name:
        raise HTTPException(
            status_code=400, detail="Experiment with this name already exists for user."
        )

    # Create experiment table record
    experiment_record = Experiment(
        user_id=user.id, name=experiment_data.experiment_name
    )
    await insert_record(experiment_record, session)

    # Create object and action records if don't exist
    # And create routinestep records
    routinestep_records = []
    for routinestep in experiment_data.routine_steps:
        # Object Record
        object_name = routinestep.object_name
        object_records = await get_records_by_field(
            object_name, "name", Object, session
        )
        if not object_records:
            object_record = Object(name=object_name)
            await insert_record(object_record, session)
        else:
            if len(object_records) > 1:
                raise HTTPException(
                    status_code=500,
                    detail="Multiple database entries for object with same name.",
                )
            object_record = object_records[0]

        # Action Record
        action_name = routinestep.action_name
        action_records = await get_records_by_field(
            action_name, "name", Action, session
        )
        if not action_records:
            action_record = Action(name=action_name)
            await insert_record(action_record, session)
        else:
            if len(action_records) > 1:
                raise HTTPException(
                    status_code=500,
                    detail="Multiple database entries for action with same name.",
                )
            action_record = action_records[0]

        # Routine Step Record
        timestamp = timing_and_order_to_timestamp(
            routinestep.timing, routinestep.step_order
        )
        routinestep_record = RoutineStep(
            experiment_id=experiment_record.id,
            action_id=action_record.id,
            object_id=object_record.id,
            timestamp=timestamp,
        )

        routinestep_records.append(routinestep_record)
    await insert_records(routinestep_records, session)

    return {"message": "Experiment succesfully started!"}


@experiment_router.put("/experiment/end", response_model=ResponseModel)
async def end_experiment(
    experiment_id: int,
    user_firebase_id: str = Depends(authenticate_user_credentials),
    session=Depends(get_session),
):

    user = await get_records_by_field(user_firebase_id, "id", User, session)
    user = user[0]

    experiment_record = await get_record(experiment_id, Experiment, session)

    if experiment_record.user_id != user.id:
        raise HTTPException(
            status_code=400,
            detail="User attempting to end experiment belonging to another user.",
        )

    experiment_record = set_experiment_end_date(experiment_record)

    await update_record(experiment_id, Experiment, experiment_record, session)

    return {"message": "Experiment ended successfully!"}


@experiment_router.put("/experiment/remove", response_model=ResponseModel)
async def remove_experiment(
    experiment_id: int,
    user_firebase_id: str = Depends(authenticate_user_credentials),
    session=Depends(get_session),
):
    """Set the deleted column of the experiment record with the given experiment_id to True."""

    user = await get_records_by_field(user_firebase_id, "id", User, session)
    user = user[0]

    experiment_record = await get_record(experiment_id, Experiment, session)

    if experiment_record.user_id != user.id:
        raise HTTPException(
            status_code=400,
            detail="User attempting to remove experiment belonging to another user.",
        )

    experiment_record.deleted = True

    await update_record(experiment_id, Experiment, experiment_record, session)

    return {"message": "Experiment removed successfully!"}
