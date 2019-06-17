import requests

def locations():
    locations = [(12.9571,77.659439),
                (12.9353173134382,77.7402628734708),
                (12.965534,77.5341921),
                (12.965716,77.5347942),
                # (12.988413,77.630671),
                # (12.9777275770552,77.7406826391816),
                # (12.9781522327987,77.7331734597683),
                # (12.9542097712404,77.7810297682881),
                (12.9598,77.6434),
                (12.9580054,77.6478705),
                (12.9667323,77.7314212),
                (12.9603074,77.6411069),
                (12.9645389,77.4449567)]
    return locations


def create_distance_matrix(locations):
    URL = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&'
    dest = ''
    for coordinates in locations:
            dest += str(coordinates[0]) + ',' + str(coordinates[1])
            if coordinates != locations[-1]:
                dest += '|'
    api_key = 'AIzaSyA0fBuKW5FDEUJFMUCiZAv_zgXAon8gSgI'
    URL += 'origins=' + dest + '&destinations=' + dest + '&key=' + api_key
    response = requests.get(URL)
    response_json = response.json()
    
create_distance_matrix(locations())
