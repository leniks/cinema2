#!/usr/bin/env python3
import asyncio
import asyncpg

async def check_urls():
    conn = await asyncpg.connect(user='admin', password='cinema', host='localhost', database='cinema')
    rows = await conn.fetch('SELECT id, title, poster_url FROM movies WHERE id IN (1,2,3,4,5) ORDER BY id')
    for row in rows:
        print(f'ID: {row[0]}, Title: {row[1]}, URL: {row[2]}')
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_urls()) 