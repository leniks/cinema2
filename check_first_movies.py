#!/usr/bin/env python3
import asyncio
import asyncpg

async def check_first_movies():
    conn = await asyncpg.connect(user='admin', password='cinema', host='localhost', database='cinema')
    movies = await conn.fetch('SELECT id, title, trailer_url FROM movies ORDER BY id LIMIT 5')
    print('🎬 First 5 movies:')
    for movie in movies:
        print(f'ID: {movie[0]}, Title: {movie[1]}, Trailer: {movie[2]}')
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_first_movies()) 