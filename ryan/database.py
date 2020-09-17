from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import aiosqlite

log = logging.getLogger(__name__)


class Database:
    """
    Provides a simple API for the internal `_connection` to an SQLIte database.

    Ideally the database is only interfaced with through an instance of this class.
    """

    DB_FILE = Path("ryan.database")

    T_NICKNAMES = "nicknames"

    C_AUTHOR = "author"
    C_TARGET = "target"
    C_NAME = "name"

    _connection: aiosqlite.Connection

    @property
    def size(self) -> int:
        """Return size of the database file in bytes."""
        return self.DB_FILE.stat().st_size

    async def open(self) -> Database:
        """
        Open a connection to the database from an asynchronous context.

        Creates necessary tables if they don't exist.

        Returns `self` to allow method chaining.
        """
        self._connection = await aiosqlite.connect(self.DB_FILE, isolation_level=None)
        log.info("Database connection open")

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
        """
        Retrieve a list of all nicknames.

        Gives an empty list should no nicknames be available.
        """
        log.debug("Database received call to `get_nicknames`")
        cursor = await self._connection.execute(
            f"""SELECT "{self.C_AUTHOR}", "{self.C_TARGET}", "{self.C_NAME}" FROM "{self.T_NICKNAMES}";"""
        )

        return [value for author, target, value in await cursor.fetchall()]

    async def add_nickname(self, author: int, target: int, name: str) -> None:
        """Add a new nickname for `target` from `author` with a value of `name`."""
        log.debug(f"Database received call to `add_nickname` (author={author}, target={target}, name={name})")
        await self._connection.execute(
            f"""INSERT INTO "{self.T_NICKNAMES}" VALUES (?, ?, ?);""",
            (author, target, name),
        )

    async def remove_nickname(self, name: str) -> None:
        """Remove rows with a name of `name`."""
        log.debug(f"Database received call to `remove_nickname` (name={name})")
        await self._connection.execute(
            f"""DELETE FROM "{self.T_NICKNAMES}" WHERE "{self.C_NAME}" = ?;""",
            (name,)
        )

    async def truncate_nicknames(self) -> None:
        """Truncate the entire nicknames table."""
        log.debug("Database received call to `truncate_nicknames`")
        await self._connection.execute(
            f"""DELETE FROM "{self.T_NICKNAMES}";"""
        )

    async def close(self) -> None:
        """Safely close the database connection from an asynchronous context."""
        await self._connection.close()
        log.info("Database connection safely closed")
