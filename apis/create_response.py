import flask
from flask import jsonify, request
import sys
sys.path.insert(0, '../')
from routing_engine.route import solver, create_data_model
import json

def create_location_object(id, lattitude, longitude):
    "returns location as a dictionary"
    return {
        'id' : id,
        'lattitude' : lattitude,
        'longitude' : longitude
    }


def routes_callback(data,manager, routing, solution):
    routes = []
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        vehicle_route = []
        vehicle_route.append(manager.IndexToNode(index))
        while not routing.IsEnd(index):
            index = solution.Value(routing.NextVar(index))
            vehicle_route.append(manager.IndexToNode(index))
        routes.append(vehicle_route)
    return routes




def get_response(data, routes):
    locations = data['locations']
    response = {}
    num_vehicles = data['num_vehicles']
    depot = locations[data['depot']]
    if len(routes) != num_vehicles:
        response['status'] = 'error'
    elif len(routes ) == num_vehicles:
        response['status_code'] = 100
        response['number_of_vehicles'] = num_vehicles
        response['depot'] = create_location_object(depot[0],depot[1],depot[2])
        route_response = []
        for vehicle_number in range(len(routes)):
            vehicle = {}
            vehicle['vehicle_code'] = vehicle_number
            vehicle_route = []
            for location_number in routes[vehicle_number] :
                location = locations[location_number]
                location_object = create_location_object(location[0], location[1], location[2])
                vehicle_route.append(location_object)
            vehicle['vehicle_route'] = vehicle_route
            route_response.append(vehicle)
        response['routes'] = route_response
        response['Errors'] = "No Errors"
        return response
