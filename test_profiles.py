#!/usr/bin/env python3
"""Read-only, privacy-preserving MongoDB profile diagnostics.

Only aggregate counts are printed. No names, emails, phone numbers, identity
numbers, profile documents, or other personal data are displayed or modified.
"""
import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()


def get_client():
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise RuntimeError("MONGO_URI must be configured before running this test")
    return MongoClient(
        uri,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
    )


def test_user_profiles():
    client = get_client()
    try:
        client.admin.command("ping")
        users = client.interngenius.users
        total = users.count_documents({})
        completed = users.count_documents({"profile_completed": True})
        print(f"MongoDB reachable. User records: {total}; completed profiles: {completed}.")
        print("No personal profile fields were read, printed, or modified.")
    finally:
        client.close()


def test_specific_user(email):
    """Return only whether a matching record exists; never print its contents."""
    client = get_client()
    try:
        client.admin.command("ping")
        return bool(client.interngenius.users.find_one({"email": email}, {"_id": 1}))
    finally:
        client.close()


if __name__ == "__main__":
    try:
        test_user_profiles()
    except Exception:
        print("Profile diagnostics failed. Verify MONGO_URI and network settings.")
