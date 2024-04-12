from cmath import nan
from operator import contains
import string
from reader import lees_invoerbestand, lees_uitvoerhtml, lees_illustratiepunten, lees_ofl
from pathlib import Path
import os
import pandas as pd


hydra_werkmap = r"C:\MyPrograms\Hydra-NL_KP_ZSS\werkmap"
okader_norm_csv = pd.read_csv(r"D:\Users\BADD\Desktop\KP ZSS\Vakken_OKADER_norm_csv_v2.csv")
df_hydra_definition = pd.read_csv(r"D:\Users\BADD\Desktop\KP ZSS\OKADER_FC_Hydra_attributes.csv")

# toevoegen orientatie dijknormaal

hydra_results = {
    'OKADER VakId':[], 
    'Uitvoerbestand':[], 
    'Terugkeertijd':[], 
    'q [m3/s/m]':[], 
    'ZSS-scenario':[], 
    'HYD_location_name':[], 
    'HYD_location_X':[], 
    'HYD_location_Y':[], 
    'Profiel':[],
    'HBN [m+NAP]':[], 
    'Zeewaterstand [m+NAP]':[], 
    'windsnelheid [m/s]':[], 
    'h, teen [m+NAP]': [], 
    'Hm0, teen [m]':[], 
    'Tm-1.0, ts':[], 
    'golfrichting [graden]':[], 
    'windrichting [graden N]':[], 
    'bijdrage ov. freq [%]':[]}


for folder in os.listdir(hydra_werkmap):

    # geïnteresseerd in de data van generieke database-namen
    string_to_match = ["Westerschelde", "Waddenzee"]

    for substring in string_to_match:
        if substring in folder:

            #zoek naar folders met string_to_match
            for root, dirs, files in os.walk(os.path.join(hydra_werkmap, folder)):
                for file in files:
                    # print(folder)
                    # op basis van invoer.hyd de eerste kolommen vullen van output
                    if file.endswith('invoer.hyd'):
                        location_invoer = os.path.join(root, file)
                        invoer, terugkeertijden = lees_invoerbestand(location_invoer)
                        

                        # path van profiel staat in invoer, strip tot naam profiel
                        profielpath = invoer['algemeen']['PROFIEL']
                        valueprofiel = profielpath.split("\\")[-1]
                        valueprofiel = valueprofiel[:-1]
                        value = valueprofiel.split(".")[0]

                        hydra_results['OKADER VakId'].append(value)
                        hydra_results['q [m3/s/m]'].append(invoer['criterium']['QCR'])
                        hydra_results['Uitvoerbestand'].append(invoer['algemeen']['UITVOERBESTAND'])
                        hydra_results['ZSS-scenario'].append(invoer['algemeen']['SCENARIONAAM'])
                        hydra_results['HYD_location_name'].append(invoer['algemeen']['LOCATIE'])
                        hydra_results['HYD_location_X'].append(invoer['algemeen']['XCOORDINAAT'])
                        hydra_results['HYD_location_Y'].append(invoer['algemeen']['YCOORDINAAT'])
                        hydra_results['Profiel'].append(valueprofiel)
                        
                        # haal ondergrens norm op uit de shapefile
                        for i in range(len(okader_norm_csv['VakId'])):
                            if okader_norm_csv['VakId'].loc[i] == int(value):
                                req_terugkeertijd = okader_norm_csv['V2_NORM_OG'].loc[i]


                    # op basis van uitvoer de andere kolommen vullen van dataframe
                    elif file.endswith('uitvoer.html'):
                        location_uitvoer = os.path.join(root, file)
                        tekst = lees_uitvoerhtml(location_uitvoer)
                        cips, ip = lees_illustratiepunten(tekst)
                        ofl = lees_ofl(tekst)
                        hydra_results['Terugkeertijd'].append(req_terugkeertijd)

                        # in dezelfde map data ophalen van berekeningen afhankelijk van norm geldend bij Okader VakID
                        hydra_results['HBN [m+NAP]'].append(ofl['hoogte'].loc[[req_terugkeertijd][0]])
                        hydra_results['Zeewaterstand [m+NAP]'].append(ip['zeews. m+NAP'].loc[[req_terugkeertijd][0]])
                        hydra_results['windsnelheid [m/s]'].append(ip['windsn. m/s'].loc[[req_terugkeertijd][0]])
                        hydra_results['h, teen [m+NAP]'].append(ip['h,teen m+NAP'].loc[[req_terugkeertijd][0]])
                        hydra_results['Hm0, teen [m]'].append(ip['Hm0,teen m'].loc[[req_terugkeertijd][0]])
                        hydra_results['Tm-1.0, ts'].append(ip['Tm-1,0,t s'].loc[[req_terugkeertijd][0]])
                        hydra_results['golfrichting [graden]'].append(ip['golfr graden'].loc[[req_terugkeertijd][0]])
                        hydra_results['windrichting [graden N]'].append(ip['r'].loc[[req_terugkeertijd][0]])
                        hydra_results['bijdrage ov. freq [%]'].append(ip['bijdrage ov. freq (%)'].loc[[req_terugkeertijd][0]])

          
df = pd.DataFrame(hydra_results)

savename = os.path.join(r"D:\Users\BADD\Desktop\KP ZSS\output", 'hydra_output_totaal.csv')
df.to_csv(savename, sep = ';', index = False)


