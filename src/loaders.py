import pandas as pd
from tqdm import tqdm 

def load_month(year,month, data_dir = "../data"):
    path = f"{data_dir}/A-{year}/F{year}-{month:02d}.xls" # 02d fills with zeros unitl 2 digits
    df_raw = pd.read_excel(path)

    # normalizes columns so that 2000 works 
    df_raw = df_raw.rename(columns={
    "HR. máx.": "HR. mx.",
    "HR. min.": "HR. mn."
    })

    # separating total summary rows
    # past logic:  
    # mask_total = (df_raw["Año"]=="Total") 
    # df = df_raw[~mask_total]
    mask = (df_raw["Año"]==year) & (df_raw["Mes"] == month)
    df = df_raw[mask]

    # droping usless columns
    cols_to_drop = ['Hora', 'T. máx.', 'Hora.1', 'T. mín.', 'Hora.2', 'HR. mx.', 'Hora.3', 'HR. mn.', 'Hora.4']
    df = df.drop(columns= cols_to_drop)

    #renaming
    rename_map = {
        "Año": "year",
        "Mes": "month",
        "Día": "day",
        "H": "H",
        "P (mm)": "rain_mm",
        "T (°C)": "temp",
        "HR %": "humidity",
        "Tens. V": "vapor_pressure",
        "Rocío": "dew_point",
    }
    df = df.rename(columns=rename_map)

    df["vapor_pressure"] = df["vapor_pressure"]*10
    
    # parsing H values
    def parse_hour(raw_value):
        chain = str(int(raw_value)).zfill(4)
        hours = chain[:2]
        minutes = chain[2:]
        return f"{hours}:{minutes}"

    df["H"] = df["H"].apply(parse_hour)

    # changing 24:00 to 00:00 (pending: adding a day)
    mask_2400 = df["H"] == "24:00"
    df.loc[mask_2400, "H"] = "00:00"

    # creating a timestamp
    df["hour"] = df["H"].str[:2]
    df["minute"] = df["H"].str[3:5]
    df["second"] = 0
    df["date"]=pd.to_datetime(df[["year","month","day","hour","minute","second"]])

    # changing the order 
    new_order = [
    "date",
    "temp",
    "humidity",
    "vapor_pressure",
    "dew_point",
    "rain_mm",
    "H",
    "year",
    "month",
    "day",
    "hour",
    "minute",
    "second"
    ]

    df = df[new_order]

    # adding a day
    df.loc[mask_2400,"date"] += pd.Timedelta(days=1)

    return df



def load_range(start_year, start_month, end_year, end_month, data_dir = "../data"):
    monthly_dfs = []
    start = f"{start_year}-{start_month:02d}-01"
    end = f"{end_year}-{end_month:02d}-01"
    months = pd.date_range(start,end,freq = "MS")
    for i in tqdm(months, desc = "loading month"):
        year = i.year
        month = i.month 
        if year < 2012: 
            monthly_dfs.append(load_month(year, month, data_dir))
        else: 
            #try:   
            monthly_dfs.append(load_month_era3(year, month, data_dir))
            #except Exception as e:
                #print(f"Error loading {month} {year}")
                #raise
    combined = pd.concat(monthly_dfs).reset_index(drop = True)
    combined = combined.drop_duplicates(subset = "date", keep = "first").reset_index(drop=True)
    df = normalize_df(combined)
    return df




# ERA SPECIFIC FUNCTIONS



def load_month_era3(year,month, data_dir = "../data"):
    path = f"{data_dir}/A-{year}/F{year}-{month:02d}.xls" # 02d fills with zeros unitl 2 digits
    df_raw = pd.read_excel(path)


    # separating total summary rows
    # past logic:  
    # mask_total = (df_raw["Año"]=="Total") 
    # df = df_raw[~mask_total]
    mask = (df_raw["Año"]==year) & (df_raw["Mes"] == month)
    df = df_raw[mask]

    # droping usless columns
    cols_to_drop = ['Hora', 'T. máx.', 'Hora.1', 'T. mín.', 'Hora.2', 'HR. mx.', 'Hora.3', 'HR. mn.', 'Hora.4']
    df = df.drop(columns= cols_to_drop)

    #renaming
    rename_map = {
        "Año": "year",
        "Mes": "month",
        "Día": "day",
        "H": "H",
        "P (mm)": "rain_mm",
        "T (°C)": "temp",
        "HR %": "humidity",
        "TV (kPa)": "vapor_pressure",
        "DTV (kPa)": "vapor_deficit",
        "Rocío (°C)": "dew_point",
        "W/m²": "radiation",
        "MJ/m²": "radiation_accum",
    }

    df = df.rename(columns=rename_map)

    # parsing H values
    def parse_hour(raw_value):
        chain = str(int(raw_value)).zfill(4)
        hours = chain[:2]
        minutes = chain[2:]
        return f"{hours}:{minutes}"

    df["H"] = df["H"].apply(parse_hour)

    # changing 24:00 to 00:00 (pending: adding a day)
    mask_2400 = df["H"] == "24:00"
    df.loc[mask_2400, "H"] = "00:00"


    # creating a timestamp
    df["hour"] = df["H"].str[:2]
    df["minute"] = df["H"].str[3:5]
    df["second"] = 0
    df["date"]=pd.to_datetime(df[["year","month","day","hour","minute","second"]])

    # changing the order 
    new_order = [
    "date",
    "temp",
    "humidity",
    "vapor_pressure",
    "vapor_deficit",
    "dew_point",
    "radiation",
    "radiation_accum",
    "rain_mm",
    "H",
    "year",
    "month",
    "day",
    "hour",
    "minute",
    "second"
    ]

    df = df[new_order]

    # adding a day
    df.loc[mask_2400,"date"] += pd.Timedelta(days=1)

    return df



def normalize_df(df):
    new_order = [
    "date",
    "temp",
    "humidity",
    "vapor_pressure",
    "vapor_deficit",
    "dew_point",
    "rain_mm",
    "radiation",
    "radiation_accum",
    ]

    df = df[new_order]
    return df