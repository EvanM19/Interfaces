# streamlit run app.py
import liquidity_management
import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Gestion de la liquidité", layout="wide")

# Titre de l'application
st.markdown("<h1 style='text-align: center;'>Gestion de la liquidité</h1>", unsafe_allow_html=True)

# Création des colonnes
col1, col2 = st.columns([1, 3])  # 1/4 de l'espace pour les sélections, 3/4 pour les graphiques

with col1:
    # Section 1 : Sélection de la date
    st.subheader("Sélectionnez la date")
    date = st.selectbox("Choisissez la date :", options=[ 
    "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", "2023-01-06",
    "2023-01-09", "2023-01-10", "2023-01-11", "2023-01-12", "2023-01-13",
    "2023-01-16", "2023-01-17", "2023-01-18", "2023-01-19", "2023-01-20",
    "2023-01-23", "2023-01-24", "2023-01-25", "2023-01-26", "2023-01-27",
    "2023-01-30", "2023-01-31", "2023-02-01", "2023-02-02", "2023-02-03",
    "2023-02-06", "2023-02-07", "2023-02-08", "2023-02-09", "2023-02-10",
    "2023-02-13", "2023-02-14", "2023-02-15", "2023-02-16", "2023-02-17",
    "2023-02-20", "2023-02-21", "2023-02-22", "2023-02-23", "2023-02-24",
    "2023-02-27", "2023-02-28", "2023-03-01", "2023-03-02", "2023-03-03",
    "2023-03-06", "2023-03-07", "2023-03-08", "2023-03-09", "2023-03-10",
    "2023-03-13", "2023-03-14", "2023-03-15", "2023-03-16", "2023-03-17",
    "2023-03-20", "2023-03-21", "2023-03-22", "2023-03-23", "2023-03-24",
    "2023-03-27", "2023-03-28", "2023-03-29", "2023-03-30", "2023-03-31",
    "2023-04-03", "2023-04-04", "2023-04-05", "2023-04-06", "2023-04-11",
    "2023-04-12", "2023-04-13", "2023-04-14", "2023-04-17", "2023-04-18",
    "2023-04-19", "2023-04-20", "2023-04-21", "2023-04-24", "2023-04-25",
    "2023-04-26", "2023-04-27", "2023-04-28", "2023-05-02", "2023-05-03",
    "2023-05-04", "2023-05-05", "2023-05-08", "2023-05-09", "2023-05-10",
    "2023-05-11", "2023-05-12", "2023-05-15", "2023-05-16", "2023-05-17",
    "2023-05-18", "2023-05-19", "2023-05-22", "2023-05-23", "2023-05-24",
    "2023-05-25", "2023-05-26", "2023-05-29", "2023-05-30", "2023-05-31",
    "2023-06-01", "2023-06-02", "2023-06-05", "2023-06-06", "2023-06-07",
    "2023-06-08", "2023-06-09", "2023-06-12", "2023-06-13", "2023-06-14",
    "2023-06-15", "2023-06-16", "2023-06-19", "2023-06-20", "2023-06-21",
    "2023-06-22", "2023-06-23", "2023-06-26", "2023-06-27", "2023-06-28",
    "2023-06-29", "2023-06-30", "2023-07-03", "2023-07-04", "2023-07-05",
    "2023-07-06", "2023-07-07", "2023-07-10", "2023-07-11", "2023-07-12",
    "2023-07-13", "2023-07-14", "2023-07-17", "2023-07-18", "2023-07-19",
    "2023-07-20", "2023-07-21", "2023-07-24", "2023-07-25", "2023-07-26",
    "2023-07-27", "2023-07-28", "2023-07-31", "2023-08-01", "2023-08-02",
    "2023-08-03", "2023-08-04", "2023-08-07", "2023-08-08", "2023-08-09",
    "2023-08-10", "2023-08-11", "2023-08-14", "2023-08-15", "2023-08-16",
    "2023-08-17", "2023-08-18", "2023-08-21", "2023-08-22", "2023-08-23",
    "2023-08-24", "2023-08-25", "2023-08-28", "2023-08-29", "2023-08-30",
    "2023-08-31", "2023-09-01", "2023-09-04", "2023-09-05", "2023-09-06",
    "2023-09-07", "2023-09-08", "2023-09-11", "2023-09-12", "2023-09-13",
    "2023-09-14", "2023-09-15", "2023-09-18", "2023-09-19", "2023-09-20",
    "2023-09-21", "2023-09-22", "2023-09-25", "2023-09-26", "2023-09-27",
    "2023-09-28", "2023-09-29", "2023-10-02", "2023-10-03", "2023-10-04",
    "2023-10-05", "2023-10-06", "2023-10-09", "2023-10-10", "2023-10-11",
    "2023-10-12", "2023-10-13", "2023-10-16", "2023-10-17", "2023-10-18",
    "2023-10-19", "2023-10-20", "2023-10-23", "2023-10-24", "2023-10-25",
    "2023-10-26", "2023-10-27", "2023-10-30", "2023-10-31", "2023-11-01",
    "2023-11-02", "2023-11-03", "2023-11-06", "2023-11-07", "2023-11-08",
    "2023-11-09", "2023-11-10", "2023-11-13", "2023-11-14", "2023-11-15",
    "2023-11-16", "2023-11-17", "2023-11-20", "2023-11-21", "2023-11-22",
    "2023-11-23", "2023-11-24", "2023-11-27", "2023-11-28", "2023-11-29",
    "2023-11-30", "2023-12-01", "2023-12-04", "2023-12-05", "2023-12-06",
    "2023-12-07", "2023-12-08", "2023-12-11", "2023-12-12", "2023-12-13",
    "2023-12-14", "2023-12-15", "2023-12-18", "2023-12-19", "2023-12-20",
    "2023-12-21", "2023-12-22", "2023-12-27", "2023-12-28", "2023-12-29"])
    st.markdown("---")

    # Section 2 : Sélection du scénario
    st.subheader("Sélectionnez le scénario")
    situation = st.radio("Choisissez la situation:", ["Normale", "Stressée"])
    seuil_atv = 0.2 if situation == "Normale" else 0.1
    st.markdown("</small>Une situation normale correspond à un cas où la quantité liquide sur une journée est égale à 0,2 fois l'Average Traded Volume sur trois mois, tandis que dans une situation stressée, elle est égale à 0,1 fois.</small>", unsafe_allow_html=True)
    
    situation = st.radio("Choisissez la situation:", ["Avec déformations", "Sans déformations"])
    deformations = True if situation == "Avec déformations" else False
    st.markdown("</small>Une situation avec déformation signifie que nous liquidons nos actifs le plus rapidement possible, ce qui entraîne une modification des poids des actifs dans notre portefeuille. À l'inverse, une situation sans déformation se produit lorsque le gestionnaire du portefeuille veille à liquider les actifs tout en maintenant la pondération. Cette méthode de liquidation est plus lente, mais elle a l'avantage d'assurer que tous les investisseurs sont confrontés au même risque. En effet, si l'un retire ses fonds en premier, les autres ne seront pas influencés, car il leur restera l'intégralité des actifs, et non seulement ceux qui sont moins liquides, comme c'est le cas dans une situation avec déformation.</small>", unsafe_allow_html=True)
    st.markdown("---")

    # Section 3 : Sélection du facteur diviseur de la quantité détenue
    st.subheader("Sélectionnez le facteur diviseur de la quantité détenue")
    seuil_quantite = st.slider("Choisissez une valeur", min_value=0.0, max_value=10.0, value=1.0, step=0.1)
    st.markdown("</small>Les pondérations initiales de notre portefeuille sont définies, mais le gestionnaire a la possibilité de déterminer la quantité à investir dans ce fonds. Il cherche à maximiser la quantité totale, tout en respectant des contraintes de liquidité. Plusieurs contraintes peuvent être définies, comme la capacité de liquider en une journée les positions des trois plus grands clients de ce fonds. Le facteur mentionné ci-dessus permet de diviser la quantité totale de notre portefeuille afin de déterminer la quantité optimale en fonction des contraintes choisies.</small>", unsafe_allow_html=True)
    st.markdown("---")

    # Prétraitement des données
    df = liquidity_management.pretraitement(date, seuil_atv, seuil_quantite)
    data = liquidity_management.avec_deformations(df) if deformations else liquidity_management.sans_deformations(df)

with col2:
    st.subheader("Quantité liquidable cumulée")
    fig = liquidity_management.plot_cumulative_liquidated_quantities(data)
    st.pyplot(fig)
    st.markdown("---")

    st.subheader("Evolution du poids")
    fig = liquidity_management.plot_poids_temps_courbe(data)
    st.pyplot(fig)
    fig = liquidity_management.plot_poids_temps_hist(data)
    st.pyplot(fig)
    st.markdown("---")

    st.subheader("Evolution de la valeur")
    fig = liquidity_management.plot_valeur_temps_courbe(data)
    st.pyplot(fig)
    fig = liquidity_management.plot_valeur_totale_temps_courbe(data)
    st.pyplot(fig)