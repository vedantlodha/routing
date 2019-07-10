from __future__ import print_function
import sys
sys.path.insert(0, '../')
from routing_engine.route import solver, create_data_model



def get_locations():
    """Returns sample coordinates for testing purposes"""
    locations = [(1,12.9571,77.659439),
                (2,12.9353173134382,77.7402628734708),
                (3,12.965534,77.5341921),
                (4,12.965716,77.5347942),
                (5,12.988413,77.630671),
                (6,12.9777275770552,77.7406826391816),
                (7,12.9781522327987,77.7331734597683),
                (8,12.9542097712404,77.7810297682881),
                (9,12.9598,77.6434),
                (10,12.9580054,77.6478705),
                (11,12.9667323,77.7314212),
                (12,12.9603074,77.6411069),
                (13,12.9645389,77.4449567)]
    return locations

def print_solution(data, manager, routing, solution):
    """Prints solution on console."""

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


def main():
    data = create_data_model(get_locations(), [0,7,3])
    manager, routing, solution = solver(data)
    if solution :
        print(routes_callback(data,manager, routing, solution))
    print("Solver status: ", routing.status())

if __name__ == "__main__":
    main()