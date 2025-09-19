import os
import re

from pathlib import Path
import xml.etree.ElementTree as ET

# hulpfuncties en -variabelen importeren
from modules.Hulpfuncties import SMILPADEN, convert_time_to_ms, multi_or_monovolume
from modules.config import PRODUCTIEFOLDERPAD
from modules.config import NCC_ROOT, NCC_NAMESPACES
from modules.config import FOLDER_SIZE, AANTAL_HTMLS

messages_top = []
messages = []

# Controleren of foldergrootte niet groter is dan 698MiB (op niveau van cd-folder, multivolume heeft dus 698 * aantal cd's)
def confirm_folder_size(productiefolder_pad, folder_size=FOLDER_SIZE):
	if folder_size > 698:
		messages_top.append("FOUT! Foldergrootte is groter dan 698MiB.")
	else:
		messages_top.append(f"OK. Foldergrootte is {folder_size} MB.")

# Controleren of het boek mono- of multivolume is (momenteel is enkel mono gewenst).
def confirm_multi_mono():
	if multi_or_monovolume() == "Monovolume":
		messages_top.append("OK. Het boek is monovolume.")
	else:
		messages_top.append("FOUT! Het boek is multivolume.")

# Controleren of het aantal html-bestanden in de productiefolder exact 1 is (=ncc.html).
def confirm_amount_htmls(productiefolder_pad, amount_htmls=AANTAL_HTMLS):
	if amount_htmls == 1:
		messages_top.append(f"OK. Aantal html-bestanden is 1.")
	else:
		messages_top.append(f"Fout! Aantal html-bestanden is {amount_htmls}.")

# Controleren of het aantal gerapporteerde ncc-elementen in de metadata van de ncc.html overeenkomt met het daadwerkelijke aantal getelde ncc-elementen in de body van de ncc.
def confirm_toc_items(productiefolder_pad, root_ncc, namespaces):
	# aantal toc-items in metadata van ncc ophalen	
	nccs_toc_items = root_ncc.find('.//xhtml:meta[@name="ncc:tocItems"]', namespaces).attrib['content']
	# daadwerkelijke aantal elementen (h1, h2, h3, h4, h5, h6 en span) tellen (range 1,7 = 1tm6)
	calc_toc = sum(len(root_ncc.findall(f'.//xhtml:h{i}', namespaces)) for i in range(1, 7)) + len(root_ncc.findall('.//xhtml:span', namespaces))

	if int(calc_toc) == int(nccs_toc_items):
		messages.append(f'OK - <i>{nccs_toc_items} elementen</i>')
	else:
		messages.append(f'FOUT! Metatag ncc:tocItems = {nccs_toc_items}. Berekend aantal = {calc_toc}')

# Controleren of de headerdiepte (1 tm max 6) in de metadata van de ncc.html overeenkomt met het daadwerkelijke diepste header niveau in de body van de ncc.
def confirm_depth(productiefolder_pad, root_ncc, namespaces):
	# depth in metadata van ncc ophalen
	ncc_depth = root_ncc.find('.//xhtml:meta[@name="ncc:depth"]', namespaces).attrib['content']
	# daadwerkelijke diepte van ncc.html berekenen
	tags = ['h2', 'h3', 'h4', 'h5', 'h6', 'h7']
	calc_depth = next((i + 1 for i, tag in enumerate(tags) if not root_ncc.findall(f'.//xhtml:{tag}', namespaces)), 0)
	
	if int(calc_depth) == int(ncc_depth):
		messages.append(f'OK - <i>{ncc_depth} element(en)</i>')
	else:
		messages.append(f'FOUT! Metatag ncc:depth = {ncc_depth}. Berekend aantal = {calc_depth}')

# Controleren of de totale tijdsduur in de metadata van de ncc.html overeenkomt met de timeInThisSmil waarde van de mastersmil
def confirm_total_time(productiefolder_pad, root_ncc, namespaces):
	# totalTime in metadata van ncc ophalen
	ncc_total_time = root_ncc.find('.//xhtml:meta[@name="ncc:totalTime"]', namespaces).attrib['content']  + '.000'
	# master.smil parsen en timeInThisSmil (totale tijd volgens metadata in master.smil) ophalen
	master_smil_pad = next(Path(productiefolder_pad).rglob('master.smil'))
	root_master_smil = ET.parse(master_smil_pad).getroot()
	master_smil_total_time = root_master_smil.find(".//meta[@name='ncc:timeInThisSmil']").attrib['content']

	# beide totalen omzetten naar milliseconden
	ncc_total_time_ms = convert_time_to_ms(ncc_total_time)
	master_smil_total_time_ms = convert_time_to_ms(master_smil_total_time)
	# absolute verschil tussen beide berekenen
	verschil_ncc_master_smil = abs(ncc_total_time_ms - master_smil_total_time_ms)

	if verschil_ncc_master_smil < 1000:
		messages.append(f'OK - <i>{ncc_total_time[:-4]}</i>')
	else:
		messages.append(f'FOUT! Metatag ncc:totalTime = {ncc_total_time}. timeInThisSmil in master.smil = {master_smil_total_time}. Dit is een verschil van {verschil_ncc_master_smil}ms.')

# Controleren of het aantal pageSpecial in de metadata van de ncc.html overeenkomt met het getelde aantal pageSpecial span-elementen in de ncc-body
def confirm_page_special(productiefolder_pad, root_ncc, namespaces):
	# pageSpecial in metadata van ncc ophalen
	ncc_page_special = root_ncc.find('.//xhtml:meta[@name="ncc:pageSpecial"]', namespaces).attrib['content']
	# daadwerkelijke aantal pageSpecial span-elementen in de ncc-body tellen
	calc_page_special = len(root_ncc.findall('.//xhtml:span[@class="page-special"]', namespaces))

	if int(ncc_page_special) == int(calc_page_special):
		messages.append(f'OK - <i> {ncc_page_special} pagina(\'s)</i>')
	else:
		messages.append(f'FOUT! Metatag ncc:pageSpecial = {ncc_page_special}. Berekend aantal = {calc_page_special}')

# Controleren of het aantal pageFront in de metadata van de ncc.html overeenkomt met het getelde aantal pageFront span-elementen in de ncc-body
def confirm_page_front(productiefolder_pad, root_ncc, namespaces):
	# pageFront in de metadata van de ncc ophalen
	ncc_page_front = root_ncc.find('.//xhtml:meta[@name="ncc:pageFront"]', namespaces).attrib['content']
	# daadwerkelijke aantal pageFront span-elementen in de ncc-body tellen
	calc_page_front = len(root_ncc.findall('.//xhtml:span[@class="page-front"]', namespaces))

	if int(ncc_page_front) == int(calc_page_front):
		messages.append(f'OK - <i>{ncc_page_front} pagina(\'s)</i>')
	else:
		messages.append(f'FOUT! Metatag ncc:pageFront = {ncc_page_front}. Berekend aantal = {calc_page_front}')

# Controleren of het aantal pageNormal in de metadata van de ncc.html overeenkomt met het getelde aantal pageNormal span-elementen in de ncc-body
def confirm_page_normal(productiefolder_pad, root_ncc, namespaces):
	# pageNormal in de metadata van de ncc ophalen
	ncc_page_normal = root_ncc.find('.//xhtml:meta[@name="ncc:pageNormal"]', namespaces).attrib['content']
	# daadwerkelijke aantal pageNormal span-elementen in de ncc-body tellen
	calc_page_normal = len(root_ncc.findall('.//xhtml:span[@class="page-normal"]', namespaces))

	if int(ncc_page_normal) == int(calc_page_normal):
		messages.append(f'OK - <i>{ncc_page_normal} pagina(\'s)</i>')
	else:
		messages.append(f'FOUT! Metatag ncc:pageNormal = {ncc_page_normal}. Berekend aantal = {calc_page_normal}')

# Controleren of het maxPageNormal paginanummer in de metadata van de ncc.html overeenkomt met de innertext van de a-tag bij span elementen in de ncc-body
# <span id="ncc_000006" class="page-normal"><a href="s005.smil#ncc_000006">7</a></span>
# Het gaat om de span a met de hoogste waarde binnen de ncc.html, hier 300
def confirm_max_page_normal(productiefolder_pad, root_ncc, namespaces):
	# maxPageNormal in de metadata van de ncc ophalen
	ncc_max_page_normal = root_ncc.find('.//xhtml:meta[@name="ncc:maxPageNormal"]', namespaces).attrib['content']
	# innertext van de a-tag bij span elementen in de ncc-body tellen (oplijsten en lengte vd lijst nemen) -> niet nodig maar voor de zekerheid bewaren
	# calc_max_page_normal = len(root_ncc.findall('.//xhtml:span', namespaces))
	# lijst alle a-tags op en neem de waarde van de hoogste integer als max_page_normal
	calc_max_page_normal = max([int(element.text) for element in root_ncc.findall('.//xhtml:a', namespaces) if element.text.isdigit()])

	if int(ncc_max_page_normal) == int(calc_max_page_normal):
		messages.append(f'OK - <i>{ncc_max_page_normal} pagina(\'s)</i>')
	else:
		messages.append(f'FOUT! Metatag ncc:maxPageNormal = {ncc_max_page_normal}. Berekend aantal = {calc_max_page_normal}')

# Controleren of het aantal bestanden (ncc:files) in de metadata van de ncc.html overeenkomt met het aantal bestanden in de productiefolder.
def confirm_files(productiefolder_pad, root_ncc, namespaces):
	# aantal bestanden in de metadata van de ncc ophalen
	ncc_file_amount = root_ncc.find('.//xhtml:meta[@name="ncc:files"]', namespaces).attrib['content']
	# daadwerkelijke aantal bestanden in de productiefolder tellen
	productiefolder_file_amount = sum([len(files) for r, d, files in os.walk(productiefolder_pad)])

	if int(ncc_file_amount) == int(productiefolder_file_amount):
		messages.append(f'OK - <i>{ncc_file_amount} bestanden</i>')
	else:
		messages.append(f'FOUT! Metatag ncc:files = {ncc_file_amount}. Aantal bestanden in productiefolder = {productiefolder_file_amount}')

# Controleren of de verplichte velden in de metadata van de ncc.html bestaan en een waarde hebben --> is deze lijst compleet?
def confirm_mandatory_ncc_meta_tags(root_ncc, namespaces):
    tags_to_check = ['dc:creator', 'dc:date', 'dc:format', 'dc:identifier', 'dc:language', 'dc:publisher', 'dc:title',
                    'ncc:charset', 'ncc:pageFront', 'ncc:pageNormal', 'ncc:pageSpecial', "ncc:setInfo"]
    
    for tag_name in tags_to_check:
        # per tag info in de metadata van de ncc.html ophalen
        meta_tag_element = root_ncc.find(f".//xhtml:meta[@name='{tag_name}']", namespaces)
        # controleer of het tag-element bestaat
        if meta_tag_element is None:
            messages.append(f'FOUT! Verplichte metatag {tag_name} bestaat niet')
        # als het element bestaat kunnen we de content uitlezen en checken of die niet leeg is
        else:
            meta_tag = meta_tag_element.attrib.get('content', None)
            if not meta_tag:
                messages.append(f'FOUT! Verplichte metatag {tag_name} bestaat maar heeft geen waarde')
            else:
                messages.append(f'OK - <i>{meta_tag}</i>')

# Controleren of de verplichte velden in de metadata van de master.smil bestaan en een waarde hebben
def confirm_mandatory_smil_meta_tags(productiefolder_pad):
	tags_to_check = ['dc:title', 'dc:format', 'dc:identifier', 'ncc:totalElapsedTime', 'ncc:timeInThisSmil', 'ncc:generator']
	# master.smil parsen
	master_smil_pad = next(Path(productiefolder_pad).rglob('master.smil'))
	root_master_smil = ET.parse(master_smil_pad).getroot()
	
	for tag_name in tags_to_check:
        # per tag info in de metadata van de master.smil ophalen
		master_smil_tag_element = root_master_smil.find(f".//meta[@name='{tag_name}']")
		# controleer of het tag-element bestaat
		if master_smil_tag_element is None:
			messages.append(f'FOUT! Verplichte metatag {tag_name} bestaat niet')
		# als het element bestaat kunnen we de content uitlezen en checken of die niet leeg is
		else:
			master_smil_meta_tag = master_smil_tag_element.attrib.get('content', None)
			# voor dc:format checken of de waarde niet leeg én de juiste is
			if tag_name == 'dc:format':
				if not master_smil_meta_tag or master_smil_meta_tag != "Daisy 2.02":
					messages.append(f'FOUT! Verplichte metatag {tag_name} bestaat maar heeft geen of de verkeerde waarde: {master_smil_meta_tag}')
				else:
					messages.append(f'OK - <i>{master_smil_meta_tag}</i>')
			elif not master_smil_meta_tag:
				messages.append(f'FOUT! Verplichte metatag {tag_name} bestaat maar heeft geen waarde')
			else:
				messages.append(f'OK - <i>{master_smil_meta_tag}</i>')

# Controleren of in iedere smil de text src niet lager is dan voorgaande src-elementen; signaleert waarbij navigatie steeds terugspringt naar hoofdstukniveau
def confirm_smil_text_srcs(smilpaden):
    new_messages = []

    for smilpad in smilpaden:
        smil_name = os.path.basename(smilpad)
        root = ET.parse(smilpad).getroot()
        par_ids = [pars.get('id') for pars in root.findall(".//par")]
        srcs = [texts.get('src') for texts in root.findall(".//text")]
        text_ids = [texts.get('id') for texts in root.findall(".//text")]

        zip_lst = list(zip(par_ids, text_ids, srcs))

        last_correct_value = srcs[0]

        for i in range(1, len(srcs)):
            if srcs[i] < last_correct_value:
                new_messages.append(f"Src-element {srcs[i]}, id={zip_lst[i][1]} van par id={zip_lst[i][0][3:]} in {smil_name} is lager dan voorgaande src-element(en).")
            else:
                last_correct_value = srcs[i]

    if new_messages:
        # Welke fouten is eigenlijk niet zo relevant (zijn er bovendien veel), het is belangrijker om te weten dat ergens in het boek een herstelling moet plaatsvinden.
        # Ik laat daarom hierboven de new_messages-melding staan voor meer details maar hanteer hieronder een generieke foutmelding.
        messages.append(f"FOUT! Er zijn fouten met de text src-elementen, zoals: '{new_messages[0]}'")
    else:
        messages.append("OK. Geen fout met text srcs in de smils.")


confirm_folder_size(PRODUCTIEFOLDERPAD)
confirm_amount_htmls(PRODUCTIEFOLDERPAD)
confirm_multi_mono()
confirm_toc_items(PRODUCTIEFOLDERPAD, NCC_ROOT, NCC_NAMESPACES)
confirm_depth(PRODUCTIEFOLDERPAD, NCC_ROOT, NCC_NAMESPACES)
confirm_total_time(PRODUCTIEFOLDERPAD, NCC_ROOT, NCC_NAMESPACES)
confirm_page_special(PRODUCTIEFOLDERPAD, NCC_ROOT, NCC_NAMESPACES)
confirm_page_front(PRODUCTIEFOLDERPAD, NCC_ROOT, NCC_NAMESPACES)
confirm_page_normal(PRODUCTIEFOLDERPAD, NCC_ROOT, NCC_NAMESPACES)
confirm_max_page_normal(PRODUCTIEFOLDERPAD, NCC_ROOT, NCC_NAMESPACES)
confirm_files(PRODUCTIEFOLDERPAD, NCC_ROOT, NCC_NAMESPACES)
confirm_mandatory_ncc_meta_tags(NCC_ROOT, NCC_NAMESPACES)
confirm_mandatory_smil_meta_tags(PRODUCTIEFOLDERPAD)
confirm_smil_text_srcs(SMILPADEN)

