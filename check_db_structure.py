#!/usr/bin/env python3
import asyncio
import asyncpg

async def check_db_structure():
    conn = await asyncpg.connect(user='admin', password='cinema', host='localhost', database='cinema')
    
    # Проверяем структуру таблицы movies
    columns = await conn.fetch("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'movies' 
        ORDER BY ordinal_position
    """)
    
    print('📋 Movies table structure:')
    for col in columns:
        print(f'  {col[0]}: {col[1]}')
    
    # Проверяем несколько записей
    movies = await conn.fetch('SELECT id, title, poster_url, trailer_url FROM movies WHERE id IN (1,2,3) ORDER BY id')
    print('\n🎬 Sample movies:')
    for movie in movies:
        print(f'  ID: {movie[0]}, Title: {movie[1]}')
        print(f'    Poster: {movie[2]}')
        print(f'    Trailer: {movie[3]}')
        print()
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_db_structure()) 