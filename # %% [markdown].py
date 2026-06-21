# %% [markdown]
# Process outline and tests

# %%
def treeindex_ndvi(city_name):
    """Runs pipeline of NDVI data retrieval
    Args:
    city_name
    year
    """
    
    directory(city_name)
    print("Directory created")
    input_folder = f"/Users/jbms/TI/{city_name}"
    output_folder = f"/Users/jbms/TI/{city_name}"
    date_start = '2017-01-01'
    date_end = '2017-12-31'
    #geotiff_caller(city_name)
    geotiff_multi_caller(city_name,bbox_city(city_name),input_folder,date_start,date_end)
    print("Data download completed")
    #convert_raster_to_CSV(input_folder,output_folder)
    return
    
def treeindex_start(city_name):
    bbox = bbox_city(city_name)
    data = trees(bbox)
    with open(f'{city_name}.json', 'w') as convert_file:
        convert_file.write(json.dumps(data))

# %%
treeindex_ndvi("Warsaw")
#bbox_city("Ciechacnow")

# %%


# %%
bbox_city("Amsterdam")

# %%


# %%
convert_raster_to_CSV("/Users/jbms/TI/Amsterdam/b89b1344f4a1bafa4a051eaa981facd0/response/","/Users/jbms/TI/Amsterdam/b89b1344f4a1bafa4a051eaa981facd0/response/")

# %%


# %%


# %%


# %%


# %%


# %%
#functions

def directory(city_name):
    import os 

    # path 

    path = f"/Users/jbms/TI/{city_name}" 

    try: 
        os.mkdir(path) 
    except OSError as error: 
        print(error)
        
def dates_list():
    """pulls list of dates"""
    

def sentinel_authentication():
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

    return token['access_token']




import urllib, json
def bbox_city(name):
    """ Returns bbox value based on the city name
    
    Args:
    name(str) - name of the city or settlement
    
    Returns:
    bbox(lst) - list of geographical points in BBOX format
    """
    link = "https://nominatim.openstreetmap.org/search/" + str(name).replace(" ","-") + "?format=geojson&polygon=1&polygon_geojson=1&limit=1"
    response = urllib.request.urlopen(link)
    data = json.loads(response.read())
    return data['features'][0]['bbox']


def clean_bbox(result):
    """Transforms BBOX returned by the bbox_city() to the right order.
    
    Args:
    result - bbox returned by the bbox_city() function
    
    Returns:
    bbox_clean - list in BBOX format in the right order
    """

    myorder = [1, 0, 3, 2]
    result_clean = [result[i] for i in myorder]
    result_clean = str(result_clean)
    bbox_clean = result_clean.replace("[","")
    return bbox_clean.replace("]","")


import time
def trees(bbox_clean):
    """Returns json with list of trees from Open Street Map
    
    Args:
    bbox_clean
    
    Returns:
    response.json() - response of the server in JSON format
    """
    query = f'https://lz4.overpass-api.de/api/interpreter?data=[out:json];(node["natural"="tree"]({bbox_clean}););out body;>;out skel qt;'
    response = requests.get(query)
    print(response.status_code)
    return response.json()


import requests, json

def geotiff_caller(name,bbox,date_from,date_to):
    """Returns geotiff per date
    
    Args:
    name
    bbox(lst) - bbox in form of the list
    date_from
    date_to
    
    """
    
    headers = {'Authorization': f'Bearer {sentinel_authentication()}'}

    files = {'request': (None, '{"input": {"bounds": {"properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"}, "bbox": [139.368439, 35.515461, 140.060577, 35.877924]}, "data": [{"type": "sentinel-2-l2a", "dataFilter": {"timeRange": {"from": "2022-10-21T01:27:21Z", "to": "2022-10-21T01:27:21Z"}, "maxCloudCoverage": 2}, "processing": {"harmonizeValues": "true"}}]}, "output": {"width": 512, "height": 512, "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}]}}'), 'evalscript': (None, '//VERSION=3\nfunction setup() {\n  return{\n    input: [{\n      bands: ["B04", "B08"],\n      units: "REFLECTANCE"\n    }],\n    output: {\n      id: "default",\n      bands: 1,\n      sampleType: SampleType.FLOAT32\n    }\n  }\n}\n\nfunction evaluatePixel(sample) {\n  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04)\n  return [ ndvi ]\n}')}

    request = json.loads(files["request"][1])
    request["input"]["bounds"]["bbox"] = bbox
    #request["input"]["bounds"]["bbox"] = [139.368439,35.515461,140.060577,35.877924]
    request["input"]["data"][0]["dataFilter"]["timeRange"]["from"] = date_from
    #request["input"]["data"][0]["dataFilter"]["timeRange"]["from"] = '2022-02-27T00:00:00Z'
    request["input"]["data"][0]["dataFilter"]["timeRange"]["to"] = date_to
    #request["input"]["data"][0]["dataFilter"]["timeRange"]["to"] = '2022-03-06T00:00:00Z'
    request["input"]["data"][0]["dataFilter"]["maxCloudCoverage"] = 15
    files["request"] = None, json.dumps(request)
    #print(files)

    response = requests.post('https://services.sentinel-hub.com/api/v1/process', headers=headers, files=files)
    date = "test date"
    with open(name+date+".tif", "wb") as f:
        f.write(response.content)

    return print(date)

# This is script may only work with sentinelhub.__version__ >= '3.4.0'
def geotiff_multi_caller(city_name,bbox_input,input_folder, date_start,date_end):
    ''' Returns geotiff and json with NDVi over years
    Args:
    bbox_input - list of bbox
    date_start - '2022-08-31'
    date_end - '2022-08-31'
    '''
    import time
    start_time = time.time()

    from sentinelhub import SentinelHubRequest, DataCollection, MimeType, CRS, BBox, SHConfig, Geometry


    # Credentials
    config = SHConfig()
    config.sh_client_id = '96acbb95-6c77-4d93-aaf3-ca218727e1b4'
    config.sh_client_secret = 'F@,ZbT*8PTZ(F}:7@.|,*;#K/K/Ev+#)uRLQ,^t2'
    evalscript = """
    //VERSION=3
    // Script to extract a time series of NDVI values using 
    // Sentinel 2 Level 2A data and  metadata file.
    function setup() {
        return {
          input: [{
            bands: ["B04", "B08"],
            units: "DN"
          }],
          output: {
            
            bands: 1,
            sampleType: SampleType.FLOAT32
          },
          mosaicking: Mosaicking.ORBIT
        }

      }

      // The following function is designed to update the number of
      // output bands without knowing beforehand how many there are
      function updateOutput(outputs, collection) {
          Object.values(outputs).forEach((output) => {
              output.bands = collection.scenes.length;
          });
      }
      // function to generate a json file with a list of the NDVI 
      // dates used in the analysis. 
      function updateOutputMetadata(scenes, inputMetadata, outputMetadata) {
          var dds = [];
          for (i=0; i<scenes.length; i++){
            dds.push(scenes[i].date)
          }
          outputMetadata.userData = { "acquisition_dates":  JSON.stringify(dds) }
      }

      function evaluatePixel(samples) {
        // Precompute an array to contain NDVI observations
        var n_observations = samples.length;
        let ndvi = new Array(n_observations).fill(0);

        // Fill the array with NDVI values
        samples.forEach((sample, index) => {
          ndvi[index] = (sample.B08 - sample.B04) / (sample.B08 + sample.B04) ;
        });

        return ndvi;
      }

    """
    bbox = BBox(bbox=bbox_input, crs=CRS.WGS84)
    from shapely.geometry import box
    #b = box(bbox_input[0],bbox_input[1],bbox_input[2],bbox_input[3])
    #geometry = Geometry(b, crs=CRS.WGS84)

    request = SentinelHubRequest(
        data_folder=input_folder,
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,          
                time_interval=(date_start, date_end),          
                other_args={"dataFilter": {"maxCloudCoverage": 15,"mosaickingOrder": "leastCC"},"processing": {"harmonizeValues": True}}
            ),
        ],
        responses=[
            SentinelHubRequest.output_response('default', MimeType.TIFF),
        SentinelHubRequest.output_response('userdata', MimeType.JSON),
        ],
        bbox=bbox,
        #geometry=geometry,
        size=[512, 512],
        config=config
    )

    r = request.save_data()
    #data = response
    #import pickle
    #with open(input_folder+"/"+city_name+'.pickle', 'wb') as f:
    #    pickle.dump(data, f)

    return r, print(f"--- {time.time() - start_time} seconds ---")

def raster_folder(name,date):
    """Writes geotiff answer from API call as file"""
    output_folder = ""

    response = geotiff_caller(date)
    with open(name+date+".tif", "wb") as f:
        f.write(response.content)


import os
import gdal2xyz
import fnmatch
def convert_raster_to_CSV(input_folder, output_folder,raster_extension='*.tif', band=1):
    """Converts multiple raster files to csv
    Args:
    input_folder - path to folder with rasters
    output_folder - path to folder for resulting CSV"""
    files_list = os.listdir(input_folder)
    for item in files_list:
        if fnmatch.fnmatch(item, raster_extension):
            print(f"processing {item}")
            in_raster = f'{input_folder}/{item}'
            out_csv_file = f'{output_folder}/{item[:-4]}.csv'
            gdal2xyz.gdal2xyz(srcfile=in_raster, dstfile=out_csv_file,delim= ',')

import pandas as pd
import json

def trees_location(city_name):
    """Returns dataframe"""
    dataframe = pd.read_json('/Users/jbms/'+city_name+".json",orient='index')
    trees = pd.DataFrame(dataframe[0]['elements'])
    trees = trees.sort_values(by=['lat','lon'], ascending=True).reset_index(drop=True)[["id","lat","lon"]]
    return trees


