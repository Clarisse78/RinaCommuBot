# RinaCommuBot - Staff Tracker Discord Bot 🛡️

<div>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Discord.py-5865F2?style=for-the-badge&logo=discord&logoColor=white"/>
  <img src="https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white"/>
  <img src="https://img.shields.io/badge/Web%20Scraping-4B8BBE?style=for-the-badge&logo=beautifulsoup&logoColor=white"/>
</div>

> [!NOTE]
> **Archived project.** The data source (`tracker.rinaorc.com`) is no longer online,
> so the bot is no longer functional. The code remains available for reference.

A Discord bot that scraped the Rinaorc staff list, detected changes (additions,
removals, rank updates), automatically updated a Discord message, and sent alerts.
🚀 Fully automated via **GitHub Actions**.

## 📸 Preview

![Discord message showing the auto-updated staff list](assets/preview.png)

## 📝 Context

A few years ago, I used to play on **Rinaorc** and I was manually posting staff
changes on Discord (new members, departures, rank updates).
I wanted to code something simple in Python, so I decided to automate this
repetitive process.

---

## ✨ Features

- Scraped the staff list from **tracker.rinaorc.com**
- Automatically updated a Discord message with the current staff
- Sent detailed alerts when changes were detected (additions, removals, rank updates)
- Fully automated via **GitHub Actions** (ran once a day at 16:00 UTC)

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

### Create a `.env` file at the root

```bash
DISCORD_TOKEN=<TOKEN_BOT>
STAFF_CHANNEL_ID=<CHANNEL_LIST_STAFF>
ALERT_CHANNEL_ID=<CHANNEL_ALERT_STAFF>
ROLE_NOTIF_STAFF_ID=<ROLE_ALERT_NOTIF>
```

### ⚙️ Run the bot locally

```bash
python bot.py
```
