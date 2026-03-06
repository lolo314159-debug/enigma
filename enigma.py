import streamlit as st
import plotly.graph_objects as go
import random
import string

# Configuration de la page
st.set_page_config(page_title="Rotor Enigma - Connexions", layout="wide")

st.title("🧩 Visualisation des croisements d'un Rotor")
st.write("Les deux alphabets sont fixes (A-Z). Les lignes représentent le câblage interne aléatoire.")

# 1. Préparation de l'alphabet (fixe)
alphabet = list(string.ascii_uppercase)
n = len(alphabet)

# 2. Gestion de la permutation (le "câblage")
if 'wiring' not in st.session_state:
    # On crée une liste d'index de 0 à 25, puis on la mélange
    indices = list(range(n))
    random.shuffle(indices)
    st.session_state.wiring = indices

# Bouton pour recâbler le rotor
if st.button('🔄 Mélanger le câblage (Croisements)'):
    indices = list(range(n))
    random.shuffle(indices)
    st.session_state.wiring = indices
    st.rerun()

# 3. Fonction pour tracer les connexions
def plot_enigma_wiring(alphabet, wiring):
    fig = go.Figure()

    for i in range(len(alphabet)):
        target_index = wiring[i] # Où la lettre à l'index 'i' atterrit-elle ?
        
        # --- Tracé de la ligne (Croisement) ---
        # x_start = i (position de la lettre d'entrée)
        # x_end = target_index (position de la lettre de sortie)
        fig.add_trace(go.Scatter(
            x=[i, target_index], 
            y=[1, 0],
            mode='lines',
            line=dict(color='rgba(20, 100, 200, 0.3)', width=1.5),
            hoverinfo='none',
            showlegend=False
        ))
        
        # --- Lettres fixes en haut (Entrée) ---
        fig.add_trace(go.Scatter(
            x=[i], y=[1.1],
            text=[alphabet[i]],
            mode='text',
            textfont=dict(size=14, color="black", family="Courier New Bold"),
            showlegend=False
        ))

        # --- Lettres fixes en bas (Sortie) ---
        fig.add_trace(go.Scatter(
            x=[i], y=[-0.1],
            text=[alphabet[i]],
            mode='text',
            textfont=dict(size=14, color="black", family="Courier New Bold"),
            showlegend=False
        ))

    fig.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.3, 1.3]),
        plot_bgcolor='white',
        showlegend=False
    )
    return fig

# Affichage
st.plotly_chart(plot_enigma_wiring(alphabet, st.session_state.wiring), use_container_width=True)
