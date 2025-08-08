import discord
import os
import json
from discord import TextChannel
from dotenv import load_dotenv
from staff_tracker import fetch_staff_list, load_previous_snapshot, compare_snapshots, save_staff_to_json, group_staff_by_grade, fetch_player_rank
import sys, asyncio

# Set event loop policy (for Windows only)
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ===============================
# Constants
# ===============================

# Get environment variables
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
staff_channel_id_env = os.getenv("STAFF_CHANNEL_ID")
alert_channel_id_env = os.getenv("ALERT_CHANNEL_ID")
role_notif_staff_id_env = os.getenv("ROLE_NOTIF_STAFF_ID")

# Check if all necessary environment variables are here
if staff_channel_id_env is None or alert_channel_id_env is None or role_notif_staff_id_env is None:
    raise ValueError("STAFF_CHANNEL_ID or ALERT_CHANNEL_ID or ROLE_NOTIF_STAFF_ID not set in .env")

STAFF_CHANNEL_ID = int(staff_channel_id_env)
ALERT_CHANNEL_ID = int(alert_channel_id_env)
ROLE_NOTIF_STAFF_ID = int(role_notif_staff_id_env)
MESSAGE_ID_FILE = "message_id.json"

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

# ===============================
# Functions
# ===============================

def load_message_id() -> int | None:
    """
    Load the ID of the staff message if it exists.

    Returns:
        int | None: The Discord message ID, or None if the file doesn't exist or is invalid.
    """
    if os.path.exists(MESSAGE_ID_FILE):
        try:
            with open(MESSAGE_ID_FILE, 'r') as f:
                raw = json.load(f).get("message_id")
                return int(raw) if isinstance(raw, int | str) and str(raw).isdigit() else None
        except Exception:
            return None
    return None

def save_message_id(message_id: int) -> None:
    """
    Persist the staff message ID.

    Args:
        message_id (int): The Discord message ID to save.
    """
    with open(MESSAGE_ID_FILE, 'w') as f:
        json.dump({"message_id": message_id}, f)

def format_staff_list(staff_data: dict[str, str]) -> str:
    """
    Build the message content listing the current staff grouped by grade.

    Args:
        staff_data (dict[str, str]): Mapping name -> grade.

    Returns:
        str: Formatted message content.
    """
    grouped = group_staff_by_grade(staff_data)
    content = "__Staff Rinaorc :__\n\n"
    for grade, members in grouped.items():
        content += f"**{grade.upper()} [{len(members)}]** :\n"
        for member in members:
            content += f"- ``{member}``\n"
        content += "\n"
    return content

def format_alerts(
    added: set[str],
    removed: set[str],
    grade_changed: dict[str, tuple[str, str]],
    old_staff: dict[str, str],
    new_staff: dict[str, str],  
    removed_rank_map: dict[str, str | None]
) -> str:
    """
    Build the alert message describing staff changes.

    Args:
        added: Names present in the new snapshot but not in the old one.
        removed: Names present in the old snapshot but not in the new one.
        grade_changed: Mapping of name -> (old_grade, new_grade) for grade changes.
        old_staff: Previous snapshot mapping name -> grade.
        new_staff: New snapshot mapping name -> grade.

    Returns:
        str: Formatted alert message.
    """
    msg = f"**Annonce Staff** | <@&{ROLE_NOTIF_STAFF_ID}> :bust_in_silhouette: \n\n"
    if added:
        for name in added:
            msg += f"``{name}`` passe de **N/A** à **{new_staff.get(name, 'N/A')}**.\n"

    if removed:
        for name in removed:
            new_grade = removed_rank_map.get(name) or "N/A"
            msg += f"``{name}`` passe de **{old_staff.get(name, 'N/A')}** à **{new_grade if new_grade else 'N/A'}**.\n"

    if grade_changed:
        for name, (old_grade, new_grade) in grade_changed.items():
            msg += f"``{name}`` passe de **{old_grade}** à **{new_grade}**.\n"

    return msg

async def check_staff_changes(client: discord.Client):
    """
    Fetch channels, compute diffs, update the main staff message, optionally send an alert,
    and save the new snapshot. Uses HTTP-only (no Gateway).

    Args:
        client (discord.Client): Discord client

    Raises:
         TypeError: If one of the configured channels is not a text channel.
    """
    try:
        staff_channel = await client.fetch_channel(STAFF_CHANNEL_ID)
        alert_channel = await client.fetch_channel(ALERT_CHANNEL_ID)
    except discord.HTTPException as e:
        print(f"[ERROR] fetch_channel: {e}")
        return

    if not isinstance(staff_channel, TextChannel) or not isinstance(alert_channel, TextChannel):
        raise TypeError("Both STAFF_CHANNEL_ID and ALERT_CHANNEL_ID must be Text Channels")

    previous_staff = await asyncio.to_thread(load_previous_snapshot)
    current_staff = await asyncio.to_thread(fetch_staff_list)

    added, removed, grade_changed = compare_snapshots(previous_staff, current_staff)

    # Update / create main message
    message_id = load_message_id()
    message_content = format_staff_list(current_staff)

    try:
        if message_id:
            try:
                msg = await staff_channel.fetch_message(message_id)
                await msg.edit(content=message_content)
            except discord.NotFound:
                msg = await staff_channel.send(message_content)
                save_message_id(msg.id)
        else:
            msg = await staff_channel.send(message_content)
            save_message_id(msg.id)
    except discord.HTTPException as e:
        print(f"[ERROR] update main message: {e}")

    # Alerts
    if added or removed or grade_changed:
        try:
            removed_sorted = sorted(removed)
            rank_tasks = [asyncio.to_thread(fetch_player_rank, name) for name in removed_sorted]
            removed_ranks = await asyncio.gather(*rank_tasks, return_exceptions=True)
            removed_rank_map: dict[str, str | None] = {}
            for name, rank in zip(removed_sorted, removed_ranks):
                if isinstance(rank, str) or rank is None:
                    removed_rank_map[name] = rank
                else:
                    removed_rank_map[name] = None

            alert_msg = format_alerts(added, removed, grade_changed, previous_staff, current_staff, removed_rank_map)
      
            await alert_channel.send(
                alert_msg,
                allowed_mentions=discord.AllowedMentions(roles=True, users=False, everyone=False),
            )
        except discord.HTTPException as e:
            print(f"[ERROR] send alert: {e}")

    await asyncio.to_thread(save_staff_to_json, current_staff)

async def main():
    """
    One-shot run: login via HTTP, update the message, optionally alert, save snapshot, exit.
    """
    if TOKEN is None:
        raise ValueError("DISCORD_TOKEN not set in .env")
    print("[DEBUG] Logging in to Discord HTTP API…")
    async with client:
        await client.login(TOKEN)
        print("[DEBUG] Logged in. Fetching staff changes…")
        await check_staff_changes(client)
        print("[DEBUG] Done. Closing client.")

if __name__ == "__main__":
    asyncio.run(main())