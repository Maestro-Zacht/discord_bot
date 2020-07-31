import os
import discord
import pandas as pd
from matplotlib import pyplot as plt

plt.style.use('seaborn')

TOKEN = os.environ.get('DISCORD_TOKEN')
GUILD = os.environ.get('GUILD_NAME')
CHANNEL = os.environ.get('CHANNEL_NAME')
print(f'Ascolterò sul canale "{CHANNEL}" del server "{GUILD}"')

client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord')


@client.event
async def on_message(message):
    if message.author != client.user and message.guild.name == GUILD and message.channel.name == CHANNEL and len(message.attachments) != 0:
        for file in message.attachments:
            with open('allegato.csv', 'wb') as f:
                await file.save(f)
            with open('allegato.csv') as f:
                with open('file.csv', 'w') as wri:
                    wri.write(f.read().replace('\t', ','))
            df = pd.read_csv('file.csv')
            players = set(df['Pilot'])
            giocatori = {}
            for i in players:
                giocatori[i] = {'volume': 0, 'percentuale': 0}
            totale_volume = 0
            for riga in df.itertuples(name='Riga'):
                giocatori[riga.Pilot]['volume'] += riga.Volume
                totale_volume += riga.Volume

            for val in giocatori.values():
                val['percentuale'] = val['volume'] / totale_volume * 100

            fig, ax = plt.subplots()

            dati_y = list(giocatori.keys())
            dati_x = []
            for giocatore in giocatori.values():
                dati_x.append(giocatore['volume'])

            ax.barh(dati_y, dati_x)

            ax.set_xlabel('Volume (metri cubi)')
            ax.set_ylabel('Pilot')

            fig.savefig('prova.jpg')
            plt.close(fig)

            await message.channel.send(file=discord.File('prova.jpg'))

            testo = 'Percentuali di raccolta:\n'
            for giocatore, val in giocatori.items():
                testo += f"{giocatore}:\t{val['percentuale']} %\n"

            await message.channel.send(testo)

client.run(TOKEN)
