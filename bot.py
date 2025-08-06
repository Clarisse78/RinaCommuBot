import discord
import os
import json
from discord.ext import tasks
from discord import TextChannel
from dotenv import load_dotenv
from staff_tracker import fetch_staff_list, load_previous_snapshot, compare_snapshots, save_staff_to_json, group_staff_by_grade, fetch_player_rank

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

# Get message id if exist
def load_message_id():
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, 'r') as f:
            return json.load(f).get("message_id")
    return None

# Save message id in json file
def save_message_id(message_id):
    with open(MESSAGE_ID_FILE, 'w') as f:
        json.dump({"message_id": message_id}, f)

# Launch bot
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await check_staff_changes()
    await client.close()

# Check the change in staff
async def check_staff_changes():
    staff_channel_raw = client.get_channel(STAFF_CHANNEL_ID)
    alert_channel_raw = client.get_channel(ALERT_CHANNEL_ID)

    # Type assertion pour Pylance
    if not isinstance(staff_channel_raw, TextChannel):
        raise TypeError("STAFF_CHANNEL_ID must be a Text Channel")

    if not isinstance(alert_channel_raw, TextChannel):
        raise TypeError("ALERT_CHANNEL_ID must be a Text Channel")

    staff_channel: TextChannel = staff_channel_raw
    alert_channel: TextChannel = alert_channel_raw

    previous_staff = load_previous_snapshot()
    current_staff = fetch_staff_list()

    added, removed, grade_changed = compare_snapshots(previous_staff, current_staff)

    # Update the main staff message
    message_id = load_message_id()
    message_content = format_staff_list(current_staff)

    if message_id:
        try:
            message = await staff_channel.fetch_message(message_id)
            await message.edit(content=message_content)
        except discord.NotFound:
            message = await staff_channel.send(message_content)
            save_message_id(message.id)
    else:
        message = await staff_channel.send(message_content)
        save_message_id(message.id)

    # Send alert if there are changes
    if added or removed or grade_changed:
        alert_msg = format_alerts(added, removed, grade_changed, previous_staff, current_staff)
        await alert_channel.send(alert_msg, allowed_mentions=discord.AllowedMentions(roles=True))

    # Update snapshot
    save_staff_to_json(current_staff)

def format_staff_list(staff_data):
    grouped = group_staff_by_grade(staff_data)
    content = "__Staff Rinaorc :__\n\n"
    for grade, members in grouped.items():
        content += f"**{grade.upper()} [{len(members)}]** :\n"
        for member in members:
            content += f"- ``{member}``\n"
        content += "\n"
    return content

def format_alerts(added, removed, grade_changed, old_staff, new_staff):
    msg = f"**Annonce Staff** | <@&{ROLE_NOTIF_STAFF_ID}> :bust_in_silhouette: \n\n"
    if added:
        for name in added:
            msg += f"``{name}`` passe de N/A à **{old_staff.get(name, 'N/A')}**.\n"

    if removed:
        for name in removed:
            new_grade = fetch_player_rank(name)
            msg += f"``{name}`` passe de **{new_staff.get(name, 'N/A')}** à **{new_grade if new_grade else 'N/A'}**.\n"

    if grade_changed:
        for name, (old_grade, new_grade) in grade_changed.items():
            msg += f"``{name}`` passe de **{old_grade}** à **{new_grade}**.\n"

    return msg

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("DISCORD_TOKEN not set in .env")

client.run(TOKEN)
