# -*- coding: utf-8 -*-
"""
Created on  : Tue Oct 25 10:19:48 2016
Author      : Guus Rongen
Project     : PR0000.00
Description :

"""


import numpy as np
import itertools
from collections import OrderedDict
import re
import pandas as pd
from html2text import html2text
import os


def _converteer_hydra_tabel(tabeltekst, index_col=999, sep="|"):
    """
    Functie om hydra htmltabel (geconverteerd naar tekst) om te zetten
    naar een pandas dataframe)
    """
    # Verwijder tussenrijen, eenhedenrij en een eventuele somrij
    # ----------------------------------------------------------------------
    regels = [regel.strip() for regel in tabeltekst.split("\n")]
    # Bepaal aantal header regels
    for i, regel in enumerate(regels):
        if "-+-" in regel:
            nheaderrows = i
            break
    else:
        nheaderrows = 1

    for regel in regels:
        # Verwijder somrij
        if "som " in regel or "som\t" in regel:
            regels.remove(regel)

    # Verwijder tussenrijen
    merged = "X".join(regels)
    while "-+-" in merged:
        for regel in regels:
            if "-+-" in regel:
                regels.remove(regel)
                merged = "X".join(regels)

    # Bepaal de header uit de headerrows
    # ----------------------------------------------------------------------
    headers = [
        [tag.strip() for tag in regel.split(sep)] for regel in regels[:nheaderrows]
    ]
    header = [" ".join(parts).strip() for parts in zip(*headers)]

    # Bepaal de gegevens
    # ----------------------------------------------------------------------
    gegevens = []
    for regel in regels[nheaderrows:]:
        gegevens.append([val.strip() for val in regel.split(sep)])

    # Bepaal de gegevens
    # ----------------------------------------------------------------------
    tabel = pd.DataFrame(gegevens, columns=header)
    for key, col in tabel.iteritems():
        tabel[key] = pd.to_numeric(col, errors="ignore")

    # Verwijder lege kolommen
    # ----------------------------------------------------------------------
    while "--" in tabel.keys():
        tabel = tabel.drop("--", 1)
    while "-- --" in tabel.keys():
        tabel = tabel.drop("-- --", 1)

    # Stel de index eventueel in
    # ----------------------------------------------------------------------
    if index_col < 999:
        idxnaam = tabel.columns[index_col]
        tabel = tabel.set_index(idxnaam)
        tabel.index.name = idxnaam

    return tabel


def _vind_ip_tabel(tekst, terugkeertijd, kering=False, onzekerheid=False):
    # Zoek naar het deel met de juiste terugkeertijd
    if len(str(int(terugkeertijd))) > 5:
        terugkeertijd = "{:4.2e}".format(terugkeertijd).replace("e+", "E\+")
    else:
        terugkeertijd = "{:5d}".format(terugkeertijd)

    # selecteer het tekstdeel met de juiste terugkeertijd
    startindicator = "Illustratiepunten bij .+ terugkeertijd {}".format(terugkeertijd)
    tekst = re.split(startindicator, tekst)[1]

    # geen keringen, geen onzekerheden
    if not kering and not onzekerheid:
        tekst = re.split("\n\s+\n", tekst)[2].strip()

    # geen keringen, wel onzekerheden
    elif not kering and onzekerheid:
        tekst = re.split("Onzekerheidswaarden", tekst)[1]
        tekst = re.split("\n\s+\n", tekst)[1].strip()

    # wel keringen, geen onzekerheden
    elif kering and not onzekerheid:
        keringindicator = "Geopende" if kering == "open" else "Gesloten"
        tekst = re.split(keringindicator, tekst)[1]
        tekst = re.split("\n\s+\n", tekst)[1].strip()

    # wel keringen, wel onzekerheden
    elif kering and onzekerheid:
        keringindicator = "Geopende" if kering == "open" else "Gesloten"
        # Selecteer keringtekst
        tekst = re.split(keringindicator, tekst)[1]
        # Selecteer onzekerheidtabel
        tekst = re.split("Onzekerheidswaarden", tekst)[1]
        tekst = re.split("\n\s+\n", tekst)[1].strip()

    return tekst


def lees_invoerbestand(invoerbestandpad):

    invoer = OrderedDict()

    with open(invoerbestandpad, "r") as f:
        freqs = 0
        categorie, key, value = "", "", ""

        for line in f.readlines():
            # Categorie regel
            if line.startswith("--"):
                continue
            elif line.startswith(";--"):
                categorie = line.replace(";", "").replace("-", "").strip()
            else:
                key = line.split("=")[0].strip()
                if key == "FREQ":
                    freqs += 1
                    key = "FREQ{:02d}".format(freqs)
                value = line.split("=")[1].strip()
                # Maak de dict voor de categorie aan als deze nog niet bestaat
                if not categorie in invoer.keys():
                    invoer[categorie] = OrderedDict()
                # Voeg de waarde toe
                invoer[categorie][key] = value

    # Bepaal de doorgerekende terugkeertijden
    terugkeertijden = []
    for key, val in invoer["criterium"].items():
        if "FREQ" in key:
            terugkeertijden.append(int(np.round(1 / float(val))))

    return invoer, terugkeertijden


def lees_terugkeertijden(tekst):
    starttag = "Berekeningsresultaten\n\s+Frequentie"
    ofltekst = re.split("\n\s+\n", re.split(starttag, tekst)[1])[0].strip()
    # Verwijder de resten en splits in regels
    ofltekst = ofltekst.strip().split("\n")[1:]
    # Selecteer gegevens, sla asterixes over
    terugkeertijden = np.array(
        [rij.split("/")[1].split()[0] for rij in ofltekst]
    ).astype(int)
    return terugkeertijden


def lees_sterkteresultaat(tekst):

    starttag = "Berekende golfcondities.*"
    ofltekst = re.split("\n\s+\n", re.split(starttag, tekst)[1])[0].strip()

    # Verwijder de resten en splits in regels
    ofltekst = ofltekst.strip().split("\n")[2:]

    # Bepaal headers
    header = ["terugkeertijd", "sterkte"]
    # Selecteer gegevens, sla asterixes over
    terugkeertijden = np.array(
        [rij.split("/")[1].split()[0] for rij in ofltekst if "-->" not in rij]
    ).astype(int)
    sterkte = np.array(
        [rij.split("/")[1].strip().split()[1] for rij in ofltekst if "-->" not in rij]
    ).astype(float)
    gegevens = np.vstack([terugkeertijden, sterkte]).T

    # Maak overschrijdingsfreqeuntielijn
    ofl = pd.DataFrame(
        gegevens[:, 1].astype(float),
        index=gegevens[:, 0].astype(int),
        columns=[header[1]],
    )
    ofl.index.name = header[0]
    ofl.sort_index(inplace=True)

    return ofl


def lees_illustratiepunten(tekst, kering=False, onzekerheid=False, afvoer=False):

    terugkeertijden = lees_terugkeertijden(tekst)
    # Bepaal illustratiepunten
    # ----------------------------------------------------------------------
    # Alle illustratiepunten worden opgezocht en opgeslagen in een boom-
    # structuur. Dit zijn eigenlijk dus conditionele illustratiepunten
    # uit de boomstructuur worden vervolgens de illustratiepunten bepaald

    # Bepaal de onderverdelingen (keringen en cond afvoer ips, onzekerheden
    #        AFVOER = True if self.invoer['criterium']['LILLUP_CONDQ'] == 'JA' else False

    # Voeg de terugkeertijden toe
    index = ["terugkeertijd"]
    combinaties = [terugkeertijden]

    # Voeg keringen aan de combinaties toe als dit relevant is
    if kering:
        combinaties.append(["open", "dicht"])
        index.append("kering")
    else:
        combinaties.append([False])

    #    # Voeg de keringssituatie eventueel toe
    #    if (('keringen' in self.invoer.keys()) or ('FAALKANSKERING' in self.invoer['algemeen'].keys())):
    #        combinaties.append(['open', 'dicht'])
    #        index.append('kering')
    #    else:
    #        combinaties.append([False])

    # Voeg de onzekerheid toe aan de combinatie (niet aan de index)
    #    if 'JA' in self.invoer['onzekerheden'].values():
    #        combinaties.append([True])
    #    else:
    #        combinaties.append([False])

    # Maak combinaties uit het product
    combinaties = itertools.product(*combinaties)

    # Ga door de combinaties heen
    tabellen = []
    for combinatie in combinaties:
        T, kering = combinatie
        # Zoek de IPtabel
        tabeltekst = _vind_ip_tabel(tekst, T, kering, onzekerheid=onzekerheid)
        tabel = _converteer_hydra_tabel(tabeltekst)
        # Zoek de onzekerheidstabel er eventueel uit
        if onzekerheid:
            tabeltekst = _vind_ip_tabel(
                tekst, terugkeertijd=T, kering=kering, onzekerheid=onzekerheid
            )
            onztabel = _converteer_hydra_tabel(tabeltekst)
            tabel[onztabel.columns] = onztabel
        # Voeg de combinatieparameters als index toe
        for parameter, waarde in zip(index, combinatie):
            tabel[parameter] = waarde

        # Voeg de tabel aan de totale tabel toe
        tabellen.append(tabel)

    # Voeg de verschillende tabellen samen
    tabellen = pd.concat(tabellen)
    # Verander de index (voeg de windrichting nog toe)
    index.append("r")
    cips = tabellen.set_index(index)

    # Zoek de illustratiepunten met de maximale kans van voorkomen
    ovfreqcol = cips.columns[cips.columns.str.contains("ov. freq")][0]

    if np.size(ovfreqcol):
        ips = cips[
            cips.groupby(cips.index.get_level_values(0))[ovfreqcol].transform(max)
            == cips[ovfreqcol]
        ]
        for i, name in enumerate(ips.index.names[1:]):
            ips.loc[:, name] = ips.index.get_level_values(i + 1)
        ips.index = ips.index.get_level_values(0)
        return cips, ips

    else:
        return cips


def lees_percentielen(tekst, terugkeertijden):

    # Bepaal percentielen
    # ----------------------------------------------------------------------
    afvoerpercentielen = {}
    meerpeilpercentielen = {}

    # Isoleer tabel
    startindicator = "Percentielen van (.+) over alle gegevensblokken"
    parts = re.split(startindicator, tekst)
    ntypes = (len(parts) - 1) / 2 / len(terugkeertijden)
    iterTs = np.c_[[terugkeertijden] * int(ntypes)].T.ravel()

    # Ga langs de verschillende percentieltabellen
    for T, k in zip(iterTs, range(1, len(parts), 2)):
        uitsplitsingstype = parts[k]
        tabeltekst = re.split("\n\s+\n", parts[k + 1].strip())[0].strip()
        df = _converteer_hydra_tabel(tabeltekst.replace("%", ""), index_col=0)
        if "afvoer" in uitsplitsingstype:
            afvoerpercentielen[T] = df
        else:
            meerpeilpercentielen[T] = df

    return afvoerpercentielen, meerpeilpercentielen


def lees_ofl(tekst):

    # Bepaal overschrijdingsfrequentielijn
    # ----------------------------------------------------------------------
    starttag = "Berekeningsresultaten\n\s+Frequentie"
    ofltekst = re.split("\n\s+\n", re.split(starttag, tekst)[1])[0].strip()

    # Verwijder de resten en splits in regels
    ofltekst = ofltekst.strip().split("\n")[1:]

    # Bepaal headers
    header = ["terugkeertijd", "hoogte"]
    # Selecteer gegevens, sla asterixes over
    terugkeertijden = np.array(
        [rij.split("/")[1].split()[0] for rij in ofltekst]
    ).astype(int)
    hoogte = np.array([rij.split("/")[1].split()[1] for rij in ofltekst]).astype(float)
    gegevens = np.vstack([terugkeertijden, hoogte]).T

    # Maak overschrijdingsfreqeuntielijn
    ofl = pd.DataFrame(
        gegevens[:, 1].astype(float),
        index=gegevens[:, 0].astype(int),
        columns=[header[1]],
    )
    ofl.index.name = header[0]
    ofl.sort_index(inplace=True)

    return ofl


def lees_uitvoerhtml(uitvoerbestand):
    # Lees het uitvoerbestand uit
    with open(uitvoerbestand, "r", encoding="utf8", errors="ignore") as f:
        htmltext = f.read()
        tekst = html2text(htmltext).strip()
    return tekst


#
#
#    # Lees de frequentielijn van het hbn uit
#    ffqpad = os.path.join(self.invoerbestandfolder, 'ffq.txt')
#    if os.path.exists(ffqpad):
#        with open(ffqpad, 'r') as f:
#            ffqdata = np.array([line.strip().split() for line in f.readlines()[1:]]).astype(float)
#            self.ffq = pd.DataFrame(ffqdata, columns = ['hbn', 'frequentie']).set_index('hbn')


def lees_freqs(bestandloc):
    # Lees de frequentielijn van de waterstand uit
    if os.path.exists(bestandloc):
        with open(bestandloc, "r") as f:
            hfreqdata = np.array(
                [line.strip().split() for line in f.readlines()[1:]]
            ).astype(float)
            hfreqs = pd.DataFrame(hfreqdata, columns=["h", "frequentie"]).set_index("h")
    else:
        raise FileNotFoundError(
            "The system cannot find the file specified: {}".format(bestandloc)
        )

    return hfreqs


def lees_profiel(pad):
    """
    Lees Hydra(-NL) profiel in.

    Parameters
    ----------
    pad : string
        pad naar het profielbestand

    Returns
    -------
    versie : str
    dam : int
    damhoogte : float
    dijknormaal : float
    kruinhoogte : float
    voorland : int
    damwand : int
    coordinaten : np.array
    memo : str
    """

    def lees_parameter(key, lines, return_index=None):
        val = None
        for i, line in enumerate(lines):
            if line.startswith(key):
                vals = line.split()
                val = vals[1] if len(vals) > 1 else None
                break
        if return_index:
            return i
        else:
            return val

    # Lees regels
    with open(pad, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    # Lees vlaggen uit
    versie = lees_parameter("VERSIE", lines)
    dam = int(lees_parameter("DAM", lines))
    damhoogte = float(lees_parameter("DAMHOOGTE", lines))
    richting = float(lees_parameter("RICHTING", lines))
    kruinhoogte = float(lees_parameter("KRUINHOOGTE", lines))
    voorland = int(lees_parameter("VOORLAND", lines))
    damwand = lees_parameter("DAMWAND", lines)
    if damwand is not None:
        damwand = int(damwand)
    else:
        damwand = 0

    # Lees coordinaten uit
    crds = [line.split() for line in lines if line[0].isdigit() or line[0] == "-"]
    coordinaten = np.array(crds[1:]).astype(float)

    # Lees memo
    memo = "\n".join(lines[(lees_parameter("MEMO", lines, return_index=True) + 1) :])

    return (
        versie,
        dam,
        damhoogte,
        richting,
        kruinhoogte,
        voorland,
        damwand,
        coordinaten,
        memo,
    )


def read_UncertaintyModelFactor(conn, hrdlocationid):
    """
    Reads model uncertainties for a location from a database

    Parameters
    ----------
    conn : sqlite3.connection
        Connection to HRD database
    hrdlocationid : int
        Location id of the location where the uncertainties are exported from
    """

    if not isinstance(hrdlocationid, (int, np.integer)):
        raise TypeError("must be int, not {}".format(type(hrdlocationid)))

    # First collect the dataids. Also replace wind direction ids with real ids
    SQL = """
    SELECT
    U.ClosingSituationId, RV.ResultVariableId, U.Mean AS MU, U.Standarddeviation AS SIGMA
    FROM
    UncertaintyModelFactor U
    INNER JOIN
    HRDResultVariables RV
    ON
    U.HRDResultColumnId = RV.HRDResultColumnId
    WHERE
    U.HRDLocationId = {};""".format(
        hrdlocationid
    )

    # Read from database
    modeluncertainty = pd.read_sql(
        SQL, conn, index_col=["ClosingSituationId", "ResultVariableId"]
    )

    # It is possible that the uncertainties vary per closing situation id
    # At the moment the maximum values are used.
    modeluncertainty = modeluncertainty.groupby(level=1).max()

    # Replace HRD result column ids
    resultvariableids = {
        1: "WS",
        2: "GH",
        4: "GP_TP",
        6: "GP_TSPEC",
    }
    modeluncertainty.index = [
        resultvariableids[iid] for iid in modeluncertainty.index.get_values()
    ]

    return modeluncertainty
