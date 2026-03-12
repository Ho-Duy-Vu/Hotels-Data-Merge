#!/bin/python3

import math
import os
import random
import re
import sys
import json
import requests
from dataclasses import dataclass, field, asdict
from typing import List, Dict

@dataclass
class Location:
    lat: float = None
    lng: float = None
    address: str = ""
    city: str = ""
    country: str = ""

@dataclass
class Amenities:
    general: List[str] = field(default_factory=list)
    room: List[str] = field(default_factory=list)

@dataclass
class Image:
    link: str
    description: str

@dataclass
class Images:
    rooms: List[Image] = field(default_factory=list)
    site: List[Image] = field(default_factory=list)
    amenities: List[Image] = field(default_factory=list)

@dataclass
class Hotel:
    id: str
    destination_id: int
    name: str = ""
    location: Location = field(default_factory=Location)
    description: str = ""
    amenities: Amenities = field(default_factory=Amenities)
    images: Images = field(default_factory=Images)
    booking_conditions: List[str] = field(default_factory=list)

class BaseSupplier:
    def endpoint(self) -> str:
        pass

    def parse(self, obj: dict) -> Hotel:
        pass

    def fetch(self) -> List[Hotel]:
        try:
            resp = requests.get(self.endpoint(), timeout=10)
            if resp.status_code == 200:
                return [self.parse(dto) for dto in resp.json()]
        except Exception:
            pass
        return []

class Acme(BaseSupplier):
    def endpoint(self):
        return 'https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/acme'

    def parse(self, dto: dict) -> Hotel:
        addr = str(dto.get('Address', '') or '').strip()
        postal = str(dto.get('PostalCode', '') or '').strip()
        full_address = f"{addr} {postal}".strip()
        
        return Hotel(
            id=dto.get('Id', ''),
            destination_id=dto.get('DestinationId'),
            name=dto.get('Name', ''),
            location=Location(
                lat=dto.get('Latitude'),
                lng=dto.get('Longitude'),
                address=full_address,
                city=dto.get('City', ''),
                country=dto.get('Country', '')
            ),
            description=dto.get('Description', ''),
            amenities=Amenities(
                general=dto.get('Facilities', []) or []
            )
        )

class Patagonia(BaseSupplier):
    def endpoint(self):
        return 'https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/patagonia'

    def parse(self, dto: dict) -> Hotel:
        images_raw = dto.get('images', {}) or {}
        return Hotel(
            id=dto.get('id', ''),
            destination_id=dto.get('destination'),
            name=dto.get('name', ''),
            location=Location(
                lat=dto.get('lat'),
                lng=dto.get('lng'),
                address=dto.get('address', '')
            ),
            description=dto.get('info', ''),
            amenities=Amenities(
                room=dto.get('amenities', []) or []
            ),
            images=Images(
                rooms=[Image(link=img.get('url', ''), description=img.get('description', '')) for img in (images_raw.get('rooms') or [])],
                amenities=[Image(link=img.get('url', ''), description=img.get('description', '')) for img in (images_raw.get('amenities') or [])]
            )
        )

class Paperflies(BaseSupplier):
    def endpoint(self):
        return 'https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/paperflies'

    def parse(self, dto: dict) -> Hotel:
        loc = dto.get('location', {}) or {}
        am = dto.get('amenities', {}) or {}
        imgs = dto.get('images', {}) or {}
        return Hotel(
            id=dto.get('hotel_id', ''),
            destination_id=dto.get('destination_id'),
            name=dto.get('hotel_name', ''),
            location=Location(
                address=loc.get('address', ''),
                country=loc.get('country', '')
            ),
            description=dto.get('details', ''),
            amenities=Amenities(
                general=am.get('general', []) or [],
                room=am.get('room', []) or []
            ),
            images=Images(
                rooms=[Image(link=img.get('link', ''), description=img.get('caption', '')) for img in (imgs.get('rooms') or [])],
                site=[Image(link=img.get('link', ''), description=img.get('caption', '')) for img in (imgs.get('site') or [])]
            ),
            booking_conditions=dto.get('booking_conditions', []) or []
        )

class HotelsService:
    def __init__(self):
        self.hotels: Dict[str, Hotel] = {}

    @staticmethod
    def _best_string(s1: str, s2: str) -> str:
        s1 = (s1 or "").strip()
        s2 = (s2 or "").strip()
        return s1 if len(s1) >= len(s2) else s2

    @staticmethod
    def _merge_arrays(arr1: List[str], arr2: List[str]) -> List[str]:
        combined = (arr1 or []) + (arr2 or [])
        unique_map = {}
        for item in combined:
            if isinstance(item, str):
                clean_item = item.strip()
                key = ''.join(e for e in clean_item.lower() if e.isalnum())
                if key and key not in unique_map:
                    unique_map[key] = clean_item
        return list(unique_map.values())

    @staticmethod
    def _merge_images(imgs1: List[Image], imgs2: List[Image]) -> List[Image]:
        combined = (imgs1 or []) + (imgs2 or [])
        unique_map = {}
        for img in combined:
            if img and img.link:
                if img.link not in unique_map:
                    unique_map[img.link] = img
                else:
                    existing = unique_map[img.link]
                    existing.description = HotelsService._best_string(existing.description, img.description)
        return list(unique_map.values())

    def merge_and_save(self, new_hotels: List[Hotel]):
        for incoming in new_hotels:
            if not incoming or not incoming.id:
                continue
            
            if incoming.id not in self.hotels:
                self.hotels[incoming.id] = incoming
            else:
                existing = self.hotels[incoming.id]
                existing.name = self._best_string(existing.name, incoming.name)
                existing.destination_id = existing.destination_id or incoming.destination_id
                existing.description = self._best_string(existing.description, incoming.description)
                
                existing.location.lat = existing.location.lat or incoming.location.lat
                existing.location.lng = existing.location.lng or incoming.location.lng
                existing.location.address = self._best_string(existing.location.address, incoming.location.address)
                existing.location.city = self._best_string(existing.location.city, incoming.location.city)
                existing.location.country = self._best_string(existing.location.country, incoming.location.country)
                
                existing.amenities.general = self._merge_arrays(existing.amenities.general, incoming.amenities.general)
                existing.amenities.room = self._merge_arrays(existing.amenities.room, incoming.amenities.room)
                
                existing.images.rooms = self._merge_images(existing.images.rooms, incoming.images.rooms)
                existing.images.site = self._merge_images(existing.images.site, incoming.images.site)
                existing.images.amenities = self._merge_images(existing.images.amenities, incoming.images.amenities)
                
                existing.booking_conditions = self._merge_arrays(existing.booking_conditions, incoming.booking_conditions)

    def find(self, hotel_ids: List[str], destination_ids: List[int]) -> List[dict]:
        results = []
        
        valid_h_ids = {str(h) for h in hotel_ids if str(h).lower() != 'none'} if hotel_ids else set()
        valid_d_ids = {int(d) for d in destination_ids if str(d).lower() != 'none'} if destination_ids else set()
        
        for h in self.hotels.values():
            match_h = (not valid_h_ids) or (str(h.id) in valid_h_ids)
            match_d = (not valid_d_ids) or (int(h.destination_id) in valid_d_ids)
            
            if match_h and match_d:
                # Lọc bỏ các giá trị None thừa nếu cần, hoặc để asdict tự xử lý
                hotel_dict = asdict(h)
                results.append(hotel_dict)
                
        return results

def fetchHotels(hotel_ids, destination_ids):
    suppliers = [
        Acme(),
        Paperflies(),
        Patagonia(),
    ]
    
    all_supplier_data = []
    for supp in suppliers:
        all_supplier_data.extend(supp.fetch())
        
    svc = HotelsService()
    svc.merge_and_save(all_supplier_data)
    
    filtered = svc.find(hotel_ids, destination_ids)
    
    # Trả về JSON format (indent=2 để dễ đọc và pass format checker của HackerRank nếu có)
    return json.dumps(filtered, indent=2)

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    hotel_ids_count = int(input().strip())

    hotel_ids = []

    for _ in range(hotel_ids_count):
        hotel_ids_item = input()
        hotel_ids.append(hotel_ids_item)

    destination_ids_count = int(input().strip())

    destination_ids = []

    for _ in range(destination_ids_count):
        destination_ids_item = int(input().strip())
        destination_ids.append(destination_ids_item)

    result = fetchHotels(hotel_ids, destination_ids)

    fptr.write(result + '\n')

    fptr.close()