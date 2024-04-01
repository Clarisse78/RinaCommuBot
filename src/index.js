require('dotenv').config();
const { Client, IntentsBitField, MessageEmbed } = require('discord.js');
const axios = require('axios');

const client = new Client({
    intents: [
        IntentsBitField.Flags.GuildMessages,
        IntentsBitField.Flags.Guilds,
        IntentsBitField.Flags.GuildMembers,
        IntentsBitField.Flags.MessageContent
    ],
});

client.once('ready', () => {
    console.log('Bot is ready.');
    /*
        // Récupérer la liste des canaux
        console.log('Liste des canaux:');
        client.channels.cache.forEach(channel => {
            console.log(`${channel.name} - ${channel.id}`);
        });
        console.log(client.channels.cache.size);
    */
    const channel = client.channels.cache.get('1006879475486699582');

    // Vérifier si le canal existe
    if (channel) {
        // Envoyer le message
        channel.send('Bonjour tout le monde!');
    } else {
        console.log('Le canal spécifié est introuvable.');
    }
});

client.login(process.env.TOKEN);

const playersByRole = {};


async function fetchFromAPI() {
    try {
        const config = {
            headers: {
                'API-Key': process.env.RINAORC_TOKEN
            }
        };

        const response = await axios.get('https://api.rinaorc.com/staff', config);
        // Traitez la réponse de l'API ici
        console.log(response.data);
        const playersByRole2 = {};

        response.data.ranks.forEach(role => {
            const playerList = role.players.map(player => player.name);
            playersByRole2[role.name] = playerList;
        });

        // Afficher les joueurs par rôle
        for (const role in playersByRole2) {
            console.log(`Rôle : ${role}`);
            console.log(`Joueurs : ${playersByRole2[role].join(', ')}`);
        }
        if (playersByRole2 == playersByRole) {
            console.log("Aucun changement");
        } else {
            console.log("Changement");
        }
    } catch (error) {
        console.error('Erreur lors de la requête à l\'API :', error);
    }
}

// Appel de la fonction pour récupérer les données de l'API
fetchFromAPI();