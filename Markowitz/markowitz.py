import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize

def extract_rendements(assets_dict, start_date, end_date):
    """
    Télécharge les données financières pour une liste de tickers, calcule les rendements mensuels,
    et retourne un DataFrame fusionné contenant les rendements pour chaque ticker.

    Args:
        assets_dict (dict): Dictionnaire où les clés sont les noms des actifs et les valeurs sont les tickers correspondants.
        start_date (str): Date de début pour récupérer les données au format 'YYYY-MM-DD'.
        end_date (str): Date de fin pour récupérer les données au format 'YYYY-MM-DD'.

    Returns:
        pd.DataFrame: Un DataFrame fusionné contenant les rendements mensuels pour chaque ticker,
                      aligné sur les dates communes.
    """
    # Initialisation d'un dictionnaire pour stocker les données individuelles
    data_dict = {}

    # Vérification que le dictionnaire n'est pas vide
    if not assets_dict:
        raise ValueError("Le dictionnaire 'assets_dict' ne doit pas être vide.")

    # Boucle sur les noms et tickers
    for name, ticker in assets_dict.items():
        try:
            # Téléchargement des données pour le ticker donné + Calcul des rendements mensuels (pct_change)
            data = yf.download(ticker, start=start_date, end=end_date, interval="1mo")['Close'].pct_change()
            
            # Réinitialisation de l'index pour une structure tabulaire propre
            data = data.reset_index()

            # Renommer la colonne 'Close' pour inclure le nom de l'actif
            data = data.rename(columns={f"{ticker}": f"{name}"})

            # Supprimer les lignes contenant des valeurs manquantes
            data.dropna(inplace=True)

            # Ajouter au dictionnaire
            data_dict[name] = data

        except Exception as e:
            print(f"Erreur lors du téléchargement des données pour {name} ({ticker}): {e}")

    # Initialisation du DataFrame fusionné
    df_merged = None

    # Fusion des données sur la colonne 'Date'
    for name, data in data_dict.items():
        if df_merged is None:
            df_merged = data[['Date', f"{name}"]]
        else:
            df_merged = pd.merge(df_merged, data[['Date', f"{name}"]], on='Date', how='inner')

    # Sélectionner uniquement les rendements
    rendements = df_merged.iloc[:, 1:]

    return rendements

def plot_matrice_correlation(rendements):
    fig, ax = plt.subplots(figsize=(10, 6))  # Créer une figure
    sns.heatmap(rendements.corr(), annot=True, cmap="coolwarm", fmt='.2f', linewidths=0.5, ax=ax)
    ax.set_title("Matrice de corrélation des actifs")
    return fig  # Retourner la figure

def calcul_rendements_annuels_actualises(rendements, taux_actualisation):
    """
    Calcule le rendement moyen annuel actualisé pour chaque actif d'un DataFrame.

    Args:
        rendements (pd.DataFrame): DataFrame contenant les rendements mensuels (colonnes = actifs, lignes = mois).
        taux_actualisation (float): Taux d'actualisation annuel.

    Returns:
        pd.Series: Série contenant le rendement moyen annuel actualisé pour chaque actif.
    """
    # Étape 1 : Actualiser les rendements
    rendements_actualises = rendements.apply(
        lambda col: [r / (1 + taux_actualisation)**(t / 12) for t, r in enumerate(col, start=1)],
        axis=0
    )
    
    # Étape 2 : Calculer la moyenne des rendements actualisés pour chaque actif
    moyenne_mensuelle_actualisee = rendements_actualises.mean(axis=0)
    
    # Étape 3 : Convertir en rendement moyen annuel
    rendements_annuels_actualises = (1 + moyenne_mensuelle_actualisee)**12 - 1
    
    return rendements_annuels_actualises

def statistiques_rendements(rendements, taux_sans_risque):
    """
    Calcule les statistiques des rendements : rendement attendu, volatilité et ratio de Sharpe.

    Args:
        rendements (pd.DataFrame): DataFrame avec les rendements mensuels des actifs.
        taux_sans_risque (float): Taux sans risque, par défaut 0.0.

    Returns:
        pd.DataFrame: DataFrame avec les statistiques (rendement attendu, volatilité, ratio de Sharpe).
    """
    # Calcul des rendements attendus
    annual_returns = np.array(calcul_rendements_annuels_actualises(rendements, taux_sans_risque))

    # Calcul de la volatilité (écart-type des rendements mensuels, annualisée)
    volatility = np.array(rendements.std() * np.sqrt(12))
    
    # Calcul du ratio de Sharpe (rendement excédentaire / volatilité)
    sharpe_ratio = (annual_returns - taux_sans_risque) / volatility
    
    # Création du DataFrame avec les informations calculées
    df_statistiques = pd.DataFrame({
        'Actif': rendements.columns,
        'Rendement': annual_returns,
        'Volatilité': volatility,
        'Ratio de Sharpe': sharpe_ratio
    })
    
    # Retourner le DataFrame avec les statistiques
    return df_statistiques

def calculate_efficient_frontier(rendements, risk_free_rate, contraintes=True):
    """
    Calcule et retourne la frontière efficiente selon la théorie de Markowitz avec la ligne de marché des capitaux.

    Args:
        rendements (pd.DataFrame): Un DataFrame contenant les rendements historiques des actifs.
        risk_free_rate (float): Le taux sans risque (par défaut, 0.045).
        contraintes (bool): Si True, les poids des actifs sont contraints entre 0 et 1, sinon il n'y a pas de contrainte sur les poids.

    Returns:
        fig (matplotlib.figure.Figure): La figure contenant la frontière efficiente et la ligne de marché des capitaux.
    """
    # Calcul des moyennes et de la matrice de covariance
    annual_returns = calcul_rendements_annuels_actualises(rendements, risk_free_rate)
    cov_matrix = np.array(rendements.cov() * 12)
    num_assets = len(annual_returns)

    # Nombre de portefeuilles à simuler
    num_portfolios = 100

    # Fonction d'objectif : Minimiser la variance
    def portfolio_volatility(weights):
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

    # Contraintes
    def portfolio_return(weights):
        return np.dot(weights, annual_returns)

    constraints = [{'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1}]  # Somme des poids = 1
    bounds = [(0, 1) for _ in range(num_assets)] if contraintes else [(-1, 1) for _ in range(num_assets)]

    # Initialisation des variables pour la frontière efficiente
    target_returns = np.linspace(annual_returns.min(), annual_returns.max(), num_portfolios)
    efficient_vols = []
    efficient_rets = []

    # Boucle pour calculer la frontière efficiente
    for target in target_returns:
        # Contrainte supplémentaire pour atteindre un rendement cible
        target_constraint = {'type': 'ineq', 'fun': lambda weights: portfolio_return(weights) - target}
        constraints_with_target = constraints + [target_constraint]

        # Minimisation de la volatilité
        result = minimize(
            portfolio_volatility,
            x0=np.ones(num_assets) / num_assets,  # Poids initiaux égaux
            constraints=constraints_with_target,
            bounds=bounds,
            method='SLSQP'
        )

        if result.success:
            efficient_vols.append(result.fun)  # Volatilité minimale
            efficient_rets.append(target)  # Rendement cible

    # Calcul de la tangente (portefeuille de marché)
    sharpe_ratios = [(ret - risk_free_rate) / vol for ret, vol in zip(efficient_rets, efficient_vols)]
    max_sharpe_idx = np.argmax(sharpe_ratios)
    market_portfolio_return = efficient_rets[max_sharpe_idx]
    market_portfolio_volatility = efficient_vols[max_sharpe_idx]

    # Création d'un DataFrame avec les poids du portefeuille de marché
    market_target_constraint = {'type': 'eq', 'fun': lambda weights: portfolio_return(weights) - market_portfolio_return}

    constraints_with_market_target = constraints + [market_target_constraint]

    result = minimize(
        portfolio_volatility,
        x0=np.ones(num_assets) / num_assets,  # Poids initiaux égaux
        constraints=constraints_with_market_target,
        bounds=bounds,
        method='SLSQP'
    )

    if result.success:
        market_weights = result.x  # Pondérations du portefeuille de marché
    else:
        raise ValueError("La minimisation des poids pour le portefeuille de marché a échoué.")

    market_weights_df = pd.DataFrame({
        'Actif': rendements.columns,
        'Poids': market_weights
    })

    # Création de la figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Affichage de la frontière efficiente
    ax.plot(efficient_vols, efficient_rets, label="Frontière Efficiente", color="blue")
    ax.scatter(market_portfolio_volatility, market_portfolio_return, color="red", label="Portefeuille de Marché", zorder=5)

    # Ajout de la CML
    cml_x = np.linspace(0, max(efficient_vols), 100)
    cml_y = risk_free_rate + cml_x * (market_portfolio_return - risk_free_rate) / market_portfolio_volatility
    ax.plot(cml_x, cml_y, label="Ligne de Marché des Capitaux (CML)", color="red", linestyle="--")

    # Labels et titre
    ax.set_xlabel("Volatilité (Risque)")
    ax.set_ylabel("Rendement")
    ax.legend()
    
    if contraintes:
        ax.set_title("Frontière Efficiente de Markowitz et Ligne de Marché des Capitaux (sans short)")  
    else: 
        ax.set_title("Frontière Efficiente de Markowitz et Ligne de Marché des Capitaux (avec short)")

    ax.set_xlim(0, 0.3)
    ax.set_ylim(0, 0.6)

    return fig, market_weights_df