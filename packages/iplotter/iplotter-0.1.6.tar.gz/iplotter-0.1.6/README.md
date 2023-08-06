IPlotter
=================

## C3.js and plotly.js charting in ipython/jupyter notebooks


- [Installation](#installation)
- [C3.js](#c3js)
- [plotly.js](#plotlyjs)
- [Usage](#usage)
- [Examples](#examples)
    - [C3 Stacked Area Spline Chart](#c3-stacked-area-spline-chart)
    - [plotly.js Grouped Bar Chart](#plotlyjs-grouped-bar-chart)
    - [plotly.js HeatMap](#plotlyjs-heatmap)
    - [Multple Charts](#multple-charts)


iplotter is a simple package for generating interactive charts ipython/jupyter notebooks using C3.js or plotly.js from simple python data structures (dictionaries, lists, etc.)

## Installation
To install this package run `pip install git+git://github.com/niloch/iplotter.git@master` or `pip install iplotter`

## [C3.js](http://c3js.org/)

C3 is a charting library based on d3 for making interactive and easy to understand charts, graphs, and plots.

Charts can be conveniently declared and bound to DOM elements with animated transitions for hiding/displaying data.

## [plotly.js](https://plot.ly/javascript/)

Plotly.js is a charting library based on d3 from plotly.  plotly provides native clients in many programming languages including python which can be rendered in an ipython notebook.  However, the native python client requires the user to create an account and by default makes all plots public. plotly.js can be used without creating an account and are rendered locally to keep everything private.  IPlotter makes use of the plotly.js library for chart rendering instead of the native python client from plotly which performs the rendering on their servers.

## Usage

The iplotter module contains clasess for both JavaScript Libraries. The plotter's functions take a dictionary parameter containing the data specifying the chart attributes.  There are optional arguments for graph size and filename if needed.  The data dictionary must have a structure equivalent to the JSON specifications from [C3.js](http://c3js.org/) or [plotly.js](https://plot.ly/javascript/).  plotly.js optionally allows specifying the chart layout as a separate dictionary.  Plots can be rendered in the ipython notebook and saved to the current directory as html, for later reference.

## Examples

### C3 Stacked Area Spline Chart

```python
from iplotter.iplotter import C3Plotter

plotter = C3Plotter()

chart = {
    "data": {
        "columns": [
            ['data1', 300, 350, 300, 0, 0, 120],
            ['data2', 130, 100, 140, 200, 150, 50],
            ['data3', 180, 75, 265, 100, 50, 100]
        ],
        "types": {
            "data1": 'area-spline',
            "data2": 'area-spline',
            "data3": 'area-spline'
        },
        "groups": [['data1', 'data2', 'data3']]
    }
}

plotter.plot(chart)
```
![Plot1](imgs/plot1.png?raw=true "Plot 1")


### plotly.js Grouped Bar Chart

```python
from iplotter.iplotter import PlotlyPlotter

plotter = PlotlyPlotter()

trace1 = {
  "x": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  "y": [20, 14, 25, 16, 18, 22, 19, 15, 12, 16, 14, 17],
  "type": 'bar',
  "name": 'Item 1',
  "marker": {
    "color": 'rgb(49,130,189)',
    "opacity": 0.7,
  }
}

trace2 = {
  "x": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  "y": [19, 14, 22, 14, 16, 19, 15, 14, 10, 12, 12, 16],
  "type": 'bar',
  "name": 'Item 2',
  "marker": {
    "opacity": 0.7
  }
}

data = [trace1, trace2]

layout = {
  "title": 'Title',
  "xaxis": {
    "tickangle": -45
  },
  "barmode": 'group'
}

plotter.plot(data,layout)
```
![Plot2](imgs/plot2.png?raw=true "Plot 2")

### plotly.js HeatMap

```python
from iplotter.iplotter import PlotlyPlotter

plotter = PlotlyPlotter()

data = [{
 'colorscale': 'YIGnBu',
 'reversescale': True,
 'type': u'heatmap',
 'x': ['class1', 'class2', 'class3'],
 'y': ['class1', 'class2', 'class3'],
 'z': [[ 0.7,  0.2,  0.1],
        [ 0.2,  0.7,  0.1],
        [ 0.15,  0.27,  0.56]]}]


plotter.plot_and_save(data, w=600, h=600, name='heatmap1', overwrite=True)
```
![Plot3](imgs/plot3.png?raw=true "Plot 3")

### Multple Charts

Saving multiple charts to one file or displaying multiple charts in one iframe can be achieved by concatenating html strings returned by the render function, and the `head` attribute which contains the script tags for loading the JavasScript libraries.

```python

from iplotter.iplotter import PlotlyPlotter
from IPython.display import HTML

plotter = PlotlyPlotter()

trace1 = {
  "x": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  "y": [20, 14, 25, 16, 18, 22, 19, 15, 12, 16, 14, 17],
  "type": 'bar',
  "name": 'Item 1',
  "marker": {
    "color": 'rgb(49,130,189)',
    "opacity": 0.7,
  }
}

trace2 = {
  "labels": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  "values": [19, 14, 22, 14, 16, 19, 15, 14, 10, 12, 12, 16],
  "type": 'pie',
  "name": 'Item 2',
  "marker": {
    "opacity": 0.7
  }
}

charts = [
    [trace1], 
    [trace2]
]

# plotter.head will return the html string containing script tags for loading the plotly.js/C3.js libraries
multiple_plot_html = plotter.head

for i, chart in enumerate(charts):
    multiple_plot_html += plotter.render(data=chart, name="chart_"+str(i))

# Write multiple plots to file    
with open("multiple_plots.html", 'w') as outfile:
    outfile.write(multiple_plot_html)


# display multiple plots in iframe   
HTML(plotter.iframe.format(multiple_plot_html, 600, 900))  
  
```
![Plot4](imgs/plot4.png?raw=true "Plot 4")