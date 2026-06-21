

from flask import Flask, render_template_string, request, render_template

import folium

import folium.plugins as plugins
from bs4 import BeautifulSoup
from folium.plugins import Geocoder,LocateControl,ScrollZoomToggler,BeautifyIcon
from geopy.geocoders import Nominatim
from geopy.point import Point
from shapely.geometry.point import Point as point_number
import shapely


app = Flask(__name__)
href="{{ url_for('static', filename='main.css')}}"

def sentinel_authentication ():
        '''Requests authentication token from Sentinel Hub

        Returns:
        auth(str) - access_token '''
        from oauthlib.oauth2 import BackendApplicationClient
        from requests_oauthlib import OAuth2Session
        from sentinelhub import SHConfig

        config = SHConfig()

        # Your client credentials
        client_id = '96acbb95-6c77-4d93-aaf3-ca218727e1b4'
        client_secret = 'F@,ZbT*8PTZ(F}:7@.|,*;#K/K/Ev+#)uRLQ,^t2'

        # Create a session
        client = BackendApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client=client)

        # Get token for the session
        token = oauth.fetch_token(token_url='https://services.sentinel-hub.com/oauth/token',
                                  client_secret=client_secret)

        # All requests using this session will have an access token automatically added
        resp = oauth.get("https://services.sentinel-hub.com/oauth/tokeninfo")

        auth = token['access_token']

        return auth

url = "https://services.sentinel-hub.com/api/v1/statistics"
headers = {
          "Authorization": "Bearer " ,
          "Accept": "application/json",
          "Content-Type": "application/json"
        }
data = {
          "input": {
            "bounds": {
              "bbox": [
                -121.00001,
                45.99999,
                -120.99999,
                46.00001
              ]
            },
            "data": [
              {
                "dataFilter": {
                  "maxCloudCoverage": 40
                },
                "type": "sentinel-2-l2a"
              }
            ]
          },
          "aggregation": {
            "timeRange": {
              "from": "2022-01-01T00:00:00Z",
              "to": "2022-12-31T23:59:59Z"
            },
            "aggregationInterval": {
              "of": "P7D"
            },
            "width": 512,
            "height": 737.053,
            "evalscript": "//VERSION=3\nfunction setup() {\n  return {\n    input: [{\n      bands: [\n        \"B04\",\n        \"B08\",\n        \"SCL\",\n        \"dataMask\"\n      ]\n    }],\n    output: [\n      {\n        id: \"data\",\n        bands: 1\n      },\n      {\n        id: \"dataMask\",\n        bands: 1\n      }]\n  }\n}\n\nfunction evaluatePixel(samples) {\n    let ndvi = (samples.B08 - samples.B04)/(samples.B08 + samples.B04)\n    \n    var validNDVIMask = 1\n    if (samples.B08 + samples.B04 == 0 ){\n        validNDVIMask = 0\n    }\n    \n    var noWaterMask = 1\n    if (samples.SCL == 6 ){\n        noWaterMask = 0\n    }\n\n    return {\n        data: [ndvi],\n        // Exclude nodata pixels, pixels where ndvi is not defined and water pixels from statistics:\n        dataMask: [samples.dataMask * validNDVIMask * noWaterMask]\n    }\n}"
          },
          "calculations": {
            "default": {}
          }
        }



@app.route('/')

def fulscreen():
    
    ###
    import geocoder
    g = geocoder.ipinfo('me')
    
    import reverse_geocoder as rg

    coordinates = g.latlng

    results = rg.search(coordinates,mode=1) # default mode = 2
    variable = results[0]["name"]
    
    data = g.latlng
    
    ###
    #import requests
    #from opencage.geocoder import OpenCageGeocode
    
    #key = '5f5d6cbf0ac5444db2b16b092667200d'
    #geocoder = OpenCageGeocode(key)
    #query = "1087LN"
    #query = request.args.get('user_input')

    # no need to URI encode query, module does that for you
    #results = geocoder.geocode(query)
    #user_lat = results[0]['geometry']['lat']
    #user_lng = results[0]['geometry']['lng']
    #variable = [[user_lat,user_lng]]
    return render_template('index.html', text=variable, data=data)  


@app.route('/results')
def results():
    import os
    import requests
    import pandas as pd
    import json
    from plotly_calplot import calplot
    import plotly.express as px
    import numpy as np
    
    df=[]
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    geolocator = Nominatim(user_agent="treeindex.nl")
    location = geolocator.reverse(Point(lat, lon))
    circle = point_number(int(float(lat)),int(float(lon))).buffer(.00001)
    temp_list = list(circle.bounds)
    temp_order = [1,0,3,2]
    bbox = [temp_list[i] for i in temp_order]
    hash_value = str(hash(str(bbox)))
   
    xy = [float(lat),float(lon)]
    print(xy)
    

    my_colorsc=[[0, 'red'], [0.33, 'yellow'], [0.66, 'greenyellow'],[1.,"green"]]
    


    
    
    
    if os.path.isfile("\data"+hash_value+".csv") == True:
        df = pd.read_csv("\data"+hash_value+".csv")
        df['date'] = pd.to_datetime(df['date'])
        fig = calplot(df, x="date", y="outputs.data.bands.B0.stats.mean",gap=0,
                  colorscale=my_colorsc)
        out = fig.to_html(full_html=False,include_plotlyjs="cdn",config = {'displayModeBar': False})

    else:
        
        data["input"]["bounds"]["bbox"] = json.loads(str(bbox).replace("%20",""))
        headers["authorization"] = "Bearer "+ sentinel_authentication()
        #json_object = json.dumps(data, indent = 4)

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        import plotly.express as px
        df_viz = pd.json_normalize(result["data"])[["interval.from","interval.to","outputs.data.bands.B0.stats.mean"]]
        df_viz["interval.from"] = df_viz["interval.from"].str.replace(r'T00:00:00Z', '')
        df_viz['date'] = pd.to_datetime(df_viz['interval.from'])
        df_viz[df_viz.columns[[2,3]]].to_csv("\data"+hash_value+".csv")
    
        #from plotly_calplot import calplot

        
        fig = calplot(df_viz, x="date", y="outputs.data.bands.B0.stats.mean",gap=0,years_title=False, colorscale=my_colorsc)
        out = fig.to_html(full_html=False,include_plotlyjs="cdn",config = {'displayModeBar': False})
        
        import seaborn as sns
        import pandas as pd
        from matplotlib import pyplot as plt

        #_, bp = pd.DataFrame.boxplot(df_viz, return_type='both')
        #outliers = [flier.get_ydata() for flier in bp["fliers"]]
        #outliers_dates = df_viz[df_viz["outputs.data.bands.B0.stats.mean"].isin(outliers)]
    

  

    return render_template('results.html', out=out,text=location, hash=hash, data=xy)
    
    
if __name__ == "__main__":
    app.run(debug=True)