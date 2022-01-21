#!/usr/bin/python3

# formulae from https://movable-type.co.uk/scripts/latlong.html

import math

def distance(a, b):
    R = 6371e3 # metres
    φ1 = math.radians(a[0])
    φ2 = math.radians(b[0])
    Δφ = math.radians(b[0]-a[0])
    Δλ = math.radians(b[1]-a[1])

    a = (math.sin(Δφ/2) * math.sin(Δφ/2) +
         math.cos(φ1) * math.cos(φ2) *
         math.sin(Δλ/2) * math.sin(Δλ/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c # in metres

def bearing(a, b):
    φ1 = math.radians(a[0])
    φ2 = math.radians(b[0])
    Δλ = math.radians(b[1]-a[1])

    y = math.sin(Δλ) * math.cos(φ2)
    x = (math.cos(φ1)*math.sin(φ2) -
         math.sin(φ1)*math.cos(φ2)*math.cos(Δλ))
    return (math.degrees(math.atan2(y, x)) + 360) % 360; # in degrees

def main():
    """Test function."""
    # https://www.openstreetmap.org/#map=19/
    charing_cross = (51.50796, -0.12640)
    great_st_marys = (52.20531, 0.11801)
    carfax = (51.75198,-1.25785)
    bath_abbey = (51.38147,-2.35835)
    print(distance(charing_cross, great_st_marys)/1000, "Km from Charing Cross to Great St Mary's")
    print(bearing(charing_cross, great_st_marys), "bearing from Charing Cross to Great St Mary's")
    print(distance(charing_cross, carfax)/1000, "Km from Charing Cross to Carfax")
    print(bearing(charing_cross, carfax), "bearing from Charing Cross to Carfax")
    print(distance(charing_cross, bath_abbey)/1000, "Km from Charing Cross to Bath Abbey")
    print(bearing(charing_cross, bath_abbey), "bearing from Charing Cross to Bath Abbey")
    print(distance(great_st_marys, carfax)/1000, "Km from Great St Mary's to Carfax")
    print(bearing(great_st_marys, carfax), "bearing from Great St Mary's to Carfax")
    print(distance(great_st_marys, carfax)/1000, "Km from Great St Mary's to Carfax")
    print(bearing(great_st_marys, carfax), "bearing from Great St Mary's to Carfax")
    print(distance(great_st_marys, bath_abbey)/1000, "Km from Great St Mary's to Bath Abbey")
    print(bearing(great_st_marys, bath_abbey), "bearing from Great St Mary's to Bath Abbey")

if __name__ == "__main__":
    main()
