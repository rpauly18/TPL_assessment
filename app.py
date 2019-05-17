import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

from pyfladesk import init_gui

from LayoutBase import colors, header, top_Divs_Base, bot_Divs_Base
from load import base_load_template

app = dash.Dash(__name__,static_folder='static')

server = app.server
app.run = app.run_server
app.config.suppress_callback_exceptions = False

external_css = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
    "https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css",
    "https://cdn.rawgit.com/amadoukane96/8f29daabc5cacb0b7e77707fc1956373/raw/854b1dc5d8b25cd2c36002e1e4f598f5f4ebeee3/test.css",
    "https://use.fontawesome.com/releases/v5.2.0/css/all.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})


app.layout = html.Div([header(),top_Divs_Base(),bot_Divs_Base()],id='full-div')



#################################
'''
These callbacks are meant to read the assessment tool basefile 
from the static folder. This effort is done so that changes to 
the basefile are automatically accounted for in the app.
'''
#################################

@app.callback(Output('tpl-assessment-store','data'),
                [Input('standard-load-button','n_clicks')],
                [State('tpl-assessment-store','data')])
def load_base_tpl_assessment_package(click, data):
    if click and not data:
        baseTemplate = base_load_template()
        return baseTemplate.index.get_level_values(0).unique().values


@app.callback(Output('capabilities-store','data'),
                [Input('tpl-assessment-store','data')])
def set_tpl_assessment_options(capabilities):
    if capabilities:
        return [{'label':names,'value':names} for names in capabilities]


@app.callback(Output('capabilities-dropdown-div','children'),
                [Input('capabilities-store','data')],
                [State('capabilities-dropdown-div','children')])
def set_tpl_assessment_topLevel_dropDown(options,Div):
    if options:
        return dcc.Dropdown(
                    id='capabilities-dropdown',
                    options = options,
                    placeholder='Select Capability',
                    value=None
                )
    else:
        return Div


@app.callback(Output('subCats-store','data'),
                [Input('capabilities-dropdown','value')])
def set_subCats_store(options):
    if options:
        return options
   

################################
'''
Now we would like to start narrowing down what we are looking at
selections are made possible through successive dropdowns
'''
################################

@app.callback(Output('left-div','hidden'),
                [Input('subCats-store','data')])
def break_left_hidden(value):
	if value:
		return False

@app.callback(Output('left-div-1','children'),
                [Input('subCats-store','data')])
def set_tpl_assessment_second_level_selection_1(value):

	if value:
		baseTemplate = base_load_template()
		subCats = baseTemplate.loc[value].index.get_level_values(0).unique().values

		options = [{'label':subcat,'value':subcat} for subcat in subCats]
		
		dropDowns = [dcc.Dropdown(id='narrowC-dropdown',
								options=options,
								value=None,
								placeholder="Select Device Capabilities"
								)]
		return dropDowns
	else:
		return  [dcc.Dropdown(id='narrowC-dropdown',
						options=[{'label':'Select Device Capabilities',
										'value':'NoCG'}],
						value=None,
						placeholder="Select Device Capabilities"
						)]

@app.callback(Output('left-div-2','children'),
                [Input('narrowC-store','data')],
                [State('subCats-store','data')])
def set_tpl_assessment_second_level_selection_2(ndata,value):

	if ndata:

		baseTemplate = base_load_template()
		subCats = baseTemplate.loc[value].loc[ndata].index.get_level_values(0).unique().values
		options = [{'label':subcat,'value':subcat} for subcat in subCats]
		
		dropDowns = [dcc.Dropdown(id='specificC-dropdown',
								options=options,
								value=None,
								placeholder="Select Device Capabilities"
								)]
		return dropDowns
	else:
		return  [dcc.Dropdown(id='specificC-dropdown',
						options=[{'label':'Select Specific Capabilities',
										'value':'NoCG'}],
						value=None,
						placeholder="Select Specific Capabilities"
						)]

@app.callback(Output('left-div-3','children'),
                [Input('specificC-store','data')],
                [State('narrowC-store','data'),
                State('subCats-store','data')])
def set_tpl_assessment_second_level_selection_3(sdata,ndata,value):

	if sdata:
		baseTemplate = base_load_template()
		try:
			subCats = baseTemplate.loc[value].loc[ndata].loc[sdata,'Question Group Description'].unique()
		except AttributeError as e:
			subCats = [baseTemplate.loc[value].loc[ndata].loc[sdata,'Question Group Description']]
			
		options = [{'label':subcat,'value':subcat} for subcat in subCats]
		
		dropDowns = [dcc.Dropdown(id='qGroup-dropdown',
								options=options,
								value=None,
								placeholder="Select Device Capabilities"
								)]
		return dropDowns
	else:
		return  [dcc.Dropdown(id='qGroup-dropdown',
						options=[{'label':'Select Device Capabilities',
										'value':'NoCG'}],
						value=None,
						placeholder="Select Device Capabilities"
						)]

@app.callback(Output('narrowC-store','data'),
                [Input('narrowC-dropdown','value')])
def set_subCats_store(value):
	if value is not 'NoCG':
		return value

@app.callback(Output('specificC-store','data'),
                [Input('specificC-dropdown','value')])
def set_specific_store(value):
	if value is not 'NoCG':
		return value

@app.callback(Output('qGroup-store','data'),
                [Input('qGroup-dropdown','value')])
def set_specific_store(value):
	if value is not 'NoCG':
		return value

@app.callback(Output('bot-left-div-2','children'),
                [Input('specificC-store','data')],
                [State('narrowC-store','data'),
                State('subCats-store','data')])
def set_specific_definition(sdata,ndata,value):

	if sdata:
		baseTemplate = base_load_template()
		try:
			description = baseTemplate.loc[value].loc[ndata].loc[sdata,'nCapability description'].unique()
		except AttributeError as e:
			description = [baseTemplate.loc[value].loc[ndata].loc[sdata,'nCapability description']]
			
		return [html.H6(f'{sdata} Definition:'),
				html.Div(description)]

@app.callback(Output('qChoice-store','data'),
                [Input('qGroup-store','data')],
                [State('specificC-store','data'),
                State('narrowC-store','data'),
                State('subCats-store','data')])
def set_question_store(qdata,sdata,ndata,value):

	if qdata:
		baseTemplate = base_load_template()
		qgrp = baseTemplate.loc[value].loc[ndata].loc[sdata,'Question Group Description']
		try:
			return qgrp[qgrp == qdata].shape[0]
		except AttributeError as e:
			return 1
		

@app.callback(Output('bot-left-div-3','children'),
                [Input('qChoice-store','data')])
def set_question_dropdown(value):

	if value:
		return [dcc.Dropdown(id='numQuestions-dropdown',
						options=[{'label':f'Question {i+1}',
										'value':i} for i in range(value)],
						value=None,
						placeholder="Select Question"
						,className='six columns')]

@app.callback(Output('bot-right-div-1','children'),
                [Input('numQuestions-dropdown','value')],
				[State('qGroup-store','data'),
				State('specificC-store','data'),
                State('narrowC-store','data'),
                State('subCats-store','data')])
def disp_question(qn,qdata,sdata,ndata,value):

	
	if qn is not None:
		baseTemplate = base_load_template()
		try:
			cols = ('Question Group Description','Question','Background','High','Medium','Low')
			qgrp = baseTemplate.loc[value].loc[ndata].loc[sdata,cols]
			qGroup = qgrp[qgrp['Question Group Description'] == qdata]
			question = qGroup['Question'].iloc[qn]
			background = qGroup['Background'].iloc[qn]
			h,m,l = (qGroup['High'].iloc[qn],
					qGroup['Medium'].iloc[qn],
					qGroup['Low'].iloc[qn])
		except (AttributeError,ValueError) as e:
			qgrp = baseTemplate.loc[value].loc[ndata].loc[sdata]
			question = qgrp.loc['Question']
			background = qgrp.loc['Background']
			h,m,l = (qGroup.loc['High'],
					qGroup.loc['Medium'],
					qGroup.loc['Low'])

		return	[html.H6(f'Question {qn+1}'),
				html.Div(question),
				html.Div(
					dcc.ConfirmDialogProvider(
					children=html.Button('Background'),
					id='background-button',
					message=background),
				className='three columns'),
				html.Div(
					dcc.ConfirmDialogProvider(
					children=html.Button('Score Guidance'),
					id='score-button',
					message=f'High: {h} \nMedium: {m} \nLow: {l}'),
				className='three columns')
				
				]









if __name__ == '__main__':
    ## Run in Browser
    app.run()
    ## run standalone
    #init_gui(app,window_title='TPL Assessment Stand Alone Tool')