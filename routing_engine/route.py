from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import requests
import json
import urllib
from urllib.request import urlopen
import routing_engine.config
def create_data_matrix(locations):
    number_of_locations = len(locations)
    #Distance Matrix API allows only 100 locations per call
    max_elements = 100
    data_matrix = []
    max_rows = max_elements // number_of_locations
    q, r = divmod(number_of_locations, max_rows)
    destinations_array = locations
    for i in range(q):
        origins_array = locations[i*max_rows : (i+1) * max_rows]
        URL = build_url(locations, origins_array, destinations_array)
        distance_matrix = build_distance_matrix(URL)
        data_matrix += distance_matrix
    if r > 0 :

        origins_array = locations[q*max_rows : q * max_rows + r]
        URL = build_url(locations, origins_array, destinations_array)
        distance_matrix = build_distance_matrix(URL)
        data_matrix += distance_matrix

    return data_matrix

def build_url(locations, origins_array, destinations_array):
    URL = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&'
    destinations = ''
    origins = ''
    #build oigin string
    for i in origins_array:
        origins += str(i[1]) + ',' + str(i[2])
        if i != origins_array[-1]:
            origins += '|'
    #build destination string
    for i in destinations_array:
        destinations += str(i[1]) + ',' + str(i[2])
        if i != destinations_array[-1]:
            destinations += '|'

    api_key = routing_engine.config.api_key
    URL += 'origins=' + origins + '&destinations=' + destinations + '&key=' + api_key
    return URL


def build_distance_matrix(URL):
    response = requests.get(URL)
    response_json = response.json()
    print(response.text)

    #computation of distance matrix
    distance_matrix = []
    print(response.text)
    for rows in response_json['rows']:
        row_list = [rows['elements'][j]['distance']['value'] for j in range(len(rows['elements']))]
        distance_matrix.append(row_list)

    #Scaling down distance matrix because of or-tools distance constraints
    for i in range(len(distance_matrix)):
        for j in range(len(distance_matrix[i])):
                distance_matrix[i][j] = int(distance_matrix [i][j] / 100)
    return distance_matrix



def create_data_model(locations, depots):
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = create_data_matrix(locations)
    data['num_vehicles'] = len(depots)
    data['depots'] = depots
    return data



def no_empty_routes(data, routing):
    """Ensures all vehicles serves atleast one station"""
    for vehicle_number in range (data['num_vehicles']):
        start_var = routing.NextVar(routing.Start(vehicle_number))
        for node_index in range (routing.Size(), routing.Size()+routing.vehicles()):
            start_var.RemoveValue(node_index)


def solver(data,no_empty_vehicles=False):
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']),
        data['num_vehicles'],
        data['depots'], data['depots'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

     # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

     # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        30000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC)
    search_parameters.local_search_metaheuristic = (
    routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = 10
    search_parameters.lns_time_limit.seconds= 50
    search_parameters.log_search = True


    #Ensure all vehicles serve atleast one station
    if no_empty_vehicles:
        no_empty_routes(data, routing)

    # Create a solver
    solution = routing.SolveWithParameters(search_parameters)
    return manager, routing, solution
