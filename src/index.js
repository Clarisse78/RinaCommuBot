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
        //channel.send('Bonjour tout le monde!');
    } else {
        console.log('Le canal spécifié est introuvable.');
    }
});

client.login(process.env.TOKEN);

let playersByRole = {};


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
        for (const role in playersByRole) {
            // Vérifier si le rôle existe dans playersByRole2
            if (playersByRole2.hasOwnProperty(role)) {
                // Vérifier si les listes de joueurs sont identiques
                if (JSON.stringify(playersByRole[role]) !== JSON.stringify(playersByRole2[role])) {
                    console.log(`Les listes de joueurs pour le rôle "${role}" sont différentes :`);
                    console.log(`Joueurs dans playersByRole : ${playersByRole[role].join(', ')}`);
                    console.log(`Joueurs dans playersByRole2 : ${playersByRole2[role].join(', ')}`);

                    // Afficher les joueurs qui sont dans playersByRole mais pas dans playersByRole2
                    const missingPlayersInRole2 = playersByRole[role].filter(player => !playersByRole2[role].includes(player));
                    if (missingPlayersInRole2.length > 0) {
                        console.log(`Joueurs manquants dans playersByRole2 : ${missingPlayersInRole2.join(', ')}`);
                    }

                    // Afficher les joueurs qui sont dans playersByRole2 mais pas dans playersByRole
                    const missingPlayersInRole1 = playersByRole2[role].filter(player => !playersByRole[role].includes(player));
                    if (missingPlayersInRole1.length > 0) {
                        console.log(`Joueurs manquants dans playersByRole : ${missingPlayersInRole1.join(', ')}`);
                    }
                } else {
                    console.log("Les listes de joueurs pour le rôle " + role + " sont identiques.");
                }
            } else {
                console.log(`Le rôle "${role}" existe dans playersByRole mais pas dans playersByRole2.`);
                console.log("Changement");
            }
        }
        playersByRole = playersByRole2;
    } catch (error) {
        console.error('Erreur lors de la requête à l\'API :', error);
    }
}

setInterval(fetchFromAPI, 1 * 60 * 60)