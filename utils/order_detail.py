import requests

from config_data.config import BING_MAPS_KEY

# адрес из координат
async def get_address_from_coordinates(latitude, longitude, BING_MAPS_KEY):
    url = f"http://dev.virtualearth.net/REST/v1/Locations/{latitude},{longitude}?o=json&key={BING_MAPS_KEY}&c=ru-RU"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        address_data = data['resourceSets'][0]['resources'][0]['address']
        
        address_parts = [
            address_data.get('addressLine'),
            address_data.get('locality'),
            address_data.get('adminDistrict'),
            address_data.get('countryRegion')
        ]
        address = ', '.join(part for part in address_parts if part)

        return address if address else None
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return None


# функция для вытаскивания адресов 
async def calculate_order_details(order):
    first_location = (order.first_latitude, order.first_longitude)
    second_location = (order.second_latitude, order.second_longitude)
    first_address = await get_address_from_coordinates(first_location[0], first_location[1], BING_MAPS_KEY)
    second_address = await get_address_from_coordinates(second_location[0], second_location[1], BING_MAPS_KEY)

    return first_address, second_address
