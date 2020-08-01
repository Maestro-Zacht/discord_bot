import os
import discord
import pandas as pd
from matplotlib import pyplot as plt

plt.style.use('seaborn')

DEBUG = os.environ.get('DEBUG')
TOKEN = os.environ.get('DISCORD_TOKEN')
GUILD = os.environ.get('GUILD_NAME')
CHANNEL = os.environ.get('CHANNEL_NAME')
print(f'Ascolterò sul canale "{CHANNEL}" del server "{GUILD}"')

client = discord.Client()


def elabora_file(channel):
    send = []

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

    rects = ax.barh(dati_y, dati_x)

    i = 0
    for rect in rects:
        width = int(rect.get_width())

        if width < 0.4 * totale_volume:
            xloc = 5
            clr = 'black'
            align = 'left'
        else:
            xloc = -5
            clr = 'white'
            align = 'right'

        yloc = rect.get_y() + rect.get_height() / 2

        ax.annotate(str(int(dati_x[i])) + ' m$^3$', xy=(width, yloc),
                    xytext=(xloc, 0), textcoords="offset points",
                    ha=align, va='center', color=clr, weight='bold', clip_on=True)
        i += 1

    ax.set_xlabel('Volume (m$^3$)')
    ax.set_ylabel('Pilot')
    ax.set_title('Society Pandora Corporation Moon Mining')

    fig.savefig('finale.jpg')
    plt.close(fig)

    send.append(channel.send(file=discord.File('finale.jpg')))

    testo = 'Percentuali di raccolta:\n'
    for giocatore, val in giocatori.items():
        testo += f"{giocatore}:\t{val['percentuale']} %\n"

    send.append(channel.send(testo))

    return send


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord')


@client.event
async def on_message(message):
    if message.author != client.user and message.guild.name == GUILD and message.channel.name == CHANNEL:
        print('messaggio ricevuto, elaborazione...')
        if len(message.attachments) != 0:
            for file in message.attachments:
                with open('allegato.csv', 'wb') as f:
                    await file.save(f)
                with open('allegato.csv') as f:
                    with open('file.csv', 'w') as wri:
                        wri.write(f.read().replace('\t', ','))
                send = elabora_file(message.channel)
                for i in send:
                    await i
        else:
            with open('file.csv', 'w') as f:
                f.write(message.content.replace('    ', ','))

            send = elabora_file(message.channel)
            for i in send:
                await i

        print('messaggio elaborato')

client.run(TOKEN)
