import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def nettoyer_donnees(df):
    """
    Filtre les données en supprimant les valeurs nulles ou égales à zéro.
    """
    colonnes_a_conserver = ['Date', 'AIR.PA_Volume', 'MC.PA_Volume', 'BNP.PA_Volume', 'SAN.PA_Volume', 'ENGI.PA_Volume', 'OR.PA_Volume', 'DG.PA_Volume', 'HO.PA_Volume', 'VIV.PA_Volume', 'RI.PA_Volume']
    data = df[colonnes_a_conserver]
    data = data[(data != 0).all(axis=1)].dropna()
    data['Date'] = pd.to_datetime(data['Date'])
    return data

def calculer_atv(data):
    """
    Calcule l'Average Traded Volume (ATV) sur une période donnée.
    """
    actions = ['AIR.PA_Volume', 'MC.PA_Volume', 'BNP.PA_Volume', 'SAN.PA_Volume', 
            'ENGI.PA_Volume', 'OR.PA_Volume', 'DG.PA_Volume', 'HO.PA_Volume', 
            'VIV.PA_Volume', 'RI.PA_Volume']
    
    for action in actions:
        data[f'{action}_ATV_3M'] = data[action].rolling(window=63).mean()
    data = data.dropna()
    for action in actions:
        data.loc[:, f'{action}_ATV_3M'] = data[f'{action}_ATV_3M'].astype(int)
    return data

def creer_tableau_atv(df, date):
    """
    Extrait et formate les données ATV pour une date donnée.
    """
    mapping_noms = {
        'AIR.PA_Volume_ATV_3M': 'Airbus',
        'MC.PA_Volume_ATV_3M': 'L\'Oréal',
        'BNP.PA_Volume_ATV_3M': 'BNP Paribas',
        'SAN.PA_Volume_ATV_3M': 'Sanofi',
        'ENGI.PA_Volume_ATV_3M': 'Engie',
        'OR.PA_Volume_ATV_3M': 'LVMH',
        'DG.PA_Volume_ATV_3M': 'Danone',
        'HO.PA_Volume_ATV_3M': 'TotalEnergies',
        'VIV.PA_Volume_ATV_3M': 'Vivendi',
        'RI.PA_Volume_ATV_3M': 'Roche'
    }
    data = df.loc[df['Date'] == date]
    colonnes_atv = [col for col in data.columns if 'ATV_3M' in col]
    data = data[colonnes_atv].T
    data.columns = ['Average Traded Volume 3 mois']
    data.index = data.index.map(mapping_noms)
    return data

def generer_statistiques_liquidite(data, seuil_atv, seuil_quantite):
    """
    Génère les statistiques de liquidité basées sur l'ATV.
    """
    np.random.seed(42)
    data['Quantité initiale portefeuille'] = (np.floor(1.5 * np.random.rand(len(data)) * data['Average Traded Volume 3 mois'])/seuil_quantite).astype(int)
    data['Quantité liquidable 1 jour'] = np.floor(seuil_atv * data['Average Traded Volume 3 mois']).astype(int)
    data['Délai de liquidation'] = np.ceil(data['Quantité initiale portefeuille'] / data['Quantité liquidable 1 jour']).astype(int)
    return data

def recuperer_prix(df, date):
    """
    Récupère et formate les prix de clôture pour une date donnée.
    """
    colonnes_prix = ['Date', 'AIR.PA_Close', 'MC.PA_Close', 'BNP.PA_Close', 'SAN.PA_Close', 'ENGI.PA_Close', 'OR.PA_Close', 'DG.PA_Close', 'HO.PA_Close', 'VIV.PA_Close', 'RI.PA_Close'] 
    prices = round(df[colonnes_prix], 2)
    prices = prices.loc[prices['Date'] == date]
    colonnes_close = [col for col in prices.columns if 'Close' in col]
    prices = prices[colonnes_close].T
    prices.columns = ['Prix']
    mapping_noms = {
        'AIR.PA_Close': 'Airbus',
        'MC.PA_Close': 'L\'Oréal',
        'BNP.PA_Close': 'BNP Paribas',
        'SAN.PA_Close': 'Sanofi',
        'ENGI.PA_Close': 'Engie',
        'OR.PA_Close': 'LVMH',
        'DG.PA_Close': 'Danone',
        'HO.PA_Close': 'TotalEnergies',
        'VIV.PA_Close': 'Vivendi',
        'RI.PA_Close': 'Roche'
    }
    prices.index = prices.index.map(mapping_noms)
    return prices

def fusionner_donnees(prices, data):
    """
    Fusionne les données ATV et les prix, puis calcule la valeur et le poids du portefeuille.
    """
    merged_data = pd.merge(prices, data, left_index=True, right_index=True, how='inner')
    merged_data['Valeur initiale portefeuille'] = (merged_data['Prix'] * merged_data['Quantité initiale portefeuille']).astype(int)
    total_valeur = merged_data['Valeur initiale portefeuille'].sum()
    merged_data['Poids initiaux portefeuille'] = round((merged_data['Valeur initiale portefeuille'] / total_valeur), 2)
    return merged_data

def pretraitement(date, seuil_atv, seuil_quantite):
    """
    Effectue le prétraitement des données de volumes et de prix pour analyser la liquidité d'un portefeuille.
    """  
    file_path = os.path.join(os.path.dirname(__file__), 'data.xlsx')
    df = pd.read_excel(file_path)
    data = nettoyer_donnees(df)
    data = calculer_atv(data)
    data = creer_tableau_atv(data, date)
    data = generer_statistiques_liquidite(data, seuil_atv, seuil_quantite)
    
    prices = recuperer_prix(df, date)
    return fusionner_donnees(prices, data)

def avec_deformations(df):
    """
    Calcule les quantités liquidées, la valeur du portefeuille et les poids de chaque position 
    pour chaque jour de liquidation dans un portefeuille, en tenant compte des déformations des 
    quantités liquidées au fil du temps.
    """
    data = df.copy()
    for i in range(1, max(data['Délai de liquidation'])+1): 
        # Calculer la quantité liquidée
        if i == 1:
            data[f'Quantité liquidée jour {i}'] = np.minimum(
                data['Quantité initiale portefeuille'],
                data['Quantité liquidable 1 jour']
            ).astype(int)
        else:
            previous_liquidated_quantity = data[[f'Quantité liquidée jour {j}' for j in range(1, i)]].sum(axis=1)
            data[f'Quantité liquidée jour {i}'] = np.minimum(
                data['Quantité initiale portefeuille'] - previous_liquidated_quantity,
                data['Quantité liquidable 1 jour']
            ).astype(int)

        # Calculer la valeur du portefeuille
        data[f'Valeur portefeuille jour {i}'] = (
            (data['Quantité initiale portefeuille'] - data[[f'Quantité liquidée jour {j}' for j in range(1, i+1)]].sum(axis=1)) * data['Prix']
        ).astype(int)

        # Calcul des poids
        data[f'Poids portefeuille jour {i}'] = round((
            data[f'Valeur portefeuille jour {i}'] / data[f'Valeur portefeuille jour {i}'].sum(axis=0)
        ).fillna(0).astype(float), 2)
    return data

def sans_deformations(df):
    """
    Calcule les quantités liquidées, la valeur du portefeuille et les poids de chaque position 
    pour chaque jour de liquidation dans un portefeuille, sans déformations des poids des actifs du portefeuille
    au fil du temps.
    """
    data = df.copy()
    delai_liquidation_max = data['Délai de liquidation'].max()

    for i in range(1, delai_liquidation_max + 1):
        # Calculer les quantités liquidés
        data[f'Quantité liquidée jour {i}'] = data['Quantité initiale portefeuille'] / delai_liquidation_max

        # Calculer la valeur du portefeuille
        data[f'Valeur portefeuille jour {i}'] = (
            (data['Quantité initiale portefeuille'] - data[[f'Quantité liquidée jour {j}' for j in range(1, i+1)]].sum(axis=1)) * data['Prix']
        ).astype(int)

        # Calcul des poids
        data[f'Poids portefeuille jour {i}'] = round((
            data[f'Valeur portefeuille jour {i}'] / data[f'Valeur portefeuille jour {i}'].sum(axis=0)
        ).fillna(0).astype(float), 2)
    return data

def plot_poids_temps_courbe(data):
    """
    Trace l'évolution des poids des entreprises dans le portefeuille au fil du temps.
    """
    weight_columns = ['Poids initiaux portefeuille'] + [f'Poids portefeuille jour {i}' for i in range(1, data['Délai de liquidation'].max()+1)]

    # Créer un DataFrame pour suivre les poids, en incluant les poids initiaux
    weight_evolution = data[weight_columns].T
    weight_evolution.columns = data.index 
    weight_evolution.index = ['Poids initiaux'] + [f'Jour {i}' for i in range(1, data['Délai de liquidation'].max()+1)]

    # Visualisation de l'évolution des poids
    fig, ax = plt.subplots(figsize=(12, 6))
    for stock in weight_evolution.columns:
        ax.plot(weight_evolution.index, weight_evolution[stock], marker='o', label=stock)

    ax.set_title("Évolution des poids du portefeuille")
    ax.set_xlabel("Jour")
    ax.set_ylabel("Poids")
    ax.set_xticks(range(len(weight_evolution.index)))
    ax.set_xticklabels(weight_evolution.index, rotation=45)  # Incliner les étiquettes pour une meilleure lisibilité
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1))
    ax.grid(True)
    fig.tight_layout()
    
    return fig

def plot_poids_temps_hist(data):
    """
    Trace un histogramme empilé de la répartition des poids des entreprises au fil du temps.
    """
    weight_columns = ['Poids initiaux portefeuille'] + [f'Poids portefeuille jour {i}' for i in range(1, data['Délai de liquidation'].max()+1)]
    weights = data[weight_columns].transpose()  # Transpose pour que les entreprises soient en colonnes
    
    # Créer un graphique en histogramme empilé
    fig, ax = plt.subplots(figsize=(12, 7))
    weights.plot(kind='bar', stacked=True, ax=ax, colormap='tab20', width=0.8)
    
    # Ajouter un titre et des labels
    ax.set_title('Répartition des poids des entreprises au fil du temps')
    ax.set_xlabel('Périodes')
    ax.set_ylabel('Poids (%)')
    ax.legend(title='Entreprises', bbox_to_anchor=(1.05, 1), loc='upper left')
    fig.tight_layout()
    
    return fig

def plot_valeur_temps_courbe(data):
    """
    Trace l'évolution des valeurs individuelles du portefeuille au fil du temps.
    """
    weight_columns = ['Valeur initiale portefeuille'] + [f'Valeur portefeuille jour {i}' for i in range(1, data['Délai de liquidation'].max()+1)]

    # Créer un DataFrame pour suivre les valeurs, en incluant la valeur initiale
    weight_evolution = data[weight_columns].T
    weight_evolution.columns = data.index 
    weight_evolution.index = ['Valeur initiale'] + [f'Jour {i}' for i in range(1, data['Délai de liquidation'].max()+1)]

    # Visualisation de l'évolution des valeurs
    fig, ax = plt.subplots(figsize=(12, 6))
    for stock in weight_evolution.columns:
        ax.plot(weight_evolution.index, weight_evolution[stock], marker='o', label=stock)

    ax.set_title("Évolution des valeurs du portefeuille")
    ax.set_xlabel("Jour")
    ax.set_ylabel("Valeur")
    ax.set_xticks(range(len(weight_evolution.index)))
    ax.set_xticklabels(weight_evolution.index, rotation=45)  # Incliner les étiquettes pour une meilleure lisibilité
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1))
    ax.grid(True)
    fig.tight_layout()  # Ajuster automatiquement la disposition pour éviter le chevauchement
    
    return fig

def plot_valeur_totale_temps_courbe(data):
    """
    Trace l'évolution de la valeur totale du portefeuille au fil du temps.
    """
    # Liste des colonnes de valeurs, incluant la valeur initiale et les valeurs des jours
    value_columns = ['Valeur initiale portefeuille'] + [f'Valeur portefeuille jour {i}' for i in range(1, data['Délai de liquidation'].max()+1)]
    
    # Calcul de la valeur totale du portefeuille pour chaque période
    total_value_evolution = data[value_columns].sum(axis=0)
    # Ajouter les périodes à l'index (Valeur initiale, Jour 1, Jour 2, etc.)
    periods = ['Valeur initiale'] + [f'Jour {i}' for i in range(1, data['Délai de liquidation'].max()+1)]
    
    # Visualisation de l'évolution de la valeur totale du portefeuille
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(periods, total_value_evolution, marker='o', label='Valeur totale portefeuille', color='b')

    ax.set_title("Évolution de la valeur totale du portefeuille")
    ax.set_xlabel("Jour")
    ax.set_ylabel("Valeur totale")
    ax.set_xticks(range(len(periods)))
    ax.set_xticklabels(periods, rotation=45)  # Incliner les étiquettes pour une meilleure lisibilité
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1))
    ax.grid(True)
    fig.tight_layout()  # Ajuster automatiquement la disposition pour éviter le chevauchement
    
    return fig

def plot_cumulative_liquidated_quantities(data):
    """
    Trace un histogramme de la proportion cumulée de la quantité liquidée par jour,
    par rapport à la quantité totale liquidée sur l'ensemble des jours.
    """
    # Calcul de la quantité liquidée totale pour chaque jour
    total_liquidated_quantities = [data[f'Quantité liquidée jour {day}'].sum() for day in range(1, data['Délai de liquidation'].max()+1)]

    # Calcul de la quantité liquidée totale sur tous les jours
    total_liquidated_all_days = sum(total_liquidated_quantities)

    # Calcul de la quantité liquidée cumulée pour chaque jour
    cumulative_liquidated_quantities = []
    cumulative_sum = 0
    for liquidated_quantity in total_liquidated_quantities:
        cumulative_sum += liquidated_quantity
        cumulative_liquidated_quantities.append(cumulative_sum)

    # Calcul de la proportion liquidée cumulée pour chaque jour par rapport au total
    cumulative_proportions = [quantity / total_liquidated_all_days * 100 for quantity in cumulative_liquidated_quantities]
    
    # Créer un histogramme pour la proportion cumulée de la quantité liquidée par jour
    fig, ax = plt.subplots(figsize=(10, 6))

    # Tracer l'histogramme de la proportion liquidée cumulée par jour
    ax.bar(range(1, data['Délai de liquidation'].max()+1), cumulative_proportions, color='green', alpha=0.7)

    # Ajouter des éléments de mise en forme
    ax.set_title("Proportion Cumulée de la Quantité Liquidée par Jour (par rapport au total liquidé)")
    ax.set_xlabel("Jours")
    ax.set_ylabel("Proportion Liquidée Cumulée (%)")
    ax.set_xticks(range(1, data['Délai de liquidation'].max()+1))
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)

    # Ajouter une ligne horizontale pour 100% (objectif théorique)
    ax.axhline(y=100, color='red', linestyle='--', label="Objectif : 100% liquidé")
    ax.legend()
    fig.tight_layout()

    return fig