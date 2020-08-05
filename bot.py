import os
import sys
import discord
from threading import get_native_id
import pandas as pd
from matplotlib import pyplot as plt

plt.style.use('seaborn')

DEBUG = os.environ.get('DEBUG')
TOKEN = os.environ.get('DISCORD_TOKEN')
GUILD = os.environ.get('GUILD_NAME')
CHANNEL = os.environ.get('CHANNEL_NAME')
MAESTRO_ID = int(os.environ.get('MAESTRO_ID'))
print(f'Ascolterò sul canale "{CHANNEL}" del server "{GUILD}"')

client = discord.Client()


def elabora_file(channel):
    send = []

    df = pd.read_csv(f'file{get_native_id()}.csv')
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

    fig.savefig(f'finale{get_native_id()}.jpg')
    plt.close(fig)

    send.append(channel.send(file=discord.File(f'finale{get_native_id()}.jpg')))

    testo = 'Percentuali di raccolta:\n'
    for giocatore, val in giocatori.items():
        testo += f"{giocatore}:\t{val['percentuale']} %\n"

    send.append(channel.send(testo))

    return send


@client.event
async def on_ready():
    print(f'{client.user} si è connesso a Discord')


@client.event
async def on_message(message):
    if message.author != client.user and message.guild.name == GUILD and message.channel.name == CHANNEL:
        print('messaggio ricevuto, elaborazione...')
        if len(message.attachments) != 0:
            for file in message.attachments:
                with open(f'allegato{get_native_id()}.csv', 'wb') as f:
                    await file.save(f)
                with open(f'allegato{get_native_id()}.csv') as f:
                    with open(f'file{get_native_id()}.csv', 'w') as wri:
                        wri.write(f.read().replace('\t', ',').replace('    ', ','))
                send = elabora_file(message.channel)
                for i in send:
                    await i
        else:
            with open(f'file{get_native_id()}.csv', 'w') as f:
                f.write(message.content.replace('    ', ',').replace('\t', ','))

            send = elabora_file(message.channel)
            for i in send:
                await i

        print('messaggio elaborato')


@client.event
async def on_error(event, *args, **kwargs):
    print('è stato rilevato un errore...')
    if event == 'on_message':
        maestro = client.get_user(MAESTRO_ID)
        messaggio = args[0]
        await maestro.send(f"É stato rilevato un errore. Il messaggio proveniva dal server ({messaggio.guild.name}) nel canale ({messaggio.channel.name}). Il contenuto che l'ha lanciato è:\n\n\n{messaggio.content}\n\n\n")
        if len(messaggio.attachments) != 0:
            await maestro.send('Il messaggio conteneva i seguenti files:', files=messaggio.attachments)

        tipo, value, trace = sys.exc_info()

        await maestro.send(f"\n\n\nL'errore è:\n\ntipo:\n{repr(tipo)}\n\nvalue:\n{repr(value)}\n\ntraceback:\n{repr(trace)}")
    else:
        raise

client.run(TOKEN)
