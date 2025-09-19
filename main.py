import os

from modules import Validatie_Aanwezigheid, Validatie_Metadata, Validatie_Tijdscontroles, Hulpfuncties
from modules.config import PRODUCTIEFOLDERPAD
from modules.config import FOLDER_SIZE, AANTAL_MP3s, AANTAL_SMILS, AANTAL_HTMLS
from validatierapport import get_luisterpunt_validation_rapport

all_messages = []

def main():
	# Voeg de messages-lijsten van elk script samen
	all_messages.extend(Validatie_Aanwezigheid.messages)
	all_messages.extend(Validatie_Metadata.messages)
	all_messages.extend(Validatie_Tijdscontroles.messages)

	return all_messages

# main-functie alleen uitvoeren als de functie direct vanuit main.py wordt uitgevoerd
if __name__ == "__main__":
    main()

# Variabelen voor de bovenste rij in het validatierapport verzamelen
variables_top = []
variables_top.extend((FOLDER_SIZE, Hulpfuncties.multi_or_monovolume(), AANTAL_MP3s, AANTAL_SMILS, AANTAL_HTMLS))

# Validatierapport samenstellen
get_luisterpunt_validation_rapport(PRODUCTIEFOLDERPAD, all_messages, Validatie_Metadata.messages_top, variables_top)



