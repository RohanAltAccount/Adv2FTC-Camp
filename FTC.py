import streamlit as st
import time

st.set_page_config(page_title="FTC Match Results", layout="wide")

# ftc aesthetic & button styling
st.markdown("""
<style>
    /* dark background & text styling */
    .stApp {
        background-color: #0d0f12;
        color: #ffffff !important;
        font-family: 'Arial', sans-serif;
    }

    p, span, label, div, h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    /* main match header */
    .match-header {
        font-size: 28px;
        font-weight: bold;
        color: #ffffff !important;
        margin-bottom: 20px;
    }

    /* score containers */
    .score-card {
        padding: 20px;
        text-align: center;
        border-radius: 4px;
        margin-bottom: 15px;
    }
    
    .red-card {
        background-color: #d32f2f;
    }

    .blue-card {
        background-color: #0288d1;
    }

    .winner-card {
        background-color: #fbc02d;
    }

    .winner-card * {
        color: #000000 !important;
    }

    .score-title {
        font-size: 24px;
        font-weight: bold;
        text-transform: uppercase;
    }

    .score-number {
        font-size: 72px;
        font-weight: 900;
        line-height: 1;
    }

    /* breakdown table styling */
    .breakdown-row {
        background-color: #e0e0e0;
        color: #111111 !important;
        font-weight: bold;
        font-size: 20px;
        padding: 8px 0;
        text-align: center;
        margin-bottom: 4px;
        border-radius: 2px;
    }

    /* timer display box */
    .phase-timer-box {
        padding: 20px;
        text-align: center;
        border-radius: 8px;
        font-weight: bold;
        margin-bottom: 20px;
        transition: background-color 0.5s ease;
    }

    .phase-shooting {
        background-color: #d32f2f;
    }

    .phase-moving {
        background-color: #0288d1;
    }

    .timer-text {
        font-size: 50px;
        margin-top: 5px;
    }

    .phase-text {
        font-size: 22px;
        text-transform: uppercase;
    }

    /* bin counter card */
    .bin-card {
        background-color: #1a1d24;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        margin-bottom: 10px;
        font-size: 20px;
        font-weight: bold;
    }

    /* default button styling - black background with white text */
    .stApp div[data-testid="stButton"] > button {
        background-color: #000000 !important;
        border: 1px solid #333333 !important;
        font-size: 22px !important;
        font-weight: bold !important;
        height: 50px !important;
    }

    .stApp div[data-testid="stButton"] > button * {
        color: #ffffff !important;
        font-size: 22px !important;
        font-weight: bold !important;
    }

    .stApp div[data-testid="stButton"] > button:hover {
        background-color: #1a1a1a !important;
        border-color: #555555 !important;
    }

    /* minus button styling - black button, red minus sign font */
    .minus-btn div[data-testid="stButton"] > button {
        background-color: #000000 !important;
    }

    .minus-btn div[data-testid="stButton"] > button * {
        color: #ff4d4d !important;
        font-size: 28px !important;
        font-weight: 900 !important;
    }

    /* plus button styling - black button, green plus sign font */
    .plus-btn div[data-testid="stButton"] > button {
        background-color: #000000 !important;
    }

    .plus-btn div[data-testid="stButton"] > button * {
        color: #00e676 !important;
        font-size: 28px !important;
        font-weight: 900 !important;
    }
</style>
""", unsafe_allow_html=True)

# initialize session state
if "r_b1" not in st.session_state: st.session_state.r_b1 = 0
if "r_b2" not in st.session_state: st.session_state.r_b2 = 0
if "r_b3" not in st.session_state: st.session_state.r_b3 = 0
if "b_b1" not in st.session_state: st.session_state.b_b1 = 0
if "b_b2" not in st.session_state: st.session_state.b_b2 = 0
if "b_b3" not in st.session_state: st.session_state.b_b3 = 0
if "show_results" not in st.session_state: st.session_state.show_results = False
if "timer_running" not in st.session_state: st.session_state.timer_running = False
if "time_remaining" not in st.session_state: st.session_state.time_remaining = 100

# score calc
def calculate_product_score(bin_1, bin_2, bin_3):
    metrics = [bin_1, bin_2, bin_3]
    total = 1
    for m in metrics:
        total *= (m if m != 0 else 1)
    return total

# determine phase info based on time
def get_phase_info(time_left):
    if time_left > 80:
        return "Shooting Phase I", "phase-shooting"
    elif time_left > 60:
        return "Moving Phase I", "phase-moving"
    elif time_left > 40:
        return "Shooting Phase II", "phase-shooting"
    elif time_left > 20:
        return "Moving Phase II", "phase-moving"
    elif time_left > 0:
        return "Shooting Phase III", "phase-shooting"
    else:
        return "Match Complete", "phase-moving"

# callbacks for bin increment/decrement
def inc_bin(key):
    st.session_state[key] += 1

def dec_bin(key):
    if st.session_state[key] > 0:
        st.session_state[key] -= 1

# sidebar setup
st.sidebar.header("Match Settings")
qual_num = st.sidebar.number_input("Qualification Match #", min_value=1, value=1, step=1)
total_quals = st.sidebar.number_input("Total Qualification Matches", min_value=1, value=16, step=1)

st.markdown(
    f'<div class="match-header">Match Results &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Qualification {qual_num} of {total_quals}</div>', 
    unsafe_allow_html=True
)

# team input columns
col_red_teams, col_center, col_blue_teams = st.columns([1.2, 2, 1.2])

with col_red_teams:
    st.subheader("Red Alliance")
    red_team1 = st.text_input("Red Team 1 Name", value="Insert Team #")
    red_team2 = st.text_input("Red Team 2 Name", value="Insert Team #")

with col_blue_teams:
    st.subheader("Blue Alliance")
    blue_team1 = st.text_input("Blue Team 1 Name", value="Insert Team #")
    blue_team2 = st.text_input("Blue Team 2 Name", value="Insert Team #")

# timer section in center
with col_center:
    st.markdown("### Match Timer & Phase")
    
    timer_placeholder = st.empty()
    
    phase_name, phase_class = get_phase_info(st.session_state.time_remaining)
    mins, secs = divmod(st.session_state.time_remaining, 60)
    timer_placeholder.markdown(f"""
        <div class="phase-timer-box {phase_class}">
            <div class="phase-text">{phase_name}</div>
            <div class="timer-text">{mins:02d}:{secs:02d}</div>
        </div>
    """, unsafe_allow_html=True)

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("Start Timer", use_container_width=True):
            st.session_state.timer_running = True
            st.session_state.show_results = False
    with btn_col2:
        if st.button("Reset Timer", use_container_width=True):
            st.session_state.timer_running = False
            st.session_state.time_remaining = 100
            st.rerun()

    # timer loop handler
    if st.session_state.timer_running and st.session_state.time_remaining > 0:
        time.sleep(1)
        st.session_state.time_remaining -= 1
        if st.session_state.time_remaining == 0:
            st.session_state.timer_running = False
        st.rerun()

st.markdown("---")

# custom bin counter without showing score numbers
def render_bin_counter(bin_name, state_key):
    st.markdown(f"<div class='bin-card'>{bin_name}</div>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        st.markdown('<div class="minus-btn">', unsafe_allow_html=True)
        st.button("➖", key=f"dec_{state_key}", on_click=dec_bin, args=(state_key,), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with b2:
        st.markdown('<div class="plus-btn">', unsafe_allow_html=True)
        st.button("➕", key=f"inc_{state_key}", on_click=inc_bin, args=(state_key,), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# scoring inputs section
st.markdown("### Scoring Inputs")
sc_col1, sc_col2 = st.columns(2)

with sc_col1:
    st.markdown("<h4 style='color: #d32f2f !important;'>Red Alliance Bins</h4>", unsafe_allow_html=True)
    r1, r2, r3 = st.columns(3)
    with r1: render_bin_counter("Bin 1", "r_b1")
    with r2: render_bin_counter("Bin 2", "r_b2")
    with r3: render_bin_counter("Bin 3", "r_b3")

with sc_col2:
    st.markdown("<h4 style='color: #0288d1 !important;'>Blue Alliance Bins</h4>", unsafe_allow_html=True)
    b1, b2, b3 = st.columns(3)
    with b1: render_bin_counter("Bin 1", "b_b1")
    with b2: render_bin_counter("Bin 2", "b_b2")
    with b3: render_bin_counter("Bin 3", "b_b3")

st.markdown("---")

# reveal results button
if st.button("End of Match", use_container_width=True):
    st.session_state.show_results = True

# results section
if st.session_state.show_results:
    red_total = calculate_product_score(st.session_state.r_b1, st.session_state.r_b2, st.session_state.r_b3)
    blue_total = calculate_product_score(st.session_state.b_b1, st.session_state.b_b2, st.session_state.b_b3)

    sc_red, sc_blue, sc_winner = st.columns([1, 1, 1])

    with sc_red:
        st.markdown(f"""
            <div class="score-card red-card">
                <div class="score-title">Red</div>
                <div class="score-number">{red_total}</div>
            </div>
        """, unsafe_allow_html=True)

    with sc_blue:
        st.markdown(f"""
            <div class="score-card blue-card">
                <div class="score-title">Blue</div>
                <div class="score-number">{blue_total}</div>
            </div>
        """, unsafe_allow_html=True)

    with sc_winner:
        if blue_total > red_total:
            winner_text = "BLUE WINNER"
        elif red_total > blue_total:
            winner_text = "RED WINNER"
        else:
            winner_text = "TIE MATCH"

        st.markdown(f"""
            <div class="score-card winner-card">
                <div class="score-title">Result</div>
                <div class="score-number" style="font-size: 36px; padding-top: 18px;">{winner_text}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("### Match Breakdown Summary")
    row_labels = ["Bin 1", "Bin 2", "Bin 3"]
    red_vals = [st.session_state.r_b1, st.session_state.r_b2, st.session_state.r_b3]
    blue_vals = [st.session_state.b_b1, st.session_state.b_b2, st.session_state.b_b3]

    for label, r_val, b_val in zip(row_labels, red_vals, blue_vals):
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            st.markdown(f"<div class='breakdown-row'>{r_val}</div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='breakdown-row'>{label}</div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='breakdown-row'>{b_val}</div>", unsafe_allow_html=True)