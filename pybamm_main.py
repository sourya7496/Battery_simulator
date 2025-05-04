import pybamm 
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def process_temperatures(t):
    t_arr=[]
    for i in range(len(t)):
        t_arr.append(t[i].mean())

    return t_arr


def generate_experiment(single_line, line_arr):
    print("Single line")
    if single_line[0]=='Charge' or single_line[0]=='Discharge':
        if single_line[1]== 'Current':
            if single_line[3]== 'Voltage':
                line= f"{single_line[0]} at {single_line[2]} A for {single_line[6]} seconds or until {single_line[5]} V"
            if single_line[3]== 'SOC':
                line= f"{single_line[0]} at {single_line[2]} A for {single_line[6]} seconds or until {single_line[5]} SOC"
        if single_line[1]== 'Power':
            if single_line[3]== 'Voltage':
                line= f"{single_line[0]} at {single_line[2]} W for {single_line[6]} seconds or until {single_line[5]} V"
            if single_line[3]== 'SOC':
                line= f"{single_line[0]} at {single_line[2]} W for {single_line[6]} seconds or until {single_line[5]} SOC"
    if single_line[0]=='Rest':
        line= f"{single_line[0]} for {single_line[6]} seconds"
    print(line)
    line_arr.append(line)
    return line_arr

def generate_model(selections, t, c, soc):
    print(selections)
    line_arr=[]
    for i in range(len(selections)):
        line_arr= generate_experiment(selections[i], line_arr)
        print(line_arr)

    model = pybamm.lithium_ion.DFN()
    param = model.default_parameter_values

# Set custom cell capacity (e.g., 3.2 Ah)
    param.update({
        f"Nominal cell capacity [A.h]": c,
        f'Upper voltage cut-off [V]': 4.5,
        f'Lower voltage cut-off [V]': 3.0,
        f"Initial temperature [K]": t,
    })
    experiment = pybamm.Experiment(line_arr)
        # [
        #     "Discharge at C/10 for 10 hours or until 3.3 V",
        #     "Rest for 1 hour",
        #     "Charge at 1 A until 4.1 V",
        #     "Hold at 4.1 V until 50 mA",
        #     "Rest for 1 hour",
        # ]
    print("SOC=", soc)
    sim = pybamm.Simulation(model, experiment=experiment)
    sim.solve(initial_soc=soc)
    solution = sim.solution
    save_file= solution.save("dummy.pkl")
    time = solution["Time [h]"].entries
    voltage = solution["Voltage [V]"].entries
    current = solution["Current [A]"].entries
    dis_cap= solution["Discharge capacity [A.h]"].entries
    temperature_2= solution["Cell temperature [K]"].entries
    temperature= process_temperatures(temperature_2)

    
    resistance= solution["Resistance [Ohm]"].entries

    # Plot
    fig = make_subplots(rows=2, cols=2, subplot_titles=(
        "Voltage(V)",  "Cell Temperature(K)", "Current(A)", "Discharge Capacity(Ah)"))

    # Plot Voltage
    fig.add_trace(go.Scatter(x=time, y=voltage, name="Voltage", line=dict(color='blue')),
                row=1, col=1)


    # Plot Temperature
    fig.add_trace(go.Scatter(x=time, y=temperature, name="Temperature(K)", line=dict(color='red')),
                row=1, col=2)

    # Plot Current
    fig.add_trace(go.Scatter(x=time, y=current, name="Current", line=dict(color='orange')),
                row=2, col=1)
    
    fig.add_trace(go.Scatter(x=time, y=dis_cap, name="Discharge Capacity", line=dict(color='pink')),
                row=2, col=2)
    


    # Update layout
    fig.update_layout(
        height=1200, width=1000,
        xaxis_title= "Time (hrs)",
        title_text="Battery Simulation Summary",
        showlegend=False
    )
    fig.update_xaxes(matches='x')

    return fig

