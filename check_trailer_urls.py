#!/usr/bin/env python3
import asyncio
import asyncpg

async def check_trailer_urls():
    conn = await asyncpg.connect(user='admin', password='cinema', host='localhost', database='cinema')
    movies = await conn.fetch('SELECT id, title, poster_url, trailer_url FROM movies WHERE id IN (1,2,3) ORDER BY id')
    print('🎬 Movies with trailer URLs:')
    for movie in movies:
        print(f'ID: {movie[0]}, Title: {movie[1]}')
        print(f'  Poster: {movie[2]}')
        print(f'  Trailer: {movie[3]}')
        print()
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_trailer_urls()) 