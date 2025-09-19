import os

'''
[22-8-25] de volgorde van de variabelen klopt niet waardoor het resultaat niet aan de juiste test wordt gekoppeld in het gemailde validatierapport
dit komt waarschijnlijk door de nieuwe test die ik later heb toegevoegd aan het metadatatests
hoe dan ook een structurele oplossing vinden zodat nieuwe tests in de toekomst makkelijker ingeintegreerd kunnen worden
'''

def normalize_checks(checks):
    '''Messages afkomstig uit foutmeldingen zijn in veel gevallen een list of strings. Deze functie zet lijsten met één string om naar een string'''
    return [check[0] if isinstance(check, list) and len(check) == 1 else check for check in checks]

def format_check(checks):
    '''Als een check bestaat uit een lijst met meedere meldingen (list of strings), wordt een line break <br> toegevoegd'''
    return ["<br>".join(check) if isinstance(check, list) else check for check in checks]

def get_luisterpunt_validation_rapport(productiefolder_pad, all_messages, messages_top, variables_top):
    # Initialisaties
    checks = normalize_checks(all_messages)

    # CSS-stijl (groen/rood) bepalen voor controles
    css_classes = ["good" if "OK" in check else "bad" for check in checks]
    # CSS-stijl (groen/rood) bepalen voor controles in de bovenste regel van het validatierapport
    css_classes_top = ["good_nowidth" if "OK" in message_top else "bad_nowidth" for message_top in messages_top]

    formatted_checks = format_check(checks)

    table_rows_aanwezigheid = [
        f'<tr><td>ncc.html aanwezig?</td><td class="{css_classes[0]}">{checks[0]}</td></tr>',
        f'<tr><td>master.smil aanwezig?</td><td class="{css_classes[1]}">{checks[1]}</td></tr>',
        f'<tr><td>Zijn alle smilbestanden waarnaar gerefereerd wordt in de master.smil aanwezig in de productiefolder?</td><td class="{css_classes[2]}">{formatted_checks[2]}</td></tr>',
        f'<tr><td>Zijn alle smilbestanden in de productiefolder aanwezig als referenties in de master.smil?</td><td class="{css_classes[3]}">{formatted_checks[3]}</td></tr>'
        f'<tr><td>Zijn alle smilbestanden waarnaar gerefereerd wordt in de ncc.html aanwezig in de productiefolder?</td><td class="{css_classes[4]}">{formatted_checks[4]}</td></tr>',
        f'<tr><td>Zijn alle smilbestanden in de productiefolder aanwezig als referenties in de ncc.html?</td><td class="{css_classes[5]}">{formatted_checks[5]}</td></tr>'
        f'<tr><td>Bestaan de ID\'s in de href attributen van a-tags in de ncc.html in het smil-bestand waarnaar verwezen wordt?</td><td class="{css_classes[12]}">{formatted_checks[12]}</td></tr>'
        f'<tr><td>Zijn alle mp3-sources die vermeld staan in de smil-bestanden aanwezig in de productiefolder?</td><td class="{css_classes[6]}">{formatted_checks[6]}</td></tr>'
        f'<tr><td>Zijn alle mp3-bestanden in de productiefolder minstens 1 keer vermeld als source in 1 van de smilbestanden?</td><td class="{css_classes[7]}">{formatted_checks[7]}</td></tr>'
        f'<tr><td>Hebben alle mp3-bestanden een bitrate van 64kbps?</td><td class="{css_classes[8]}">{formatted_checks[8]}</td></tr>'
        f'<tr><td>Zit er tussen de mp3-bestanden in de productiefolder minstens 1 bestand die een naam bevat typisch voor een disclaimer?</td><td class="{css_classes[9]}">{formatted_checks[9]}</td></tr>'
        f'<tr><td>Zitten er in de productiefolder bestanden die niet thuishoren in een Daisy-boek?</td><td class="{css_classes[10]}">{formatted_checks[10]}</td></tr>'
        f'<tr><td>Is de opzet van het previewbestand oke?</td><td class="{css_classes[11]}">{formatted_checks[11]}</td></tr>'
    ]

    table_rows_metadata_ncc = [
        f'<tr><td>aantal ncc-elementen in metadata ncc.html = aantal getelde ncc-elementen in ncc-body?</td><td class="{css_classes[13]}">{formatted_checks[13]}</td></tr>'
        f'<tr><td>headerdiepte (1 t.e.m. max 6) in metadata van de ncc.html = diepste header niveau in ncc-body?</td><td class="{css_classes[14]}">{formatted_checks[14]}</td></tr>'
        f'<tr><td>totale tijdsduur in metadata van ncc.html = timeInThisSmil van mastersmil?</td><td class="{css_classes[15]}">{formatted_checks[15]}</td></tr>'
        f'<tr><td>aantal pageSpecial in metadata van ncc.html = geteld aantal pageSpecial span-elementen in ncc-body?</td><td class="{css_classes[16]}">{formatted_checks[16]}</td></tr>'
        f'<tr><td>aantal pageFront in metadata van ncc.html = geteld aantal pageFront span-elementen in ncc-body?</td><td class="{css_classes[17]}">{formatted_checks[17]}</td></tr>'
        f'<tr><td>aantal pageNormal in metadata van ncc.html = geteld aantal pageNormal span-elementen in ncc-body?</td><td class="{css_classes[18]}">{formatted_checks[18]}</td></tr>'
        f'<tr><td>MaxPageNormal paginanummer in metadata van ncc.html = innertext van de a-tag bij span elementen in ncc-body?</td><td class="{css_classes[19]}">{formatted_checks[19]}</td></tr>'
        f'<tr><td>Aantal bestanden (ncc:files) in metadata van ncc.html = aantal bestanden in productiefolder?</td><td class="{css_classes[20]}">{formatted_checks[20]}</td></tr>'
        f'<tr><td>dc:creator</td><td class="{css_classes[21]}">{formatted_checks[21]}</td></tr>'
        f'<tr><td>dc:date</td><td class="{css_classes[22]}">{formatted_checks[22]}</td></tr>'
        f'<tr><td>dc:format</td><td class="{css_classes[23]}">{formatted_checks[23]}</td></tr>'
        f'<tr><td>dc:identifier</td><td class="{css_classes[24]}">{formatted_checks[24]}</td></tr>'
        f'<tr><td>dc:language</td><td class="{css_classes[25]}">{formatted_checks[25]}</td></tr>'
        f'<tr><td>dc:publisher</td><td class="{css_classes[26]}">{formatted_checks[26]}</td></tr>'
        f'<tr><td>dc:title</td><td class="{css_classes[27]}">{formatted_checks[27]}</td></tr>'
        f'<tr><td>ncc:charset</td><td class="{css_classes[28]}">{formatted_checks[28]}</td></tr>'
        f'<tr><td>ncc:pageFront</td><td class="{css_classes[29]}">{formatted_checks[29]}</td></tr>'
        f'<tr><td>ncc:pageNormal</td><td class="{css_classes[30]}">{formatted_checks[30]}</td></tr>'
        f'<tr><td>ncc:pageSpecial</td><td class="{css_classes[31]}">{formatted_checks[31]}</td></tr>'
        f'<tr><td>ncc:setInfo</td><td class="{css_classes[32]}">{formatted_checks[32]}</td></tr>'
        f'<tr><td>Text src-elementen in smils zijn niet kleiner dan voorgaand src-element</td><td class="{css_classes[39]}">{formatted_checks[39]}</td></tr>'
    ]

    table_rows_metadata_smil = [
        f'<tr><td>dc:title</td><td class="{css_classes[33]}">{formatted_checks[33]}</td></tr>'
        f'<tr><td>dc:format</td><td class="{css_classes[34]}">{formatted_checks[34]}</td></tr>'
        f'<tr><td>dc:identifier</td><td class="{css_classes[35]}">{formatted_checks[35]}</td></tr>'
        f'<tr><td>ncc:totalElapsedTime</td><td class="{css_classes[36]}">{formatted_checks[36]}</td></tr>'
        f'<tr><td>ncc:timeInThisSmil</td><td class="{css_classes[37]}">{formatted_checks[37]}</td></tr>'
        f'<tr><td>ncc:generator</td><td class="{css_classes[38]}">{formatted_checks[38]}</td></tr>'
    ]

    table_rows_tijdscontroles = [
        f'<tr><td>totalElapsedTime in headers smilbestanden = totalElapsedTime van vorige smilbestand + vorige timeInThisSmil?</td><td class="{css_classes[43]}">{formatted_checks[43]}</td></tr>'
        f'<tr><td>smilbestanden: clip-end audiotag > clip-begin audiotag?</td><td class="{css_classes[45]}">{formatted_checks[45]}</td></tr>'
        f'<tr><td>smilbestanden: clip-end vorige audiotag = clip-begin huidige audiotag?</td><td class="{css_classes[46]}">{formatted_checks[46]}</td></tr>'
        f'<tr><td>seq_dur in smil-body = ncc:timeInThisSmil header smilbestand?</td><td class="{css_classes[40]}">{formatted_checks[40]}</td></tr>'
        f'<tr><td>timeInThisSmil header master.smil = totalElapsedTime laatste smilbestand in productiefolder? (alfanumerieke sortering)</td><td class="{css_classes[44]}">{formatted_checks[44]}</td></tr>'
        f'<tr><td>seq_dur = tijdswaarde clip-end laatste audiotag smil?</td><td class="{css_classes[41]}">{formatted_checks[41]}</td></tr>'
        f'<tr><td>seq_dur niet groter dan speelduur laatst gerefereerde mp3?</td><td class="{css_classes[42]}">{formatted_checks[42]}</td></tr>'
        f'<tr><td>Is totaltime in NCC verschillend van som speelduur mp3\'s?</td><td class="{css_classes[47]}">{formatted_checks[47]}</td></tr>'
    ]

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
    .body {{
        font-family: Arial, sans-serif;
    }}
    .good {{
        background-color: #ebffeb;
        color: green;
        width: 70%;
    }}
    .good_nowidth {{
        background-color: #ebffeb;
        color: green;
    }}
    .bad {{
        background-color: #ffe6e6;
        color: red; 
        width: 70% 
    }}
    .bad_nowidth {{
        background-color: #ffe6e6;
        color: red; 
    }}
    .warning {{
        background-color: #ffe5c7;
        color: #a15b00;
        width: 70%    
    }}
    table {{
        border: 1px solid black;
        border-collapse: collapse;
        width: 100%;
    }}
    td, th {{
        border: 1px solid black;
        padding: 5px;
    }}
    .title {{
        font-size: 24px;
        color: #007a9c;
    }}
    </style>
    </head>
    <body>
    <h1>Validatierapport boeknummer {productiefolder_pad.split("/", -1)[-2]}</h1>
    <p class="title"><b>{formatted_checks[27].split(" ", 2)[-1]}</b> door <b>{formatted_checks[21].split(" ", 2)[-1]}</b></p>
    <p>Locatie productiefolder: {productiefolder_pad}</p>
    <table>
    <tr><th>Foldergrootte</th><th>Multivolume</th><th>#mp3</th><th>#smil</th><th>#html</th></tr>
    <tr><td class="{css_classes_top[0]}">{variables_top[0]} MB</td><td class="{css_classes_top[2]}">{variables_top[1]}</td>
    <td>{variables_top[2]}</td><td>{variables_top[3]}</td><td class="{css_classes_top[1]}">{variables_top[4]}</td></tr>
    </table>
    <h2>Integriteit bestanden</h2>
    <table>
    <tr><th>Controle</th><th>Resultaat</th></tr>
    {''.join(table_rows_aanwezigheid)}
    </table>
    <h2>Metadata ncc.html</h2>
    <table>
    <tr><th>Controle</th><th>Resultaat</th></tr>
    {''.join(table_rows_metadata_ncc)}
    </table>
    <h2>Metadata smil-bestanden</h2>
    <table>
    <tr><th>Controle</th><th>Resultaat</th></tr>
    {''.join(table_rows_metadata_smil)}
    </table>
    <h2>Tijdscontroles</h2>
    <table>
    <tr><th>Controle</th><th>Resultaat</th></tr>
    {''.join(table_rows_tijdscontroles)}
    </table>
    </body>
    </html>
    """

    send_mail_message(
        from_addr="ict@luisterpunt.be",
        to_addr="jurrian.kooiman@luisterpuntbibliotheek.be",
        subject="Validatierapport",
        body=html,
        smtp_server='smtp.office365.com'
    )

def send_mail_message(from_addr, to_addr, subject, body, smtp_server):
    '''Mail componenten invullen en verzenden (functie wordt aangeroepen binnen get_luisterpunt_validation_rapport)'''
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')

    if not smtp_user or not smtp_pass:
        raise ValueError("SMTP-gebruikersnaam of -wachtwoord werd niet gevonden in omgevingsvariabelen.")

    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP(smtp_server, 587) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        print(f"Het validatierapport is verstuurd naar {to_addr}")