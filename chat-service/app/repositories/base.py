from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model

    async def get(self, id: int) -> Optional[ModelType]:
        return await self.session.get(self.model, id)

    async def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, update_data: dict) -> ModelType:
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def list(self, limit: int = 100, offset: int = 0) -> List[ModelType]:
        stmt = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
