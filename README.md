# RinaCommuBot — Staff Tracker Discord Bot 🛡️

<div>
   <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Discord.py-5865F2?style=for-the-badge&logo=discord&logoColor=white"/>
  <img src="https://img.shields.io/badge/GitHub Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white"/>
  <img src="https://img.shields.io/badge/Web Scraping-4B8BBE?style=for-the-badge&logo=beautifulsoup&logoColor=white"/>
</div>

Un bot Discord qui scrappe la liste du staff Rinaorc (https://tracker.rinaorc.com/), détecte les changements (ajouts, suppressions, changements de grade), met à jour automatiquement un message Discord, et envoie des alertes.

🚀 Totalement automatisé via **GitHub Actions**.

---

## 📝 Contexte
Il y a quelques années, je jouais à **Rinaorc** et je faisais à la main les annonces de changements de staff sur Discord (ajouts, départs, changements de grade).  

J'avais envie de faire un peu de Python pour quelque chose de simple, j’ai donc décidé d’automatiser ce process.

---

## ✨ Fonctionnalités
- Scrapping de la liste de staff depuis **tracker.rinaorc.com**
- Mise à jour d'un message Discord
- Alertes détaillées sur les changements (ajouts, suppressions, changements de grade)
- Full automatisation via **GitHub Actions** (une fois par jour à 16h UTC)

---

## 🛠️ Prérequis
- Python 3.10+
- Un bot Discord configuré sur ton serveur (avec les permissions Envoyer des messages, Lire les messages, etc.)

---

## 📦 Installation locale (Développement)
```bash
git clone https://github.com/Clarisse78/RinaCommuBot.git
cd RinaCommuBot
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
```

### Créer un fichier .env à la racine :

```bash
DISCORD_TOKEN=<TOKEN_BOT>
STAFF_CHANNEL_ID=<CHANNEL_LIST_STAFF>
ALERT_CHANNEL_ID=<CHANNEL_ALERT_STAFF>
ROLE_NOTIF_STAFF_ID=<ROLE_ALERT_NOTIF>
```

### ⚙️ Lancer le bot localement

python bot.py