from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import requests
import json
import urllib
from urllib.request import urlopen
import pdb
# def create_data_model(depot, stations, number_of_vehicles):
#     URL = ''
#     api_key = ''
#     locations = depot + stations
#     data = {}
#     data['depot'] = 0
#     data['number_of_vehicles'] = number_of_vehicles
#     data['distance_matrix'] = []
#     rquotient, remainder = divmod(len(locations),100)
#     #Distance Matrix API accepts maximum 100 elements per request
#     maximum_elements = 100
#     number_of_addresses = len(locations)
    

def create_data():
  """Creates the data."""
  data = {}
  data['API_key'] = 'AIzaSyA0fBuKW5FDEUJFMUCiZAv_zgXAon8gSgI'
  data['addresses'] = ['3610+Hacks+Cross+Rd+Memphis+TN', # depot
                       '1921+Elvis+Presley+Blvd+Memphis+TN',
                       '149+Union+Avenue+Memphis+TN',
                       '1034+Audubon+Drive+Memphis+TN',
                       '1532+Madison+Ave+Memphis+TN',
                       '706+Union+Ave+Memphis+TN',
                       '3641+Central+Ave+Memphis+TN',
                       '926+E+McLemore+Ave+Memphis+TN',
                       '4339+Park+Ave+Memphis+TN',
                       '600+Goodwyn+St+Memphis+TN',
                       '2000+North+Pkwy+Memphis+TN',
                       '262+Danny+Thomas+Pl+Memphis+TN',
                       '125+N+Front+St+Memphis+TN',
                       '5959+Park+Ave+Memphis+TN',
                       '814+Scott+St+Memphis+TN',
                       '1005+Tillman+St+Memphis+TN'
                      ]
  return data

def create_distance_matrix(data):
  addresses = data["addresses"]
  API_key = data["API_key"]
  # Distance Matrix API only accepts 100 elements per request, so get rows in multiple requests.
  max_elements = 100
  num_addresses = len(addresses) # 16 in this example.
  max_rows = max_elements 
  # num_addresses = q * max_rows + r 
  q, r = divmod(num_addresses, max_rows)
  dest_addresses = addresses
  distance_matrix = []
  # Send q requests, returning max_rows rows per request.
  for i in range(q):
    origin_addresses = addresses[i * max_rows: (i + 1) * max_rows]
    response = send_request(origin_addresses, dest_addresses, API_key)
    distance_matrix += build_distance_matrix(response)

  # Get the remaining remaining r rows, if necessary.
  if r > 0:
    origin_addresses = addresses[q * max_rows: q * max_rows + r]
    response = send_request(origin_addresses, dest_addresses, API_key)
z    distance_matrix += build_distance_matrix(response)
  return distance_matrix

def send_request(origin_addresses, dest_addresses, API_key):
  """ Build and send request for the given origin and destination addresses."""
  def build_address_str(addresses):
    # Build a pipe-separated string of addresses
    address_str = ''
    for i in range(len(addresses) - 1):
      address_str += addresses[i] + '|'
    address_str += addresses[-1]
    return address_str

  request = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial'
  origin_address_str = build_address_str(origin_addresses)
  dest_address_str = build_address_str(dest_addresses)
  request = request + '&origins=' + origin_address_str + '&destinations=' + \
                       dest_address_str + '&key=' + API_key
  jsonResult = urlopen(request).read()
  response = json.loads(jsonResult)
  return response

def build_distance_matrix(response):
  distance_matrix = []
  for row in response['rows']:
    row_list = [row['elements'][j]['distance']['value'] for j in range(len(row['elements']))]
    distance_matrix.append(row_list)
  return distance_matrix


def create_data_model():
    """Stores the data for the problem."""
    data = {}
    # data['distance_matrix'] = [
    #     [
    #         0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354,
    #         468, 776, 662
    #     ],
    #     [
    #         548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674,
    #         1016, 868, 1210
    #     ],
    #     [
    #         776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164,
    #         1130, 788, 1552, 754
    #     ],
    #     [
    #         696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822,
    #         1164, 560, 1358
    #     ],
    #     [
    #         582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708,
    #         1050, 674, 1244
    #     ],
    #     [
    #         274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628,
    #         514, 1050, 708
    #     ],
    #     [
    #         502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856,
    #         514, 1278, 480
    #     ],
    #     [
    #         194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320,
    #         662, 742, 856
    #     ],
    #     [
    #         308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662,
    #         320, 1084, 514
    #     ],
    #     [
    #         194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388,
    #         274, 810, 468
    #     ],
    #     [
    #         536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764,
    #         730, 388, 1152, 354
    #     ],
    #     [
    #         502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114,
    #         308, 650, 274, 844
    #     ],
    #     [
    #         388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194,
    #         536, 388, 730
    #     ],
    #     [
    #         354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0,
    #         342, 422, 536
    #     ],
    #     [
    #         468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536,
    #         342, 0, 764, 194
    #     ],
    #     [
    #         776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274,
    #         388, 422, 764, 0, 798
    #     ],
    #     [
    #         662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730,
    #         536, 194, 798, 0
    #     ],
    #     # [0,2,6,9],
    #     # [2,0,8,4],
    #     # [6,8,0,3],
    #     # [9,11,3,0]
    # ]
    location_details = create_data()
    data['distance_matrix'] = create_distance_matrix(location_details)
    data['num_vehicles'] = 3
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


def solver(data):
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


pdb.set_trace()
test()