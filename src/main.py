import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.append(str(PROJECT_DIR))

from data.data import get_data_df

from taipy.gui import Gui, Markdown
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import string, requests
from string import Template
from icecream import ic
import datetime as dt


def dt_prefix():
    return f"{dt.datetime.now().strftime('%H:%M:%S')} |> "


ic.configureOutput(prefix=dt_prefix, includeContext=True)
ic.lineWrapWidth = 150

df = get_data_df()
counties = requests.get(
    "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
).json()

# Fix IBRC_Geo_ID. See notebooks/eda.ipynb
geoid_category_map = {
    old_cat: f"0{old_cat[:-1]}"
    for old_cat in df.IBRC_Geo_ID.dtype.categories
    if old_cat[-1] == " "
}
df["IBRC_Geo_ID"] = df.IBRC_Geo_ID.cat.rename_categories(geoid_category_map)

# Enhance NAICS Description
naics_category_map = {
    old_cat: old_cat.lstrip(string.punctuation + string.whitespace)
    for old_cat in df["NAICS Description"].cat.categories
}
df["NAICS Description"] = df["NAICS Description"].cat.rename_categories(
    naics_category_map
)

# Set Year category as ordered
df["Year"] = df.Year.astype(
    pd.CategoricalDtype(sorted(df.Year.cat.categories), ordered=True)
)

# Dicts of codes to names
geoid_to_county_name = (
    df.drop_duplicates("IBRC_Geo_ID").set_index("IBRC_Geo_ID")["Description"].to_dict()
)
naics_code_to_industry_name = (
    df.drop_duplicates("NAICS Code")
    .set_index("NAICS Code")["NAICS Description"]
    .to_dict()
)
lq_code_to_lq_name = (
    df.drop_duplicates("PA-LQ_Code")
    .set_index("PA-LQ_Code")["PA-LQ_Code_Description"]
    .to_dict()
)

######################################## MAP ########################################
year_list = sorted(df.Year.unique().tolist())
selected_year = year_list[-1]

industry_code_list = list(naics_code_to_industry_name.items())
industry_code_list.sort(key=lambda x: x[1])
selected_industry_code = industry_code_list[0][0]

lq_code_list = [("300", "LQ"), ("200", "CLQ")]
selected_lq_code = lq_code_list[1][0]


def create_map_fig(industry_code, lq_code, year):
    _df = df[
        (df["NAICS Code"] == industry_code)
        & (df["PA-LQ_Code"] == lq_code)
        & (df["Year"] == year)
    ]
    fig = px.choropleth_mapbox(
        _df,
        geojson=counties,
        locations="IBRC_Geo_ID",
        color="PA-LQ_Data",
        color_continuous_scale="Reds",
        mapbox_style="carto-positron",
        zoom=3,
        center={"lat": 37.0902, "lon": -95.7129},
        opacity=0.5,
        hover_data="Description",
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


map_fig = create_map_fig(selected_industry_code, selected_lq_code, selected_year)

selected_indices = []
mean_value = 0

map_md = """
## Map 🗺️

<map_selectors|layout|columns=2 1 1|

<|{selected_industry_code}|selector|lov={industry_code_list}|value_by_id|dropdown|filter|label=Industry|class_name=fullwidth|>

<|{selected_lq_code}|selector|lov={lq_code_list}|value_by_id|dropdown|label=Metric|class_name=fullwidth|>

<|{selected_year}|selector|lov={year_list}|dropdown|label=Year|class_name=fullwidth|>

|map_selectors>

### Mean Value of Selection: <|{round(mean_value,2)}|text|raw|>

<|chart|figure={map_fig}|selected={selected_indices}|>
"""

######################################## LINE CHART ########################################
color_var_options = ["NAICS Code", "PA-LQ_Code"]
selected_color_var = color_var_options[1]

geoid_list = list(geoid_to_county_name.items())
geoid_list.sort(key=lambda x: x[1])
selected_geoid = geoid_list[0][0]


def create_line_fig(color_var, geoid, *, industry_code=None, lq_code=None):
    _df = df[df["IBRC_Geo_ID"] == geoid]
    if industry_code:
        _df = _df[_df["NAICS Code"] == industry_code]
    if lq_code:
        _df = _df[_df["PA-LQ_Code"] == lq_code]

    title = f"Location Quotients for {geoid_to_county_name.get(geoid)}"
    if color_var == "PA-LQ_Code":
        _df = _df[_df["PA-LQ_Code"].isin(["300", "200"])]
        title += (
            f"<br><sup>Industry: {naics_code_to_industry_name.get(industry_code)}</sup>"
        )
        fig = px.line(
            _df,
            x="Year",
            y="PA-LQ_Data",
            color="PA-LQ_Code_Description",
            hover_data=color_var,
            title=title,
            labels={"PA-LQ_Code_Description": "Metric"},
        )
        fig.update_layout(
            yaxis_title="Value",
        )
    else:
        title += f"<br><sup>LQ: {lq_code_to_lq_name.get(lq_code)}</sup>"
        fig = px.line(
            _df,
            x="Year",
            y="PA-LQ_Data",
            color=color_var,
            hover_data="NAICS Description",
            title=title,
        )

    return fig


line_fig = create_line_fig(
    selected_color_var, selected_geoid, industry_code=selected_industry_code
)


line_md = """
## Metrics over Time 📈

<lc_selectors|layout|columns=1 1|

<|{selected_industry_code}|selector|lov={industry_code_list}|value_by_id|dropdown|filter|label=Industry|class_name=fullwidth|active={selected_color_var!="NAICS Code"}|>

<|{selected_geoid}|selector|lov={geoid_list}|value_by_id|dropdown|filter|label=County|class_name=fullwidth|>

|lc_selectors>

<|chart|figure={line_fig}|>
"""

######################################## MAIN PAGE ########################################

template_md = Template(
    """
<|toggle|theme|>

<|container|

# 🏭 Measuring Industrial Agglomeration

<intro_card|card|

## A New Metric for Industrial Agglomeration

Traditionally, industrial agglomeration is measured using a metric called 
Location Quotient (LQ). This metric is simple but has its limits. 
For example, less populated and remote counties will sometimes have high LQs, 
despite having low employment counts. 
This <a href="https://www.statsamerica.org/downloads/user-guides/user-guide-PALQ.pdf" target="_blank">paper</a> 
proposes a new metric to resolve these issues called 
Proximity Adjusted Location Quotients (PA-LQ or CLQ).

<br/>

You can explore LQs and CLQs for different industries and counties below and notice
the differences in the results.


|intro_card>

<br/>

<map_card|card|

$map_md

|map_card>

<br/>

<line_card|card|

$line_md

|line_card>

<br/>

<data_card|card|

## View Data 🗃️

<|Click to expand|expandable|expanded=False|
<|{df}|table|filter|>
|>

|data_card>

|>
"""
)

md = Markdown(template_md.substitute(map_md=map_md, line_md=line_md))

map_fig_selectors = {"selected_year", "selected_industry_code", "selected_lq_code"}
line_fig_selectors = {
    "selected_color_var",
    "selected_geoid",
    "selected_industry_code",
    "selected_lq_code",
}


def on_change(state, var_name, var_value):
    if isinstance(var_value, go.Figure):
        ic(var_name)
    else:
        ic(var_name, var_value)

    if var_name in map_fig_selectors:
        state.map_fig = create_map_fig(
            state.selected_industry_code, state.selected_lq_code, state.selected_year
        )
    if var_name in line_fig_selectors:
        if state.selected_color_var == "NAICS Code":
            state.line_fig = create_line_fig(
                state.selected_color_var,
                state.selected_geoid,
                lq_code=state.selected_lq_code,
            )
        elif state.selected_color_var == "PA-LQ_Code":
            state.line_fig = create_line_fig(
                state.selected_color_var,
                state.selected_geoid,
                industry_code=state.selected_industry_code,
            )

    if var_name == "selected_indices":
        _df = df[
            (df["NAICS Code"] == state.selected_industry_code)
            & (df["PA-LQ_Code"] == state.selected_lq_code)
            & (df["Year"] == state.selected_year)
        ]
        indices = state.selected_indices
        if indices:
            state.mean_value = _df.iloc[indices]["PA-LQ_Data"].mean()
        else:
            state.mean_value = 0


if __name__ == "__main__":
    gui = Gui(page=md)
    gui_properties = {
        "dark_mode": False,
        "title": "🏭 Measuring Industrial Agglomeration",
        "run_browser": False,
    }
    gui.run(**gui_properties)
