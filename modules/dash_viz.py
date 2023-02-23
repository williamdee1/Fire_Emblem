from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Stat columns, to be used for ordering:
STAT_COLS = ['HP', 'Str', 'Mag', 'Dex', 'Spd', 'Def', 'Res', 'Lck', 'Bld']


def bar_buttons(df):
    # Create the character drop down menus:
    character_dropdown_1 = dcc.Dropdown(
        id='character-1-dropdown',
        options=[{'label': name, 'value': name} for name in df['Name'].unique()],
        value=df['Name'].unique()[0]
    )
    character_dropdown_2 = dcc.Dropdown(
        id='character-2-dropdown',
        options=[{'label': name, 'value': name} for name in df['Name'].unique()],
        value=df['Name'].unique()[1]
    )

    # Create the level slider button:
    level_slider = dcc.Slider(
        id='level-slider',
        min=df['int_lev'].min(),
        max=df['int_lev'].max(),
        step=1,
        value=df['int_lev'].min(),
        marks={i: str(i) for i in range(df['int_lev'].min(), df['int_lev'].max() + 1)}
    )

    # Create the class dropdowns:
    class_dropdown_1 = dcc.Dropdown(
        id='class-dropdown-1'
    )

    class_dropdown_2 = dcc.Dropdown(
        id='class-dropdown-2'
    )

    buttons = [character_dropdown_1, character_dropdown_2, class_dropdown_1, class_dropdown_2, level_slider]

    return buttons


def bar_layout(app, buttons):
    # Define the app layout
    app.layout = html.Div([
        dcc.Graph(id='metric-chart'),
        html.Div([
            # Add the character dropdowns
            html.Div([
                html.Label('Character 1'),
                buttons[0]
            ], style={'width': '40%', 'display': 'inline-block', 'padding-left': '50px', 'padding-right': '50px'}),

            html.Div([
                html.Label('Character 2'),
                buttons[1]
            ], style={'width': '40%', 'display': 'inline-block'}),
        ], style={'width': '100%', 'display': 'inline-block'}),

        html.Div([
            # Add the class dropdowns
            html.Div([
                html.Label('Class 1'),
                buttons[2]
            ], style={'width': '40%', 'display': 'inline-block', 'padding-left': '50px', 'padding-right': '50px'}),

            html.Div([
                html.Label('Class 2'),
                buttons[3]
            ], style={'width': '40%', 'display': 'inline-block'}),
        ], style={'width': '100%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Internal Level', style={'text-align': 'center'}),
            buttons[4]
        ], style={'padding-top': '20px', 'text-align': 'center'})
    ])

    return app


def bar_callbacks(app, df):
    @app.callback(
        [Output('level-slider', 'min'),
         Output('level-slider', 'value')],
        [Input('character-1-dropdown', 'value'),
         Input('character-2-dropdown', 'value')]
    )
    def update_slider_min_and_value(character_name_1, character_name_2):
        min_level_1 = df[df['Name'] == character_name_1]['int_lev'].min()
        min_level_2 = df[df['Name'] == character_name_2]['int_lev'].min()
        min_level = max(min_level_1, min_level_2)
        return min_level, min_level

    # Define the callback to update the class dropdowns
    @app.callback(
        [Output('class-dropdown-1', 'options'),
         Output('class-dropdown-1', 'value'),
         Output('class-dropdown-2', 'options'),
         Output('class-dropdown-2', 'value')],
        [Input('character-1-dropdown', 'value'),
         Input('character-2-dropdown', 'value')]
    )
    def update_class_dropdowns(character_name_1, character_name_2):
        # Get the list of available classes for the selected character
        class_options_1 = [{'label': c, 'value': c} for c in df[df['Name'] == character_name_1]['Promo_Class'].unique()]
        class_options_2 = [{'label': c, 'value': c} for c in df[df['Name'] == character_name_2]['Promo_Class'].unique()]

        # Return the options for both dropdowns, and set the default value to the first class in the list
        return class_options_1, class_options_1[0]['value'], class_options_2, class_options_2[0]['value']

    # Define the callback to update the chart
    @app.callback(
        Output('metric-chart', 'figure'),
        [Input('character-1-dropdown', 'value'),
         Input('character-2-dropdown', 'value'),
         Input('level-slider', 'value'),
         Input('class-dropdown-1', 'value'),
         Input('class-dropdown-2', 'value'),
         ]
    )
    def update_metric_chart(character_name_1, character_name_2, level, class_name_1, class_name_2):
        # Filter the dataframe to include the selected characters and classes at the given level
        filt_df = df[(df['Name'].isin([character_name_1, character_name_2])) &
                     (df['int_lev'] == level) &
                     (df['Promo_Class'].isin([class_name_1, class_name_2]))]

        # Return the characters current class (may be different from eventual promotion):
        curr_class1 = filt_df.loc[(filt_df['Name'] == character_name_1) & (filt_df['Promo_Class'] == class_name_1
                                                                           )]['Class'].reset_index(drop=True)[0]
        curr_class2 = filt_df.loc[(filt_df['Name'] == character_name_2) & (filt_df['Promo_Class'] == class_name_2
                                                                           )]['Class'].reset_index(drop=True)[0]

        # If characters have same name, add class to name so bar chart differentiates between them:
        if (character_name_1 == character_name_2) & (class_name_1 != class_name_2):
            filt_df.loc[(filt_df['Name'] == character_name_1) & (filt_df['Promo_Class'] == class_name_1
                                                                 ), 'Name'] = '%s (%s)' % (
            character_name_1, class_name_1)
            filt_df.loc[(filt_df['Name'] == character_name_2) & (filt_df['Promo_Class'] == class_name_2
                                                                 ), 'Name'] = '%s (%s)' % (
            character_name_2, class_name_2)

        # Re-order to ensure correct ordering of bar chart corresponding to drop down selectors:
        filt_df['Metric'] = pd.Categorical(filt_df['Metric'], STAT_COLS)
        if class_name_1 != class_name_2:
            filt_df['Promo_Class'] = pd.Categorical(filt_df['Promo_Class'], [class_name_1, class_name_2])
        filt_df = filt_df.sort_values(['Metric', 'Promo_Class'])

        # Create the bar chart using Plotly Express
        fig = px.bar(filt_df, x='Metric', y='Value', color='Name', barmode='group')  # , color_discrete_map=color_dict

        # Update the chart title and axis labels
        fig.update_layout(
            title=f'{character_name_1} ({curr_class1}) vs. {character_name_2} ({curr_class2}) at Level {level}')
        fig.update_layout(title_x=0.5)
        fig.update_xaxes(title='Metric')
        fig.update_yaxes(title='Value')

        return fig

    return app


def scatter_buttons(df):
    x_dropdown = dcc.Dropdown(
        id='x-axis',
        options=[{'label': i, 'value': i} for i in df['Metric'].unique()],
        value='HP'
    )
    y_dropdown = dcc.Dropdown(
        id='y-axis',
        options=[{'label': i, 'value': i} for i in df['Metric'].unique()],
        value='Str'
    )
    slider = dcc.Slider(
        id='level-slider',
        min=df['int_lev'].min(),
        max=df['int_lev'].max(),
        step=1,
        value=df['int_lev'].min(),
        marks={str(level): str(level) for level in df['int_lev'].unique()}
    )

    return [x_dropdown, y_dropdown, slider]


def scatter_layout(app, buttons):
    # Define the layout
    app.layout = html.Div([
        dcc.Graph(id='scatterplot'),
        html.Div([
            # Add the metric dropdowns
            html.Div([
                buttons[0]
            ], style={'width': '40%', 'display': 'inline-block', 'padding-left': '50px', 'padding-right': '50px'}),

            html.Div([
                buttons[1]
            ], style={'width': '40%', 'display': 'inline-block'}),
        ], style={'width': '100%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Internal Level', style={'text-align': 'center'}),
            buttons[2]
        ], style={'padding-top': '20px', 'text-align': 'center'})
    ])

    return app


def scatter_callbacks(app, df):
    # Define the callback to update the scatterplot
    @app.callback(
        Output('scatterplot', 'figure'),
        Input('x-axis', 'value'),
        Input('y-axis', 'value'),
        Input('level-slider', 'value')
    )
    def update_scatterplot(x_axis, y_axis, level):
        filtered_df = df[df['int_lev'] == level]
        x_df = filtered_df[filtered_df['Metric'] == x_axis].rename(columns={'Value': x_axis})
        y_df = filtered_df[filtered_df['Metric'] == y_axis].rename(columns={'Value': y_axis})
        merged_df = x_df.merge(y_df, on=['Name', 'int_lev', 'Class', 'Promo_Class'])

        fig = px.scatter(merged_df, x=x_axis, y=y_axis,
                         color='Name', hover_data=['Name', 'Promo_Class', x_axis, y_axis])

        fig.update_layout(transition_duration=500)
        return fig

    return app