import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.title("Prévision des Objectifs du Funnel Commercial")

# Section pour charger le fichier Excel
uploaded_file = st.file_uploader("Télécharger votre fichier Excel des opportunités", type=["xlsx"])

if uploaded_file:
    # Lecture du fichier Excel
    data = pd.read_excel(uploaded_file)
    st.success("Fichier chargé avec succès!")
    
    # Affichage des premières lignes du DataFrame
    st.subheader("Aperçu des données chargées")
    st.write(data.head())

    # Conversion de la colonne 'Date' en type datetime si ce n'est pas déjà le cas
    if not np.issubdtype(data['Date'].dtype, np.datetime64):
        data['Date'] = pd.to_datetime(data['Date'])

    # Sélection du type de service
    st.sidebar.subheader("Filtres")
    types_service = data['Type de service'].unique()
    selected_service = st.sidebar.selectbox("Sélectionnez le type de service", types_service)

    # Sélection de la période
    min_date = data['Date'].min()
    max_date = data['Date'].max()
    selected_period = st.sidebar.date_input("Sélectionnez la période", [min_date, max_date], min_value=min_date, max_value=max_date)

    # Filtrage des données en fonction du type de service et de la période
    mask_service = data['Type de service'] == selected_service
    mask_period = (data['Date'] >= pd.to_datetime(selected_period[0])) & (data['Date'] <= pd.to_datetime(selected_period[1]))
    data_filtered = data[mask_service & mask_period]

    st.subheader(f"Données filtrées pour le service '{selected_service}' du {selected_period[0]} au {selected_period[1]}")
    st.write(data_filtered)

    # Calculs des agrégations historiques
    st.subheader("Agrégations Historiques")

    # Nombre total d'opportunités
    total_opportunites = data_filtered['Opportunités'].nunique()
    st.write(f"**Nombre total d'opportunités :** {total_opportunites}")

    # Nombre d'offres (étapes spécifiques)
    offres_etapes = ['Gagné', 'Perdu', 'Proposition']
    data_offres = data_filtered[data_filtered['Dernière étape en date'].isin(offres_etapes)]
    total_offres = data_offres['Opportunités'].nunique()
    st.write(f"**Nombre total d'offres :** {total_offres}")

    # Nombre d'offres gagnées
    data_gagnees = data_filtered[data_filtered['Dernière étape en date'] == 'Gagné']
    total_gagnees = data_gagnees['Opportunités'].nunique()
    st.write(f"**Nombre d'offres gagnées :** {total_gagnees}")

    # Chiffre d'affaire total des opportunités gagnées
    ca_total = data_gagnees['Chiffre d\'affaire'].sum()
    st.write(f"**Chiffre d'affaires total :** {ca_total} €")

    # Calcul du panier moyen historique
    if total_gagnees > 0:
        panier_moyen_historique = ca_total / total_gagnees
    else:
        panier_moyen_historique = 0
    st.write(f"**Panier moyen historique :** {panier_moyen_historique:.2f} €")

    # Taux de conversion historique
    if total_offres > 0:
        taux_conversion_gagne_offre = total_gagnees / total_offres
    else:
        taux_conversion_gagne_offre = 0
    st.write(f"**Taux de conversion Gagné/Offre :** {taux_conversion_gagne_offre:.2%}")

    if total_opportunites > 0:
        taux_conversion_offre_opportunite = total_offres / total_opportunites
    else:
        taux_conversion_offre_opportunite = 0
    st.write(f"**Taux de conversion Offre/Opportunité :** {taux_conversion_offre_opportunite:.2%}")

    # Section pour définir les objectifs
    st.sidebar.subheader("Définition des Objectifs")
    ca_objectif = st.sidebar.number_input("Chiffre d'affaires à atteindre (€)", min_value=0.0, value=ca_total)
    periode_previsionnelle = st.sidebar.date_input("Période prévisionnelle", [datetime.today(), datetime.today()])

    # Calcul des projections
    st.subheader("Projections pour les Objectifs")

    # Calcul du nombre de clients prévisionnel
    if panier_moyen_historique > 0:
        nombre_clients_previsionnel = ca_objectif / panier_moyen_historique
    else:
        nombre_clients_previsionnel = 0
    st.write(f"**Nombre de clients prévisionnel :** {int(nombre_clients_previsionnel)}")

    # Calcul du nombre d'offres prévisionnel
    nombre_offres_previsionnel = 0
    if taux_conversion_gagne_offre > 0:
        nombre_offres_previsionnel = nombre_clients_previsionnel / taux_conversion_gagne_offre
    st.write(f"**Nombre d'offres prévisionnel :** {int(nombre_offres_previsionnel)}")

    # Calcul du nombre d'opportunités prévisionnel
    nombre_opportunites_previsionnel = 0
    if taux_conversion_offre_opportunite > 0:
        nombre_opportunites_previsionnel = nombre_offres_previsionnel / taux_conversion_offre_opportunite
    st.write(f"**Nombre d'opportunités prévisionnel :** {int(nombre_opportunites_previsionnel)}")

    st.success("Les objectifs ont été calculés avec succès!")

else:
    st.warning("Veuillez charger un fichier Excel pour commencer.")
