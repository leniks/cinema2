#!/usr/bin/env python3
"""
Скрипт для настройки публичного доступа к bucket MinIO
"""

import asyncio
import json
from aiobotocore.session import get_session

# Настройки S3 (MinIO)
S3_CONFIG = {
    "endpoint_url": "http://localhost:9000",
    "region_name": "us-east-1",
    "aws_access_key_id": "minioadmin",
    "aws_secret_access_key": "minioadmin123"
}

bucket_name = "cinema-files"

# Публичная политика для чтения
public_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
        }
    ]
}

async def setup_public_access():
    """Настраивает публичный доступ к bucket"""
    session = get_session()
    async with session.create_client("s3", **S3_CONFIG) as s3:
        try:
            # Проверяем, существует ли bucket
            try:
                await s3.head_bucket(Bucket=bucket_name)
                print(f"✅ Bucket '{bucket_name}' exists")
            except Exception as e:
                print(f"❌ Bucket '{bucket_name}' does not exist: {e}")
                # Создаем bucket
                await s3.create_bucket(Bucket=bucket_name)
                print(f"✅ Created bucket '{bucket_name}'")
            
            # Устанавливаем публичную политику
            policy_json = json.dumps(public_policy)
            await s3.put_bucket_policy(
                Bucket=bucket_name,
                Policy=policy_json
            )
            print(f"✅ Set public read policy for bucket '{bucket_name}'")
            
            # Проверяем политику
            try:
                response = await s3.get_bucket_policy(Bucket=bucket_name)
                print(f"✅ Current policy: {response['Policy']}")
            except Exception as e:
                print(f"⚠️ Could not retrieve policy: {e}")
                
        except Exception as e:
            print(f"❌ Error setting up public access: {e}")

if __name__ == "__main__":
    asyncio.run(setup_public_access()) 