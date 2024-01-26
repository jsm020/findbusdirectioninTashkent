import time
import asyncio
import requests
from geopy.distance import geodesic
from data import data
from databus import numbers

# Initialize x_data as an empty list

async def get_location(loc):
    details_distances = []

    for item in data:
        id, stationId, name, uzName = item["id"], item["stationId"], item["name"], item["uzName"]
        ly, lx = item["ly"], item["lx"]
        loc2 = (ly, lx)
        distance = geodesic(loc, loc2).kilometers
        details_distances.append((id, stationId, name, uzName, loc2, distance))

    details_distances.sort(key=lambda x: x[-1])
    return details_distances[:2]

async def find_location(location):
    sata = []
    if location:
        tasks = []
        for item in location:
            stationId, uzName = item[1], item[3]
            print(stationId, uzName)

            if stationId:
                unique_ids = set()
                task = asyncio.create_task(fetch_routes(stationId, unique_ids, sata))
                tasks.append(task)

        await asyncio.gather(*tasks)

    return sata

async def fetch_routes(stationId, unique_ids, sata):
    routes = requests.get(f"http://207.90.194.130:8084/routes/map/station/routes/{stationId}").json()

    for item in routes:
        if "routeNumber" in item and item["routeNumber"].isdigit() and int(item["routeNumber"]) < 200:
            if item["id"] not in unique_ids:
                unique_ids.add(item["id"])
                sata.append(item)

async def find_common_elements(list1, list2, key='routeNumber'):
    set1 = {item[key] for item in list1}
    set2 = {item[key] for item in list2}
    common_values = set1.intersection(set2) 
    if not common_values:
        print(set1)
        print(set2)
        print(1)
        halm = set(set2)
        tasks = []
        for element in halm:
            data = []
            bus_numb = numbers.get(element)
            task = asyncio.create_task(fetch_routes_by_bus(element, set1, data))
            tasks.append(task)

        await asyncio.gather(*tasks)
    else:
        for item in common_values:
            x = f"Avvalom bor siz {item}ga minib sungi manzilga yetib olasiz"
            print(x)


async def fetch_routes_by_bus(bus_number, set1, data):
    x_data = [] 
    routes_bus = requests.get(f"http://207.90.194.130:8084/routes/stations/{bus_number}").json()

    unique_ids = set()

    for item in routes_bus:
        stationId = item["stationId"]
        routes = requests.get(f"http://207.90.194.130:8084/routes/map/station/routes/{stationId}").json()
        data.append(routes)
        
        for dataid in routes:
            if dataid["routeNumber"] in set1 and dataid["id"] not in unique_ids:
                x = f"Avvalom bor siz {bus_number}ga minib {item['uzName']}ga borasz va {dataid['routeNumber']}orqali sungi manzilga yetib olasiz"
                unique_ids.add(dataid["id"])
                x_data.append(x)
        break
    if x_data :
        print(x_data)
    elif not x_data:
        print("topilmadi")

async def main():
    location = await get_location(loc=(41.30376417457077, 69.2481972407017))

    print(location)
    location_2 = await find_location(location)
    print("----------------------------------------------------------------------------")
    location = await get_location(loc=(41.259418, 69.223833))

    print(location)

    location_3 = await find_location(location)
    print("----------------------------------------------------------------------------")
    print("----------------------------------------------------------------------------")

    await find_common_elements(list1=location_2, list2=location_3, key="routeNumber")



if __name__ == "__main__":
    asyncio.run(main())