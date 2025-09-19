import os
import re

from pathlib import Path
import xml.etree.ElementTree as ET
from mutagen.mp3 import MP3

# hulpfuncties en -variabelen importeren
from modules.Hulpfuncties import convert_time_to_s, SMILPADEN
from modules.config import PRODUCTIEFOLDERPAD
from modules.config import NCC_ROOT, NCC_NAMESPACES

messages = []

# Controleren of elke seq dur waarde in de body van een smil overeenkomt met ncc:timeInThisSmil in de header van elk smilbestand
def confirm_time_in_this_smil_equals_seq_dur(productiefolder_pad, smilpaden):
    new_messages = []

    for smilpad in smilpaden:
        smilnaam = os.path.basename(smilpad)
        root = ET.parse(smilpad).getroot()
        # duur ophalen uit ncc:timeInThisSmil en omzetten naar seconden (ssss.msmsms)
        time_in_this_smil = root.find(".//meta[@name='ncc:timeInThisSmil']").attrib['content']
        time_in_this_smil_sec = convert_time_to_s(time_in_this_smil)
        # seq dur ophalen uit de body van smil
        seq_dur = root.find(".//seq").attrib['dur']
        seq_dur_sec = float(seq_dur.replace('s', ''))

        if round(time_in_this_smil_sec, ndigits = 3) != round(seq_dur_sec, ndigits = 3):
            new_messages.append(f'FOUT! <a class="bad" href="{smilpad}">{smilnaam}</a> timeInThisSmil ({time_in_this_smil} ({time_in_this_smil_sec}s)) niet gelijk aan seq dur ({seq_dur}).')

    if new_messages:
        messages.append(new_messages)
    else:
        messages.append("OK. Elke seq dur waarde in de body van een smil komt overeen met ncc:timeInThisSmil in de header van elk smilbestand.")

# Controleren of elke seq dur waarde overeenkomt met de tijdswaarde van het clip-end attribuut in de laatste audiotag van het smilbestand. Beide waarden bevinden zich in de body.
def confirm_last_clip_end_smil_equals_seq_dur(productiefolder_pad, smilpaden):
    new_messages = []

    for smilpad in smilpaden:
        smilnaam = os.path.basename(smilpad)
        root = ET.parse(smilpad).getroot()
        # seq dur ophalen uit de body van smil
        seq_dur = root.find(".//seq").attrib['dur']
        # clip-end van laatste audiotag ophalen
        audio = root.findall(".//audio")
        index = len(audio) - 1
        clipend = audio[index].get('clip-end').replace('npt=', '')
        # checken of clip-end niet leeg is én de juiste waarde heeft
        if not clipend:
            new_messages.append(f'FOUT! <a class="bad" href="{smilpad}">{smilnaam}</a> gaf een probleem bij het ophalen van de laatste clip-end')
        elif clipend != seq_dur:
            new_messages.append(f'FOUT! <a class="bad" href="{smilpad}">{smilnaam}</a> seq dur ({seq_dur}) niet gelijk aan laatste clip-end ({clipend}).')
    
    if new_messages:
        messages.append(new_messages)
    else:
        messages.append("OK. Elke seq dur waarde komt overeen met de tijdswaarde van het clip-end attribuut in de laatste audiotag van het smilbestand.")

# Controleren of elke seq dur waarde van een smil niet groter is dan de speelduur van het laatst gerefereerde mp3-bestand in dat smil-bestand.
def confirm_seq_dur_not_bigger_than_size_last_ref_mp3(productiefolder_pad, smilpaden):
    new_messages = []

    for smilpad in smilpaden:
        smilnaam = os.path.basename(smilpad)
        root = ET.parse(smilpad).getroot()
        # seq dur ophalen uit de body van smil en omzetten naar ms
        seq_dur = root.find(".//seq").attrib['dur']
        seq_dur_in_ms = int(float(seq_dur.replace('s', '')) * 1000)
        # tag van laatst gerefereerde mp3-bestand ophalen uit smil
        audio_elements = root.findall('.//audio')
        mp3bestand = audio_elements[-1].attrib['src']
        mp3pad = os.path.join(os.path.dirname(smilpad), mp3bestand)
        # speelduur van ieder mp3-bestand ophalen
        try:
            with open(mp3pad, 'rb') as audio_file:
                audio = MP3(audio_file)
                speelduur_mp3_in_ms = int(float(audio.info.length) * 1000)
                # controleren of seq dur niet groter is dan mp3-speelduur
                if seq_dur_in_ms > speelduur_mp3_in_ms:
                    new_messages.append(f'FOUT! {smilnaam} seq dur ({seq_dur_in_ms}ms) is groter dan speelduur {mp3bestand} ({speelduur_mp3_in_ms}ms)')
        except FileNotFoundError:
             print(f"FileNotFoundError: Het bestand {mp3pad} is niet gevonden.")
    
    if new_messages:
        messages.append(new_messages)
    else:
        messages.append("OK. Elke seq dur waarde van een smil is niet groter dan de speelduur van het laatst gerefereerde mp3-bestand in dat smil-bestand.")

# Controle of totalElapsedTime in de header van elk smilbestand overeenkomt met de totalElapsedTime van het vorige smilbestand + vorige timeInThisSmil
def confirm_total_elapsed_time(productiefolder_pad, smilpaden):
    new_messages = []

    total_ok = '00:00:00.000'
    inthissmil_ok = '00:00:00.000'
    vorige_total_elapsed_time = '00:00:00.000'
    vorige_time_in_this_smil = '00:00:00.000'

    for teller, smilpad in enumerate(smilpaden, start=1):
        root = ET.parse(smilpad).getroot()
        # tijdsinfo ophalen
        total_elapsed_time = root.find(".//meta[@name='ncc:totalElapsedTime']").attrib['content']
        if total_elapsed_time is None:
            new_messages.append("FOUT! Geen total elapsed time tag in tenminste het eerste smilbestand")
            return messages
        time_in_this_smil = root.find(".//meta[@name='ncc:timeInThisSmil']").attrib['content']
        # milliseconden toevoegen als die niet aanwezig zijn
        total_ok = total_elapsed_time if '.' in total_elapsed_time else total_elapsed_time + '.000'
        inthissmil_ok = time_in_this_smil if '.' in time_in_this_smil else time_in_this_smil + '.000'
        # tijd omzetten naar formaat ssss.msmsms
        vorige_total_elapsed_time_ms = convert_time_to_s(vorige_total_elapsed_time)
        total_elapsed_time_ms = convert_time_to_s(total_ok)
        vorige_time_in_this_smil_ms = convert_time_to_s(vorige_time_in_this_smil)
        time_in_this_smil_ms = convert_time_to_s(inthissmil_ok)

        if teller > 1:
            if round(vorige_total_elapsed_time_ms + vorige_time_in_this_smil_ms, 3) != round(total_elapsed_time_ms, 3):
                new_messages.append(f'FOUT! total elapsed time {total_elapsed_time} in smil {os.path.basename(smilpad)} is niet gelijk aan vorige elapsed time ({vorige_total_elapsed_time}) + vorige timeInThisSmil ({vorige_time_in_this_smil})')
        # tijd van huidige smil naar vorige smil verplaatsen
        vorige_total_elapsed_time = total_ok
        vorige_time_in_this_smil = inthissmil_ok

    if new_messages:
        messages.append(new_messages)
    else:
        messages.append("OK. De totalElapsedTime in de header van elk smilbestand komt overeen met de totalElapsedTime van het vorige smilbestand + vorige timeInThisSmil.")

# Controleren of timeInThisSmil in de header van master.smil overeenkomt met de totalElapsedTime van het laatste smilbestand in de productiefolder.
# Er wordt uitgegaan van alfanumerieke sortering om te bepalen welk bestand het laatste smilbestand is
def confirm_time_in_this_smil_master(productiefolder_pad, smilpaden):
    aantal_messages = len(messages)

    # master.smil parsen en timeInThisSmil (totale tijd volgens metadata in master.smil) ophalen
    master_smil_pad = next(Path(productiefolder_pad).rglob('master.smil'))
    root_master_smil = ET.parse(master_smil_pad).getroot()
    master_smil_time_in_smil = root_master_smil.find(".//meta[@name='ncc:timeInThisSmil']").attrib['content']
    # totalElapsedTime uit laatste 'reguliere' smil verzamelen
    smilpaden.sort()
    last_smil_pad = smilpaden[-1]
    root_last_smil = ET.parse(last_smil_pad).getroot()
    last_smil_total_elapsed_time = root_last_smil.find(".//meta[@name='ncc:totalElapsedTime']").attrib['content']
    last_smil_time_in_smil = root_last_smil.find(".//meta[@name='ncc:timeInThisSmil']").attrib['content']
    # tijd uit master.smil en laatste smil omzetten naar formaat ssss.msmsms
    master_smil_time_in_smil_s = convert_time_to_s(master_smil_time_in_smil)
    last_smil_total_elapsed_time_s = convert_time_to_s(last_smil_total_elapsed_time)
    last_smil_time_in_smil_s = convert_time_to_s(last_smil_time_in_smil)
    # tijd uit laatste smil optellen en vergelijken met die uit master.smil
    last_smil_calc_time = last_smil_total_elapsed_time_s + last_smil_time_in_smil_s
    if master_smil_time_in_smil_s != last_smil_calc_time:
        messages.append(f"FOUT! timeInThisSmil ({master_smil_time_in_smil}) in master.smil is niet gelijk aan de som van de totalElapsedTime ({last_smil_total_elapsed_time}) en timeInThisSmil ({last_smil_time_in_smil}) van het laatste smilbestand {os.path.basename(last_smil_pad)}")

    if len(messages) == aantal_messages:
        messages.append("OK. De timeInThisSmil in de header van master.smil komt overeen met de totalElapsedTime van het laatste smilbestand in de productiefolder.")

# Nagaan of clip-endwaarde in elke audiotag van smilbestanden groter is dan de clip-beginwaarde
def confirm_smil_audio_tag_chronology(productiefolder_pad, smilpaden):
    new_messages = []

    # alle smilbestanden audio-data ophalen (id, begin, eind)
    for smilpad in smilpaden:
        root = ET.parse(smilpad).getroot()
        audio_tags = root.findall(".//audio")

        for audio in audio_tags:
            begin = audio.get('clip-begin')
            end = audio.get('clip-end')
            audio_id = audio.get('id')

            # begin- en eindwaarde samenstellen obv regex; "npt=47.969s" -> 47969
            if begin and end:
                b_match = re.match(r'npt=(\d+)\.(\d{3})s$', begin)
                e_match = re.match(r'npt=(\d+)\.(\d{3})s$', end)
    
                if b_match and e_match:
                    b_s, b_ms = map(int, b_match.groups())
                    e_s, e_ms = map(int, e_match.groups())
        
                    beginwaarde = b_s * 1000 + b_ms
                    eindwaarde = e_s * 1000 + e_ms

                    # de beginwaarde mag niet groter dan of gelijk zijn aan de eindwaarde
                    if beginwaarde >= eindwaarde:
                        new_messages.append(f'FOUT! {os.path.basename(smilpad)} id={audio_id} clip-end ({end}) volgt niet op clip-begin ({begin})')

    if new_messages:
        messages.append(new_messages)
    else:
        messages.append("OK. De clip-endwaarde in elke audiotag van smilbestanden is groter dan de clip-beginwaarde.")

# Nagaan of clip-end en clip-begin attributen van opeenvolgende audiotags gelijk zijn aan elkaar binnen een smilbestand
def confirm_smil_clip_continuity(productiefolder_pad, smilpaden):
    new_messages = []

    for smilpad in smilpaden:
        root = ET.parse(smilpad).getroot()
        audio_tags = root.findall(".//audio")
        # audio-data oplijsten zodat ze een index krijgen
        begin = [audio.get('clip-begin') for audio in audio_tags]
        end = [audio.get('clip-end') for audio in audio_tags]
        audio_id = [audio.get('id') for audio in audio_tags]
        # foutmelding geven als beginwaarde niet gelijk is aan eindwaarde van index ervoor
        for i in range(1, len(begin)):
            if begin[i] != end[i-1]:
                new_messages.append(f'FOUT! {os.path.basename(smilpad)} id={audio_id[i]} clip-begin {begin[i]} is niet gelijk aan vorige clip-end {end[i-1]}')
    
    if new_messages:
        messages.append(new_messages)
    else:
        messages.append("OK. De clip-end en clip-begin attributen van opeenvolgende audiotags zijn gelijk aan elkaar binnen een smilbestand.")

# Nagaan wat de afwijking is in seconden tussen de totale speelduur in de NCC en de som van speelduren van de mp3-bestanden.
# Is deze groter dan 2 minuten, dan een waarschuwing.
def confirm_ncc_total_time_vs_mp3_calc_time(productiefolder_pad, root_ncc, namespaces):
    aantal_messages = len(messages)

    # totalTime in metadata van ncc ophalen
    ncc_total_time = root_ncc.find('.//xhtml:meta[@name="ncc:totalTime"]', namespaces).attrib['content']  + '.000'
    ncc_total_time_ms = int(float(convert_time_to_s(ncc_total_time) * 1000))

    # mp3-bestanden oplijsten; speelduur verzamelen, oplijsten en optellen
    mp3_paden = {f for f in Path(productiefolder_pad).rglob('*.mp3')}
    verzamelde_speelduur = [int(float(MP3(mp3_pad).info.length) * 1000) for mp3_pad in mp3_paden]
    totale_speelduur = sum(verzamelde_speelduur)
    # verschil berekenen en beoordelen dmv absolute waarden
    verschil_in_speelduur = (ncc_total_time_ms - totale_speelduur)/1000
    
    if abs(verschil_in_speelduur) > 120:
        messages.append(f"FOUT! Verschil tussen speelduur NCC en som speelduur mp3-bestanden is {abs(verschil_in_speelduur)}s.")
    
    if len(messages) == aantal_messages:
        messages.append(f"OK. Het verschil tussen speelduur NCC en som speelduur mp3-bestanden is {abs(verschil_in_speelduur)}s.")

confirm_time_in_this_smil_equals_seq_dur(PRODUCTIEFOLDERPAD, SMILPADEN)
confirm_last_clip_end_smil_equals_seq_dur(PRODUCTIEFOLDERPAD, SMILPADEN)
confirm_seq_dur_not_bigger_than_size_last_ref_mp3(PRODUCTIEFOLDERPAD, SMILPADEN)
confirm_total_elapsed_time(PRODUCTIEFOLDERPAD, SMILPADEN)
confirm_time_in_this_smil_master(PRODUCTIEFOLDERPAD, SMILPADEN)
confirm_smil_audio_tag_chronology(PRODUCTIEFOLDERPAD, SMILPADEN)
confirm_smil_clip_continuity(PRODUCTIEFOLDERPAD, SMILPADEN)
confirm_ncc_total_time_vs_mp3_calc_time(PRODUCTIEFOLDERPAD, NCC_ROOT, NCC_NAMESPACES)
