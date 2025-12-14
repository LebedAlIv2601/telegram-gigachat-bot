import json
import logging
import os
from typing import Dict, Optional
from threading import Lock

logger = logging.getLogger(__name__)


class SummaryStorage:
    def __init__(self, storage_file: str = "user_summaries.json"):
        self.storage_file = storage_file
        self.lock = Lock()

    def load_summaries(self) -> Dict[int, str]:
        """Load all summaries from JSON file"""
        with self.lock:
            if not os.path.exists(self.storage_file):
                logger.info(f"Summary storage file {self.storage_file} does not exist, starting fresh")
                return {}

            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert string keys back to integers
                    summaries = {int(user_id): summary for user_id, summary in data.items()}
                    logger.info(f"Loaded {len(summaries)} summaries from {self.storage_file}")
                    return summaries
            except Exception as e:
                logger.error(f"Error loading summaries from {self.storage_file}: {e}")
                return {}

    def save_summary(self, user_id: int, summary: str) -> bool:
        """Save single user summary to JSON file"""
        with self.lock:
            try:
                # Load existing summaries
                summaries = {}
                if os.path.exists(self.storage_file):
                    with open(self.storage_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        summaries = {int(uid): s for uid, s in data.items()}

                # Update with new summary
                summaries[user_id] = summary

                # Save back to file
                # Convert int keys to strings for JSON serialization
                data_to_save = {str(uid): s for uid, s in summaries.items()}
                with open(self.storage_file, 'w', encoding='utf-8') as f:
                    json.dump(data_to_save, f, ensure_ascii=False, indent=2)

                logger.info(f"Saved summary for user {user_id} to {self.storage_file}")
                return True
            except Exception as e:
                logger.error(f"Error saving summary for user {user_id}: {e}")
                return False

    def delete_summary(self, user_id: int) -> bool:
        """Remove user summary from JSON file"""
        with self.lock:
            try:
                if not os.path.exists(self.storage_file):
                    logger.info(f"Summary storage file {self.storage_file} does not exist, nothing to delete")
                    return True

                # Load existing summaries
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    summaries = {int(uid): s for uid, s in data.items()}

                # Remove user summary if exists
                if user_id in summaries:
                    del summaries[user_id]

                    # Save back to file
                    data_to_save = {str(uid): s for uid, s in summaries.items()}
                    with open(self.storage_file, 'w', encoding='utf-8') as f:
                        json.dump(data_to_save, f, ensure_ascii=False, indent=2)

                    logger.info(f"Deleted summary for user {user_id} from {self.storage_file}")
                else:
                    logger.info(f"No summary found for user {user_id} in {self.storage_file}")

                return True
            except Exception as e:
                logger.error(f"Error deleting summary for user {user_id}: {e}")
                return False

    def get_summary(self, user_id: int) -> Optional[str]:
        """Retrieve summary for specific user from file"""
        with self.lock:
            try:
                if not os.path.exists(self.storage_file):
                    return None

                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    summaries = {int(uid): s for uid, s in data.items()}
                    return summaries.get(user_id)
            except Exception as e:
                logger.error(f"Error getting summary for user {user_id}: {e}")
                return None
