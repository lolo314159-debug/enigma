import streamlit as st
import plotly.graph_objects as go
import random
import string
import time

# --- 1. INITIALISATION ---
def generate_derangement():
    indices = list(range(26))
    while True:
        random.shuffle(indices)
        if all(indices[i] != i for i in range(26)): return indices

if 'r1_base' not in st.session_state:
    st.session_state.r1_base = generate_derangement()
    st.session_state.r2_base = generate_derangement()
    st.session_state.r3_base = generate_derangement()
    st.session_state.off1, st.session_state.off2, st.session_state.off3 = 0, 0, 0
    st.session_state.text_in, st.session_state.text_out = "", ""
    st.session_state.pressed_key = None

st.set_page_config(page_title="Enigma : Modèle Physique Correct", layout="wide")
alphabet = list(string.ascii_uppercase)

# --- 2. LOGIQUE ENIGMA (Modèle : r(offset, lettre) -> lettre) ---
def get_rotor_output(base_wiring, offset, char_idx):
    # Entrée dans le rotor décalé
    shift_in = (char_idx + offset) % 26
    # Passage dans le câblage interne
    out_raw = base_wiring[shift_in]
    # Sortie du rotor (on revient à l'index de la lettre résultante)
    return (out_raw - offset) % 26

def get_enigma_path(key_char, o1, o2, o3):
    idx0 = alphabet.index(key_char)
    # Le signal traverse chaque rotor et ressort sur une lettre précise
    idx1 = get_rotor_output(st.session_state.r1_base, o1, idx0)
    idx2 = get_rotor_output(st.session_state.r2_base, o2, idx1)
    idx3 = get_rotor_output(st.session_state.r3_base, o3, idx2)
    return [idx0, idx1, idx2, idx3]

# --- 3. INTERFACE ---
st.title("📟 Enigma : Trajet Continu (Physique Réelle)")

delay = st.sidebar.slider("Délai d'observation (sec)", 0.0, 3.0, 1.0, step=0.5)

col_log, col_kbd = st.columns([1, 1.3])
with col_log:
    st.write(f"**Positions :** `{alphabet[st.session_state.off1]}-{alphabet[st.session_state.off2]}-{alphabet[st.session_state.off3]}`")
    st.info(f"**Texte clair :** `{st.session_state.text_in}`")
    st.success(f"**Texte chiffré :** `{st.session_state.text_out}`")
    if st.button("⏪ Reset Machine", use_container_width=True):
        st.session_state.off1, st.session_state.off2, st.session_state.off3 = 0, 0, 0
        st.session_state.text_in, st.session_state.text_out = "" , ""
        st.session_state.pressed_key = None
        st.rerun()

with col_kbd:
    # Clavier AZERTY 26 touches
    for row in [["A","Z","E","R","T","Y","U","I","O","P"], 
                ["Q","S","D","F","G","H","J","K","L","M"], 
                ["W","X","C","V","B","N"]]:
        cols = st.columns(len(row))
        for i, key in enumerate(row):
            if cols[i].button(key, key=f"k_{key}", use_container_width=True):
                st.session_state.pressed_key = key
                st.session_state.text_in += key
                p = get_enigma_path(key, st.session_state.off1, st.session_state.off2, st.session_state.off3)
                st.session_state.text_out += alphabet[p[3]]

# --- 4. DESSIN ---
def draw_viz():
    fig = go.Figure()
    levels = [2.2, 1.5, 0.8, 0.1] # Ligne 1 (Clavier), 2 (Sortie R1), 3 (Sortie R2), 4 (Sortie R3)
    path = get_enigma_path(st.session_state.pressed_key, st.session_state.off1, st.session_state.off2, st.session_state.off3) if st.session_state.pressed_key else None

    # Dessin des fils (uniquement les fils actifs en rouge pour la clarté)
    if path:
        for s in range(3):
            # Le fil va de la lettre sur la ligne s à la lettre sur la ligne s+1
            fig.add_trace(go.Scatter(
                x=[path[s], path[s+1]], y=[levels[s], levels[s+1]],
                mode='lines', line=dict(color="red", width=4), showlegend=False
            ))

    # Dessin des boîtes de lettres
    for l_idx, y_val in enumerate(levels):
        for i in range(26):
            is_active = (path and path[l_idx] == i)
            fig.add_trace(go.Scatter(
                x=[i], y=[y_val], mode='markers+text',
                marker=dict(symbol='square', size=20, color='white', 
                            line=dict(color="red" if is_active else "#ddd", width=2 if is_active else 1)),
                text=alphabet[i],
                textfont=dict(size=10, color="red" if is_active else "black"),
                showlegend=False
            ))

    fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor='white',
                      xaxis=dict(showgrid=False, range=[-0.5, 25.5], showticklabels=False),
                      yaxis=dict(showgrid=False, showticklabels=False))
    return fig

st.plotly_chart(draw_viz(), use_container_width=True)

# --- 5. ROTATION ---
if st.session_state.pressed_key:
    if delay > 0: time.sleep(delay)
    st.session_state.off1 = (st.session_state.off1 + 1) % 26
    if st.session_state.off1 == 0:
        st.session_state.off2 = (st.session_state.off2 + 1) % 26
    st.session_state.pressed_key = None
    st.rerun()
