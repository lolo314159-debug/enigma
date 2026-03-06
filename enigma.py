import streamlit as st
import plotly.graph_objects as go
import random
import string

st.set_page_config(page_title="Enigma : Les 3 Rotors", layout="wide")

## Titre et Configuration
st.title("⚙️ Système à Trois Rotors Enigma")
st.write("Le signal traverse trois rotors successivement. Chaque rotor est un dérangement unique.")

# --- Logique de calcul ---
def generate_derangement(n):
    indices = list(range(n))
    while True:
        random.shuffle(indices)
        if all(indices[i] != i for i in range(n)):
            return indices

alphabet = list(string.ascii_uppercase)
n = len(alphabet)

# Initialisation des 3 rotors
for key in ['r1', 'r2', 'r3']:
    if key not in st.session_state:
        st.session_state[key] = generate_derangement(n)

if st.button('🔄 Recâbler tous les rotors'):
    for key in ['r1', 'r2', 'r3']:
        st.session_state[key] = generate_derangement(n)
    st.rerun()

# --- Fonction de dessin ---
def draw_rotor(wiring, label, color_seed):
    fig = go.Figure()
    offset = 0.15
    # Couleurs variées basées sur la seed
    base_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#17becf']
    
    for i in range(n):
        target = wiring[i]
        # On fait varier la couleur selon la lettre d'entrée
        color = base_colors[(i + color_seed) % len(base_colors)]
        h_level = 0.2 + (i * (0.6 / n))
        
        # Tracé orthogonal
        fig.add_trace(go.Scatter(
            x=[i - offset, i - offset, target + offset, target + offset],
            y=[1, h_level, h_level, 0],
            mode='lines',
            line=dict(color=color, width=1.5),
            hoverinfo='skip',
            showlegend=False
        ))

        # Lettres (uniquement si c'est le haut ou le bas pour ne pas surcharger)
        fig.add_trace(go.Scatter(
            x=[i], y=[1.1], text=[alphabet[i]], mode='text',
            textfont=dict(size=12, family="Courier New Bold"), showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=[i], y=[-0.1], text=[alphabet[i]], mode='text',
            textfont=dict(size=12, family="Courier New Bold"), showlegend=False
        ))

    fig.update_layout(
        title=f"<b>{label}</b>",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.2, 1.2]),
        plot_bgcolor='white',
    )
    return fig

# --- Affichage vertical ---
st.subheader("Rotor I (Entrée Rapide)")
st.plotly_chart(draw_rotor(st.session_state.r1, "Rotor 1", 0), use_container_width=True)

st.subheader("Rotor II (Intermédiaire)")
st.plotly_chart(draw_rotor(st.session_state.r2, "Rotor 2", 5), use_container_width=True)

st.subheader("Rotor III (Sortie lente)")
st.plotly_chart(draw_rotor(st.session_state.r3, "Rotor 3", 10), use_container_width=True)
