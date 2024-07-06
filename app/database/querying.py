from fastapi import HTTPException, status
from sqlmodel import select
from app.models.user import User


async def insert_record(record, session) -> None:
    session.add(record)
    session.commit()
    # expire the current nun committed object attributes in memory and reload from database
    # A Session object’s default behavior is to expire all state whenever the Session.rollback()
    # or Session.commit() methods are called but useful for the specific case
    # that a non-ORM SQL statement was emitted in the current transaction.
    session.refresh(record)


async def insert_records(records, session) -> None:
    session.add_all(records)
    session.commit()
    # refreshing each record is saved here, see insert_record()


async def get_record(record_id, data_model, session):
    record = session.get(data_model, record_id)
    if record:
        return record
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record with supplied ID doesn't exist",
        )


async def get_records_by_field(field_value, field_name, data_model, session):
    statement = select(data_model).where(getattr(data_model, field_name) == field_value)
    records = session.exec(statement).all()
    return records


async def get_records_by_fields(constraints_dict, data_model, session):
    statement = select(data_model)
    for field_name in constraints_dict:
        statement = statement.where(
            getattr(data_model, field_name) == constraints_dict[field_name]
        )
    records = session.exec(statement).all()
    return records


async def select_all(data_model, session):
    records = session.exec(select(data_model)).all()
    return records


async def inner_join(data_model_w_fk, data_model, session):
    """Inner join for table which includes a foreign key column pointing to the other."""
    statement = select(data_model_w_fk, data_model).join(data_model)
    records = session.exec(statement).all()
    return records


async def cross_inner_join_w_constraints(data_models_dict, session):
    statement = select(*data_models_dict)

    for data_model in data_models_dict:
        field_1, field_2, constraints_dict = data_models_dict[data_model]

        if field_1 and field_2:
            statement = statement.join(data_model, field_1 == field_2)

        if constraints_dict:
            for field_name in constraints_dict:
                statement = statement.where(
                    getattr(data_model, field_name) == constraints_dict[field_name]
                )

    records = session.exec(statement).all()
    return records


async def update_record(record_id, data_model, updated_record, session):
    record = await get_record(record_id, data_model, session=session)
    record_data = updated_record.dict(exclude_unset=True)
    for key, value in record_data.items():
        setattr(record, key, value)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


async def delete_record(record_id, data_model, session):
    record = await get_record(record_id, data_model, session=session)
    session.delete(record)
    session.commit()
