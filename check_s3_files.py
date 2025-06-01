#!/usr/bin/env python3
import asyncio
from aiobotocore.session import get_session

# Настройки S3 (MinIO)
S3_CONFIG = {
    "endpoint_url": "http://localhost:9000",
    "region_name": "us-east-1",
    "aws_access_key_id": "minioadmin",
    "aws_secret_access_key": "minioadmin123"
}

bucket_name = "cinema-files"

async def list_s3_files():
    session = get_session()
    async with session.create_client("s3", **S3_CONFIG) as s3:
        try:
            response = await s3.list_objects_v2(Bucket=bucket_name)
            
            if 'Contents' in response:
                print(f"📁 Files in {bucket_name}:")
                print("=" * 50)
                
                backdrop_files = []
                poster_files = []
                other_files = []
                
                for obj in response['Contents']:
                    key = obj['Key']
                    size = obj['Size']
                    
                    if 'backdrop' in key:
                        backdrop_files.append((key, size))
                    elif 'poster' in key:
                        poster_files.append((key, size))
                    else:
                        other_files.append((key, size))
                
                print(f"\n🖼️  BACKDROP files ({len(backdrop_files)}):")
                for key, size in backdrop_files[:10]:  # Показываем первые 10
                    print(f"  {key} ({size} bytes)")
                
                print(f"\n🎬 POSTER files ({len(poster_files)}):")
                for key, size in poster_files[:10]:  # Показываем первые 10
                    print(f"  {key} ({size} bytes)")
                
                if other_files:
                    print(f"\n📄 OTHER files ({len(other_files)}):")
                    for key, size in other_files[:5]:
                        print(f"  {key} ({size} bytes)")
                
                print(f"\n📊 Total: {len(backdrop_files)} backdrops, {len(poster_files)} posters, {len(other_files)} others")
            else:
                print("❌ No files found in bucket")
                
        except Exception as e:
            print(f"❌ Error listing files: {e}")

if __name__ == "__main__":
    asyncio.run(list_s3_files()) 