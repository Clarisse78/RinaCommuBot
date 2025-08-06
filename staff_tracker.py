import requests
import json
from bs4 import BeautifulSoup, Tag
import json
from datetime import datetime
from collections import defaultdict
from typing import Tuple, Dict

URL = "https://tracker.rinaorc.com/"

# Load the previous snapshot of staff
def load_previous_snapshot(filename="staff_snapshot.json") -> Dict[str, str]:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            snapshot = json.load(f)
            return snapshot['staff']
    except FileNotFoundError:
        return {}

def fetch_staff_list():
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    staff_data =  {}
    
    # Select one staff rank group
    staff_ranks = soup.select('.staff-rank-group')
    for rank in staff_ranks:

        # Get the tag of the rank
        grade_tag = rank.select_one('.staff-rank-title')
        if not grade_tag:
            continue

        # Get the name of the rank
        grade_name = grade_tag.get_text(strip=True)

        # Get the informations of the members part of this rank
        staff_infos = rank.select('.staff-info')

        # Parkour the informations of each members
        for info in staff_infos:

            # Get h3 that contains the name of the members
            h3 = info.find('h3')
            if isinstance(h3, Tag):
                name = h3['title']

                # Store the rank of the members in a dictionary
                staff_data[name] = grade_name

    return staff_data

# Compare the two version of the staff
def compare_snapshots(old_staff: Dict[str, str], new_staff: Dict[str, str]):
    d1_keys = set(old_staff.keys())
    d2_keys = set(new_staff.keys())
    shared_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (old_staff[o], new_staff[o]) for o in shared_keys if old_staff[o] != new_staff[o]}
    return added, removed, modified

# Group staff by grade
def group_staff_by_grade(staff_data):
    grouped = defaultdict(list)
    for name, grade in staff_data.items():
        grouped[grade].append(name)
    return dict(grouped)

# Save the list of staff in json file
def save_staff_to_json(staff_data, filename="staff_snapshot.json"):
    snapshot = {
        "staff": staff_data
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=4)

def fetch_player_rank(pseudo: str) -> str | None:
    url = f"https://tracker.rinaorc.com/player/{pseudo}"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    rank_span = soup.select_one('.custom-rank-color')
    if rank_span:
        return rank_span.get_text(strip=True)

    return None
