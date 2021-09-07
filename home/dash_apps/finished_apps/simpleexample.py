import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash

#%%APP

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

external_stylesheets = [
    'https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css',
    '/style.css'
]

external_scripts = [
    'https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js'
]

app = DjangoDash('Consumer-expenditures', external_stylesheets=external_stylesheets)

#%% DATA PACKAGES
import json
import os
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
from urllib.request import urlopen
from dash.dependencies import Output, Input
import numpy as np
import time

#%% Load Data

"""
Get the initial files to extract the data.
The data will be used in the dashboard.
"""

dirname = os.path.dirname(__file__)

# Fetch and set US states geojson.
with urlopen(
        'https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json') as response:
    states = json.load(response)

# PICKLE
# time0 = time.time()
# expenditures = pd.read_pickle(os.path.join(
#     dirname, 
#     '../assets/consumer_expenditures/final_triangulation_oscar_variables_fixed_pickle.pkl'))
# expenditures.insert(1, 'Unnamed: 0.1', 0)
# time1 = time.time()
# print("THIS IS THE TIME TO TAKES READING FILE", time1-time0)

# CSV
time0 = time.time()
expenditures = pd.read_csv(os.path.join(
    dirname, 
    '../assets/consumer_expenditures/final_triangulation_oscar_variables_fixed_dash.csv'))
time1 = time.time()
print("THIS IS THE TIME TO TAKES READING FILE", time1-time0)

time0 = time.time()
expenditures['RACE ETNICITY'] = expenditures['RACE ETNICITY'].apply(lambda x: 'White' if x == 'Non-Hispanic - N/A - White' 
                                                else 'Mexican' if x =='Hispanic - Mexican - White'
                                                else 'Cuban' if x == 'Hispanic - Cuban - White'
                                                else 'Puerto Rican' if x =='Hispanic - Puerto Rican - White'
                                                else 'Other Hispanic' if x == 'Hispanic - Other - White'
                                                else 'Asian' if x =='Non-Hispanic - N/A - Asian'
                                                else 'Black' if x == 'Non-Hispanic - N/A - Black'
                                                else 'Non-Hispanic Multirace' if x =='Non-Hispanic - N/A - Multirace'
                                                else 'Native American' if x =='Non-Hispanic - N/A - Native American'
                                                else 'Pacific Islander')
time1 = time.time()
print("THIS IS THE TIME TO DOING APPLY", time1-time0)

"""
Prepare data frames that will be processed to be inserted into graphics and maps.
And set configuration data for insertion in the dashboard. 
"""

# Color scale to be used on the map. Specifically in the grouping of employees by companies
color_scale = 'blues'

"""
Create graphic object like maps and bar charts.
Add the graphic object data to the Figure.
The Figure will be inserted in the layout page.
"""

#%% Filter function
dropdown_values = (None, None, None, None)

def filter_data(expenditures,
                food_type = None, 
                gender = None, 
                age = None, 
                race = None, 
                income = None):
    """
    Filter rows by employees range
    :param rows: Companies rows
    :param employees_ranges: Employees ranges
    :return:
    """
    filtered = expenditures

    relevant_columns = list(filtered.columns[1:14])

    if food_type:
        food_type_zip_data = ["Total Category "+i for i in food_type]
        filtered = filtered.filter(relevant_columns + food_type + food_type_zip_data)
    if gender:
        filtered = filtered[filtered['SEX'].isin(gender)]
    if age:
        filtered = filtered[filtered['AGE'].isin(age)]
    if race:
        filtered = filtered[filtered['RACE ETNICITY'].isin(race)]
    if income:
        filtered = filtered[filtered['HOUSEHOLD INCOME'].isin(income)]

    return filtered

#%% Us Brev Function

def US_state_abrev(to_abreviation = True,
                   vector_or_list = False,
                   fips = False,
                   to_fip = True):
    if fips:
        value = 'FIPS'
    else:
        value = 'Name'

    zip_db = pd.read_csv(os.path.join(dirname, 
                                        '../assets/consumer_expenditures/codes_final.csv'))

    zip_db.FIPS = zip_db.FIPS.astype(str).str.zfill(2)

    if not to_abreviation:
        if to_fip:
            zip_dict = zip_db.set_index('Postal Code')[value].to_dict()
            return zip_dict
        else:
            zip_dict = zip_db.set_index(value)['Postal Code'].to_dict()

            if not vector_or_list:
                return zip_dict
            else:
                change_abreviation = lambda t: zip_dict[t]
                vfunc = np.vectorize(change_abreviation)
                return vfunc
    else:
        zip_dict = zip_db.set_index('Name')['Postal Code'].to_dict()
    
        if not vector_or_list:
            return zip_dict
        else:
            change_abreviation = lambda t: zip_dict[t]
            vfunc = np.vectorize(change_abreviation)
            return vfunc

#%% Number to string function

def number_to_str(number):
    
    def apply_str(number, value):
        if value == 1000000:
            indicator = "M"
        else:
            indicator = "K"           
        number = np.round((number/value),1)
        if isinstance(number, float):
             number_after_coma = str(number).split(".")[1]
             if number_after_coma == "0":
                 number = str(number).split(".")[0]+indicator
             else:
                 number = str(number).split(".")[0]+"."+str(number).split(".")[1]+indicator
        return number
    
    if len(str(number).split(".")[0]) <= 3:
        number = str(number)
    else:
        if len(str(number).split(".")[0]) >= 7:
            number = apply_str(number, 1000000)
        else:
            number = apply_str(number, 1000)
            
                 
    return number

#%% Consumption chart

def most_consumption_chart(
    food_type, gender, age, 
    race, income, 
    soft_filter):

    time0 = time.time()
    """
    Create top state/zip_code consumption chart 
    :param soft_filter:
    :param industries: Iterable with industries or None for all
    :param employees_ranges: Tuple with ranges or None for all (e.g. (1, 50))
    :param name_states: Iterable with the state or None for all
    :param locality_names: Iterable with the localities or None for all
    :return: Figure instance with the chart
    """
    time_preparation0 = time.time()

    time_bar_before_if0 = time.time()
    #food type must be a list
    graph_data = expenditures

    graph_data = filter_data(graph_data, food_type, gender, age, race, income) 
    
    graph_data.zip_code = graph_data.zip_code.astype(int)
    
    graph_data.zip_code = graph_data.zip_code.astype(str).str.zfill(5)

    US_fips =US_state_abrev(to_abreviation = False,
                vector_or_list = False,
                fips = True, to_fip = False)

    if not food_type:
        food_type = list(graph_data.columns[17:36])
    if not gender:
        gender = list(graph_data.SEX.unique())
    if not age:
        age = list(graph_data.AGE.unique())
    if not race:
        race = list(graph_data['RACE ETNICITY'].unique())
    if not income:
        income = list(graph_data['HOUSEHOLD INCOME'].unique())

    ######################################
    time_bar_before_if1 = time.time()
    print("Tiempo antes del if en top bar", time_bar_before_if1-time_bar_before_if0)

    if soft_filter and soft_filter['State']:
        fip = soft_filter['State']
        graph_data = graph_data[graph_data['STATE'].isin([US_fips[fip]])]

        total_category_soft_filter = ["Total Category "+i for i in food_type]
        graph_data = graph_data.groupby('zip_code').mean().reset_index()[
            ['zip_code']+total_category_soft_filter] 
        
        graph_data['Consumption of %s' % ' & '.join(total_category_soft_filter)] = graph_data[total_category_soft_filter] \
            .apply(lambda x: sum(x), axis = 1)

        graph_data = graph_data.sort_values(
            'Consumption of %s' % ' & '.join(total_category_soft_filter), 
            ascending = False).head(10).sort_values(
                by = 'Consumption of %s' % ' & '.join(total_category_soft_filter),    
                )

        y =  graph_data['zip_code']
        
        x = graph_data['Consumption of %s' % ' & '.join(total_category_soft_filter)]
         
        text = x.apply(lambda x: "$ "+number_to_str(int(np.round(x))))

        xaxis_title = "Weekly expenditure per capita <br> in dollars for chosen food."
        yaxis_title = "Zip codes"

    else:
        graph_data['Consumption of %s' % ' & '.join(food_type)] = graph_data[food_type].apply(lambda x: sum(x), axis = 1)

        graph_data = graph_data.groupby(['STATE']).mean().reset_index()[[
            'STATE',
            'Consumption of %s' % ' & '.join(food_type)]].sort_values(
                by = 'Consumption of %s' % ' & '.join(food_type),
                ascending= False).head(10).sort_values(
                by = 'Consumption of %s' % ' & '.join(food_type),    
                )

        us_dict = US_state_abrev(to_abreviation = False)

        y = graph_data['STATE'].apply(lambda x: us_dict[x])

        x = graph_data['Consumption of %s' % ' & '.join(food_type)]
        text = x.apply(lambda x: "$ "+str(np.round(x,2)))

        xaxis_title = "Weekly total individual expenditure <br> in dollars for chosen food."
        yaxis_title = "States"

    time_preparation1 = time.time()
    print("Tiempo de preparacón data Top bar", time_preparation1 - time_preparation0)

    creation_bar_time0 = time.time()
    # Create chart
    fig = go.Figure(go.Bar(
        x = x,
        y = y,
        text =text,
        textposition = 'auto',
        marker = dict(
            color = '#ba5062'
        ),
        orientation='h'))

    # Remove margins
    fig.update_layout(
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
        height = 500,
        xaxis_title = xaxis_title,
        xaxis_title_font_size = 15,
        yaxis_title = yaxis_title,
        yaxis_title_font_size = 15,
        font=dict(
        family="Mulish, sans-serif")
    )
    creation_bar_time1 = time.time()
    print("Tiempo de creación Top bar", creation_bar_time0 - creation_bar_time1)
    time1 = time.time()

    print("TOP BAR TIME", time1-time0)
    return fig

#%% Map

def consumption_states_map( 
    food_type, 
    gender, 
    age, 
    race, 
    income,
    selected_points,                 
    # soft_filter
    ):
    time0 = time.time()
    """
    Create companies mapbox with the data computed
    :param company_names: Iterable with company names or None for all
    :param industries: Iterable with industries or None for all
    :param employees_ranges: Tuple with ranges or None for all (e.g. (1, 50))
    :param name_states: Iterable with the state or None for all
    :param locality_names: Iterable with the localities or None for all
    :param selected_points:
    :param soft_filter:
    :return:
    """
    # Set companies with locations
    map_data = expenditures

    # Filter rows
    map_data = filter_data(map_data, food_type, gender, age, race, income)

    if not food_type:
        food_type = list(map_data.columns[17:36])
    if not gender:
        gender = list(map_data.SEX.unique())
    if not age:
        age = list(map_data.AGE.unique())
    if not race:
        race = list(map_data['RACE ETNICITY'].unique())
    if not income:
        income = list(map_data['HOUSEHOLD INCOME'].unique())    

    map_data['Consumption of %s' % ' & '.join(food_type)] = map_data[food_type] \
            .apply(lambda x: sum(x), axis = 1)
            
    map_data = map_data.groupby('STATE').mean().reset_index()[[
        'STATE',
        'Consumption of %s' % ' & '.join(food_type),
        ]]

    US_fips =US_state_abrev(to_abreviation = False,
                   vector_or_list = False,
                   fips = True)

    map_data['FIPS'] = map_data['STATE'].apply(lambda x: US_fips[x])

    # Graphic objects

    #fernando append shapes to data then graph them all to have different and more
    #pretty labels, not used here
    data = []
    
    map_data['names'] = map_data['Consumption of %s' % ' & '.join(food_type)] \
        .apply(lambda x: "$ {} Total weekly individual expenditure".format(x))
    
    # names = '''
    #     <i> $ {} Weekly individual expenditure </i> <br>
    # '''.format(employees[0])

    # Create grey scale values grouping by employees range

    us_dict = US_state_abrev(to_abreviation = False)
    heatmap = go.Choroplethmapbox(
                geojson = states,
                locations = map_data.FIPS,
                z = map_data['Consumption of %s' % ' & '.join(food_type)].apply(lambda x: np.round(x,2)),
                colorscale ='blues',
                selectedpoints = selected_points,
                showscale = True,
                colorbar = dict(
                    ticklen = 2,
                    title =  "Weekly total <br> individual <br> expenditure"
                    ),
                text = map_data.STATE.apply(lambda x: '<b>'+us_dict[x]+'</b> <br>').to_list(),
                )

    # Create figure element
    map_figure = go.Figure(heatmap)

    # Update Mapbox settings
    map_figure.update_layout(
        mapbox_style='carto-positron',
        mapbox_zoom=3,
        height=500,
        mapbox_center={'lat': 37.0902, 'lon': -95.7129},
        margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
        clickmode='event+select',
        font=dict(
                family="Mulish, sans-serif")
    )

    time1 = time.time()

    print("MAP TIME", time1-time0)
    return map_figure

#%% stacked bar

def stacked_demo_bar(
    food_types, 
    demo,
    soft_filter):  
    
    time0 = time.time()

    stacked_data = expenditures

    expenditures_cols = list(expenditures.columns)
    relevant_columns = list(stacked_data.columns[2:5])
    food_columns = list(stacked_data.columns[17:36])

    #set demo
    if not demo:
        demo = ['SEX','Percent population for age']
    else:

        demo_index = expenditures_cols.index(demo)
        demo = [demo]+[expenditures_cols[demo_index+1]]

    #set food type columns
    if not food_types:
        food_types = food_columns
        if soft_filter and soft_filter['State']:
            food_types = ["Total Category "+i for i in food_columns]                  
    else:
        if soft_filter and soft_filter['State']:
            food_types = ["Total Category "+i for i in food_types]  
        else:
            food_types

    #have stacked data according to dropdown selection
    stacked_data = stacked_data[
        relevant_columns + demo + food_types]
    #sum consumption of selected food
    stacked_data['Consumption of %s' % ' & '.join(food_types)] = stacked_data[food_types] \
            .apply(lambda x: sum(x), axis = 1)

    #have the total people who consume type of food selected
    stacked_data['%s consumption of %s' % (demo[0] ,' & '.join(food_types))] = \
        stacked_data['Total population']* \
            stacked_data[demo[1]]* \
                stacked_data['Consumption of %s' % ' & '.join(food_types)]
    
    #dict for fips
    US_fips =US_state_abrev(to_abreviation = False,
                vector_or_list = False,
                fips = True, to_fip = False)

    #function to have tops (zip or state)
    def top_location(stacked_data,agrupation):

        variable = 'Consumption of %s' % ' & '.join(food_types)
        top = stacked_data.groupby([agrupation]).mean().reset_index(). \
        sort_values(by = variable,
                    ascending = False).head(10)[agrupation].to_list()
        return top

    #have total for stacked bar
    def have_total(stacked_data,
                    agrupation,
                    variable,
                    state = None):

        total_stateOrzip = stacked_data.groupby(
                demo[0]
                ).mean().reset_index()[
                    [demo[0],
                    variable,
                    ]]
        if state:
            total_stateOrzip.insert(0, agrupation, 'Total %s' % state)
            return total_stateOrzip
        else:
            total_stateOrzip.insert(0, agrupation, 'Total US')
            return total_stateOrzip

    #define final agrupation before concating with total
    def agrupation_graph(
        stacked_data, 
        agrupation,
        variable):

        stacked_data = stacked_data. \
            groupby([agrupation, demo[0]]).mean(). \
                    reset_index()[[
                        agrupation,
                        demo[0],
                        variable,
                        ]]
        return stacked_data

    #have data according softfilter

    if  soft_filter and soft_filter['State']:

        variable = '%s consumption of %s' % (demo[0] ,' & '.join(food_types))
        agrupation = 'zip_code'
        fip = soft_filter['State']
        stacked_data = stacked_data[stacked_data['STATE'].isin([US_fips[fip]])]
        top = top_location(stacked_data, agrupation)

        total_locality_agrupation = have_total(stacked_data,agrupation, variable, US_fips[fip])

        stacked_data = stacked_data[stacked_data[agrupation].isin(top)]
        
        #agrupation by demo
        stacked_data = agrupation_graph(stacked_data, agrupation, variable)
        
        #values can not be sorted
        # stacked_data = stacked_data.sort_values(
        #     by = '%s consumption of %s' % (demo[0] ,' & '.join(food_types)),
        #     ascending = False)

        #fix zipcode
        stacked_data.zip_code = stacked_data.zip_code.astype(int)
        stacked_data.zip_code = stacked_data.zip_code.astype(str).str.zfill(5) 

        #concat with total    
        stacked_data = pd.concat([stacked_data, total_locality_agrupation], axis = 0)

    else:
        agrupation = 'STATE'
        variable = 'Consumption of %s' % ' & '.join(food_types)

        top = top_location(stacked_data, agrupation)   
 
        total_locality_agrupation = have_total(stacked_data,agrupation, variable)

        stacked_data = stacked_data[stacked_data[agrupation].isin(top)]
         #agrupation by demo
        stacked_data = agrupation_graph(stacked_data, agrupation, variable)  

        us_dict = US_state_abrev(to_abreviation = False)
        stacked_data.STATE = stacked_data.STATE.apply(lambda x: us_dict[x])

        #concat with total    
        stacked_data = pd.concat([stacked_data, total_locality_agrupation], axis = 0)

    stacked_data = stacked_data.groupby([stacked_data.columns[0], stacked_data.columns[1]]).agg({stacked_data.columns[2]: 'sum'})
    # Change: groupby state_office and divide by sum
    stacked_data = stacked_data.groupby(level=0).apply(lambda x:
                                                    100 * x / float(x.sum()))
    stacked_data = stacked_data.reset_index()
    
    data = []
    #THIS IS FOR SET THE ORDER IN WHICH BARS ARE STACKED
    if demo[0] == 'SEX':
        stacked_data.SEX = stacked_data.SEX.apply(lambda x: 'Male' if x == 'male' else 'Female')
        variables = ['Male', 'Female', 
            ]

    if demo[0] == 'HOUSEHOLD INCOME':
        variables = ['Less than $10,000','$10,000 to $14,999', '$15,000 to $24,999',
                    '$25,000 to $34,999', '$35,000 to $49,999', '$50,000 to $74,999',
                    '$75,000 to $99,999', '$100,000 to $149,999', '$150,000 to $199,999', 
                    '$200,000 or more', 
            ]

    if demo[0] == 'RACE ETNICITY':    
        variables = [
                    'White', 'Mexican',
                    'Cuban', 'Puerto Rican',
                    'Other Hispanic', 'Asian', 
                    'Black', 'Non-Hispanic Multirace',
                    'Native American', 'Pacific Islander', 
                    ] 

    if demo[0] == 'AGE':
        variables = ['15 to 19 years', '20 - 24 years', '25 - 34 years', '35 - 44 years', '45 - 54 years',
                   '55 - 59 years', '60 - 64 years', '65 - 74 years', '75 - 84 years',
                   '85 years and over']


    #CONVERT ZIP TO STRING OR STATE ABREV TO STATE

    try:
        top = pd.Series(top).apply(lambda x: str(int(x))).str.zfill(5).to_list()
        top = top + ['Total '+US_fips[fip]]
    except:
        top = pd.Series(top).apply(lambda x: us_dict[x]).to_list()
        top = top + ['Total US']


    for variable in variables:
        name = variable

        one_stack_data = stacked_data[stacked_data[stacked_data.columns[1]] == name]
        
        one_stack_data = one_stack_data.set_index(one_stack_data.columns[0])
        one_stack_data = one_stack_data.reindex(top)
        one_stack_data = one_stack_data.reset_index()

        x = one_stack_data[one_stack_data.columns[0]]
        y = one_stack_data[one_stack_data.columns[2]]

        data.append(go.Bar(
            x = x,
            y = y,
            name = name
        ))

    # Create chart
    fig = go.Figure(
        data = data)

    # Remove margins
    fig.update_layout(
        xaxis=dict(type="category"),
        barmode='stack',
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
        height = 400,
        width = 1425,
        font=dict(
        family="Mulish, sans-serif"
    ))

    time1 = time.time()

    print("TIME STACKED BAR", time1-time0)
    return fig

#%%

#%%
app.layout = html.Div(
    className = "row card",
    id = 'graph-1',
    children = [

            html.Div([
                html.H1('CONSUMER EXPENDITURES'),
                # dcc.Graph(
                #     id='slider-graph', 
                #     animate=True, 
                #     style={"backgroundColor": "#1a2d46", 'color': '#ffffff'}),
                # dcc.Slider(
                #     id='slider-updatemode',
                #     marks={i: '{}'.format(i) for i in range(20)},
                #     max=20,
                #     value=2,
                #     step=1,
                #     updatemode='drag',
                # ),
                ])
    ]
)
