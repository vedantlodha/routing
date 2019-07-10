 class vehicle:
     def __init__(self, vehicle_id, servicable_area=[]):
         self.vehicle_id = vehicle_id
         self.servicable_area = servicable_area
    def assign_route(self, route):
        self.route = route
