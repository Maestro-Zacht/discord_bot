# per le variabili d'ambiente
import os

# per error handling
import traceback

# per OrderedDict
import collections

import discord

# per distinguere i file
from threading import get_native_id

# per leggere i csv
import pandas as pd

from matplotlib import pyplot as plt

plt.style.use('seaborn')

DEBUG = (os.environ.get('DEBUG') == 'True')
TOKEN = os.environ.get('DISCORD_TOKEN')
GUILD = os.environ.get('GUILD_NAME')
CHANNEL = os.environ.get('CHANNEL_NAME')
MAESTRO_ID = int(os.environ.get('MAESTRO_ID'))
print(f'Ascolterò sul canale "{CHANNEL}" del server "{GUILD}"')

client = discord.Client()


def elabora_file(channel):
    send = []
    NOME_THREAD = get_native_id()

    df = pd.read_csv(f'media/file{NOME_THREAD}.csv')

    # elenco dei nomi dei giocatori
    players = set(df['Pilot'])
    giocatori_volume = {}
    for i in players:
        giocatori_volume[i] = {'volume': 0, 'percentuale': 0}
    totale_volume = 0

    # analisi i volumi
    for riga in df.itertuples(name='Riga'):
        giocatori_volume[riga.Pilot]['volume'] += riga.Volume
        totale_volume += riga.Volume

    # calcolo percentuali
    for val in giocatori_volume.values():
        val['percentuale'] = val['volume'] / totale_volume * 100

    # il grafico con il volume totale
    fig_totale, ax_finale = plt.subplots()

    dati_y = list(giocatori_volume.keys())
    dati_x = []
    for giocatore in giocatori_volume.values():
        dati_x.append(giocatore['volume'])

    rects = ax_finale.barh(dati_y, dati_x)

    # volumi scritti nel grafico
    i = 0
    for rect in rects:
        width = int(rect.get_width())

        if width < 0.4 * ax_finale.get_xlim()[1]:
            xloc = 5
            clr = 'black'
            align = 'left'
        else:
            xloc = -5
            clr = 'white'
            align = 'right'

        yloc = rect.get_y() + rect.get_height() / 2

        ax_finale.annotate(str(int(dati_x[i])) + ' m$^3$', xy=(width, yloc),
                           xytext=(xloc, 0), textcoords="offset points",
                           ha=align, va='center', color=clr, weight='bold', clip_on=True)
        i += 1

    ax_finale.set_xlabel('Volume (m$^3$)')
    ax_finale.set_ylabel('Pilot')
    ax_finale.set_title(f"Society Pandora Corporation Moon Mining {df['Timestamp'][0]}")
    ax_finale.grid(True)
    fig_totale.tight_layout()

    fig_totale.savefig(f'media/finale{NOME_THREAD}.jpg')
    plt.close(fig_totale)

    send.append(channel.send(file=discord.File(f'media/finale{NOME_THREAD}.jpg')))

    # grafico con volume nel corso del tempo
    fig_time, ax_time = plt.subplots()

    dati_x = list(set(df['Timestamp']))
    giocatori_tempo = {}
    for i in players:
        giocatori_tempo[i] = {}
        for giorno in dati_x:
            giocatori_tempo[i][giorno] = 0

    for riga in df.itertuples(name='Riga'):
        giocatori_tempo[riga.Pilot][riga.Timestamp] += riga.Volume

    giocatori_tempo_ordinato = {}
    for key, valu in giocatori_tempo.items():
        giocatori_tempo_ordinato[key] = collections.OrderedDict(sorted(valu.items()))

    for nome, gioca in giocatori_tempo_ordinato.items():
        dati_y = []
        parz = 0
        for estr in gioca.values():
            parz += estr
            dati_y.append(parz)

        ax_time.plot_date(dati_x, dati_y, linestyle='solid', marker='', label=nome)

    ax_time.set_ylabel('Volume (m$^3$)')
    ax_time.set_title('Volume totale minato')
    ax_time.legend()
    ax_time.grid(True)

    fig_time.autofmt_xdate()
    fig_time.tight_layout()

    fig_time.savefig(f'media/velocità{NOME_THREAD}.jpg')
    plt.close(fig_time)

    send.append(channel.send(file=discord.File(f'media/velocità{NOME_THREAD}.jpg')))

    # grafico con il volume per ogni giorno
    fig_velocita, ax_velocita = plt.subplots()

    for nome, gioca in giocatori_tempo_ordinato.items():
        # il volume giornaliero di ogni giocatore
        dati_y = [x for x in gioca.values()]

        ax_velocita.plot_date(dati_x, dati_y, linestyle='solid', marker='', label=nome)

        # grafico con volume giornaliero di ogni giocatore
        fig_giocatore, ax_giocatore = plt.subplots()

        ax_giocatore.plot_date(dati_x, dati_y, linestyle='solid', marker='')

        ax_giocatore.set_xlabel('Giorno')
        ax_giocatore.set_ylabel('Volume (m$^3$)')
        ax_giocatore.set_title(f'Volume giornaliero estratto da {nome}')

        fig_giocatore.autofmt_xdate()
        fig_giocatore.tight_layout()

        fig_giocatore.savefig(f'media/giornaliero_{nome}{NOME_THREAD}.jpg')
        plt.close(fig_giocatore)
        send.append(channel.send(file=discord.File(f'media/giornaliero_{nome}{NOME_THREAD}.jpg')))

    ax_velocita.set_ylabel('Volume (m$^3$)')
    ax_velocita.set_title('Volume giornaliero minato')
    ax_velocita.legend()
    ax_velocita.grid(True)

    fig_velocita.autofmt_xdate()
    fig_velocita.tight_layout()

    fig_velocita.savefig(f'media/velocità_rel{NOME_THREAD}.jpg')
    plt.close(fig_velocita)
    send.append(channel.send(file=discord.File(f'media/velocità_rel{NOME_THREAD}.jpg')))

    # testo con percentuali di raccolta di ogni giocatore
    testo = 'Percentuali di raccolta:\n'
    for giocatore, val in giocatori_volume.items():
        testo += f"{giocatore}:\t{val['percentuale']} %\n"

    send.append(channel.send(testo))

    return send


@client.event
async def on_ready():
    print(f'{client.user} si è connesso a Discord')


@client.event
async def on_message(message):
    NOME_THREAD = get_native_id()

    # non accetta DM o messaggi da se stesso
    if message.guild is None and message.author != client.user:
        if message.author.dm_channel is None:
            await message.author.create_dm()
        await message.author.dm_channel.send('Non rispondo ai messaggi in privato\n:money_mouth:')
        print('risposto a dm')

    # cattura il messaggio solo se in specifico canale
    elif message.author != client.user and message.guild.name == GUILD and message.channel.name == CHANNEL:
        print('messaggio ricevuto, elaborazione...')

        if len(message.attachments) != 0:
            # ci sono allegati

            for file in message.attachments:

                # salva il file
                with open(f'media/allegato{NOME_THREAD}.txt', 'wb') as f:
                    await file.save(f)

                # converte il contenuto in valido csv
                with open(f'media/allegato{NOME_THREAD}.txt') as f:
                    with open(f'media/file{NOME_THREAD}.csv', 'w') as wri:
                        wri.write(f.read().replace('\t', ',').replace('    ', ','))

                send = elabora_file(message.channel)
                print('messaggio elaborato')
                for i in send:
                    await i
        else:
            # solo testo
            with open(f'media/file{NOME_THREAD}.csv', 'w') as f:
                f.write(message.content.replace('    ', ',').replace('\t', ','))

            send = elabora_file(message.channel)
            print('messaggio elaborato')
            for i in send:
                await i

        print('messaggi inviati')


@client.event
async def on_error(event, *args, **kwargs):
    print('è stato rilevato un errore...')
    if event == 'on_message':

        # prende il mio utente
        maestro = client.get_user(MAESTRO_ID)

        # prende il messaggio (il primo parametro di on_message)
        messaggio = args[0]
        await maestro.send(f"É stato rilevato un errore. Il messaggio proveniva dal server ({messaggio.guild.name}) nel canale ({messaggio.channel.name}). Il contenuto che l'ha lanciato è:\n\n\n{messaggio.content}\n\n\n")

        # manda anche i file
        if len(messaggio.attachments) != 0:
            await maestro.send('Il messaggio conteneva i seguenti files:', files=[await x.to_file() for x in messaggio.attachments])

        # manda il traceback
        await maestro.send(f"\n\n\nL'errore è:\n\n{traceback.format_exc()}")
        print('errore handlato')
    else:
        raise

client.run(TOKEN)
