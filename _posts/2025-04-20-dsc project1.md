```python
# Initialize Otter
import otter
grader = otter.Notebook("project.ipynb")
```

# Project 1 – MTS Transit: Navigating San Diego's Bus Network 🚌

## DSC 80, Spring 2025

### Checkpoint Due Date (Questions 1): Friday, April 11th
### Due Date: Friday, April 18th

## Instructions

---

### Working on the Project

This Jupyter Notebook contains the statements of the problems and provides code and Markdown cells to display your answers to the problems.

* Like the lab, your coding work will be developed in the accompanying `project.py` file, that will be imported into the current notebook. This code will be autograded.
    
* **For the Checkpoint, which is required, you only need to turn in a `project.py` containing solutions for Part 1!**
    - The "Project 1 Checkpoint" autograder on Gradescope does not thoroughly check your code – it only runs the public tests on Questions XX to make sure that you have completed them. There are no hidden tests for the checkpoint, and you will see your score upon submission. 
    - When you submit the final version of the project, however, we will use hidden tests to check your answers more thoroughly.
    - Note that this means you will ultimately have to submit the project twice – once to the "Project 1 Checkpoint" autograder (Questions XX), and once to the "Project 1" autograder (once you're fully done).
- **Do not change the function names in `project.py` file!** The functions in `project.py` are how your assignment is graded, and they are graded by their name. If you changed something you weren't supposed to, you can find the original code in the [course GitHub repository](https://github.com/dsc-courses/dsc80-2024-sp).
- **To ensure that all of your work to be submitted is in `project.py`, we've included a script named `project-validation.py` in the project folder. You shouldn't edit it, but instead, you should call it from the command line (e.g. the Terminal) to test your work.** More details on its usage are given at the bottom of this notebook.
- You are encouraged to write your own additional helper functions to solve the project, as long as they also end up in `project.py`.

### Warning! 🚨

Many questions in the project intentionally build off of each other and the final result matters! In fact, you can "get a question correct," but only receive partial credit for it because a previous answer was wrong.

### Working with a Partner 👯

You may work together on projects (and projects only!) with a partner. If you work with a partner, you are both required to actively contribute to all parts of the project. You must both be working on the assignment at the same time together, either physically or virtually on a Zoom call. You are encouraged to follow the pair programming model, in which you work on just a single computer and alternate who writes the code and who thinks about the problems at a high level.

In particular, you **cannot** split up the project and each work on separate parts independently.

Note that if you do work with a partner, you and your partner must submit the Checkpoint together and the whole project together. See [here](https://dsc80.com/syllabus/#projects) for more details.


```python
%load_ext autoreload
%autoreload 2
```


```python
import pandas as pd
import numpy as np
from pathlib import Path
import json
import re

###
from collections import deque
from shapely.geometry import Point
###

import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
pd.options.plotting.backend = 'plotly'

from IPython.display import display

def plot_histogram_with_mean_line(data, nbins=10, title="Interval Distribution"):
    mean_interval = data.mean()
    fig = px.histogram(data, nbins=nbins, title=title)
    fig.update_layout(bargap=0.1)
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='lines',line=dict(color='Red', width=2),
        showlegend=True, name='Mean Interval Length'
    ))
    fig.update_layout(
        title=title,
        xaxis_title='Interval Length (Minutes)',
        yaxis_title='Count',
        shapes=[dict(type='line', x0=mean_interval,
                y0=0, x1=mean_interval,
                y1=50, line=dict(color='Red', width=2))])
    return fig

import warnings
warnings.filterwarnings("ignore")
```


```python
from project import *
```

## About the Assignment 📌

Welcome to an in-depth exploration of the San Diego Metropolitan Transit System (MTS)! In this assignment, you will delve into the complexities of urban transit through a real life dataset. By working with this dataset, you will gain practical experience in data visualization, algorithmic analysis, and urban planning. Get ready to navigate the intricate web of bus routes, optimize travel times, and understand the paradoxes of public transit. Let's load in the data.


Run the cell below to load `schedule` of buses in the city of San Diego. 


```python
schedule = pd.read_csv('data/schedule.csv')
schedule.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>trip_id</th>
      <th>stop_id</th>
      <th>stop_sequence</th>
      <th>shape_dist_traveled</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>17403779</td>
      <td>94048</td>
      <td>1</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>1</th>
      <td>17403779</td>
      <td>13510</td>
      <td>2</td>
      <td>0.672</td>
    </tr>
    <tr>
      <th>2</th>
      <td>17403779</td>
      <td>10478</td>
      <td>3</td>
      <td>2.340</td>
    </tr>
    <tr>
      <th>3</th>
      <td>17403779</td>
      <td>13391</td>
      <td>4</td>
      <td>2.420</td>
    </tr>
    <tr>
      <th>4</th>
      <td>17403779</td>
      <td>10106</td>
      <td>5</td>
      <td>2.541</td>
    </tr>
  </tbody>
</table>
</div>



Each row of the DataFrame corresponds to a specific stop along a particular bus trip. It provides detailed information about the arrival time of the bus at that stop, the sequence in which the stop is visited during the trip, and the unique identifiers for both the trip and the stop.

- `trip_id`: An identifier for each bus trip.
- `stop_id`: An identifier for the bus stop.
- `stop_sequence`: The order in which stops are visited within a trip.
- `shape_dist_traveled`: The distance from previous bus stop. 


Run the cell below to load `stops` of buses in the city of San Diego. 


```python
stops = pd.read_csv('data/stations.csv')
stops.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>stop_id</th>
      <th>stop_name</th>
      <th>stop_lat</th>
      <th>stop_lon</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>94048</td>
      <td>Fashion Valley Transit Center</td>
      <td>32.765652</td>
      <td>-117.168972</td>
    </tr>
    <tr>
      <th>1</th>
      <td>13510</td>
      <td>Hotel Circle South &amp; Bachman Pl</td>
      <td>32.760653</td>
      <td>-117.167336</td>
    </tr>
    <tr>
      <th>2</th>
      <td>10478</td>
      <td>University Av &amp; 7th Av</td>
      <td>32.748268</td>
      <td>-117.158930</td>
    </tr>
    <tr>
      <th>3</th>
      <td>13391</td>
      <td>University Av &amp; 8th Av</td>
      <td>32.748308</td>
      <td>-117.157548</td>
    </tr>
    <tr>
      <th>4</th>
      <td>10106</td>
      <td>University Av &amp; 10th Av</td>
      <td>32.748318</td>
      <td>-117.155463</td>
    </tr>
  </tbody>
</table>
</div>



Each row of the `stops` DataFrame corresponds to a specific bus stop. It provides detailed information about the location of the bus stop and its unique identifier.

- `stop_id`: An identifier for the bus stop.
- `stop_name`: The name of the bus stop.
- `stop_lat`: The latitude of the bus stop location.
- `stop_lon`: The longitude of the bus stop location.

Run the cell below to load `trips` of buses in the city of San Diego. 


```python
trips = pd.read_csv('data/routes.csv')
trips.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>route_id</th>
      <th>service_id</th>
      <th>trip_id</th>
      <th>direction_name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>81554-1111100-0</td>
      <td>17403779</td>
      <td>East</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>81554-1111100-0</td>
      <td>17403796</td>
      <td>West</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1</td>
      <td>81554-1111100-0</td>
      <td>17403787</td>
      <td>West</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2</td>
      <td>81331-1111100-0</td>
      <td>17285759</td>
      <td>North</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2</td>
      <td>81331-1111100-0</td>
      <td>17285758</td>
      <td>South</td>
    </tr>
  </tbody>
</table>
</div>



나의 프로젝트 노트
데이터확인용


```python

```


```python
# 데이터프레임의 통계 요약
print("Schedule 데이터의 통계 요약:")
display(schedule.describe())
print("\n")

print("Stops 데이터의 통계 요약:")
display(stops.describe())
print("\n")

print("Trips 데이터의 통계 요약:")
display(trips.describe())
```

    Schedule 데이터의 통계 요약:



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>trip_id</th>
      <th>stop_id</th>
      <th>stop_sequence</th>
      <th>shape_dist_traveled</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>7.304000e+03</td>
      <td>7304.000000</td>
      <td>7304.000000</td>
      <td>7304.000000</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>1.736488e+07</td>
      <td>41195.031490</td>
      <td>18.499589</td>
      <td>7.205836</td>
    </tr>
    <tr>
      <th>std</th>
      <td>9.070924e+04</td>
      <td>32484.229281</td>
      <td>13.460630</td>
      <td>11.456401</td>
    </tr>
    <tr>
      <th>min</th>
      <td>1.533136e+07</td>
      <td>10001.000000</td>
      <td>1.000000</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>1.728707e+07</td>
      <td>11824.000000</td>
      <td>8.000000</td>
      <td>2.111000</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>1.740207e+07</td>
      <td>39016.500000</td>
      <td>16.000000</td>
      <td>4.360000</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>1.740377e+07</td>
      <td>60698.000000</td>
      <td>26.000000</td>
      <td>7.552500</td>
    </tr>
    <tr>
      <th>max</th>
      <td>1.754589e+07</td>
      <td>99999.000000</td>
      <td>72.000000</td>
      <td>88.218002</td>
    </tr>
  </tbody>
</table>
</div>


    
    
    Stops 데이터의 통계 요약:



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>stop_id</th>
      <th>stop_lat</th>
      <th>stop_lon</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>4130.000000</td>
      <td>4130.000000</td>
      <td>4130.000000</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>39859.991525</td>
      <td>32.750665</td>
      <td>-117.075319</td>
    </tr>
    <tr>
      <th>std</th>
      <td>31845.838325</td>
      <td>0.109165</td>
      <td>0.134254</td>
    </tr>
    <tr>
      <th>min</th>
      <td>10001.000000</td>
      <td>32.542819</td>
      <td>-117.277924</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>11797.250000</td>
      <td>32.689011</td>
      <td>-117.153025</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>30385.500000</td>
      <td>32.745325</td>
      <td>-117.089904</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>60467.500000</td>
      <td>32.805484</td>
      <td>-117.036301</td>
    </tr>
    <tr>
      <th>max</th>
      <td>99999.000000</td>
      <td>33.256887</td>
      <td>-116.184458</td>
    </tr>
  </tbody>
</table>
</div>


    
    
    Trips 데이터의 통계 요약:



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>trip_id</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>3.060000e+02</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>1.733791e+07</td>
    </tr>
    <tr>
      <th>std</th>
      <td>2.475290e+05</td>
    </tr>
    <tr>
      <th>min</th>
      <td>1.533136e+07</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>1.728712e+07</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>1.740197e+07</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>1.740335e+07</td>
    </tr>
    <tr>
      <th>max</th>
      <td>1.754589e+07</td>
    </tr>
  </tbody>
</table>
</div>


Each row of the `trips` DataFrame contains information on each bus route, including the direction and service ID.

- `route_id`: An identifier for the bus route.
- `service_id`: An identifier for the service schedule.
- `trip_id`: An identifier for each bus trip.
- `direction_name`: The direction of the trip (e.g., East, West).

The `schedule`, `stops`, and `trips` dataframes collectively provide a comprehensive view of the San Diego Metropolitan Transit System (MTS). The `schedule` dataframe details the timing and sequence of bus arrivals at various stops, while the `stops` dataframe offers location-specific information for each bus stop, including their geographic coordinates. The `trips` dataframe ties these elements together by defining the bus line for each bus trip. Together, these datasets enable a detailed analysis of the bus transit network, allowing for visualization of routes, optimization of travel times, and understanding of transit patterns.



---

<a id='outline'></a>

### Navigating the Project 🗺

Click on the links below to navigate to different parts of the project. 


- [✅ Part 1: Visualizing the Network 🚏](#part1)
    - [✅ Question 1 (Checkpoint Question)](#question1)
- [Part 2: The Quest for the Shortest Route 📍](#part2)
    - [Question 2](#question2)
- [Part 3: The Time Paradox ⏳](#part3)
    - [Question 3](#question3)
    - [Question 4](#question4)
---

<!--     - [✅ Question 1 (Checkpoint Question)](#Question-1) -->

<a id='part1'></a>

## Part 1: Visualizing the Network

([return to the outline](#outline))

The city's bus lines form a web of connections, linking neighborhoods, workplaces, and leisure spots. On average, MTS serves approximately 226,345 riders every weekday.  Your first task is to visualize this intricate network. By mapping all the bus lines in San Diego, you'll create a visual representation of the city's lifeline, uncovering patterns and insights that go beyond the ordinary commute.

We will start by visualizing the San Diego city boundary using a `shapefile`. A shapefile is a popular geospatial vector file to store map data.

This shapefile in `/data_city` provides a geographic outline of the city, serving as the foundation for plotting our bus stops. Run the following code, it plots an interactive visualization of San Diego city boundary using Plotly.


```python
# Load the shapefile for San Diego city boundary
san_diego_boundary_path = 'data/data_city/data_city.shp'
san_diego_city_bounds = gpd.read_file(san_diego_boundary_path)

# Ensure the coordinate reference system is correct
san_diego_city_bounds = san_diego_city_bounds.to_crs("EPSG:4326")

# Extract the coordinates from the geometry
san_diego_city_bounds['lon'] = san_diego_city_bounds.geometry.apply(lambda x: x.centroid.x)
san_diego_city_bounds['lat'] = san_diego_city_bounds.geometry.apply(lambda x: x.centroid.y)

# Plot using Plotly
fig = go.Figure()

# Add city boundary
fig.add_trace(go.Choroplethmapbox(
    geojson=san_diego_city_bounds.__geo_interface__,
    locations=san_diego_city_bounds.index,
    z=[1] * len(san_diego_city_bounds),
    colorscale="Greys",
    showscale=False,
    marker_opacity=0.5,
    marker_line_width=1,
))

# Update layout
fig.update_layout(
    mapbox=dict(
        style="carto-positron",
        center={"lat": san_diego_city_bounds['lat'].mean(), "lon": san_diego_city_bounds['lon'].mean()},
        zoom=10,
    ),
    margin={"r":0,"t":0,"l":0,"b":0}
)

fig.show()

```



<!-- ### ✅ Question 1 (Checkpoint Question) -->

### ✅ Question 1 (Checkpoint Question)


<a id='question1'></a>

([return to the outline](#outline))

Now, your objective is to extend this visualization by plotting the bus stops on top of the city boundary, color-coded by bus line. Before we can do that, we must explore the provided DataFrames and identify which CSV files are necessary for plotting. 

#### `create_detailed_schedule`
Complete the implementation of the function `create_detailed_schedule`, which takes in the following inputs:

- `schedule` (DataFrame): This is the DataFrame of bus schedules. 
- `stops` (DataFrame): This is the DataFrame of bus stops. 
- `trips` (DataFrame): This is the DataFrame of trip made by San Diego buses.
- `bus_lines` (List): A list of unique bus lines. 

The function should return a DataFrame indexed by `trip_id`, containing detailed information about which bus lines stop at each bus station. 

***Notes:***
- The `stops` DataFrame includes the coordinate locations of bus stops but does not indicate which buses stop there. Merge relevant DataFrames to link each stop to its bus route.
- In the output DataFrame, ensure that rows are ordered so that all stops for each route appear sequentially, in the exact order that `bus_lines` lists them. For example, if `bus_lines` lists route 105 before route 30, all rows for route 105 should appear before any rows for route 30.
- Try filtering for route 105 in the trips data; you’ll find it has multiple unique paths a bus line can take, depending on various circumstances (e.g., time of day or detours). In your output, ensure these paths are sorted so that the shortest unique path (with the fewest stops) appears first, followed by paths with longer stops in ascending order of length.

  
Expected Columns: 

- `trip_id` (Index): An identifier for each bus trip.
- `stop_id`: The ID of the bus stop.
- `stop_sequence`: The order in which the bus stops are visited.
- `shape_dist_traveled`: The distance traveled from the start of the route to the stop.
- `stop_name`: The name of the bus stop.
- `stop_lat`: The latitude of the bus stop.
- `stop_lon`: The longitude of the bus stop.
- `route_id`: The ID of the bus route.
- `service_id`: The ID of the service.
- `direction_name`: The direction of the bus route.

**Hint:** Use `pd.Categorical()` to ensure the bus routes in the DataFrame are sorted in the same order as they appear in the `bus_lines` list.

<br>

#### `visualize_bus_network`

Once your data is prepared, create a Plotly visualization of your 10 chosen bus routes by completing the function visualize_bus_network. We’ve provided the city boundary plot, so plot the routes over this base map.

Function Inputs:

- `bus_df` (DataFrame): The DataFrame returned by `create_detailed_schedule()` containing all relevant data for plotting the bus routes.

**Note:** Assign Colors to Bus Lines: Use a dictionary to assign each bus line a unique color. You can manually select hex color codes (e.g., #EF553B) or use Plotly’s `px.colors.qualitative.Plotly` for an automatic color palette.

Plot Bus Stops for Each Route Using a Loop:

- Use a for `loop` to iterate through the bus lines and call `go.Scattermapbox()` in each iteration, resulting in 10 `Scattermapbox()` traces.
- Filter `bus_df` to include only rows for the current bus line.
- Use stop_lat and stop_lon columns from bus_df to plot each bus stop.
- Set the `name` parameter in `Scattermapbox()` to follow the format `Bus Line XX`.
- Use the `text` parameter to display bus stop names when users hover over a marker.

For additional help with debugging and understanding the code structure, you can refer to the example provided [here](https://plotly.com/python/tile-scatter-maps/#nuclear-waste-sites-on-campuses). The approach in that example is similar to what you’ll be doing, although it’s focused on different data.

Function Output Example:

![10 Bus Lines](images/network.png)


You may use ChatGPT to help you plot the bus stops. Here are some prompts to help you get started: 
- "What are the differences between `Scattermapbox` and `Choroplethmapbox` in Plotly?"
- "I’m working on a function to plot bus routes using Plotly. How can I use `go.Scattermapbox()` to plot points for each bus stop?"
- "How do I assign unique colors to each bus line using Plotly’s color palette?"



```python
def create_detailed_schedule(schedule, stops, trips, bus_lines):
    """
    Complete the implementation of this function.
    """
    
    # Merge relevant DataFrames to link each stop to its bus route
    detailed_schedule = pd.DataFrame()
    for line in bus_lines:
        # Filter trips DataFrame to only include the current bus line
        line_trips = trips[trips['route_id'] == line]
        
        # Merge the line_trips DataFrame with the schedule and stops DataFrames
        line_schedule = pd.merge(schedule, stops, on='stop_id')
        line_schedule = pd.merge(line_schedule, line_trips, on='trip_id')
        
        # Sort the rows by trip_id and stop_sequence
        line_schedule = line_schedule.sort_values(['trip_id', 'stop_sequence'])
        
        # Append the current bus line's schedule to the detailed_schedule DataFrame
        detailed_schedule = pd.concat([detailed_schedule, line_schedule], ignore_index=True)
    
    
    # Ensure the bus lines are sorted in the order they appear in bus_lines
    detailed_schedule['route_id'] = pd.Categorical(detailed_schedule['route_id'], categories=bus_lines, ordered=True)
    detailed_schedule = detailed_schedule.sort_values('route_id')
    # Set the index to 'trip_id'
    detailed_schedule = detailed_schedule.set_index('trip_id')
    
    return detailed_schedule
```


```python
def visualize_bus_network(bus_df):
    # Load the shapefile for San Diego city boundary
    san_diego_boundary_path = 'data/data_city/data_city.shp'
    san_diego_city_bounds = gpd.read_file(san_diego_boundary_path)
    
    # Ensure the coordinate reference system is correct
    san_diego_city_bounds = san_diego_city_bounds.to_crs("EPSG:4326")
    
    san_diego_city_bounds['lon'] = san_diego_city_bounds.geometry.apply(lambda x: x.centroid.x)
    san_diego_city_bounds['lat'] = san_diego_city_bounds.geometry.apply(lambda x: x.centroid.y)
    
    fig = go.Figure()
    
    # Add city boundary
    fig.add_trace(go.Choroplethmapbox(
        geojson=san_diego_city_bounds.__geo_interface__,
        locations=san_diego_city_bounds.index,
        z=[1] * len(san_diego_city_bounds),
        colorscale="Greys",
        showscale=False,
        marker_opacity=0.5,
        marker_line_width=1,
    ))

    # Add bus stops for each route
    color_palette = px.colors.qualitative.Plotly
    for i, route in enumerate(bus_df['route_id'].unique()):
        route_stops = bus_df[bus_df['route_id'] == route]
        fig.add_trace(go.Scattermapbox(
            lat=route_stops['stop_lat'],
            lon=route_stops['stop_lon'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=8,
                color=color_palette[i],
            ),
            name=f"Bus Line {route}",
            text=route_stops['stop_name']
        ))
    
    # Update layout
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center={"lat": san_diego_city_bounds['lat'].mean(), "lon": san_diego_city_bounds['lon'].mean()},
            zoom=10,
        ),
        margin={"r":0,"t":0,"l":0,"b":0},
        legend_title_text='Bus Lines'
    )
    return fig
```


```python
# don't change this cell, but do run it -- it is needed for the tests
unique_route_ids = ["201", "202", "30", "35", "43", "44", "105", "31", "5", "10"]
output_preprocessing = create_detailed_schedule(schedule, stops, trips, unique_route_ids)
fig = visualize_bus_network(output_preprocessing)
fig_json = fig.to_json()
fig_data = json.loads(fig_json)
fig.show()
```




```python
# hidden test setup
unique_route_ids = [ "105", "DNE", "31", "202"]
prep_2 = create_detailed_schedule(schedule, stops, trips, unique_route_ids)
```


```python
grader.check("q1")
```




<p><strong style='color: red;'><pre style='display: inline;'>q1</pre> results:</strong></p><p><strong><pre style='display: inline;'>q1 - 1</pre> result:</strong></p><pre>    Test case passed!</pre><p><strong><pre style='display: inline;'>q1 - 2</pre> result:</strong></p><pre>    Test case passed!</pre><p><strong><pre style='display: inline;'>q1 - 3</pre> result:</strong></p><pre>    Trying:
        output_preprocessing.shape == (740, 9)
    Expecting:
        True
    **********************************************************************
    Line 1, in q1 2
    Failed example:
        output_preprocessing.shape == (740, 9)
    Expected:
        True
    Got:
        False
</pre><p><strong><pre style='display: inline;'>q1 - 3</pre> message:</strong> correct shape</p><p><strong><pre style='display: inline;'>q1 - 4</pre> result:</strong></p><pre>    Test case passed!</pre><p><strong><pre style='display: inline;'>q1 - 5</pre> result:</strong></p><pre>    Test case passed!</pre><p><strong><pre style='display: inline;'>q1 - 6</pre> result:</strong></p><pre>    Test case passed!</pre><p><strong><pre style='display: inline;'>q1 - 7</pre> result:</strong></p><pre>    Test case passed!</pre><p><strong><pre style='display: inline;'>q1 - 8</pre> result:</strong></p><pre>    Trying:
        prep_2.shape == (224, 9)
    Expecting:
        True
    **********************************************************************
    Line 1, in q1 7
    Failed example:
        prep_2.shape == (224, 9)
    Expected:
        True
    Got:
        False
</pre><p><strong><pre style='display: inline;'>q1 - 8</pre> message:</strong> correct shape</p>



<a id='part2'></a>

## Part 2: The Quest for the Shortest Route 📍

([return to the outline](#outline))

Next, let's find the shortest path between two points. Given the start and end destinations, your task is to output the stops that makes up the shortest path between these two points. Leverage the Breadth-First Search (BFS) algorithm, which you learned in DSC 30. This algorithm is well-suited for finding the shortest path in an unweighted graph, such as our bus stop network. 




### Question 2


<a id='question2'></a>

([return to the outline](#outline))

#### `find_neighbors`
In order to find the shortest path, you will need a helper function to find the closest neighbor(s) at a given station. Complete the implementation of the function `find_neighbors`, which takes the following inputs:

- `station_name` (str): The name of the current station.
- `detailed_schedule` (DataFrame): Preprocessed DataFrame created from `create_detailed_schedule` function in Part 1.

The function should return an `array` containing the strings of next station name(s). 

**Note:** This is a non-trivial task, so let’s break it down with an example. Suppose we are looking for the neighboring nodes of `Gilman Dr & Eucalyptus Grove Ln`. There are three unique bus routes that travel through `Gilman Dr & Eucalyptus Grove Ln`. Let's focus on route 30. As you learned, some bus lines have more than one unique path. In this case, route 30 has two unique paths that both travel through `Gilman Dr & Eucalyptus Grove Ln`. For one path, the next stop is `Gilman Dr & Myers Dr`, and for the other path, the next stop is `N Torrey Pines Rd & Revelle College Dr`. Ensure your function considers both cases. 


**Hint:** Since `trip_id` uniquely identifies each trip, consider how it can help you find all trips passing through the station. Then, use the `stop_sequence` to locate the stop that immediately follows the current station in each trip. This approach ensures you capture all possible next stops across different trips.


####  `bfs`

To complete this section, you must return the shortest path from point A to point B. That means, you may use an algorithm of your choice to find the least number of bus stops from a given `start_station` to the `end_station`. Complete the implementation of the function `bfs`. Think of how you can use your previously created function find_neighbors() as an helper function to solve this. If no path can be found, the function should return the string "No path found".

- `start_station` (string): This is the name of the starting point station. 
- `end_station` (string): This is the name of the end point station.
- `detailed_schedule` (DataFrame): Preprocessed DataFrame created from `create_detailed_schedule` function in Part 1.

If the `start_station` does not exist, the function should return `"Start station {start_station} not found."` For example, "UTC" is not a real station name. Therefore, the function would return `"Start station UTC not found."`Also, if the end station does not exist, the function should return `"End station '{end_station}' not found."`

The output DataFrame should include:

- `stop_name`: The name of the bus stop.
- `stop_lat`: Latitude of the bus stop.
- `stop_lon`: Longitude of the bus stop.
- `stop_num`: The order in which the stops are visited on the shortest path.

Example, say we want to find the shortest path from UC San Diego to UTC. Your function should return the following: 

|         | stop_name                        | stop_lat  | stop_lon    | stop_num |
|---------|----------------------------------|-----------|-------------|----------|
| **0**   | Gilman Dr & Eucalyptus Grove Ln  | 32.875266 | -117.238755 | 1        |
| **1**   | Gilman Dr & Myers Dr             | 32.876949 | -117.235533 | 2        |
| **2**   | VA Hospital                      | 32.874753 | -117.233834 | 3        |
| **3**   | La Jolla Village Dr & Lebon Dr   | 32.871250 | -117.223855 | 4        |
| **4**   | La Jolla Village Dr & Regents Rd | 32.871503 | -117.218669 | 5        |
| **5**   | UTC Transit Center               | 32.869248 | -117.213559 | 6        |




```python

```


```python

```


```python
# don't change this cell, but do run it -- it is needed for the tests
unique_route_ids = ["201", "202", "30", "35", "43", "44", "105", "31", "5", "10"]
detailed_schedule = create_detailed_schedule(schedule, stops, trips, unique_route_ids)
# public test setup
neighbors_output_na = find_neighbors("Nonexistent Station", detailed_schedule)
neighbors_output = find_neighbors("La Jolla Village Dr & Lebon Dr", detailed_schedule)
bfs_output = bfs("Gilman Dr & Eucalyptus Grove Ln", "UTC Transit Center", detailed_schedule)
# hidden test setup
neighbors_hidden = find_neighbors("UTC Transit Center", detailed_schedule)
neighbors_hidden2 = find_neighbors("Pacific Hwy & Enterprise St", detailed_schedule)
bfs_hidden = bfs("Gilman Dr & Eucalyptus Grove Ln", "Nobel Dr & La Jolla Village Square Drwy", detailed_schedule)
```


```python
bfs_output
```

Now that you have implemented the `bfs` function to find the shortest path between two bus stops, it's time to see it in action! The code provided below will help you visualize the data and validate your algorithm. By running this cell, you will be able to see the shortest path from your specified start_station to end_station plotted on a map, giving you a clear visual representation of the route.

This step is crucial for verifying that your algorithm works correctly and efficiently. It will also help you understand how the bus routes are connected in the San Diego Metropolitan Transit System. Simply run the cell, and observe the output to ensure your function is performing as expected.


```python
def shortest_path_visualization(route_points_sorted):

    geometry = [Point(xy) for xy in zip(route_points_sorted['stop_lon'], route_points_sorted['stop_lat'])]
    stops_gdf = gpd.GeoDataFrame(route_points_sorted, geometry=geometry)
    stops_gdf.crs = "EPSG:4326"

    san_diego_boundary_path = 'data/data_city/data_city.shp'
    san_diego_city_bounds = gpd.read_file(san_diego_boundary_path)
    san_diego_city_bounds = san_diego_city_bounds.to_crs("EPSG:4326")


    # Plot city boundary using Plotly
    fig = go.Figure()

    fig.add_trace(go.Choroplethmapbox(
        geojson=san_diego_city_bounds.__geo_interface__,
        locations=san_diego_city_bounds.index,
        z=[1] * len(san_diego_city_bounds),
        colorscale="Greys",
        showscale=False,
        marker_opacity=0.5,
        marker_line_width=1,
    ))

    center_lat = route_points_sorted['stop_lat'].mean()
    center_lon = route_points_sorted['stop_lon'].mean()

    # Add bus stops of shortest path
    fig.add_trace(go.Scattermapbox(
        lat=route_points_sorted['stop_lat'],
        lon=route_points_sorted['stop_lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=12,
            color='red',
            opacity=0.7
        ),
        name="Shortest Path",
        text=route_points_sorted['stop_name']
    ))

    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            zoom=14,
            center=dict(lat=center_lat, lon=center_lon),
        ),
        legend_title_text='Bus Lines',
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    return fig
```


```python
shortest_path_visualization(bfs_output)
```


```python
grader.check("q2")
```

<a id='part3'></a>

## Part 3: The Waiting Time Paradox ⏳

([return to the outline](#outline))

Have you ever waited longer than 15 minutes for a bus that’s supposed to arrive every 10 minutes? You might wonder why you are so unlucky. However, using the Poisson process, we can explain that this is actually quite normal. This phenomenon is known as the Waiting Time Paradox.

> Imagine you are at a bus station where buses arrive throughout the day, with a bus coming every 10 minutes on average. If the most recent bus leaves just before you arrive, you might have to wait 9 or 10 minutes for the next one. If you randomly arrive at the station, an educated guess for your “waiting time” might be 5 minutes, which is half the time between buses on average. However, this guess does NOT capture the whole picture. In reality, you will typically wait longer than 5 minutes. In fact, your expected waiting time will be closer to 10 minutes. **In the following sections we will explore why your your average wait time is longer than half the interval.**

Let’s simulate bus arrivals and see how waiting times are distributed. We will generate a series of random bus arrival times and calculate the intervals between them. By plotting these intervals, we can visualize their distribution and understand why waiting longer than 15 minutes is not uncommon.


### Question 3

<a id='question3'></a>

([return to the outline](#outline))

#### `simulate_bus_arrivals`

Complete the implementation of the function `simulate_bus_arrivals_uniform`. Your task is to generate bus arrival times, randomly spread out using a uniform distribution from 6 AM to 12 AM (midnight). Assume that, on average, buses are scheduled to arrive every `tau` minutes. For example, if `tau` is 10, roughly 6 buses should arrive at the bus station every hour. 

function input:
- `tau` (float): The average time between bus arrivals in minutes.

The function should return a DataFrame with the following columns:
- `Arrival Time` (str): Bus arrival times as strings.
- `Interval` (float): The interval in minutes between consecutive bus arrivals.

**Hint:** Think about how to represent the time range between 6:00 AM (360 minutes) and 12:00 AM (1440 minutes) to simplify calculations. If buses arrive, on average, every `tau` minutes, you can estimate the total number of buses using:

$$
\text{Number of Buses} = \frac{1440 - 360}{\tau}
$$

This formula estimates the expected number of buses by dividing the total time range by `tau`. How might you use this to generate a uniform distribution of bus arrivals? An example output might look like this:

|   | Arrival Time | Interval   |
|--------|--------------|------------|
| 0      | 06:08:29     | 8.49       |
| 1      | 06:17:20     | 8.86       |
| 2      | 06:20:11     | 2.85       |
| 3      | 06:20:50     | 0.65       |
| 4      | 06:38:57     | 18.12      |

**Note:** For the first bus (index 0), the `Interval` column should represent the time elapsed from 6:00 AM to its arrival.



```python

```


```python

```

Run the cell below to call `simulate_bus_arrivals` to simulate bus arrivals every 10 minutes. Make sure to run this cell before moving forward, otherwise the tests won't work correctly.


```python
bus_distribution = simulate_bus_arrivals(10)
bus_distribution.head()
```

If you have implemented the bus arrival simulation correctly, the histogram of the intervals between bus arrivals should roughly follow a decreasing exponential distribution. Run the following to confirm you simulation is implemented correctly. 


```python
data = simulate_bus_arrivals(10)['Interval'] 
plot_histogram_with_mean_line(data).show()
```


```python
grader.check("q3")
```

By simulating bus arrivals and plotting the intervals between them, we can see that the intervals follow an exponential distribution. **This is a key attribute of the Poisson process: the time intervals between events decrease exponentially.** In other words, shorter intervals are more common, but longer intervals, although less frequent, do occur and can significantly affect the average waiting time. The Waiting Time Paradox occurs because when you arrive at the bus stop at a random time, you are more likely to arrive during a longer interval between buses rather than a shorter one. 

### Question 4
<a id='question4'></a>

([return to the outline](#outline))

Even though buses are scheduled to arrive every 10 minutes on average, your actual waiting time can often be longer. To explore this concept further, let's create a chart that visualizes passenger waiting times based on simulated bus arrivals. Your task is to simulate the arrival of random passengers, calculate the waiting times for each passenger, and plot the bus arrival times and passenger waiting times to visualize the distribution: 

![San Diego Shortest Path](images/vis.png)

<br>

####  `simulate_wait_times`

Complete the implementation of the function `simulate_wait_times`. This function will take the simulated bus arrival times and calculate the waiting time for each passenger, as well as the index and the arrival time of the bus they will catch.

- `arrival_times` (DataFrame): This is the bus arrivals generated by `simulate_bus_arrivals_uniform(tau)`. 
- `n_passengers` (int): The number of passengers

The function should A DataFrame containing the following columns:
- `Passenger Arrival Time` (str): The randomly generated arrival times of passengers at the bus stop (as str objects).
- `Bus Arrival Time` (str): The actual arrival time of the bus that each passenger will catch (as str objects).
- `Bus Index` (int): The index of the bus that each passenger will catch.
- `Wait Time` (float): The calculated waiting times for each passenger in minutes.


**Note**: You need to generate random arrival times for passengers starting from 6 AM and continuing until the latest bus arrival. First, think about how to represent 6 AM in terms of minutes (since we’re working with time in minutes). Then, calculate the maximum possible time a passenger can arrive by using the latest bus arrival time. Use `np.random.rand` which generates random numbers to simulate passengers arriving at different times between these two points (6 AM and the latest bus arrival). Once you have the random arrival times for passengers, make sure they are sorted in ascending order. This will help you when calculating how long each passenger waits for the next bus.

**Hint:** You may need to use a loop that checks each bus time and advances to the next bus until you find one that is later than the passenger’s arrival.

<br>

####  `visualize_wait_times`
Now that you have the passenger wait times and bus arrival times calculated, the next step is to visualize this data to understand how the Waiting Time Paradox affects passengers. You will create a Plotly visualization to show the distribution of both bus arrivals and passenger wait times within a specific one-hour block. Title the visualization as `Passenger Wait Times`.

Function Inputs:
- `wait_times_df` (DataFrame): A DataFrame containing the bus and passenger arrival times, wait times, and bus indices.
- `timestamp` (pd.Timestamp): The start time of the block, in the format of `HH:MM:SS`.

**Note:** You are not required to understand all the details of Plotly, but you should focus on visualizing the bus routes. We encourage you to use ChatGPT to help create the visualization. When prompting ChatGPT for assistance, focus on three things:
  
- Plot bus arrival times as blue markers: Use `go.Scatter()` to plot the bus arrival times on the x-axis, with y-values set to 0.
- Plot passenger arrival times and wait times as red markers: Use another `go.Scatter()` to plot passenger arrival times on the x-axis and their wait times on the y-axis.
- Draw vertical lines for each passenger from their arrival time (x) to their wait time (y) to illustrate the waiting duration. Try using a for loop when iterating through the passengers. 



```python

```


```python

```


```python
# don't change this cell, but do run it -- it is needed for the tests
passenger_wait_times_df = simulate_wait_times(simulate_bus_arrivals(10), 1000) 
passenger_wait_times_df.head()
```


```python
# don't change this cell, but do run it -- it is needed for the tests
wait_times_df = simulate_wait_times(simulate_bus_arrivals(10), 2000)
fig_q4 = visualize_wait_times(wait_times_df, pd.Timestamp('13:00:00'))
visualize_wait_times_fig = fig_q4.data
fig_q4
```

The Waiting Time Paradox occurs because when you arrive at the bus stop at a random time, you are more likely to arrive during a longer interval between buses. **This happens because longer intervals simply cover more time, making it more probable that you will find yourself waiting during one of these longer gaps.**

This paradox helps explain why passengers frequently experience longer wait times than the scheduled intervals might suggest. By visualizing both bus arrivals and passenger waiting times within a specific one-hour block, we can see this phenomenon in action.


```python
# Test Cases
passenger_wait_times_df
```


```python
grader.check("q4")
```

### Real Data

So far, we've been using simulated data, which we generated under the assumptions of the Poisson process. But does real bus data follow this same distribution? Let's find out with actual bus arrival data:


```python
arrivals = pd.read_csv('data/arrivals.csv')
arrivals.head()
```

To see if real bus data follows a Poisson process, we will analyze the intervals between actual bus arrivals and compare the distribution of these intervals to our simulated data. If the real bus intervals follow an exponential distribution, it would suggest that they follow a Poisson process. However, if they deviate significantly, it would indicate that real-world bus systems do not follow this theoretical model. Run the cell below to find out:


```python
arrivals["Interval"] = (pd.to_datetime(arrivals['Arrival Time'], format='%H:%M:%S').dt.hour * 60 + 
                        pd.to_datetime(arrivals['Arrival Time'], format='%H:%M:%S').dt.minute + 
                        pd.to_datetime(arrivals['Arrival Time'], format='%H:%M:%S').dt.second / 60).sort_values().diff()

plot_histogram_with_mean_line(arrivals['Interval'] ).show()
```

Upon examining the results, it looks like the interval arrivals of buses in real life does not decrease exponentially. This means that the arrival of buses does not follow a Poisson point process. This makes sense because, in practice, bus schedules are structured to optimize service for passengers, not to follow a random Poisson process. Buses do not start their routes at random times but follow a deliberate schedule designed to provide regular and reliable service. 


Now, let's check if the Waiting Time Paradox still exists. Using the function `simulate_wait_times()`, we can calculate the average wait times using real bus arrivals. The Waiting Time Paradox states that the average waiting time for a passenger who arrives at a random time will be longer than half the average interval between buses.

Let's see if this holds true with real-world bus data. Run the cell below: 


```python
wait_times = simulate_wait_times(arrivals, 1000)  # wait time of random passengers arriving to real bus data
passenger_wait_times = wait_times['Wait Time'].mean()
average_bus_arrival_times = arrivals["Interval"].mean()

print('Average Passenger Wait Time: ' + str(passenger_wait_times))
print('Average Bus Arrival Interval Length: ' + str(average_bus_arrival_times))
```

Despite the fact that real bus arrivals do not follow a Poisson process, we observe that the average waiting time for passengers (6 minutes) is still very close to the average interval between buses (7 minutes). This suggests that passengers are still experiencing longer waiting times, which is consistent with the Waiting Time Paradox.

### Real-World Bus Systems

In practice, bus schedules are structured to optimize service for passengers, not to follow a random Poisson process. Buses do not start their routes at random times but follow a deliberate schedule designed to provide regular and reliable service.

### Lessons Learned

The larger lesson here is to be cautious with assumptions in data analysis. While the Poisson process is a useful model for certain types of arrival data, it does not always apply to real-world scenarios. Assumptions that seem correct theoretically can lead to incorrect conclusions when applied to practical situations. For a more in-depth explanation, check out this [article](https://jakevdp.github.io/blog/2018/09/13/waiting-time-paradox/) which delves into the probabilistic reasons behind this paradox.

## Congratulations, you've finished Project 1! 🎉

As a reminder, all of the work you want to submit needs to be in `project.py`.

To ensure that all of the work you want to submit is in `project.py`, we've included a script named `project-validation.py` in the project folder. You shouldn't edit it, but instead, you should call it from the command line (e.g. the Terminal) to test your work.

Once you've finished the project, you should open the command line and run, in the directory for this project:

```
python project-validation.py
```

**This will run all of the `grader.check` cells that you see in this notebook, but only using the code in `project.py` – that is, it doesn't look at any of the code in this notebook. If all of your `grader.check` cells pass in this notebook but not all of them pass in your command line with the above command, then you likely have code in your notebook that isn't in your `project.py`!**

You can also use `project-validation.py` to test individual questions. For instance,

```
python project-validation.py q1 q2
```

will run the `grader.check` cells for Questions 1 and 2 – again, only using the code in `project.py`.

Once `python project-validation.py` shows that you're passing all test cases, you're ready to submit your `project.py` (and only your `project.py`) to Gradescope. Once submitting to Gradescope, make sure to stick around until all test cases pass.

There is also a call to `grader.check_all()` below in _this_ notebook, but make sure to also follow the steps above.


```python

```

---

To double-check your work, the cell below will rerun all of the autograder tests.


```python
grader.check_all()
```


```python

```
