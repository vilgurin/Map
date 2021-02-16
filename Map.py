import folium
import haversine

from geopy.exc import GeocoderUnavailable

from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="specify")

from geopy.extra.rate_limiter import RateLimiter
geocode = RateLimiter(geolocator.geocode,  min_delay_seconds  =  0.3) 

def f_input():
    '''
    The function takes three argumetns, which represent 
    a year of film and the location which includes longtitude and latitude
    '''
    year = input("Please enter a year you would like to have a map for:")
    location = input("Please enter your location")
    location = location.split(" ")
    location.append(year)
    return location

def reading(path):
    '''
    The function reads information from a file and converts 
    it to a more convenient shape, sorming a list
    '''
    locations_list = []
    with open(path,"r") as locations:
        for line in locations:
            line = line.strip("\n")
            line = line.split("\t")
            line[0] = line[0].replace(")","(")
            line[0] = line[0].split("(")
            if "(" in line[-1]:
                line = [line[0][0].replace('"',""), line[0][1],line[-2]]
            else:
                line = [line[0][0].replace('"',""), line[0][1],line[-1]]
            locations_list.append(line)
    locations.close()
    return locations_list



def year_sort(year,lst):
    '''
    The function takes a list and ejects the lines
    which contain a particular year without repetitions
    >>> year_sort(2015,[['#1 Single ', '2006', 'Los Angeles, California, USA'],\
     ['#1 Single ', '2006', 'New York City, New York, USA'],\
      ['#15SecondScare ', '2015', 'Coventry, West Midlands, England, UK'],\
       ['#15SecondScare ', '2015', 'West Hills, California, USA'],\
        ['#15SecondScare ', '2015', 'West Hills, California, USA'],\
         ['#2WheelzNHeelz ', '2017', 'Nashville, Tennessee, USA']])

    [['#15SecondScare ', '2015', 'Coventry, West Midlands, England, UK'],\
     ['#15SecondScare ', '2015', 'West Hills, California, USA']]
    '''
    year_list = []
    for line in lst :
        if str(year) in line:
            if line not in year_list:
                year_list.append(line)
    return year_list



def calculate_coordinates(lst):
    '''
    The function creates a list of elements which contains latitude and 
    longtitude of each location
    '''
    for line in lst:
        try:
            line[-1] = line[-1].split(",")[-2:]
            line[-1] = ",".join(line[-1])
            location = geolocator.geocode(line[-1].split(","))
            line[-1] = str(location.latitude) 
            line.append(str(location.longitude))
        except AttributeError:
            pass
        except GeocoderUnavailable:
            pass
    return lst


def calculate_distance(lst,coordinates):
    '''
    The function calculates a distance between your location and a location of 
    each film.
    '''
    new_list =[]
    for line in lst:
        try:
            if line[-1] != "":
                line.append(haversine.haversine((float(line[-2]),float(line[-1])),coordinates))
                new_list.append(line)
        except ValueError:
            pass
    return sorted(new_list, key = lambda x: x[-1])[:10]


def folium_map(lst,coordinates):
    '''
    The function draws a map with the marks which represents 
    a particular films
    '''

    film_map = folium.Map(tiles='OpenStreetMap', location=[coordinates[0], coordinates[1]], zoom_start=10)

    fg = folium.FeatureGroup(name='map')

    for line in lst:
            fg.add_child(folium.Marker(location=(line[-3], line[-2]),
                                    popup = line[0]))

    film_map.add_child(fg)

    fg1 = folium.FeatureGroup(name='lines')

    for line in lst:
        fg1.add_child(folium.PolyLine([(coordinates[0], coordinates[1]),(line[-3], line[-2])]))

    film_map.add_child(fg1)

    film_map.save("Film_location.html")

