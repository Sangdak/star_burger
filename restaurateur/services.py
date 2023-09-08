from django.utils.timezone import now
from geopy import distance
import requests

from location.models import Location


def fetch_coordinates(apikey, address):
    try:
        location = Location.objects.get(address=address)
        return location.longitude, location.latitude
    except Location.DoesNotExist:
        base_url = "https://geocode-maps.yandex.ru/1.x"
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        })
        response.raise_for_status()

        try:
            found_places = response.json()['response']['GeoObjectCollection']['featureMember']
        except (AttributeError, KeyError):
            return None

        most_relevant = found_places[0]
        longitude, latitude = most_relevant['GeoObject']['Point']['pos'].split(" ")

        Location.objects.create(
            updated_at=now(),
            address=address,
            longitude=longitude,
            latitude=latitude,
        )

        return latitude, longitude


def compute_distance(start_coords, end_coords):
    return distance.distance(start_coords, end_coords).km
