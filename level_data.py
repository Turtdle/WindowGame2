import json
import os

SAVE_FILE_PATH = "level_data.json"

def load_completed_levels():
    """Load the completed levels from the JSON file."""
    if not os.path.exists(SAVE_FILE_PATH):
        default_data = {
            "completed_levels": []
        }
        save_completed_levels(default_data["completed_levels"])
        return default_data["completed_levels"]
    
    try:
        with open(SAVE_FILE_PATH, 'r') as f:
            data = json.load(f)
            return data.get("completed_levels", [])
    except (json.JSONDecodeError, FileNotFoundError):
        default_data = {
            "completed_levels": []
        }
        save_completed_levels(default_data["completed_levels"])
        return default_data["completed_levels"]

def save_completed_levels(completed_levels):
    """Save the list of completed levels to the JSON file."""
    data = {
        "completed_levels": completed_levels
    }
    
    try:
        with open(SAVE_FILE_PATH, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving level data: {e}")
        return False

def mark_level_completed(level_name):
    """Mark a level as completed."""
    completed_levels = load_completed_levels()
    
    if level_name not in completed_levels:
        completed_levels.append(level_name)
        save_completed_levels(completed_levels)
        print(f"Level {level_name} marked as completed and saved to file")
    
    return completed_levels