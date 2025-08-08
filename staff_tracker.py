from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup, Tag

# ===============================
# Constants
# ===============================

# Default URL for the Rinaorc tracker
URL = "https://tracker.rinaorc.com/"
# Timeout (in seconds) for all HTTP requests (connect, read)
DEFAULT_TIMEOUT: Tuple[int, int] = (5, 15)
# Custom HTTP headers 
HEADERS = {"User-Agent": "RinaCommuBot/1.0 (+https://github.com/Clarisse78/RinaCommuBot)"}

_SESSION: Optional[requests.Session] = None

# ===============================
# Functions
# ===============================

def _get_session() -> requests.Session:
    """Return a global requests session configured with retries.

    Returns:
        requests.Session: actual session
    """
    global _SESSION
    if _SESSION is None:
        s = requests.Session()
        s.headers.update(HEADERS)

        # Retry on common transient errors: 5xx, connect/read errors.
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.5,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=frozenset(["GET"]),  # we're only doing GETs here
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        s.mount("http://", adapter)
        s.mount("https://", adapter)

        _SESSION = s
    return _SESSION


def load_previous_snapshot(filename="staff_snapshot.json") -> Dict[str, str]:
    """
    Load the previous saved staff snapshot from a JSON file.

    Args:
        filename (str, optional): Path to the JSON file containing the last saved staff list.
                                  Defaults to "staff_snapshot.json".

    Returns:
        Dict[str, str]: Dictionary mapping player pseudonyms to their grade.
                        Returns an empty dict if the file doesn't exist or is invalid.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            snapshot = json.load(f)
            return snapshot.get('staff', {})
    except (FileNotFoundError, json.JSONDecodeError): # File not found or json in bad format
        return {}

def fetch_staff_list(timeout: Tuple[int, int] = DEFAULT_TIMEOUT) -> Dict[str, str]:
    """
    Fetch the current staff list from the tracker website.

    Args:
        timeout (Tuple[int, int], optional): Timeout (connect_timeout, read_timeout) (in seconds) for the HTTP request.
                                             Defaults to DEFAULT_TIMEOUT.

    Raises:
        RuntimeError: If the HTTP request fails or if parsing the HTML fails.

    Returns:
        Dict[str, str]: Dictionary mapping player pseudonyms to their grade.
    """
    session = _get_session()
    try:
        response = session.get(URL, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"fetch_staff_list: HTTP error: {e}") from e

    try:
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

            # Browse each member's information
            for info in staff_infos:

                # Get h3 that contains the name of the members
                h3 = info.find('h3')
                if isinstance(h3, Tag) and h3.has_attr('title'): # Check if h3 has a title
                    name = h3['title']

                    # Store the rank of the members in a dictionary
                    staff_data[name] = grade_name

        return staff_data
    except Exception as e:
        raise RuntimeError(f"fetch_staff_list: parse error: {e}") from e

def compare_snapshots(old_staff: Dict[str, str], new_staff: Dict[str, str])-> Tuple[Set[str], Set[str], Dict[str, Tuple[str, str]]]:
    """
    Compare two staff snapshots and determine differences.

    Args:
        old_staff (Dict[str, str]): Previous snapshot mapping pseudonyms to grades.
        new_staff (Dict[str, str]): New snapshot mapping pseudonyms to grades.

    Returns:
        tuple:
            - added (set): Names present in the new snapshot but not in the old one.
            - removed (set): Names present in the old snapshot but not in the new one.
            - modified (dict): Names whose grade changed, mapping name -> (old_grade, new_grade).
    """
    d1_keys = set(old_staff.keys())
    d2_keys = set(new_staff.keys())
    shared_keys = d1_keys.intersection(d2_keys)
    removed = d1_keys - d2_keys
    added = d2_keys - d1_keys
    modified = {o : (old_staff[o], new_staff[o]) for o in shared_keys if old_staff[o] != new_staff[o]}
    return added, removed, modified

def group_staff_by_grade(staff_data: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Group staff members by grade.

    Args:
        staff_data (Dict[str, str]): Mapping of player names to their grade.

    Returns:
        Dict[str, list]: Mapping of grade -> list of player names.
    """
    grouped = defaultdict(list)
    for name, grade in staff_data.items():
        grouped[grade].append(name)
    for names in grouped.values():
        names.sort()
    return dict(grouped)

def save_staff_to_json(staff_data, filename="staff_snapshot.json") -> None:
    """
    Save the staff snapshot to a JSON file.

    Args:
        staff_data (Dict[str, str]): Mapping of player names to their grade.
        filename (str, optional): Path to the JSON file to create/overwrite.
                                  Defaults to "staff_snapshot.json".
    """
    snapshot = {
        "staff": staff_data
    }
    tmp = f"{filename}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=4, sort_keys=True)
    os.replace(tmp, filename)

def fetch_player_rank(pseudo: str, timeout: Tuple[int, int] = DEFAULT_TIMEOUT) -> str | None:
    """
    Fetch the rank of a single player by visiting their profile page.

    Args:
        pseudo (str): Player pseudonym.
        timeout (Tuple[int, int], optional): Timeout (connect_timeout, read_timeout) (in seconds) for the HTTP request.
                                             Defaults to DEFAULT_TIMEOUT.

    Returns:
        str | None: The player's grade if found, otherwise None.
                    Returns None if the player does not exist or if any error occurs.
    """
    session = _get_session()
    url = f"{URL}player/{pseudo}"

    try:
        response = session.get(url, timeout=timeout)
        if response.status_code == 404:
            return None
        response.raise_for_status()
    except requests.RequestException:
        return None

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        rank_span = soup.select_one('.custom-rank-color')
        if rank_span:
            return rank_span.get_text(strip=True)

        return None
    except Exception:
        return None