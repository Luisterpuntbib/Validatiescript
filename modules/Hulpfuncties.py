import os
from pathlib import Path
import xml.etree.ElementTree as ET
import sys

# hulpvariabelen importeren
from modules.config import PRODUCTIEFOLDERPAD, NCC_ROOT, NCC_NAMESPACES

# hulpfuncties
# paden van smils (behalve master.smil) oplijsten
def get_normal_smil_paths(productiefolder_pad):
    smil_bestanden = list(Path(productiefolder_pad).rglob('*.smil'))
    return [str(path) for path in smil_bestanden if path.name != 'master.smil']

SMILPADEN = get_normal_smil_paths(PRODUCTIEFOLDERPAD)

# tijd in format hh:mm:ss.msmsms wordt msmsmsmsms
def convert_time_to_ms(tijd):
    try:
        h, m, s_ms = tijd.split(':')
        s, ms = s_ms.split('.')
        total_ms = (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)
        return total_ms
    except ValueError as err:
        print(f"Er is een ongeldige tijdwaarde ingevuld: {err}. De tijdwaarde kan niet worden omgezet.", file=sys.stderr)
        sys.exit(1)  # Beëindig het script met een foutcode
    except Exception as e:
        print(f"Er is een onverwachte fout opgetreden: {e}.", file=sys.stderr)
        sys.exit(1)

# tijd in format hh:mm:ss.msmsms wordt ssss.msmsms
def convert_time_to_s(tijd):
    try:
        h, m, s_ms = tijd.split(':')
        s, ms = s_ms.split('.')
        total_s = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        return total_s
    except ValueError as err:
        print(f"Er is een ongeldige tijdwaarde ingevuld: {err}. De tijdwaarde kan niet worden omgezet.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Er is een onverwachte fout opgetreden: {e}.", file=sys.stderr)
        sys.exit(1)

# Multi-/monovolume bepalen (Berekend veld bovenaan het validatierapport)
def multi_or_monovolume(root_ncc=NCC_ROOT, namespaces=NCC_NAMESPACES):
    # Inhoud van hrefs oplijsten uit <a>-elementen in ncc.html
    hrefs = [a.text for a in NCC_ROOT.findall('.//xhtml:a', NCC_NAMESPACES)]
    for href in hrefs:
        if "Dit is een multi volume titel" in href:
            return "Multivolume"
    return "Monovolume"
