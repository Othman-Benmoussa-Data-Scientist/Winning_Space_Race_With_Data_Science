# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)
app.title = "SpaceX Launch Records"

# Options pour le dropdown
site_options = [{"label": "All Sites", "value": "ALL"}] + [
    {"label": site, "value": site} for site in sorted(spacex_df["Launch Site"].unique())
]

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),

        # TASK 1: Dropdown sélection du site
        dcc.Dropdown(
            id="site-dropdown",
            options=site_options,
            value="ALL",
            placeholder="Select a Launch Site",
            clearable=False,
            style={"width": "60%", "margin": "0 auto"},
        ),
        html.Br(),

        # TASK 2: Pie chart des succès
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),

        html.P("Payload range (Kg):", style={"textAlign": "center"}),

        # TASK 3: Range slider pour la plage de payload
        dcc.RangeSlider(
            id="payload-slider",
            min=min_payload,
            max=max_payload,
            value=[min_payload, max_payload],
            step=1000,
            marks={
                int(min_payload): str(int(min_payload)),
                int((min_payload + max_payload) / 2): str(int((min_payload + max_payload) / 2)),
                int(max_payload): str(int(max_payload)),
            },
            tooltip={"placement": "bottom", "always_visible": False},
        ),
        html.Br(),

        # TASK 4: Nuage de points (payload vs succès)
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ],
    style={"maxWidth": "1100px", "margin": "0 auto", "padding": "10px 20px"},
)

# TASK 2:
# Callback: entrée = site-dropdown, sortie = success-pie-chart
@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value"),
)
def update_pie(selected_site):
    if selected_site == "ALL":
        # Total des succès par site
        df_group = (
            spacex_df.groupby("Launch Site", as_index=False)["class"].sum()
            .rename(columns={"class": "Successes"})
        )
        fig = px.pie(
            df_group,
            values="Successes",
            names="Launch Site",
            title="Total Successful Launches by Site",
        )
    else:
        # Pour un site spécifique: succès vs échecs
        df_site = spacex_df[spacex_df["Launch Site"] == selected_site]
        # value_counts sur la classe (1=success, 0=failure)
        counts = df_site["class"].value_counts().rename(index={1: "Success", 0: "Failure"}).reset_index()
        counts.columns = ["Outcome", "Count"]
        fig = px.pie(
            counts,
            values="Count",
            names="Outcome",
            title=f"Launch Outcomes for {selected_site}",
        )
    return fig

# TASK 4:
# Callback: entrées = site-dropdown & payload-slider, sortie = success-payload-scatter-chart
@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [Input("site-dropdown", "value"), Input("payload-slider", "value")],
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    # Filtrage par payload
    mask_payload = (spacex_df["Payload Mass (kg)"] >= low) & (spacex_df["Payload Mass (kg)"] <= high)
    df_filtered = spacex_df[mask_payload].copy()

    # Filtrage site si nécessaire
    if selected_site != "ALL":
        df_filtered = df_filtered[df_filtered["Launch Site"] == selected_site]

    fig = px.scatter(
        df_filtered,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category" if "Booster Version Category" in df_filtered.columns else None,
        hover_data=["Launch Site", "Booster Version"] if "Booster Version" in df_filtered.columns else ["Launch Site"],
        title=("Correlation between Payload and Success" if selected_site == "ALL"
               else f"Correlation between Payload and Success for {selected_site}"),
        labels={"class": "Launch Outcome (1=Success, 0=Failure)"},
    )
    return fig

# Run the app
if __name__ == "__main__":
    # app.run_server(debug=True)  # Optionnel en dev
    app.run(port=8080)
