import flask
from flask import request, jsonify
import create_response
import sys
import routing_engine


def convert_locations(locations_string):
    locations_raw = locations_string.split('|')
    locations = [(float(i.split(',')[0]), float(i.split(',')[1]), float(i.split(',')[2])) for i in locations_raw]
    return locations




app = flask.Flask(__name__) 
app.config['Debug'] = True
data_request = {}
@app.route('/api/routes', methods=['GET'])
def get_route():
    if 'locations' in request.args :
        data_request['locations'] = request.args['locations']
    else :
        return 'Error!Locations not provided'
    
    if 'depot' in request.args :
        data_request['depot'] = request.args['depot']
    else :
        return "Error! Starting location not provided"
    

    if 'num_vehicles' in request.args :
        data_request['num_vehicles'] = request.args['num_vehicles']
    else:
        return "Error! Number of vehicles not provided"

    locations = convert_locations(data_request['locations'])
    num_vehicles = int(request.args['num_vehicles'])
    depot_str = request.args['depot']
    depot = tuple(float(i) for i in depot_str.split(','))
    locations.insert(0,depot)

    data = routing_engine.route.create_data_model(locations,num_vehicles)
    data['locations'] = locations
    manager, routing, solution = routing_engine.route.solver(data)
    routes = create_response.routes_callback(data, manager, routing, solution)
    print(routes)
    response = create_response.get_response(data, routes)
    return jsonify(response)
    # locations_string = request.args['locations']
    # return (str(convert_locations(locations_string)))
    # return ()

app.run()

