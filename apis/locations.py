def convert_locations(locations_string):
    locations_raw = locations_string.split('|')
    locations = [(int(i[0]), int(i[1]), int(i[2])) for i in locations_raw]
    return locations