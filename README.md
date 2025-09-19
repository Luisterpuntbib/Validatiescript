# Validatiescript Luisterpuntbibliotheek

Versie september 2025


## Uitleg

Het validatiescript werd oorspronkelijk in Powershell geschreven door Dries Blanchaert. De bedoeling is om Daisy-boeken te controleren op veelvoorkomende fouten. Het script (in de huidige opzet zijn het eigenlijk meerdere, samenhangende scripts) wordt gebruikt door zowel de productiecentra in Vlaanderen als de (post)productie bij Luisterpunt. De laatste versie van het script is geschreven in Python met als doel om het onderhoud en het toevoegen van nieuwe controlefuncties te vergemakkelijken. Deze versie is nog niet in gebruik bij de productiecentra en de (post)productie bij Luisterpunt.

Het script voert een kleine 50 tests of controlefuncties uit die variëren van simpelweg controleren of de bestandsmap een ncc.html bevat tot technischere controles rondom bijvoorbeeld de audiotags van een boek. Iedere controle komt overeen met een functie in het script, eventueel ondersteund door hulpfuncties. Het resultaat van een functie is een string bestaande uit 'OK' of 'Fout' en een toelichting bij het resultaat. Deze strings worden opgelijst en in het validatierapport gematcht met een bijbehorende vraag (bv. 'Is er een ncc.html aanwezig?'). Het toevoegen van meldingen heeft twee flows: ofwel wordt de melding direct toegevoegd aan de lijst, ofwel bestaat de controle uit meerdere meldingen die worden opgelijst en als 'list of strings' worden toegevoegd aan de resultatenlijst.


Inhoud bestandsmap met scripts:

main.py								verzamelt de lijst met controleresultaten en stuurt het validatierapport aan
validatierapport.py:				normaliseert resultatenlijst, koppelt resultatenlijst aan vraag, stelt validatierapport samen en stuurt dit per mail
requirementments.txt:				oplijsting enkele externe libraries

modules:

init.py: hulpbestand bij modules, bevat verder geen code

config.py: stelt enkele veelgebruikte variabelen vast, waaronder het productiefolderpad

Hulpfuncties.py: bevat enkele hulpfuncties, zoals voor de conversie van uren naar seconden

Validatie_Aanwezigheid.py: validatiefuncties die een productiefolder controleren op aanwezigheid van noodzakelijke bestanden en verwijzingen

Validatie_Metadata.py: validatiefuncties die de vereisten van metadata controleren binnen de productiefolder

Validatie_Tijdscontroles.py: validatiefuncties die een aantal vereisten rondom tijd en verwijzingen controleren


Overige bestanden: 'Overzicht functies.xlsx', oude versies van het Powershellscript en de map 'EAC' met daarin testboeken


## Gebruik

Run main.py om de validatie uit te voeren en het validatierapport te genereren.
Het te valideren boek stel je in door de variabele 'PRODUCTIEFOLDERPAD' in config.py te wijzigen naar het pad.


## Nog toe te toevoegen

Het doel van de eerste Python-versie van het validatiescript was om een werkende versie van het PowerShell-script te maken. Er zijn nog veel mogelijkheden voor verbetering in een twee versie:

- Verder modulair maken van het script zodat gemakkelijker functies toegevoegd/verwijderd kunnen worden, ook in het validatierapport zelf;
- Rapporten kunnen genereren voor meerdere bestandsmappen tegelijk;
- Validatierapport verder opschonen; vragen uit het validatierapport zijn nu losse strings in een lijst die obv positie worden gekoppeld aan de resultatenlijst, dat is zeer onhandig zodra er functies worden toegevoegd of verwijderd;
- OOP waarbij vraag/antwoord-combinatie wordt gegenereerd in de controlefunctie zelf.
