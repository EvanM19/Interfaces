import streamlit as st
from datetime import datetime, timedelta
import markowitz

# Configuration de la page
st.set_page_config(page_title="Modèle d'allocation d'actifs : théorie de Markowitz", layout="wide")

# Dictionnaire des actifs avec leurs tickers
actifs = {
    "S&P500": "^GSPC",
    "CAC40": "^FCHI",
    "DAX": "^GDAXI",
    "NIKKEI": "^N225",
    "FTSE": "^FTSE",
    "EUR/USD": "EURUSD=X",
    "GOLD": "GC=F",
    "BITCOIN": "BTC-USD",
    "PETROLE": "CL=F", 
    "US 5Y Treasury Bonds":"^FVX",
    "US 10Y Treasury Bonds":"^TNX",
    "US 30Y Treasury Bonds":"^TYX"
}

# Titre de l'application
st.title("Modèle d'allocation d'actifs : théorie de Markowitz")

# Section 1 : Sélection des actifs
st.subheader("1. Sélectionnez les actifs financiers")
st.markdown("Veuillez sélectionner au moins deux actifs. La théorie de Markowitz étant basée sur la diversification, il est vivement recommandé de sélectionner l’ensemble des actifs dans un premier temps. Une sélection plus ciblée pourra ensuite être effectuée.")
selected_names = st.multiselect(
    "Choisissez les actifs à suivre :",
    options=list(actifs.keys()),
    default=[]  # Pas de sélection par défaut
)

# Ligne de séparation
st.markdown("---")

# Section 2 : Sélection des dates
st.subheader("2. Sélectionnez les dates de début et de fin")
st.markdown("Assurez-vous de disposer d'un historique d'au moins un an.")
col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("Date de début :", datetime(2020, 1, 1))

with col2:
    end_date = st.date_input("Date de fin :", datetime.today())

# Ligne de séparation
st.markdown("---")

# Section 3 : Taux sans risque
st.subheader("3. Sélectionnez le taux sans risque")
taux_sans_risque = st.number_input("Taux sans risque :", value=0.04, min_value=0.0, max_value=1.0)

# Validation des entrées
if st.button("Valider les données"):
    if len(selected_names) <= 1:
        st.error("Veuillez sélectionner au moins deux actifs financiers.")
    elif start_date > end_date:
        st.error("La date de début ne peut pas être postérieure à la date de fin.")
    elif (end_date - start_date) < timedelta(days=365):
        st.error("L'écart entre les dates doit être d'au moins 1 an.")
    else:
        st.success("Les données ont été validées avec succès.")

        # Construire le dictionnaire des actifs sélectionnés
        try:
            selected_dict = {name: actifs[name] for name in selected_names}

            # Extraction des rendements
            rendements = markowitz.extract_rendements(selected_dict, start_date, end_date)

            if rendements.empty:
                st.warning("Aucune donnée n'a été récupérée pour les actifs et les dates sélectionnés.")
            else:
                st.markdown("---")
                # Afficher les corrélations
                st.subheader("4. Présentation du modèle de Markowitz")

                # Ajouter une description avec des emojis
                st.write("💡 Voici les hypothèses principales :")

                # Utiliser st.markdown avec une liste en Markdown
                st.markdown("""
                - 🎯 **Décisions rationnelles** uniquement basées sur le couple rendement-risque
                - 📊 **Contrôle du risque** via la diversification
                - 💰 Accès **illimité au taux sans risque** pour prêter ou emprunter
                - ⚖️ **Absence de coûts de transactions** et de variations de position dominante sur le marché
                """)

                # Ajouter une section pour la construction mathématique
                st.write("🧮 **Construction mathématique du modèle :**")

                # Afficher une formule en LaTeX
                st.latex(r"""
                \text{Minimisation du risque sous contrainte de rendement cible } \mu_T:
                """)
                st.latex(r"""
                \text{argmin}_{\omega} \quad \omega^T \Sigma \omega
                """)
                st.latex(r"""
                \text{Sous contraintes : }
                """)
                st.latex(r"""
                \omega^T \mu \geq \mu_T, \quad \omega^T \mathbf{1} = 1
                """)
                st.latex(r"""
                \text{🔍 Remarque : La matrice de variance-covariance } \Sigma \text{ doit être inversible pour garantir une solution optimale.}
                """)

                # Ajouter une ligne de séparation
                st.markdown("---")

                # Afficher les corrélations
                st.subheader("5. Corrélations entre les actifs")
                fig_correlation = markowitz.plot_matrice_correlation(rendements)
                st.pyplot(fig_correlation)
                st.markdown("La matrice de corrélation permet d'identifier les actifs faiblement corrélés et de vérifier l'hypothèse d'inversibilité de la matrice de covariance. Veillez à retirer les actifs trop corrélés, puis relancez l'analyse.")
                st.markdown("---")

                # Afficher les statistiques des actifs
                st.subheader("6. Statistiques annuelles des actifs")
                df = markowitz.statistiques_rendements(rendements, taux_sans_risque)
                st.dataframe(df)
                st.markdown("---")

                # Frontière efficiente de Markowitz
                st.subheader("7. Frontière efficiente de Markowitz")
                st.markdown("L'intersection entre la tangente passant par le taux sans risque et la frontière efficiente de Markowitz permet d'identifier le portefeuille optimal. Si l'on souhaite un risque inférieur à celui de ce portefeuille, une partie des fonds est investie dans celui-ci, tandis que le reste est placé en cash, maximisant ainsi le rendement ajusté au risque. À l’inverse, pour prendre plus de risque, il est possible d'emprunter au taux sans risque et d'investir l'intégralité des fonds dans le portefeuille optimal.")

                # Calcul des frontières efficientes
                fig_frontiere_avec_contraintes, df_frontiere_avec_contraintes = markowitz.calculate_efficient_frontier(
                    rendements, risk_free_rate=taux_sans_risque, contraintes=True
                )
                fig_frontiere_sans_contraintes, df_frontiere_sans_contraintes = markowitz.calculate_efficient_frontier(
                    rendements, risk_free_rate=taux_sans_risque, contraintes=False
                )

                # Organiser les graphiques côte à côte dans des colonnes
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### Poids entre 0 et 1 : long only")
                    st.pyplot(fig_frontiere_avec_contraintes)   

                with col2:
                    st.markdown("#### Poids entre -1 et 1 : long and short")
                    st.pyplot(fig_frontiere_sans_contraintes)

                st.markdown("---")

                # Section pour afficher les poids du portefeuille de marché
                st.subheader("8. Poids du Portefeuille de Marché")

                # Organiser les graphiques côte à côte dans des colonnes
                col1, col2 = st.columns(2)

                with col1:
                    # Affichage des poids associés au portefeuille de marché
                    st.markdown("#### Poids entre 0 et 1 : long only")
                    st.dataframe(df_frontiere_avec_contraintes)

                with col2:
                    st.markdown("#### Poids entre -1 et 1 : long and short")
                    st.dataframe(df_frontiere_sans_contraintes)

        except Exception as e:
            st.error(f"Une erreur s'est produite lors de l'extraction des données : {e}")
