import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# Configuration de la page pour mobile
st.set_page_config(page_title="Devise Square DZ", page_icon="🇩🇿", layout="centered")

# --- FONCTION DE SCRAPING AVEC CACHE ---
# Le ttl=3600 signifie que l'app garde le résultat en mémoire pendant 1 heure (3600 secondes)
@st.cache_data(ttl=3600)
def obtenir_taux_square():
    url_source = "https://www.algerie360.com/economie/bourse-et-devises/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    taux_achat, taux_vente = 242.0, 240.0 # Taux par défaut en cas d'échec
    statut = "Estimé (Erreur de connexion/Scraping)"

    try:
        response = requests.get(url_source, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            texte_page = soup.get_text()
            
            # Recherche des valeurs autour de 200-300
            matches = re.findall(r"(?:euro|EUR).*?(\d{3})", texte_page, re.IGNORECASE)
            if matches:
                taux_potentiels = [float(m) for m in matches if 200 <= float(m) <= 300]
                if len(taux_potentiels) >= 2:
                    taux_achat = max(taux_potentiels)
                    taux_vente = min(taux_potentiels)
                    statut = "En direct (Mis à jour récemment)"
    except Exception as e:
        pass # On garde les taux par défaut
        
    return taux_achat, taux_vente, statut

# --- INTERFACE UTILISATEUR STREAMLIT ---

st.title("🇩🇿 Convertisseur DZD / EUR")
st.markdown("**Basé sur les taux du marché parallèle (Square Port Saïd)**")

# Récupération des taux
taux_achat, taux_vente, statut = obtenir_taux_square()

# Affichage des taux du jour dans des "cartes" (Metrics)
col1, col2 = st.columns(2)
with col1:
    st.metric(label="💶 Achat (1 €)", value=f"{taux_achat} DA")
with col2:
    st.metric(label="💶 Vente (1 €)", value=f"{taux_vente} DA")
    
st.caption(f"Statut des données : {statut}")
st.divider()

# Section Conversion
st.subheader("🔄 Calculatrice de change")

tab1, tab2 = st.tabs(["Euros ➡️ Dinars", "Dinars ➡️ Euros"])

with tab1:
    st.info("Tu donnes des Euros, le cambiste te donne des Dinars (Calculé sur le taux d'Achat).")
    montant_eur = st.number_input("Montant en Euros (€)", min_value=0.0, value=100.0, step=10.0, key="eur_input")
    resultat_dzd = montant_eur * taux_achat
    st.success(f"💰 Tu recevras : **{resultat_dzd:,.2f} DA**")

with tab2:
    st.info("Tu donnes des Dinars, le cambiste te donne des Euros (Calculé sur le taux de Vente).")
    montant_dzd = st.number_input("Montant en Dinars (DA)", min_value=0.0, value=24000.0, step=1000.0, key="dzd_input")
    if taux_vente > 0:
        resultat_eur = montant_dzd / taux_vente
        st.success(f"💰 Tu recevras : **{resultat_eur:,.2f} €**")
