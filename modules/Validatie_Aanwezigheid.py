import os
import re

from pathlib import Path
import xml.etree.ElementTree as ET
from mutagen.mp3 import MP3
from fuzzywuzzy import fuzz

# hulpfuncties en -variabelen importeren
from modules.Hulpfuncties import SMILPADEN
from modules.config import PRODUCTIEFOLDERPAD
from modules.config import NCC_ROOT, NCC_NAMESPACES #--> alleen nog geïmplementeerd bij laatste functie
# from modules.config import NCCPATH


messages = []

# Is ncc.html aanwezig in de productiefolder?
def find_ncc_html(productiefolder_pad):
    for path in Path(productiefolder_pad).rglob('*.html'):
        if path.name == 'ncc.html':
            messages.append('OK. Ncc.html is aanwezig.')
            # toevoeging van break: verlaat loop zodra bestand is gevonden, geen verdere bestanden worden gecontroleerd
            break
    else:
        messages.append('ncc.html is niet aanwezig')

# Is master.smil aanwezig in de productiefolder?
def find_master_smil(productiefolder_pad):
    for path in Path(productiefolder_pad).rglob('*.smil'):
        if path.name == 'master.smil':
            messages.append('OK. Master.smil is aanwezig.')
            break
    else:
        messages.append('master.smil is niet aanwezig')

# Zijn alle smilbestanden waarnaar gerefereerd wordt in de master.smil aanwezig in de productiefolder?
def find_master_smil_refs(productiefolder_pad):
    new_messages = []
    # Reflijst uit master.smil samenstellen
    try:
        # zoeken naar de eerstvolgende master.smil binnen productiefolder_pad en xml parsen
        mastersmil_pad = next(Path(productiefolder_pad).rglob('master.smil'))
        mastersmil_data = ET.parse(mastersmil_pad).getroot()
        # alle smils oplijsten door src-attributen uit ref-elementen te halen
        smil_refs = [ref.attrib["src"] for ref in mastersmil_data.findall(".//ref")]
    except StopIteration:
        messages.append('master.smil is niet aanwezig') # error als er geen master-smil wordt gevonden
        return messages

    # Vergelijking met smilbestanden in productiefolder
    smil_bestanden = list(Path(productiefolder_pad).rglob('*.smil'))
    # dit stukje stond in Dries' code: haalt in smil.refs bij bv s001.smil#extra_info alles vanaf de # weg
    # --> vragen aan Tom of/wanneer dit voorkomt
    for ref in smil_refs:
        ref = ref.split('#')[0]
        found = False
        for smil_bestand in smil_bestanden:
            if smil_bestand.name.endswith('.smil') and smil_bestand.name != 'master.smil':
                if ref == smil_bestand.name:
                    found = True
                    break
        if not found:
            new_messages.append(f"FOUT! Referentie {ref} uit master.smil is onvindbaar in productiefolder.")

    if new_messages:
        messages.append(new_messages)
    else:
        messages.append("OK. Alle smilbestanden waarnaar gerefereerd wordt in de master.smil zijn aanwezig in de productiefolder.")

# Zijn alle smilbestanden in de productiefolder aanwezig als referenties in de master.smil?
def find_smil_in_master_smil_refs(productiefolder_pad):
    new_messages = []
    # Reflijst uit master.smil samenstellen
    try:
        # zoeken naar de eerstvolgende master.smil binnen productiefolder_pad en xml parsen
        mastersmil_pad = next(Path(productiefolder_pad).rglob('master.smil'))
        mastersmil_data = ET.parse(mastersmil_pad).getroot()
        # alle smils oplijsten door src-attributen uit ref-elementen te halen
        smil_refs = [ref.attrib["src"] for ref in mastersmil_data.findall(".//ref")]      
    except StopIteration:
        messages.append('master.smil is niet aanwezig') # error als er geen master-smil wordt gevonden
        return messages

    # Smilbestanden in productiefolder opzoeken in reflijst
    smil_bestanden = list(Path(productiefolder_pad).rglob('*.smil'))
    for smil_bestand in smil_bestanden:
        if smil_bestand.name.endswith('.smil') and smil_bestand.name != 'master.smil':
            # dit stukje stond in Dries' code: haalt in smil.refs bij bv s001.smil#extra_info alles vanaf de # weg
            # --> vragen aan Tom of/wanneer dit voorkomt
            found = False
            for ref in smil_refs:
                ref = ref.split('#')[0]
                if smil_bestand.name == ref:
                    found = True
                    break
            if not found:
                new_messages.append(f"FOUT! Smilbestand {smil_bestand.name} in productiefolder is onvindbaar als referentie in master.smil.")

    if new_messages:
        messages.append(new_messages)
    else:
        messages.append("OK. Alle smilbestanden in de productiefolder zijn aanwezig als referenties in de master.smil.")

# Zijn alle smilbestanden waarnaar gerefereerd wordt in de ncc.html aanwezig in de productiefolder?
def find_ncc_html_hrefs(productiefolder_pad):
    new_messages = []
    # Reflijst uit ncc.html samenstellen
    try:
    # zoeken naar de eerstvolgende ncc.html binnen productiefolder_pad en xml parsen
        ncchtml_pad = next(Path(productiefolder_pad).rglob('ncc.html'))
        ncchtml_data = ET.parse(ncchtml_pad).getroot()
        # Hrefs oplijsten uit <a>-elementen in ncc.html, namespace expliciet gedefinieerd (dict aan het einde)
        smil_hrefs = [a.get('href').split('#')[0] for a in ncchtml_data.findall('.//xhtml:a', {'xhtml': 'http://www.w3.org/1999/xhtml'})]
        # Alleen unieke waarden oplijsten
        smil_hrefs = list(dict.fromkeys(smil_hrefs))
    except StopIteration:
        messages.append('ncc.html is niet aanwezig') # error als er geen master-smil wordt gevonden
        return messages

    # Smilbestanden in productiefolder oplijsten en vergelijken met hreflijst
    smil_bestanden = [f.name for f in Path(productiefolder_pad).rglob('*.smil') if f.name.lower() != 'master.smil']
    for href in smil_hrefs:
        if href not in smil_bestanden:
            new_messages.append(f"FOUT! Referentie {href} uit ncc.html is onvindbaar in productiefolder.")
    
    if new_messages:
        messages.append(new_messages)
    else:
        messages.append("OK. Alle smilbestanden waarnaar gerefereerd wordt in de ncc.html zijn aanwezig in de productiefolder.")

# Zijn alle smilbestanden in de productiefolder aanwezig als referenties in de ncc.html?
def find_smil_in_ncc_html_hrefs(productiefolder_pad):
    new_messages = []
    # Reflijst uit ncc.html samenstellen
    try:
    # zoeken naar de eerstvolgende ncc.html binnen productiefolder_pad en xml parsen
        ncchtml_pad = next(Path(productiefolder_pad).rglob('ncc.html'))
        ncchtml_data = ET.parse(ncchtml_pad).getroot()
        # Hrefs oplijsten uit <a>-elementen in ncc.html, namespace expliciet gedefinieerd (dict aan het einde)
        smil_hrefs = [a.get('href').split('#')[0] for a in ncchtml_data.findall('.//xhtml:a', {'xhtml': 'http://www.w3.org/1999/xhtml'})]
        # Alleen unieke waarden oplijsten
        smil_hrefs = list(dict.fromkeys(smil_hrefs))
    except StopIteration:
        messages.append('ncc.html is niet aanwezig') # error als er geen master-smil wordt gevonden
        return messages

    # Smilbestanden in productiefolder oplijsten en vergelijken met hreflijst
    smil_bestanden = [f.name for f in Path(productiefolder_pad).rglob('*.smil') if f.name.lower() != 'master.smil']
    for smil_bestand in smil_bestanden:
        if smil_bestand not in smil_hrefs:
            new_messages.append(f"FOUT! Smilbestand {smil_bestand} in productiefolder is onvindbaar als referentie in ncc.html.")
    
    if new_messages:
        messages.append(new_messages)
    else:
        messages.append("OK. Alle smilbestanden in de productiefolder zijn aanwezig als referenties in de ncc.html.")

# Zijn alle mp3-sources die vermeld staan in de smil-bestanden aanwezig in de productiefolder?
def find_smil_mp3_sources(productiefolder_pad):
    new_messages = []
    # Verzamel alle smilbestanden die niet master.smil zijn
    smil_paden = [f for f in Path(productiefolder_pad).rglob('*.smil') if f.name.lower() != 'master.smil']
    smil_namen = [f.name for f in smil_paden]
    # Verzamel alle unieke mp3-sources in smilbestanden die niet master.smil zijn
    unieke_mp3s = set()
    smil_bestand_bronnen = {}

    for smilpad in smil_paden:
        try:
            root = ET.parse(smilpad).getroot()
            mp3s = [audio.get('src') for audio in root.findall(".//audio")]
            # unieke mp3's in smils toevoegen aan set, incl bijbehorende smil
            for mp3 in mp3s:
                if mp3 not in unieke_mp3s:
                    unieke_mp3s.add(mp3)
                    smil_bestand_bronnen[mp3] = smilpad.name
        except ET.ParseError:
            messages.append(f'FOUT! Kan {smilpad} niet parsen.')

    # Vergelijk unieke mp3's met mp3's in productiefolder
    mp3s_productiefolder = {f.name for f in Path(productiefolder_pad).rglob('*.mp3')}
    for unieke_mp3 in unieke_mp3s:
        if unieke_mp3 not in mp3s_productiefolder:
            new_messages.append(f'FOUT! Mp3-source {unieke_mp3} uit smilbestand {smil_bestand_bronnen[unieke_mp3]} werd niet gevonden in de productiefolder.')

    if new_messages:
        messages.append(new_messages)
    else:
        messages.append("OK. De mp3-sources die vermeld staan in de smil-bestanden zijn aanwezig in de productiefolder.")

# Zijn alle mp3-bestanden in de productiefolder minstens één keer vermeld als source in één van de smilbestanden?
def find_mp3_in_smil_mp3_sources(productiefolder_pad):
    new_messages = []
    # Oplijsten mp3-bestanden in de productiefolder
    mp3s_productiefolder = {f.name for f in Path(productiefolder_pad).rglob('*.mp3')}
    # Verzamel alle smilbestanden die niet master.smil zijn
    smil_paden = [f for f in Path(productiefolder_pad).rglob('*.smil') if f.name.lower() != 'master.smil']
    
    # Verzamel alle unieke mp3-sources in smilbestanden die niet master.smil zijn
    unieke_mp3s = set()
    for smilpad in smil_paden:
        try:
            root = ET.parse(smilpad).getroot()
            mp3s = [audio.get('src') for audio in root.findall(".//audio")]
            # unieke mp3's in smils toevoegen aan set, incl bijbehorende smil
            for mp3 in mp3s:
                if mp3 not in unieke_mp3s:
                    unieke_mp3s.add(mp3)
        except ET.ParseError:
            messages.append(f'FOUT! Kan {smilpad} niet parsen.')

    # Check voor alle mp3-bestanden in de productiefolder of ze voorkomen bij de unieke mp3's
    for mp3_productiefolder in mp3s_productiefolder:
        if mp3_productiefolder not in unieke_mp3s:
            new_messages.append(f'FOUT! {mp3_productiefolder} wordt in geen enkel smilbestand opgegeven als source.')

    if new_messages:
        messages.append(new_messages)
    else:
        messages.append("OK. Alle mp3-bestanden in de productiefolder zijn minstens één keer vermeld als source in één van de smilbestanden.")

# Hebben alle mp3-bestanden in de productiefolder de gewenste audioparameters?
# Bitrate: 64kbps / frequentie: 22.050Hz / kanaal: mono
def find_mp3_parameters(productiefolder_pad):
    new_messages = []
    # Oplijsten mp3-bestanden in de productiefolder
    mp3s_productiefolder = {f for f in Path(productiefolder_pad).rglob('*.mp3')}

    # Bitrates, frequenties en kanalen controleren
    for mp3_productiefolder in mp3s_productiefolder:
        audio = MP3(mp3_productiefolder)
        afwijkingen = []
        if audio.info.bitrate // 1000 != 64: # checken of bitrate 64kbps is
            afwijkingen.append(f"bitrate van {audio.info.bitrate // 1000}kbps")
        if audio.info.sample_rate != 22050: # checken of frequentie/sample rate 22.050Hz is
            afwijkingen.append(f"frequentie van {audio.info.sample_rate}Hz")
        if audio.info.channels != 1: # checken of kanaal mono is
            afwijkingen.append(f"{audio.info.channels} kanalen")
        if afwijkingen:
            new_messages.append(f'<a class="warning" href="{mp3_productiefolder}">{mp3_productiefolder}</a> heeft een afwijkende {", ".join(afwijkingen)}')
    
    if new_messages:
        messages.append(new_messages)
    else:
        messages.append("OK. Alle mp3-bestanden in de productiefolder hebben de gewenste audioparameters.")

# Zit er tussen de mp3-bestanden in de productiefolder minstens 1 bestand die een naam bevat typisch voor een disclaimer?
def find_separate_disclaimer_mp3_file(productiefolder_pad):
    # Oplijsten termenlijst voor disclaimers
    disclaimer_lijst = [
        'Productgegevens', 'productgegevens', 'producentgegevens', 'Gegevens gesproken boek',
        'Producent Informatie', 'Prod_gegevens', 'Prod. gegevens', 'producent_gegevens',
        'producent gegevens', 'Producentgegevns', 'producent_gegevens', 'Producentgegegevens',
        'Producentgegvens', 'Produktgegevens', 'bibliotheekgegevens'
    ]

    # Oplijsten mp3-bestanden in de productiefolder
    mp3s_productiefolder = {f.name for f in Path(productiefolder_pad).rglob('*.mp3')}

    # Vergelijking
    found_disclaimer = False
    for mp3_productiefolder in mp3s_productiefolder:
        for disclaimer in disclaimer_lijst:
            # matching op basis van voorkomen van string: bibliotheekgegevens=OK, azerbibliotheekgegevens=OK, bibliotheekazergegevens=niet OK
            # fuzzy string matching toegevoegd: deze woorden inclusief afgeleiden zijn OK
            # Het is ok als een bestandsnaam een fout bevat en het bestand in orde is. Match tussen bestandsnaam en smil-bestand wordt gecheckt in find_smil_mp3_sources en find_mp3_in_smil_mp3_sources
            if fuzz.partial_ratio(disclaimer.lower(), mp3_productiefolder.lower()) > 80:
                messages.append(f"OK. {mp3_productiefolder} wordt herkend als een afzonderlijke disclaimer-mp3.")
                found_disclaimer = True
                break
        if found_disclaimer:
            break

    if not found_disclaimer:
        messages.append(f'FOUT! Er is geen afzonderlijke disclaimer-mp3 herkend.')

# Zit er tussen de bestanden in de productiefolder bestanden die niet thuishoren in een Daisy-boek?
def find_foreign_files(productiefolder_pad):
    new_messages = []
    # Bestanden ophalen en controleren op extensie
    bestanden = [f.name for f in Path(productiefolder_pad).rglob('*') if f.is_file()]
    for bestand in bestanden:
        if bestand.endswith(('.mp3', '.smil', '.html')): # or bestand.endswith('.smil') or bestand.endswith('.html'):
            continue
        else:
            new_messages.append(f'FOUT! <a class="bad" href="{os.path.join(productiefolder_pad, bestand)}">{bestand}</a>')

    if new_messages:
        messages.append(new_messages)
    else:
        messages.append("OK. De productiefolder bevat geen bestanden die niet thuishoren in een Daisy-boek.")

# Preview-analyse
def find_preview(productiefolder_pad):
    aantal_messages = len(messages)
    # Bevat de naam van de subfolder de term 'preview'?
    preview_folders = [entry for entry in Path(productiefolder_pad).rglob('*preview*') if entry.is_dir()]
    # Is er één en slechts één subfolder aanwezig?
    if len(preview_folders) != 1:
        messages.append("FOUT! Er werd geen subfolder gevonden voor previews." if len(preview_folders) == 0 else "FOUT! Er werden meerdere subfolders gevonden.")
    else:
        bestanden = [entry for entry in os.scandir(str(preview_folders[0])) if entry.is_file()]
        # Bevat de subfolder één en slechts één bestand? Is het bestand een mp3 bestand?
        if len(bestanden) != 1:
            messages.append("FOUT! Er werd geen bestand gevonden in de previewfolder." if len(bestanden) == 0 else "FOUT! Er werd meerdere bestanden gevonden in de previewfolder.")
        else:
            bestand = bestanden[0]
            _, ext = os.path.splitext(bestand.name) # extensie extraheren
            if ext not in {'.mp3', '.wav'}:
                messages.append("FOUT! De subfolder bevat geen compatibel audiobestand.")
            else:
                speelduur_preview_ms = 0
                if ext == '.mp3':
                    with open(bestand.path, 'rb') as audio_file:
                        audio = MP3(audio_file)
                        speelduur_preview_ms = int(audio.info.length * 1000)
                # Speelduur controleren: is de speelduur van het bestand tussen de 30 seconden en 5 minuten?
                if speelduur_preview_ms < 30000 and speelduur_preview_ms != 0:
                    messages.append("FOUT! De speelduur van de preview is kleiner dan 30 seconden.")
                elif speelduur_preview_ms > 300000:
                    messages.append("FOUT! De speelduur van de preview is groter dan 5 minuten.")
                elif ext == '.wav':
                    messages.append("FOUT! WAV-bestand. Speelduur kan niet berekend worden.")
    if len(messages) == aantal_messages:
        messages.append("OK. De preview is in orde.")

# Bestaan de ID's in de href attributen van a-tags in de ncc.html in het smil-bestand waarnaar verwezen wordt?
def find_ncc_href_in_smil_src(productiefolder_pad, root_ncc, namespaces):
    new_messages = []
    # Parse de ncc.html om alle href-attributen te vinden
    # hrefs = [a.get('href') for a in root_ncc.findall('.//a', namespaces)]
    ncc_hrefs = [a.get('href') for a in root_ncc.findall('.//xhtml:a', namespaces)]
    paginanrs = [a.text for a in root_ncc.findall('.//xhtml:a', namespaces)]
    # Maak een lijst van ID's uit de smil-bestanden
    ids = [f"{os.path.basename(pad)}#{text.get('id')}" for pad in SMILPADEN for text in ET.parse(pad).findall('.//text')]

    # Controleer of elke href in de ncc.html overeenkomt met een ID in de smil-bestanden, voeg paginanr en smilbestand toe als een referentie ontbreekt
    for i, href in enumerate(ncc_hrefs):
        paginanr = paginanrs[i]
        if href not in ids:
            smilfile = href.split('#')[0]
            new_messages.append(f"Referentie {href}, pagina {paginanr} in de ncc.html werd niet gevonden in {smilfile}.")

    if new_messages:
        messages.append(new_messages)
    else:
        messages.append("OK. Alle ID's in de href attributen van a-tags in de ncc.html bestaan in het smil-bestand waarnaar verwezen wordt.")

find_ncc_html(PRODUCTIEFOLDERPAD)
find_master_smil(PRODUCTIEFOLDERPAD)
find_master_smil_refs(PRODUCTIEFOLDERPAD)
find_smil_in_master_smil_refs(PRODUCTIEFOLDERPAD)
find_ncc_html_hrefs(PRODUCTIEFOLDERPAD)
find_smil_in_ncc_html_hrefs(PRODUCTIEFOLDERPAD)
find_smil_mp3_sources(PRODUCTIEFOLDERPAD)
find_mp3_in_smil_mp3_sources(PRODUCTIEFOLDERPAD)
find_mp3_parameters(PRODUCTIEFOLDERPAD)
find_separate_disclaimer_mp3_file(PRODUCTIEFOLDERPAD)
find_foreign_files(PRODUCTIEFOLDERPAD)
find_preview(PRODUCTIEFOLDERPAD)
find_ncc_href_in_smil_src(PRODUCTIEFOLDERPAD, NCC_ROOT, NCC_NAMESPACES)
