import streamlit as st
import plotly.graph_objects as go
import random
import string

# Configuration de la page
st.set_page_config(page_title="Simulateur Enigma", layout="wide")

st.title("🧩 Visualisation d'un Rotor Enigma")
st.write("Chaque rotor d'Enigma effectue une permutation de l'alphabet.")

# Initialisation de l'alphabet
alphabet = list(string.ascii_uppercase)

# Gestion de la permutation dans le cache de la session
if 'permutation' not in st.session_state:
    shuffled = alphabet.copy()
    random.shuffle(shuffled)
    st.session_state.permutation = shuffled

# Bouton pour changer la permutation
if st.button('🔄 Générer une nouvelle permutation'):
    shuffled = alphabet.copy()
    random.shuffle(shuffled)
    st.session_state.permutation = shuffled
    st.rerun()

# Fonction pour créer le graphique
def plot_permutation(original, mapped):
    fig = go.Figure()

    for i, (char_orig, char_map) in enumerate(zip(original, mapped)):
        # Ligne de connexion entre le haut et le bas
        fig.add_trace(go.Scatter(
            x=[i, i], 
            y=[1, 0],
            mode='lines',
            line=dict(color='rgba(100, 100, 100, 0.2)', width=1),
            hoverinfo='none'
        ))
        
        # Lettres du haut (Alphabet source)
        fig.add_trace(go.Scatter(
            x=[i], y=[1.1],
            text=[char_orig],
            mode='text',
            textfont=dict(size=14, color="blue", family="Courier New Bold"),
        ))

        # Lettres du bas (Alphabet permuté)
        fig.add_trace(go.Scatter(
            x=[i], y=[-0.1],
            text=[char_map],
            mode='text',
            textfont=dict(size=14, color="red", family="Courier New Bold"),
        ))

    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.3, 1.3]),
        plot_bgcolor='white',
        showlegend=False
    )
    return fig

# Affichage du graphique
st.plotly_chart(plot_permutation(alphabet, st.session_state.permutation), use_container_width=True)
