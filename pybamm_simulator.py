import streamlit as st
import pybamm 
import pybamm_main

st.set_page_config(layout="wide")
st.title("Select Battery Cycler Procedure")

columns_main = ["Mode", "Type", "Value", "End Mode", "End operator", "End Value", "Maximum Time (s)"]
options_mode = ["Charge", "Discharge", "Rest"]   ##"Waveform"
options_type = ['Current', 'Power']
options_end_type = ['Voltage', 'Current']
options_end_sign = ['>=', '<=', '=', '<', '>']

# Initialize session state
if "row_ids" not in st.session_state:
    st.session_state.row_ids = [0]  # Start with one row (ID = 0)
    st.session_state.next_id = 1    # To keep unique keys for new rows


if "hold_confirm" not in st.session_state:
    st.session_state.hold_confirm=0

if "c_rate" not in st.session_state:
    st.session_state.c_rate=3.2

if "temp" not in st.session_state:
    st.session_state.temp=298

value = 0.0

# Function to render a row
def create_row(row_id):
    cols = st.columns(len(columns_main) + 1)
    selected0 = cols[0].selectbox(columns_main[0], options=options_mode, key=f'row{row_id}_0')
    selected1 = cols[1].selectbox(columns_main[1], options=options_type, key=f'row{row_id}_1')
    selected2 = cols[2].number_input(columns_main[2], value=value, key=f'row{row_id}_2')
    selected3 = cols[3].selectbox(columns_main[3], options=options_end_type, key=f'row{row_id}_3')
    selected4 = cols[4].selectbox(columns_main[4], options=options_end_sign, key=f'row{row_id}_4')
    selected5 = cols[5].number_input(columns_main[5], value=value, key=f'row{row_id}_5')
    selected6 = cols[6].number_input(columns_main[6], value=value, key=f'row{row_id}_6')

    # Delete button
    if cols[7].button("Delete", key=f'delete_{row_id}'):
        st.session_state.row_ids.remove(row_id)
        for i in range(7):
            st.session_state.pop(f'row{row_id}_{i}', None)
        st.rerun()

    return [selected0, selected1, selected2, selected3, selected4, selected5, selected6]

# Create rows dynamically
st.session_state.selections = []
for row_id in st.session_state.row_ids:
    st.session_state.selections.append(create_row(row_id))

temperature_input= st.number_input("Temperature", value=298.3, key='tem', label_visibility="visible")
temperature= float(temperature_input)
c_rate= st.number_input("C-rate", value=3.2, key='ah', label_visibility="visible")
s_o_c= st.number_input("Initial SOC in fraction", value=0.5, key='soc', label_visibility="visible")

# Add row button
if st.button("+ Add row"):
    new_id = st.session_state.next_id
    st.session_state.row_ids.append(new_id)
    st.session_state.next_id += 1
    st.rerun()

# Confirm button
if st.button("Confirm"):
    st.write("You selected:")
    for i, row_id in enumerate(st.session_state.row_ids):
        row = [st.session_state.get(f'row{row_id}_{j}') for j in range(7)]
        st.write(f"Row {i+1}: {row}")
    st.session_state.hold_confirm=1

if st.session_state.hold_confirm==1:
    if st.button("Generate plot and data"):
        print("Selecetions", st.session_state.selections)
        figure= pybamm_main.generate_model(st.session_state.selections, temperature, c_rate, s_o_c)
        st.plotly_chart(figure)

        with open("dummy.pkl", "rb") as f:
            pkl_bytes = f.read()
        st.download_button(
            label="Download Pickle File",
            data=pkl_bytes,
            file_name="dummy.pkl",
            mime="application/octet-stream"
        )
