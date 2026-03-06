import streamlit as st
import plotly.graph_objects as go
import random
import string

st.set_page_config(page_title="Enigma : 3 Rotors Intégrés", layout="wide")

st.title("🧩 Cheminement à travers les 3 Rotors")
st.write("Le signal descend du Rotor 1 (haut) vers le Rotor 3 (bas). Les alphabets intermédiaires sont partagés.")

# --- Logique des Dérangements ---
def generate_derangement(n):
    indices = list(range(n))
    while True:
        random.shuffle(indices)
        if all(indices[i] != i for i in range(n)):
            return indices

alphabet = list(string.ascii_uppercase)
n = len(alphabet)

# Initialisation des câblages
if 'r1' not in st.session_state:
    st.session_state.r1 = generate_derangement(n)
    st.session_state.r2 = generate_derangement(n)
    st.session_state.r3 = generate_derangement(n)

if st.button('🔄 Recâbler les 3 étages'):
    st.session_state.r1 = generate_derangement(n)
    st.session_state.r2 = generate_derangement(n)
    st.session_state.r3 = generate_derangement(n)
    st.rerun()

# --- Construction du Schéma Unique ---
def plot_triple_rotor():
    fig = go.Figure()
    offset = 0.15
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    # On définit 4 niveaux de Y (3 étages)
    # y=3 (Haut R1), y=2 (Bas R1 / Haut R2), y=1 (Bas R2 / Haut R3), y=0 (Bas R3)
    levels = [3, 2, 1, 0]
    wirings = [st.session_state.r1, st.session_state.r2, st.session_state.r3]
    labels = ["ROTOR I", "ROTOR II", "ROTOR III"]

    for stage in range(3):
        current_wiring = wirings[stage]
        y_top = levels[stage]
        y_bottom = levels[stage + 1]
        
        # Titre de l'étage
        fig.add_annotation(x=-2, y=(y_top + y_bottom)/2, text=labels[stage], showarrow=False, textangle=-90, font=dict(size=16, color="grey"))

        for i in range(n):
            target = current_wiring[i]
            color = colors[i % len(colors)]
            # Niveau horizontal interne à l'étage pour éviter les collisions
            h_level = y_bottom + 0.2 + (i * (0.6 / n))

            # Tracé du fil (Entrée décalée -> Palier -> Sortie décalée)
            fig.add_trace(go.Scatter(
                x=[i - offset, i - offset, target + offset, target + offset],
                y=[y_top, h_level, h_level, y_bottom],
                mode='lines',
                line=dict(color=color, width=1.5),
                hoverinfo='skip',
                showlegend=False
            ))

    # Affichage des alphabets aux interfaces
    for y_val in levels:
        for i in range(n):
            fig.add_trace(go.Scatter(
                x=[i], y=[y_val + (0.1 if y_val == 3 else -0.1)],
                text=[alphabet[i]],
                mode='text',
                textfont=dict(size=12, family="Courier New Bold", color="black"),
                showlegend=False
            ))

    fig.update_layout(
        height=800,
        margin=dict(l=50, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-3, 27]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 3.5]),
        plot_bgcolor='white',
    )
    return fig

st.plotly_chart(plot_triple_rotor(), use_container_width=True)
