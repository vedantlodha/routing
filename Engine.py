from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import requests
import json
import urllib
from urllib.request import urlopen

def create_data_matrix():
    URL = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&'
    dest = ''

    #build the URL
    locations = get_locations()
    for coordinates in locations:
            dest += str(coordinates[0]) + ',' + str(coordinates[1])
            if coordinates != locations[-1]:
                dest += '|'
    
    api_key = 'AIzaSyA0fBuKW5FDEUJFMUCiZAv_zgXAon8gSgI'
    URL += 'origins=' + dest + '&destinations=' + dest + '&key=' + api_key

    #Http get request
    response = requests.get(URL)
    response_json = response.json()

    #computation of distance matrix
    distance_matrix = []
    for rows in response_json['rows']:
        row_list = [rows['elements'][j]['distance']['value'] for j in range(len(rows['elements']))]
        distance_matrix.append(row_list)
    
    #Scaling down distance matrix because of or-tools distance constraints
    for i in range(len(distance_matrix)):
        for j in range(len(distance_matrix[i])):
                distance_matrix[i][j] = int(distance_matrix [i][j] / 100)
    return distance_matrix

def get_locations():
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
def create_data_model(locations, num_vehicles):
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = create_data_matrix()
    data['num_vehicles'] = num_vehicles
    data['depot'] = 0
    return data

def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    #only for testing purpose
    max_route_distance = 0
    total_distance = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
        total_distance += route_distance
    print('Maximum of the route distances: {}m'.format(max_route_distance))
    print('Total distance travelled = ', total_distance)

def no_empty_routes(data, routing):
    """Ensures all vehicles serves atleast one station"""
    for vehicle_number in range (data['num_vehicles']):
        start_var = routing.NextVar(routing.Start(vehicle_number))
        for node_index in range (routing.Size(), routing.Size()+routing.vehicles()):
            start_var.RemoveValue(node_index)


def solver(data,no_empty_vehivles=false):
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']), 
        data['num_vehicles'], 
        data['depot'])
    
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

def test():
    data = create_data_model()
    manager, routing, solution = solver(data)
    if solution :
        print_solution(data, manager, routing, solution)
    print("Solver status: ", routing.status())
test()