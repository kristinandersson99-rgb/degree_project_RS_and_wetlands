""" 
Hjälpfunktioner för att läsa in, bearbeta och visualisera klimatdata 
från SMHI (Sveriges meteorologiska och hydrologiska institut). 
Innehåller logik för att hantera SMHI:s specifika filformat för observationsdata
och för att diagramföra historiska väderavvikelser mot klimatnormaler.
"""

import pandas as pd

def read_smhi_csv(path):
    """
    Läser in en nedladdad datafil (.csv) från SMHI:s öppna data.
    SMHI:s filer börjar ofta med en varierande mängd rader som innehåller metadatatext
    innan själva mät-tabellen börjar. Denna funktion letar dynamiskt upp var tabellen
    faktiskt startar (genom att söka efter rubriken 'Datum' eller 'Från Datum') 
    och laddar sedan in den på ett robust sätt.
    """
    with open(path, encoding="utf-8-sig") as f:
        lines = f.readlines()

    # Hantera olika SMHI-varianter av rubrikraden, t.ex. "Datum" eller "Från Datum".
    skiprows = next(
        (
            i
            for i, line in enumerate(lines)
            if line.lstrip("\ufeff").strip().startswith("Från Datum")
            or "Datum;" in line
        ),
        None,
    )

    if skiprows is None:
        sample = "\n".join(l.rstrip("\n") for l in lines[:12])
        raise ValueError(
            f"Kunde inte hitta rubrikrad med 'Datum' i filen: {path}\n"
            f"Första rader i filen:\n{sample}"
        )

    df = pd.read_csv(path, sep=";", skiprows=skiprows, encoding="utf-8-sig", low_memory=False)
    df.columns = df.columns.str.strip()

    # Standardisera datumkolumn för att fungera med samma kod i notebooken.
    if "Datum" not in df.columns and "Från Datum" in df.columns:
        df = df.rename(columns={"Från Datum": "Datum"})

    return df


DATUM_COL = "Representativt dygn"
STATION_COL = "Station"
MIN_DATE = pd.Timestamp("1984-05-01")
MAX_DATE = pd.Timestamp("2025-08-31")

def prep_df(df, value_col, station_name=None, station_col=STATION_COL):
    """
    Rensar en inläst SMHI-tabell: 
    1. Väljer enbart datum-kolumnen och efterfrågade mätvärden (t.ex. 'Lufttemperatur').
    2. Omvandlar datum-text till ett datorvänligt tidsformat (datetime).
    3. Filtrerar bort år/datum som ligger helt utanför uppsatsens intresseperiod (innan maj 1984).
    """
    out = df[[DATUM_COL, value_col]].copy()

    if station_name is not None:
        out[station_col] = station_name

    out[DATUM_COL] = pd.to_datetime(out[DATUM_COL], format="%Y-%m-%d")
    out = out.dropna(subset=[DATUM_COL])
    return out[(out[DATUM_COL] >= MIN_DATE) & (out[DATUM_COL] <= MAX_DATE)]

def combine_stations(station_list, value_col):
    """
    Sammanslår mätserier från flera olika SMHI-stationer för att skapa en enda lång, 
    sammanhängande tidsserie. Eftersom en enskild väderstation ibland lagts ner eller 
    startat sent under en viss tidsperiod (ex. saknar data innan 1995), kan vi med 
    denna funktion "skarva ihop" data smidigt (ex. Gävle som stängs -> Gävle A tar vid).
    
    Parametrar:
    -----------
    station_list : list av dicts
        Instruktioner om när varje station bidrar, ex: [{'station': 'Gävle', 'start': '1984-05', 'stop': '1995-07', ...}]
    value_col    : str
        Namnet på mätkolumnen (t.ex. 'Lufttemperatur').
    """
    frames = []
    for s in station_list:
        df_raw = read_smhi_csv(s["file"])
        df = prep_df(df_raw, value_col, station_name=s["station"])
        
        # Filtrera på användningsintervall
        start = pd.Timestamp(s["start"])
        stop  = pd.Timestamp(s["stop"] + "-31")
        mask  = (df[DATUM_COL] >= start) & (df[DATUM_COL] <= stop)
        frames.append(df[mask])
    
    return pd.concat(frames).sort_values(DATUM_COL).reset_index(drop=True)


def load_normal(path, station_name, months=(5, 6, 7, 8)):
    """
    Slår upp det historiska "klimatnormalvärdet" från en standardiserad SMHI-excelfil 
    Denna funktion beräknar och returnerar ett ETT ENDA genomsnitt över de valda månaderna.
    """
    df = pd.read_excel(path, sheet_name="Data", skiprows=3)
    df.columns = df.columns.str.strip()
    
    month_map = {
        1: "jan", 2: "feb", 3: "mar", 4: "apr",
        5: "maj", 6: "jun", 7: "jul", 8: "aug",
        9: "sep", 10: "okt", 11: "nov", 12: "dec"
    }
    
    row = df[df["Station"] == station_name]
    if row.empty:
        raise ValueError(f"Station '{station_name}' hittades inte i normalvärdesfilen.")
    
    month_cols = [month_map[m] for m in months]
    return float(row[month_cols].mean(axis=1).values[0])


def load_normal_monthly(path, station_name, months=(5, 6, 7, 8)):
    """
    Till skillnad från load_normal() som ger ett sommar-snitt, letar denna funktion
    upp klimatnormalvärdet separat för VARJE SPECIFIK MÅNAD.
    Gör att graferna kan räkna ut att exempelvis just *Augusti* avvek starkt mot 
    hur man förväntar sig att en *Normal Augusti* (enligt 1991-2020) ska se ut.
    
    Returnerar:
    -----------
    dict : Mappning mellan månadsnummer (5=maj) och referensvärdet, ex. {5: 8.85, 6: 13.75, ...}
    """
    df = pd.read_excel(path, sheet_name="Data", skiprows=3)
    df.columns = df.columns.str.strip()

    month_map = {
        1: "jan", 2: "feb", 3: "mar", 4: "apr",
        5: "maj", 6: "jun", 7: "jul", 8: "aug",
        9: "sep", 10: "okt", 11: "nov", 12: "dec"
    }

    row = df[df["Station"] == station_name]
    if row.empty:
        raise ValueError(f"Station '{station_name}' hittades inte i normalvärdesfilen.")

    return {m: float(row[month_map[m]].values[0]) for m in months}


def plot_climate_monthly_style_plot(df, value_col, normal_monthly, ylabel, title,
                                  output_path, agg="mean", months=(5, 6, 7, 8),
                                  mode="diff", threshold_std=1.5, scene_years=None):
    """
    Skapar huvuddiagrammen (bestående av ett del-diagram eller "subplot" för varje månad, uppifrån och ner) 
    som visuellt visar hur mycket varmare/kallare eller blötare/torrare ett visst år var, 
    jämfört med det förväntade "normala vädret" (där Normalen får representera 0-strecket).

    Parametrar:
    -----------
    df              : pd.DataFrame, den samlade historiska väderdatan för alla år.
    value_col       : str, vilken väderkategori man plottar (t.ex. 'Air temperature' eller 'Precipitation').
    normal_monthly  : dict, månadsspecifika "nollstreck" (klimatnormaler) som hämtas via load_normal_monthly.
    ylabel / title  : str, text/etiketter som syns utåt i de färdiga graferna.
    output_path     : str, mål-sökväg dit PNG-bilden slutligen skrivs ut på disk.
    agg             : str, 'mean' om man vill kolla dygnsMEDEL-temperatur per månad, 'sum' räknar TOTAL nederbördsmängd.
    mode            : str, avgör skala. 'diff' ger absolut avvikelse i °C. 'percent' visar procentuell skillnad av en normalmånads nederbörd.
    threshold_std   : float, relik från extremårs-tillägg. Används ej aktivt i denna design, utelämnas vanligtvis.
    scene_years     : lista av int, [Frivilligt] ritar ut stående gröna referensstreck de år då vi hade molnfria satellitbilder.
    """
    import matplotlib.pyplot as plt
    import matplotlib as mpl

    month_labels = {5: "May", 6: "June", 7: "July", 8: "August"}

    # Aggregera till månadsvärden per år
    df = df.copy()
    df["year"]  = df[DATUM_COL].dt.year
    df["month"] = df[DATUM_COL].dt.month

    monthly = (
        df[df["month"].isin(months)]
        .groupby(["year", "month"])[value_col]
        .agg(agg)
        .reset_index()
    )

    # Gjorde figsize något smalare (från '14' ner till '11')
    fig, axes = plt.subplots(4, 1, figsize=(11, 12), sharex=True)
    fig.suptitle(title, y=1.01)  # ← ingen fontsize

    for ax, m in zip(axes, months):
        sub = monthly[monthly["month"] == m].set_index("year")[value_col]
        normal = normal_monthly[m]

        if mode == "percent":
            anomaly = (sub / normal) * 100 - 100
            zero_line = 0
            ax.set_ylabel("Deviation (%)")
            unit = "mm"
        else:
            anomaly = sub - normal
            zero_line = 0
            ax.set_ylabel("Deviation (°C)")
            unit = "°C"

        std = anomaly.std()
        # Anpassa färger beroende på om det är nederbörd eller temperatur
        if mode == "percent":
            colors = ["#3564a0" if v > 0 else "#84a9d9" for v in anomaly] # Blå över normalt, ljusblå under
            ax.set_ylim(-110, 310) # Anpassa y-axeln för precip
        else:
            colors = ["#d73027" if v > 0 else "#fdae61" for v in anomaly] # Röd över normalt, orange under
            ax.set_ylim(-3.5, 4) # Anpassa y-axelnför temp

        ax.bar(anomaly.index, anomaly.values, color=colors, alpha=0.8, width=0.4) # width = bredden på staplarna
        ax.axhline(0, color="black", linewidth=0.8,
                   label=f"Normal value: {normal:.1f} {unit}")

        # Scenår
        if scene_years is not None:
            for yr in scene_years:
                if yr in anomaly.index:
                    ax.axvline(yr, color="green", linewidth=0.8,
                               alpha=0.5, linestyle=":")

        ax.set_title(month_labels[m], loc="left", pad=6, fontsize=10, fontweight="bold")
        # Placera legend ute till höger men PÅ SAMMA RAD som titeln (ovanför själva grafboxen)
        ax.legend(loc="lower right", bbox_to_anchor=(1.0, 1.0), frameon=False, fontsize=9, ncol=2)
        
        # Stäng av x-grid (inga streck över årtalen) och slå på y-grid
        ax.grid(False, axis="x")
        ax.grid(True, axis="y", linestyle="--", color="gray", alpha=0.4)
        # Se till att grid-linjerna lägger sig BAKOM staplarna
        ax.set_axisbelow(True)
        
        # Sätt fasta x-ticks för varje axel och visa texten (labelbottom) trots sharex
        ax.set_xticks([1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025])
        ax.set_xlim(1983, 2026)
        ax.tick_params(labelbottom=True, direction="in")
        
    # axes[-1].set_xlabel("Year")
    # Bygg in lite extra padding i h_pad (mellan bilderna) för att x-axlarna ska få plats
    plt.tight_layout(h_pad=1.5)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()