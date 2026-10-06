"""Explicitly assign pre-authentication records to one account."""

import argparse
import sys
from pathlib import Path

from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.db.session import should_use_tls

COLLECTIONS = ("tasks", "calendar_events", "documents", "agent_runs", "transactions")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True, help="Account email that should own legacy records")
    parser.add_argument("--apply", action="store_true", help="Apply updates; without this flag only preview counts")
    args = parser.parse_args()

    client_options = {"serverSelectionTimeoutMS": 10000}
    if should_use_tls(settings.DATABASE_URL):
        client_options["tls"] = True

    with MongoClient(settings.DATABASE_URL, **client_options) as client:
        database = client[settings.DATABASE_NAME]
        client.admin.command("ping")
        user = database["users"].find_one({"email": args.email.strip().lower()}, {"_id": 1})
        if user is None:
            raise SystemExit("No account found for that email; create the account before migrating records.")

        legacy_filter = {"$or": [{"owner_id": {"$exists": False}}, {"owner_id": None}]}
        for collection_name in COLLECTIONS:
            collection = database[collection_name]
            count = collection.count_documents(legacy_filter)
            if args.apply and count:
                result = collection.update_many(legacy_filter, {"$set": {"owner_id": user["_id"]}})
                count = result.modified_count
            action = "assigned" if args.apply else "would be assigned"
            print(f"{collection_name}: {count} records {action}")

    if not args.apply:
        print("Preview only. Re-run with --apply to assign these records.")


if __name__ == "__main__":
    main()