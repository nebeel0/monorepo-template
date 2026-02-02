"""Example CRUD endpoint — auto-discovered by the dynamic router loader."""

import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.models.item import ItemCreate, ItemRead, ItemUpdate
from core.database import AppDbSessionDep
from core.schemas.item import Item

router = APIRouter()


@router.get("/", response_model=list[ItemRead])
async def list_items(session: AppDbSessionDep, limit: int = 20, offset: int = 0) -> list[ItemRead]:
    result = await session.execute(select(Item).limit(limit).offset(offset))
    return [ItemRead.model_validate(row) for row in result.scalars().all()]


@router.post("/", response_model=ItemRead, status_code=201)
async def create_item(session: AppDbSessionDep, payload: ItemCreate) -> ItemRead:
    item = Item(title=payload.title, description=payload.description)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return ItemRead.model_validate(item)


@router.get("/{item_id}", response_model=ItemRead)
async def get_item(session: AppDbSessionDep, item_id: uuid.UUID) -> ItemRead:
    item = await session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemRead.model_validate(item)


@router.patch("/{item_id}", response_model=ItemRead)
async def update_item(
    session: AppDbSessionDep, item_id: uuid.UUID, payload: ItemUpdate
) -> ItemRead:
    item = await session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await session.commit()
    await session.refresh(item)
    return ItemRead.model_validate(item)


@router.delete("/{item_id}", status_code=204)
async def delete_item(session: AppDbSessionDep, item_id: uuid.UUID) -> None:
    item = await session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await session.delete(item)
    await session.commit()
