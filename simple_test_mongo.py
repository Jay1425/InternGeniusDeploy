#!/usr/bin/env python3
"""Safe MongoDB connectivity smoke test.

This script verifies connectivity only. It does not read, print, or modify user records.
"""
import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()


def main():
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise RuntimeError("MONGO_URI must be configured before running this test")

    client = MongoClient(
        uri,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
    )
    try:
        client.admin.command("ping")
        print("MongoDB connection successful. No user data was read or modified.")
    finally:
        client.close()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("MongoDB connection test failed. Verify MONGO_URI and network settings.")
