from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Item as ItemModel

router = APIRouter(prefix="/items", tags=["items"])

class ItemIn(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)

class ItemOut(ItemIn):
    id: UUID
    model_config = ConfigDict(from_attributes=True)  

@router.get("/", response_model=List[ItemOut])
def list_items(db: Session = Depends(get_db)):
    rows = db.query(ItemModel).all()
    return rows

@router.post("/", response_model=ItemOut, status_code=201)
def create_item(item: ItemIn, db: Session = Depends(get_db)):
    row = ItemModel(name=item.name, price=item.price)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: UUID, db: Session = Depends(get_db)):
    row = db.get(ItemModel, str(item_id))
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    return row

@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: UUID, db: Session = Depends(get_db)):
    row = db.get(ItemModel, str(item_id))
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(row)
    db.commit()
