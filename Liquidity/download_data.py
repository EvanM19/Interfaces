import yfinance as yf
import pandas as pd

def extract_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Extrait toutes les données boursières pour un ticker donné à partir de Yahoo Finance.
    
    :param ticker: Le symbole du ticker (ex: "AAPL" pour Apple).
    :param start_date: La date de début au format "YYYY-MM-DD".
    :param end_date: La date de fin au format "YYYY-MM-DD".
    :return: Un DataFrame contenant toutes les données disponibles (Open, High, Low, Close, Volume, Adj Close).
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            print(f"Aucune donnée trouvée pour le ticker {ticker} entre {start_date} et {end_date}.")
            return pd.DataFrame()
        # Ajouter un préfixe au nom des colonnes pour identifier le ticker
        data = data.add_prefix(f"{ticker}_")
        # Réinitialiser l'index pour avoir une seule colonne d'index
        data = data.reset_index()
        data.columns = data.columns.droplevel(1)
        data = data.set_index('Date')
        return data
    except Exception as e:
        print(f"Erreur lors de l'extraction des données pour {ticker} : {e}")
        return pd.DataFrame()

def merge_cac40_data(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fusionne les données des actions du CAC40 en un DataFrame.
    
    :param start_date: La date de début au format "YYYY-MM-DD".
    :param end_date: La date de fin au format "YYYY-MM-DD".
    :return: Un DataFrame fusionné avec toutes les données (Open, High, Low, Close, Volume, etc.) 
             pour chaque action, et les dates en index.
    """
    tickers = ["AIR.PA", "MC.PA", "BNP.PA", "SAN.PA", "ENGI.PA", 
               "OR.PA", "DG.PA", "HO.PA", "VIV.PA", "RI.PA", "^FCHI"]
    all_data = []

    for ticker in tickers:
        stock_data = extract_stock_data(ticker, start_date, end_date)
        if not stock_data.empty:
            all_data.append(stock_data)

    # Fusionner les DataFrames sur l'index (les dates)
    merged_data = pd.concat(all_data, axis=1)

    # Télécharger en excel
    merged_data.to_excel("Liquidity\data.xlsx")
    return merged_data

# merge_cac40_data(start_date = "2022-01-01", end_date = "2024-01-01")