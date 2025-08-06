# RinaCommuBot — Staff Tracker Discord Bot 🛡️

<div>
   <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Discord.py-5865F2?style=for-the-badge&logo=discord&logoColor=white"/>
  <img src="https://img.shields.io/badge/GitHub Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white"/>
  <img src="https://img.shields.io/badge/Web Scraping-4B8BBE?style=for-the-badge&logo=beautifulsoup&logoColor=white"/>
</div>

A Discord bot that scrapes the Rinaorc staff list (https://tracker.rinaorc.com/), detects changes (additions, removals, rank updates), automatically updates a Discord message, and sends alerts.

🚀 Fully automated via **GitHub Actions**.

## 📝 Context
A few years ago, I used to play on **Rinaorc** and I was manually posting staff changes on Discord (new members, departures, rank updates).

I wanted to code something simple in Python, so I decided to automate this repetitive process.

---

## ✨ Features
- Scrapes the staff list from **tracker.rinaorc.com**
- Automatically updates a Discord message with the current staff
- Sends detailed alerts when changes are detected (additions, removals, rank updates)
- Fully automated via **GitHub Actions** (runs once a day at 16:00 UTC)

## 🛠️ Requirements
- Python 3.10+
- A Discord bot with permissions to send/read messages in the relevant channels

---

## 📦 Local Installation (Development)
```bash
git clone https://github.com/Clarisse78/RinaCommuBot.git
cd RinaCommuBot
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Create a ``.env`` file at the root: :

```bash
DISCORD_TOKEN=<TOKEN_BOT>
STAFF_CHANNEL_ID=<CHANNEL_LIST_STAFF>
ALERT_CHANNEL_ID=<CHANNEL_ALERT_STAFF>
ROLE_NOTIF_STAFF_ID=<ROLE_ALERT_NOTIF>
```

### ⚙️ Run the bot locally

python bot.py