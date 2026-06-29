import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

dbPath = os.getenv("SQL_PATH")

if not dbPath:
    raise ValueError("SQL_PATH not found in .env")


def getConnection():
    return sqlite3.connect(dbPath)


def createTable():
    with getConnection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repositories (
                repoLink TEXT PRIMARY KEY,
                repoHash TEXT NOT NULL
            )
        """)
        conn.commit()


def insertRepo(repoLink, repoHash):
    with getConnection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO repositories (repoLink, repoHash) VALUES (?, ?)",
            (repoLink, repoHash)
        )
        conn.commit()


def repoExists(repoLink):
    with getConnection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM repositories WHERE repoLink = ?",
            (repoLink,)
        )
        return cursor.fetchone() is not None


def hashMatches(repoLink, repoHash):
    with getConnection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM repositories WHERE repoLink = ? AND repoHash = ?",
            (repoLink, repoHash)
        )
        return cursor.fetchone() is not None


def updateHash(repoLink, newHash):
    with getConnection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE repositories SET repoHash = ? WHERE repoLink = ?",
            (newHash, repoLink)
        )
        conn.commit()
        return cursor.rowcount > 0


def deleteRepo(repoLink):
    with getConnection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM repositories WHERE repoLink = ?",
            (repoLink,)
        )
        conn.commit()
        return cursor.rowcount > 0


if __name__ == "__main__":
    createTable()