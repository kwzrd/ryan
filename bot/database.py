from __future__ import annotations

import logging
from typing import List

import aiosqlite

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Database:
    """Provides a simple API for the internal `_connection` to an SQLIte database.

    Ideally the database is only interfaced with through an instance of this class.
    """

    DB_NAME = "ryan.database"

    T_NICKNAMES = "nicknames"

    C_AUTHOR = "author"
    C_TARGET = "target"
    C_NAME = "name"

    _connection: aiosqlite.Connection

    async def open(self) -> Database:
        """Open a connection to the database from an asynchronous context.

        Creates necessary tables if they don't exist.

        Returns `self` to allow method chaining.
        """
        self._connection = await aiosqlite.connect(self.DB_NAME, isolation_level=None)

        await self._connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS "{self.T_NICKNAMES}" (
                "{self.C_AUTHOR}"  INTEGER NOT NULL,
                "{self.C_TARGET}"  INTEGER NOT NULL,
                "{self.C_NAME}"    TEXT NOT NULL UNIQUE
            );
            """
        )

        return self

    async def get_nicknames(self) -> List[str]:
        """Retrieve a list of all nicknames."""
        cursor = await self._connection.execute(
            f"""SELECT "{self.C_NAME}" FROM "{self.T_NICKNAMES}";"""
        )

        return [value for author, target, value in await cursor.fetchall()]

    async def add_nickname(self, author: int, target: int, name: str) -> None:
        """Add a new nickname for `target` from `author` with a value of `name`."""
        await self._connection.execute(
            f"""INSERT INTO "{self.T_NICKNAMES}" VALUES (?, ?, ?);""",
            (author, target, name),
        )

    async def remove_nickname(self, name: str) -> None:
        """Remove rows with a name of `name`."""
        await self._connection.execute(
            f"""DELETE FROM "{self.T_NICKNAMES}" WHERE "{self.C_NAME}" = ?;""",
            (name,)
        )

    async def truncate_nicknames(self) -> None:
        """Truncate the entire nicknames table."""
        await self._connection.execute(
            f"""DELETE FROM "{self.T_NICKNAMES}";"""
        )

    async def close(self) -> None:
        """Safely close the database connection from an asynchronous context."""
        await self._connection.close()
