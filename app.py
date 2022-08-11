import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from jupyter_dash import JupyterDash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#%%capture
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_text = '''
Over the past century the percentage of women in the labor force has continued to grow.  Women are pursing higher levels of education and working longer hours.  However, many studies show there is a significant gender wage gap between men and women across all races. The data from the 2018 Census Bureau showed that on average women make 82 cents for every $1 dollar earned by a man (1). This equates to a 18 cent difference between men and women. To further explore the wage gender gap we pulled data from The General Social Survey or GSS (2). The GSS is a nationally representative survey to monitor the opinions, behaviors, and attitudes in American Society.

Resources:  
(1) https://www.americanprogress.org/article/quick-facts-gender-wage-gap/ 
(2) https://www.gss.norc.org/About-The-GSS
'''

gss_clean_table = gss_clean.groupby('sex').agg({'income': 'mean',
                                               'job_prestige': 'mean',
                                               'socioeconomic_index': 'mean',
                                               'education': 'mean'}).reset_index()
gss_clean_table = gss_clean_table.round(2)
gss_clean_table.loc[:, 'income'] = gss_clean_table['income'].map('{:,.2f}'.format)
gss_clean_table = gss_clean_table.rename({'sex': 'Sex',
                                         'income': 'Income',
                                         'job_prestige': 'Occupational Prestige',
                                         'socioeconomic_index': 'Socioeconomic Index',
                                         'education': 'Years of Eduction'}, axis=1)

gss_clean_table_flip = gss_clean_table.transpose().reset_index()
gss_clean_table_flip = gss_clean_table_flip.iloc[1:,:]
gss_clean_table_flip = gss_clean_table_flip.rename({0: 'female',
                                                   1: 'male',
                                                   'index': ''}, axis = 1)

gss_clean_df = gss_clean[['income', 'sex', 'job_prestige']]
gss_clean_df['job_prestige_category'] = pd.cut(gss_clean_df.job_prestige, bins=[12,24,36,48,60,72,84], labels = ['12-24', '24-36', '36-48', '48-60', '60-72', '72-84'])
gss_clean_df = gss_clean_df.dropna()

colorscale = [[0, '#0E2132'], [.5, '#DBDBDB'], [1, '#FAFAFA']]
table2 = ff.create_table(gss_clean_table_flip, colorscale = colorscale, height_constant=20)

dropdown_categories = ['Job Satisfaction: On the whole, how satisfied are you with the work you do?', 
                       "Relationship: A working mother can establish just as warm and secure a relationship with her children.", 
                       'Male Breadwinner: It is much better if the man is the achiever outside the home.', 
                       'Men Bettersuitted: Most men are better suited emotionally for politics than women.', 
                       'Child Suffer: A preschool child is likely to suffer if his or her mother works.', 
                       'Men Overwork: Family life often suffers because men concentrate too much on their work.']

dropdown_groups = ['Sex',
                   'Region',
                   'Years of Education']


gss_clean_groupbar = gss_clean.groupby(['sex', 'male_breadwinner']).size()
gss_clean_groupbar = gss_clean_groupbar.reset_index()
gss_clean_groupbar = gss_clean_groupbar.rename({0:'count'}, axis=1)
gss_clean_groupbar['male_breadwinner'] = gss_clean_groupbar['male_breadwinner'].astype('category')
gss_clean_groupbar['male_breadwinner'] = gss_clean_groupbar['male_breadwinner'].cat.reorder_categories(['strongly agree',
                                                                                                        'agree',
                                                                                                        'disagree',
                                                                                                       'strongly disagree'])
barchart2 = px.bar(gss_clean_groupbar, x='male_breadwinner', y='count', color='sex',
            labels={'male_breadwinner':'Responses', 'count':'Count', 'sex': 'Sex'},
            text='count',
            title = 'Male Breadwinner: It is much better if the man is the achiever outside the home.',
            barmode = 'group')

barchart2.update_layout(showlegend=True)
barchart2.update_layout(legend=dict(
    orientation="h",
    yanchor="top",
    y=1.14,
    xanchor="center",
    x=0.5
))
barchart2.update_layout(title=dict(
    y=0.9,
    x=0.5,
    xanchor='center',
    yanchor='top'
))

scatterplot2 = px.scatter(gss_clean, 
                          x='job_prestige', 
                          y='income',
                          color = 'sex',
                          height = 445,
                          trendline='lowess',
                          labels={'job_prestige':'Occupational Prestige', 
                        'income':'Income',
                        'education': 'Years of Education',
                        'socioeconomic_index': 'Socioeconomic Index',
                        'sex': 'Sex'},
                          hover_data=['education', 'socioeconomic_index'])
scatterplot2.update_traces(marker=dict(size=5,
                              opacity=0.5,
                              line=dict(width=1,
                                        color='black')),
                  selector=dict(mode='markers'))
scatterplot2.update_layout(legend=dict(
    orientation="h",
    yanchor="top",
    y=1.14,
    xanchor="center",
    x=0.5
))

boxplot2 = px.box(gss_clean, x='sex', y = 'job_prestige', color = 'sex', height = 400,
                   labels={'job_prestige':'Occupational Prestige', 'sex':''})
boxplot2.update_layout(showlegend=False)

gss_clean_df2 = gss_clean[['income', 'sex', 'job_prestige', 'education']]
gss_clean_df2['job_prestige_category'] = pd.cut(gss_clean_df.job_prestige, bins=[12,24,36,48,60,72,84], labels = ['12-24', '24-36', '36-48', '48-60', '60-72', '72-84'])
gss_clean_df2 = gss_clean_df2.dropna()

scatter_facet = px.scatter(gss_clean_df2, x='education', y = 'income', color = 'sex',
                   facet_col='job_prestige_category',
                   facet_col_wrap=2,
                   labels={'job_prestige_category':'Occupational Prestige Category', 'sex':''})
scatter_facet.update_layout(showlegend=True)
scatter_facet.update_layout(legend=dict(
    orientation="h",
    yanchor="top",
    y=1.2,
    xanchor="center",
    x=0.5
))

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])

app.layout = html.Div(
    [
        html.H1("Exploring Gender Wage Gap",
               style={
                 'font': 'Roboto',
                 'font-weight': 'bold',
                 'font-size': '40px',
                 'textAlign': 'left',
                 'margin-top': '20px',
                 'margin-left':'20px',
                 'margin-right':'30px',
                 'margin-bottom': '10px'}),
        
        dcc.Markdown(children = markdown_text,
                    style={
                         'font': 'Roboto',
                         'font-weight': 'light',
                         'font-size': '14px',
                         'textAlign': 'left',
                         'margin-top': '20px',
                         'margin-left':'20px',
                         'margin-right':'20px',
                         'margin-bottom': '0px'}),
        
        html.Div(style={'backgroundColor': '#173954',
                       'margin-top': '0px',
                       'margin-left':'20px',
                       'margin-right':'20px',
                       'margin-bottom': '10px'},
                 children=[
                     
                     html.H4('Statement Responses by Group',
                            style={
                                 'font': 'Roboto',
                                 'font-weight': 'light',
                                 'font-size': '26px',
                                 'textAlign': 'left',
                                 'margin-top': '10px',
                                 'margin-left':'10px',
                                 'margin-right':'10px',
                                 'margin-bottom': '10px'}),
                     
                     
                     html.H4('Pick a Statement:',
                             style={
                                 'font': 'Roboto',
                                 'font-weight': 'light',
                                 'font-size': '18px',
                                 'textAlign': 'left',
                                 'margin-top': '10px',
                                 'margin-left':'20px',
                                 'margin-right':'20px',
                                 'margin-bottom': '10px'}
                            ),
                     dcc.Dropdown(dropdown_categories, 
                                  dropdown_categories[2], 
                                  id='categorydropdown',
                                 style={
                                     'font': 'Roboto',
                                     'font-weight': 'light',
                                     'font-size': '14px',
                                     'color': '#000000',
                                     'textAlign': 'left',
                                     'margin-top': '10px',
                                     'margin-left':'10px',
                                     'margin-right':'30px',
                                     'margin-bottom': '10px'}),
                    
                     html.H4('Pick a Group:',
                             style={
                                 'font': 'Roboto',
                                 'font-weight': 'light',
                                 'font-size': '18px',
                                 'textAlign': 'left',
                                 'margin-top': '10px',
                                 'margin-left':'20px',
                                 'margin-right':'20px',
                                 'margin-bottom': '10px'}
                            ),
                     
                     dcc.Dropdown(dropdown_groups, 
                                  dropdown_groups[0], 
                                  id='groupdropdown',
                                 style={
                                     'font': 'Roboto',
                                     'font-weight': 'light',
                                     'font-size': '14px',
                                     'color': '#000000',
                                     'textAlign': 'left',
                                     'margin-top': '10px',
                                     'margin-left':'10px',
                                     'margin-right':'30px',
                                     'margin-bottom': '10px'}),
                     
                     dcc.Graph(figure=barchart2,
                               id = 'bargraph',
                               style={
                                     'margin-top': '10px',
                                     'margin-left':'20px',
                                     'margin-right':'20px',
                                     'margin-bottom': '20px'})
                              
                              ]),

        
        
        html.Div(style={'backgroundColor': '#173954',
                        'width':'53%', 
                        'float':'left',
                       'margin-top': '0px',
                       'margin-left':'20px',
                       'margin-right':'20px',
                       'margin-bottom': '10px'},
                 children=[
            
            html.H4("Income vs Occupational Prestige by Sex",
                   style={'font': 'Roboto',
                      'font-weight': 'Bold',
                      'font-size': '26px',
                      'textAlign': 'left',
                      'margin-top': '10px',
                      'margin-left':'10px',
                      'margin-right':'10px',
                      'margin-bottom': '10px'}),
            
            dcc.Graph(figure=scatterplot2,
                     style = {
                       'margin-top': '10px',
                       'margin-left':'20px',
                       'margin-right':'20px',
                       'margin-bottom': '20px'})
            
        ]),
        
        html.Div(style={'backgroundColor': '#173954',
                        'width':'41%', 
                        'float':'right',
                       'margin-top': '0px',
                       'margin-left':'0px',
                       'margin-right':'20px',
                       'margin-bottom': '10px'},
                 children=[
                     
                     html.H4("Men vs Women by Measure",
                   style={'font': 'Roboto',
                      'font-weight': 'Bold',
                      'font-size': '26px',
                      'textAlign': 'left',
                      'margin-top': '10px',
                      'margin-left':'10px',
                      'margin-right':'10px',
                      'margin-bottom': '10px'}),
                     
                     dcc.Dropdown(id='measuredropdown', options=[
                         {'label': 'Income', 'value': 'income'},
                         {'label': 'Occupational Prestige', 'value': 'job_prestige'},
                         {'label': 'Socioeconomic Index', 'value': 'socioeconomic_index'},
                         {'label': 'Years of Education', 'value': 'education'}], value = 'income',
                                   style={
                                     'font': 'Roboto',
                                     'font-weight': 'light',
                                     'font-size': '14px',
                                     'color': '#000000',
                                     'textAlign': 'left',
                                     'margin-top': '10px',
                                     'margin-left':'10px',
                                     'margin-right':'30px',
                                     'margin-bottom': '10px'}),
                     
            dcc.Graph(figure=boxplot2,
                      id = 'boxplot',
                     style = {
                       'margin-top': '10px',
                       'margin-left':'20px',
                       'margin-right':'20px',
                       'margin-bottom': '20px'})
                 ]),
        
        html.Div(style={'backgroundColor': '#173954',
                        'width':'97%', 
                        'float':'left',
                       'margin-top': '0px',
                       'margin-left':'20px',
                       'margin-right':'20px',
                       'margin-bottom': '10px'},
                 children=[
            
            dcc.Graph(figure=table2,
                     style = {
                       'margin-top': '10px',
                       'margin-left':'20px',
                       'margin-right':'20px',
                       'margin-bottom': '10px'})
            
        ]),
        html.Div(style={'backgroundColor': '#173954',
                        'width':'97%', 
                        'float':'left',
                       'margin-top': '0px',
                       'margin-left':'20px',
                       'margin-right':'20px',
                       'margin-bottom': '10px'},
                 children=[
            
            dcc.Graph(figure=scatter_facet,
                     style = {
                       'margin-top': '10px',
                       'margin-left':'20px',
                       'margin-right':'20px',
                       'margin-bottom': '10px'})
            
        ])
        
    
    ]
)

@app.callback(Output(component_id="bargraph",component_property="figure"), 
                  [Input(component_id='categorydropdown',component_property="value"),
                   Input(component_id='groupdropdown',component_property="value")])

def make_figure(categorydropdown, groupdropdown):
    if categorydropdown == 'Job Satisfaction: On the whole, how satisfied are you with the work you do?':
        categorycolumn = 'satjob'
        order = ['very satisfied','mod. satisfied','a little dissat','very dissatisfied']
                   
    elif categorydropdown == 'Relationship: A working mother can establish just as warm and secure a relationship with her children.':
        categorycolumn = 'relationship'
        order = ['strongly agree','agree','disagree','strongly disagree']

    elif categorydropdown == 'Male Breadwinner: It is much better if the man is the achiever outside the home.':
        categorycolumn = 'male_breadwinner'
        order = ['strongly agree','agree','disagree','strongly disagree']

    elif categorydropdown == 'Men Bettersuitted: Most men are better suited emotionally for politics than women.':
        categorycolumn = 'men_bettersuited'
        order = ['agree','disagree']

    elif categorydropdown == 'Child Suffer: A preschool child is likely to suffer if his or her mother works.':
        categorycolumn = 'child_suffer'
        order = ['strongly agree','agree','disagree','strongly disagree']

    elif categorydropdown == 'Men Overwork: Family life often suffers because men concentrate too much on their work.':
        categorycolumn = 'men_overwork'
        order = ['strongly agree','agree','neither agree nor disagree','disagree','strongly disagree']
    

    if groupdropdown == 'Sex':
        groupcolumn = 'sex'

    elif groupdropdown == 'Region':
        groupcolumn = 'region'


    elif groupdropdown == 'Years of Education':
        groupcolumn = 'education'
                   
    gss_clean_groupbar = gss_clean.groupby([categorycolumn, groupcolumn]).size()
    gss_clean_groupbar = gss_clean_groupbar.reset_index()
    gss_clean_groupbar = gss_clean_groupbar.rename({0:'count'}, axis=1)
    gss_clean_groupbar[categorycolumn] = gss_clean_groupbar[categorycolumn].astype('category')
    gss_clean_groupbar[categorycolumn] = gss_clean_groupbar[categorycolumn].cat.reorder_categories(order)
                   
    barchart2 = px.bar(gss_clean_groupbar, 
                       x=categorycolumn, 
                       y='count', 
                       color=groupcolumn,
                       labels={categorycolumn:'Responses', 'count':'Count', groupcolumn: groupdropdown},
                       title = categorydropdown,
                       barmode = 'group')

                   
    barchart2.update_layout(showlegend=True)
    barchart2.update_layout(legend=dict(
                       orientation="h",
                       yanchor="top",
                       y=1.14,
                       xanchor="center",
                       x=0.5))

    barchart2.update_layout(title=dict(
                    y=0.9,
                    x=0.5,
                    xanchor='center',
                    yanchor='top'
                   ))
                      
    return barchart2

@app.callback(Output(component_id="boxplot",component_property="figure"), 
                  [Input(component_id='measuredropdown',component_property="value")])

def make_boxplot(measuredropdown):
    
    if measuredropdown == 'income':
        label = "Income"
        
    elif measuredropdown == 'job_prestige': 
        label = "Occupational Prestige"
        
    elif measuredropdown == 'socioeconomic_index':
        label = 'Socioeconomic Index'
        
    elif measuredropdown == 'education':
        label = 'Years of Education'
    
    
    
    boxplot2 = px.box(gss_clean, x='sex', y = measuredropdown, color = 'sex',height = 400,
                   labels={measuredropdown:label, 'sex':''})
    boxplot2.update_layout(showlegend=False)
    
    return boxplot2





if __name__ == '__main__':
    app.run_server(debug=True, port=8000)
