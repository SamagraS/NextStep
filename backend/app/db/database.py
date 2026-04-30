from pathlib import Path

import aiosqlite

from app.db.schema import INDEX_STATEMENTS, TABLE_STATEMENTS


class Database:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self._connection: aiosqlite.Connection | None = None

    async def connect(self) -> aiosqlite.Connection:
        if self._connection is None:
            database_path = Path(self.database_url)
            database_path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = await aiosqlite.connect(database_path)
            self._connection.row_factory = aiosqlite.Row
            await self._connection.execute("PRAGMA foreign_keys = ON;")
        return self._connection

    async def initialize(self) -> None:
        connection = await self.connect()
        for statement in TABLE_STATEMENTS:
            await connection.execute(statement)
        for statement in INDEX_STATEMENTS:
            await connection.execute(statement)
        await connection.commit()

    async def ping(self) -> bool:
        try:
            connection = await self.connect()
            async with connection.execute("SELECT 1;") as cursor:
                row = await cursor.fetchone()
            return bool(row)
        except Exception:
            return False

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None
