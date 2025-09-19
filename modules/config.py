from pathlib import Path
import xml.etree.ElementTree as ET

# Configuatievariabelen
PRODUCTIEFOLDERPAD = ""

# Hulpvariabelen voor ncc.html
NCCPATH = next(Path(PRODUCTIEFOLDERPAD).rglob('ncc.html'))
NCC_ROOT = ET.parse(NCCPATH).getroot()
NCC_NAMESPACES = {'xhtml': 'http://www.w3.org/1999/xhtml'}

# Berekende velden bovenaan het validatierapport
FOLDER_SIZE = round(sum(file.stat().st_size for file in Path(PRODUCTIEFOLDERPAD).rglob('*'))/1024 ** 2, 2)

AANTAL_MP3s = len(list(Path(PRODUCTIEFOLDERPAD).rglob('*.mp3')))
AANTAL_SMILS = len(list(Path(PRODUCTIEFOLDERPAD).rglob('*.smil')))
AANTAL_HTMLS = len(list(Path(PRODUCTIEFOLDERPAD).rglob('*.html')))
