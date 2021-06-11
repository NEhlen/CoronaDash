from dataHandling import *
import plotly.graph_objs as go

colorLookup = {
    'lightBlue' : '#ebf7ff',
    'purple' : '#944e94',
    'red' : '#fc6203',
    'green' : '#0eba0b'
}

def death_confirmed_plot(deaths, confirmed):
    
    fig = go.Figure()
    popt, pcov, curve = death_vs_confirmed(deaths, confirmed)
    fig.add_trace(
        go.Scatter(
            x=confirmed, y=deaths, text=confirmed.index.values, name='Countries', mode='markers',
            hovertemplate= '%{text}'+'<br>'+'(%{x}, %{y})',
            marker=dict(
                color = "#0377fc"
            )
        )
    )
    fig.add_trace(
        go.Scatter(x=[1, np.amax(confirmed)], y=[np.exp(curve(np.log(i), *popt)) for i in [1, np.amax(confirmed)]],
        mode='lines', name="linear regression",
        marker=dict(
                color = "#fc6203"
            )
        )
    )
    
    fig.update_xaxes(type='log', automargin=True, showline=True, mirror=True, ticks='outside')
    fig.update_yaxes(type='log', automargin=True, showline=True, mirror=True, ticks='outside')

    fig.update_layout(
        template = 'plotly_dark',
        paper_bgcolor = 'rgba(0,0,0,0)',
        xaxis_title="# Confirmed",
        yaxis_title="# Deaths",
        margin={"r":0,"t":50,"l":0,"b":0},
        autosize=True,
        xaxis = dict(
            #tickfont_color = '#000000',
            #linecolor = 'black',
            nticks = 10,),
            #gridcolor = '#555555'),
        yaxis = dict(
            nticks = 10,
            zeroline = False,),
            #linecolor = 'black',
            #tickfont_color = '#000000',
            #gridcolor = '#555555'),
        plot_bgcolor = '#ebf7ff'
    )
    return fig
