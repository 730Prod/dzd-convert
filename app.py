import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# Configuration de la page pour le mobile
st.set_page_config(page_title="Devise Square DZ", page_icon="🇩🇿", layout="centered")

@st.cache_data(ttl=3600)  # Mise en cache pendant 1 heure pour éviter d'être bloqué
def obtenir_taux_square():
    # Nouvelle source officielle de ton choix
    url_source = "https://devisesalgerie.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    # Valeurs de secours basées sur les taux actuels du site (Juin 2026)
    taux_achat = 279.0  
    taux_vente = 281.0  
    statut = "Taux de secours (Le site met du temps à répondre ou bloque l'accès)"

    try:
        response = requests.get(url_source, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # On extrait tout le texte de la page en espaçant bien les mots
            texte_page = soup.get_text(separator=" ").replace('\xa0', ' ')
            
            # Expression régulière sur mesure pour le format de devisesalgerie.com
            # Le site affiche généralement : "Euro [Achat] DA [Vente] DA"
            match_euro = re.search(r"Euro\s+(\d{3})\s*DA\s+(\d{3})\s*DA", texte_page, re.IGNORECASE)
            
            if match_euro:
                # Le premier chiffre trouvé est l'Achat, le second est la Vente
                taux_achat = float(match_euro.group(1))
                taux_vente = float(match_euro.group(2))
                statut = "🟢 En direct (Synchronisé avec devisesalgerie.com)"
            else:
                statut = "⚠️ Taux de secours (Structure du site modifiée)"
    except Exception:
        pass 
        
    return taux_achat, taux_vente, statut

# --- INTERFACE UTILISATEUR STREAMLIT ---

st.title("🇩🇿 Convertisseur DZD / EUR")
st.markdown("**Taux du marché parallèle (Source : devisesalgerie.com)**")

# Récupération des taux
taux_achat, taux_vente, statut = obtenir_taux_square()

# Affichage visuel des taux
col1, col2 = st.columns(2)
with col1:
    st.metric(label="💶 Cambiste t'achète (1 €)", value=f"{taux_achat:.2f} DA")
with col2:
    st.metric(label="💶 Cambiste te vend (1 €)", value=f"{taux_vente:.2f} DA")
    
st.caption(f"Statut : {statut}")
st.divider()

st.subheader("🔄 Calculatrice Rapide")

tab1, tab2 = st.tabs(["Tu as des Euros (€)", "Tu as des Dinars (DA)"])

with tab1:
    st.info("💡 Si tu vends tes Euros au Square, le calcul se fait sur le taux d'Achat.")
    montant_eur = st.number_input("Combien d'Euros veux-tu vendre ?", min_value=0.0, value=100.0, step=10.0, key="eur_input")
    resultat_dzd = montant_eur * taux_achat
    st.success(f"💰 Le cambiste te donnera : **{resultat_dzd:,.2f} DA**")

with tab2:
    st.info("💡 Si tu achètes des Euros au Square, le calcul se fait sur le taux de Vente.")
    # Montant pré-rempli correspondant à peu près à 100€
    montant_dzd = st.number_input("Combien de Dinars veux-tu échanger ?", min_value=0.0, value=28100.0, step=1000.0, key="dzd_input")
    if taux_vente > 0:
        resultat_eur = montant_dzd / taux_vente
        st.success(f"💰 Tu recevras environ : **{resultat_eur:,.2f} €**")
