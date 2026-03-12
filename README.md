# Phân Tích Chi Tiết Code Main.py - Hotels Data Merge

## 📋 Mục Lục
1. [Tổng Quan Dự Án](#tổng-quan-dự-án)
2. [Cấu Trúc Tổng Thể](#cấu-trúc-tổng-thể)
3. [Các Khái Niệm OOP Được Sử Dụng](#các-khái-niệm-oop-được-sử-dụng)
4. [Phân Tích Chi Tiết Từng Thành Phần](#phân-tích-chi-tiết-từng-thành-phần)
5. [Luồng Xử Lý Logic](#luồng-xử-lý-logic)
6. [Design Patterns](#design-patterns)
7. [Tổng Kết](#tổng-kết)

---

## 🎯 Tổng Quan Dự Án

### Mục đích
Xây dựng một hệ thống để:
- **Lấy dữ liệu** khách sạn từ nhiều nhà cung cấp (suppliers) khác nhau
- **Phân tích** và làm sạch dữ liệu thô
- **Gộp (merge)** dữ liệu từ nhiều nguồn thành một tập dữ liệu hoàn chỉnh
- **Lọc** và trả về kết quả theo yêu cầu

### Bài toán thực tế
Giống như các trang web đặt phòng (Booking.com, Agoda), dữ liệu khách sạn đến từ nhiều nguồn khác nhau với format và chất lượng khác nhau. Cần hợp nhất để có dữ liệu tốt nhất.

---

## 🏗️ Cấu Trúc Tổng Thể

### 1. Import Modules
```python
import math, os, random, re, sys, json, requests
from dataclasses import dataclass, field, asdict
from typing import List, Dict
```

**Giải thích:**
- `requests`: Gọi API để lấy dữ liệu từ suppliers
- `dataclasses`: Tạo các class dữ liệu một cách ngắn gọn
- `typing`: Type hints để code rõ ràng hơn
- `json`: Xử lý dữ liệu JSON

### 2. Kiến Trúc Phân Tầng

```
┌─────────────────────────────────────────┐
│   Entry Point (main / fetchHotels)      │
├─────────────────────────────────────────┤
│   HotelsService (Business Logic)        │
├─────────────────────────────────────────┤
│   Suppliers (Acme, Patagonia, etc.)     │
├─────────────────────────────────────────┤
│   BaseSupplier (Abstract Layer)         │
├─────────────────────────────────────────┤
│   Data Models (Hotel, Location, etc.)   │
└─────────────────────────────────────────┘
```

---

## 🎓 Các Khái Niệm OOP Được Sử Dụng

### 1. **Dataclass** (Python 3.7+)

#### Khái niệm
Dataclass là một decorator giúp tạo class chứa dữ liệu một cách ngắn gọn, tự động sinh ra các method như `__init__`, `__repr__`, `__eq__`.

#### Ví dụ trong code:
```python
@dataclass
class Location:
    lat: float = None
    lng: float = None
    address: str = ""
    city: str = ""
    country: str = ""
```

**Tương đương với:**
```python
class Location:
    def __init__(self, lat=None, lng=None, address="", city="", country=""):
        self.lat = lat
        self.lng = lng
        self.address = address
        self.city = city
        self.country = country
```

#### Lợi ích:
- ✅ Code ngắn gọn, dễ đọc
- ✅ Tự động có `__init__`, `__repr__`
- ✅ Type hints rõ ràng
- ✅ Dễ convert sang dict với `asdict()`

### 2. **Inheritance (Kế thừa)**

#### Khái niệm
Class con kế thừa thuộc tính và phương thức từ class cha.

#### Ví dụ:
```python
class BaseSupplier:  # Class cha (Abstract/Base class)
    def endpoint(self) -> str:
        pass  # Method placeholder
    
    def parse(self, obj: dict) -> Hotel:
        pass  # Method placeholder
    
    def fetch(self) -> List[Hotel]:
        # Logic chung cho tất cả suppliers
        ...

class Acme(BaseSupplier):  # Class con kế thừa BaseSupplier
    def endpoint(self):
        return 'https://...acme'  # Override method cha
    
    def parse(self, dto: dict) -> Hotel:
        # Logic riêng cho Acme
        ...
```

#### Lợi ích:
- ✅ Tránh lặp code (DRY - Don't Repeat Yourself)
- ✅ `fetch()` được viết 1 lần, tất cả suppliers dùng chung
- ✅ Mỗi supplier chỉ cần implement `endpoint()` và `parse()`

### 3. **Encapsulation (Đóng gói)**

#### Khái niệm
Gom dữ liệu và hành vi liên quan vào một class.

#### Ví dụ:
```python
class HotelsService:
    def __init__(self):
        self.hotels: Dict[str, Hotel] = {}  # Dữ liệu private
    
    # Methods để thao tác với dữ liệu
    def merge_and_save(self, new_hotels):
        ...
    
    def find(self, hotel_ids, destination_ids):
        ...
```

#### Lợi ích:
- ✅ Dữ liệu được bảo vệ trong class
- ✅ Logic liên quan được gom lại
- ✅ Dễ bảo trì và mở rộng

### 4. **Polymorphism (Đa hình)**

#### Khái niệm
Các class khác nhau có thể có method cùng tên nhưng hành vi khác nhau.

#### Ví dụ:
```python
suppliers = [Acme(), Patagonia(), Paperflies()]

for supp in suppliers:
    supp.fetch()  # Gọi cùng method nhưng mỗi supplier xử lý khác nhau
```

#### Lợi ích:
- ✅ Code linh hoạt, dễ mở rộng
- ✅ Thêm supplier mới không cần sửa code cũ

---

## 📦 Phân Tích Chi Tiết Từng Thành Phần

### PHẦN 1: Data Models (Mô hình dữ liệu)

#### 1.1. Class `Location`
```python
@dataclass
class Location:
    lat: float = None      # Latitude (vĩ độ)
    lng: float = None      # Longitude (kinh độ)
    address: str = ""      # Địa chỉ
    city: str = ""         # Thành phố
    country: str = ""      # Quốc gia
```

**Mục đích:** Lưu trữ thông tin vị trí của khách sạn

**Default values:** 
- `None` cho số (có thể không có tọa độ)
- `""` cho string (tránh None khi xử lý text)

---

#### 1.2. Class `Amenities`
```python
@dataclass
class Amenities:
    general: List[str] = field(default_factory=list)
    room: List[str] = field(default_factory=list)
```

**Mục đích:** Lưu tiện nghi của khách sạn

**Tại sao dùng `field(default_factory=list)`?**
```python
# ❌ SAI - Tất cả instances dùng chung 1 list
class Amenities:
    general: List[str] = []

# ✅ ĐÚNG - Mỗi instance có list riêng
class Amenities:
    general: List[str] = field(default_factory=list)
```

**Giải thích:**
- `default_factory=list` tạo list mới cho mỗi object
- Tránh bug khi nhiều object cùng trỏ đến 1 list

---

#### 1.3. Class `Image`
```python
@dataclass
class Image:
    link: str           # URL của hình ảnh
    description: str    # Mô tả hình ảnh
```

**Mục đích:** Đại diện cho 1 hình ảnh

**Không có default:** Vì mỗi ảnh BẮT BUỘC phải có link và description

---

#### 1.4. Class `Images`
```python
@dataclass
class Images:
    rooms: List[Image] = field(default_factory=list)      # Ảnh phòng
    site: List[Image] = field(default_factory=list)       # Ảnh khách sạn
    amenities: List[Image] = field(default_factory=list)  # Ảnh tiện nghi
```

**Mục đích:** Quản lý tất cả hình ảnh của khách sạn

**Cấu trúc:** Phân loại ảnh theo mục đích sử dụng

---

#### 1.5. Class `Hotel` (Core Model)
```python
@dataclass
class Hotel:
    id: str                                              # ID khách sạn (required)
    destination_id: int                                  # ID điểm đến (required)
    name: str = ""                                       # Tên khách sạn
    location: Location = field(default_factory=Location)
    description: str = ""                                # Mô tả
    amenities: Amenities = field(default_factory=Amenities)
    images: Images = field(default_factory=Images)
    booking_conditions: List[str] = field(default_factory=list)
```

**Mục đích:** Model chính đại diện cho 1 khách sạn

**Kiến trúc:**
- Composite pattern: Hotel chứa các object khác (Location, Amenities, Images)
- Hierarchical structure: Dữ liệu có tổ chức, dễ quản lý

---

### PHẦN 2: Base Supplier Class

```python
class BaseSupplier:
    def endpoint(self) -> str:
        pass  # Method trừu tượng - class con phải implement
    
    def parse(self, obj: dict) -> Hotel:
        pass  # Method trừu tượng - class con phải implement
    
    def fetch(self) -> List[Hotel]:
        try:
            resp = requests.get(self.endpoint(), timeout=10)
            if resp.status_code == 200:
                return [self.parse(dto) for dto in resp.json()]
        except Exception:
            pass
        return []
```

#### Phân tích từng method:

##### `endpoint()` - Abstract Method
```python
def endpoint(self) -> str:
    pass
```
- **Mục đích:** Trả về URL của supplier
- **Tại sao là `pass`?** Đây là abstract method, mỗi supplier có URL riêng
- **Return type:** `str` (URL)

##### `parse()` - Abstract Method
```python
def parse(self, obj: dict) -> Hotel:
    pass
```
- **Mục đích:** Chuyển đổi dữ liệu thô (dict) thành object Hotel
- **Input:** `obj: dict` - dữ liệu JSON từ API
- **Output:** `Hotel` object
- **Tại sao mỗi supplier khác nhau?** Vì format JSON của mỗi supplier khác nhau

##### `fetch()` - Concrete Method (Có implementation)
```python
def fetch(self) -> List[Hotel]:
    try:
        resp = requests.get(self.endpoint(), timeout=10)
        if resp.status_code == 200:
            return [self.parse(dto) for dto in resp.json()]
    except Exception:
        pass
    return []
```

**Phân tích từng dòng:**

```python
resp = requests.get(self.endpoint(), timeout=10)
```
- Gọi API với URL từ `endpoint()`
- `timeout=10`: Chờ tối đa 10 giây (tránh treo)
- `self.endpoint()`: Gọi method của class con (polymorphism)

```python
if resp.status_code == 200:
```
- Kiểm tra request thành công (200 = OK)
- HTTP status codes: 200 (OK), 404 (Not Found), 500 (Server Error)

```python
return [self.parse(dto) for dto in resp.json()]
```
- **List comprehension:** Vòng lặp ngắn gọn
- `resp.json()`: Parse response thành list of dicts
- `self.parse(dto)`: Convert mỗi dict thành Hotel object
- Kết quả: `List[Hotel]`

**Tương đương với:**
```python
hotels = []
for dto in resp.json():
    hotel = self.parse(dto)
    hotels.append(hotel)
return hotels
```

```python
except Exception:
    pass
return []
```
- Bắt mọi lỗi (network, timeout, JSON parse error)
- Trả về list rỗng nếu có lỗi (fail gracefully)

---

### PHẦN 3: Concrete Suppliers

#### 3.1. Class `Acme`

```python
class Acme(BaseSupplier):
    def endpoint(self):
        return 'https://5f2be0b4ffc88500167b85a0.mockapi.io/suppliers/acme'
```
- Override `endpoint()` với URL của Acme

```python
def parse(self, dto: dict) -> Hotel:
    addr = str(dto.get('Address', '') or '').strip()
    postal = str(dto.get('PostalCode', '') or '').strip()
    full_address = f"{addr} {postal}".strip()
```

**Phân tích logic:**

```python
dto.get('Address', '')
```
- `get(key, default)`: Lấy value của key, nếu không có trả về default
- Tránh KeyError khi key không tồn tại

```python
str(dto.get('Address', '') or '').strip()
```
**Tại sao phức tạp thế?**

1. `dto.get('Address', '')` → Có thể trả về: `"  abc  "`, `""`, hoặc `None`
2. `or ''` → Nếu kết quả là `None`, thay bằng `''`
3. `str(...)` → Chuyển về string (đề phòng số hoặc kiểu khác)
4. `.strip()` → Xóa khoảng trắng đầu/cuối

**Ví dụ:**
```python
# Input: {'Address': '  123 Main St  ', 'PostalCode': None}
addr = str(dto.get('Address', '') or '').strip()  # "123 Main St"
postal = str(dto.get('PostalCode', '') or '').strip()  # ""
full_address = f"{addr} {postal}".strip()  # "123 Main St"
```

```python
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
```

**Mapping data:**
- Acme gọi là `Facilities` → Ta map vào `amenities.general`
- Acme có `Latitude`, `Longitude` → Ta lưu vào `location.lat`, `location.lng`
- Acme KHÔNG có ảnh → `images` sẽ dùng default (rỗng)

---

#### 3.2. Class `Patagonia`

```python
def parse(self, dto: dict) -> Hotel:
    images_raw = dto.get('images', {}) or {}
```
- Lấy images, nếu None thì thay bằng `{}`
- Tránh lỗi khi gọi `.get()` trên None

```python
images=Images(
    rooms=[Image(link=img.get('url', ''), description=img.get('description', '')) 
           for img in (images_raw.get('rooms') or [])],
    amenities=[Image(link=img.get('url', ''), description=img.get('description', '')) 
               for img in (images_raw.get('amenities') or [])]
)
```

**Nested list comprehension:**

**Phân tích từng phần:**
```python
images_raw.get('rooms') or []
```
- Lấy list rooms, nếu None hoặc không có → dùng `[]`

```python
for img in (images_raw.get('rooms') or [])
```
- Lặp qua từng image trong list

```python
Image(link=img.get('url', ''), description=img.get('description', ''))
```
- Tạo Image object từ mỗi item

**Tương đương:**
```python
rooms_images = []
rooms_list = images_raw.get('rooms') or []
for img in rooms_list:
    link = img.get('url', '')
    desc = img.get('description', '')
    rooms_images.append(Image(link=link, description=desc))
```

---

#### 3.3. Class `Paperflies`

```python
def parse(self, dto: dict) -> Hotel:
    loc = dto.get('location', {}) or {}
    am = dto.get('amenities', {}) or {}
    imgs = dto.get('images', {}) or {}
```
- Lấy nested objects trước để code gọn hơn

```python
amenities=Amenities(
    general=am.get('general', []) or [],
    room=am.get('room', []) or []
)
```
- Paperflies có CẢ `general` VÀ `room` amenities
- Khác với Acme (chỉ có general) và Patagonia (chỉ có room)

---

### PHẦN 4: HotelsService - Business Logic Core

```python
class HotelsService:
    def __init__(self):
        self.hotels: Dict[str, Hotel] = {}
```
- **Storage:** Dictionary với key = hotel ID, value = Hotel object
- **Tại sao dùng Dict không phải List?**
  - ✅ Tra cứu nhanh O(1) thay vì O(n)
  - ✅ Tự động loại trùng lặp
  - ✅ Dễ merge data

---

#### 4.1. Static Method `_best_string()`

```python
@staticmethod
def _best_string(s1: str, s2: str) -> str:
    s1 = (s1 or "").strip()
    s2 = (s2 or "").strip()
    return s1 if len(s1) >= len(s2) else s2
```

**Mục đích:** Chọn string dài hơn (giả định là chi tiết hơn)

**Logic:**
1. Chuẩn hóa: None → "", xóa khoảng trắng
2. So sánh độ dài
3. Trả về cái dài hơn

**Ví dụ:**
```python
_best_string("Hilton", "Hilton Hotel Singapore") 
# → "Hilton Hotel Singapore"

_best_string("Nice hotel", "Nice")
# → "Nice hotel"
```

**Tại sao `@staticmethod`?**
- Không cần truy cập `self` (instance data)
- Có thể gọi mà không cần tạo object: `HotelsService._best_string()`
- Nhóm logic liên quan vào class

---

#### 4.2. Static Method `_merge_arrays()`

```python
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
```

**Mục đích:** Merge 2 arrays, loại trùng lặp THÔNG MINH

**Phân tích từng bước:**

##### Bước 1: Gộp arrays
```python
combined = (arr1 or []) + (arr2 or [])
```
- Nối 2 list (handle None)

##### Bước 2: Tạo unique map
```python
unique_map = {}
```
- Dict để loại trùng

##### Bước 3: Xử lý từng item
```python
for item in combined:
    if isinstance(item, str):  # Đảm bảo là string
        clean_item = item.strip()  # Xóa khoảng trắng
```

##### Bước 4: Tạo normalized key
```python
key = ''.join(e for e in clean_item.lower() if e.isalnum())
```

**Phân tích chi tiết:**
```python
clean_item.lower()  # "WiFi" → "wifi"
```
- Chuyển về lowercase để so sánh không phân biệt hoa/thường

```python
for e in clean_item.lower()  # Lặp từng ký tự
```

```python
if e.isalnum()  # Chỉ giữ chữ cái và số
```
- `isalnum()`: True nếu là chữ cái hoặc số
- Loại bỏ: khoảng trắng, dấu câu, ký tự đặc biệt

```python
''.join(...)  # Nối các ký tự lại
```

**Ví dụ:**
```python
"Wi-Fi"     → key: "wifi"
"WiFi"      → key: "wifi"
"wi fi"     → key: "wifi"
"Pool"      → key: "pool"
"Pool "     → key: "pool"
```

##### Bước 5: Lưu vào map (loại trùng)
```python
if key and key not in unique_map:
    unique_map[key] = clean_item
```
- Chỉ lưu lần đầu gặp
- Giữ nguyên format gốc (Wi-Fi, không phải wifi)

**Ví dụ hoàn chỉnh:**
```python
arr1 = ["WiFi", "Pool", "Gym"]
arr2 = ["Wi-Fi", "pool", "Parking"]

_merge_arrays(arr1, arr2)
# unique_map = {
#     "wifi": "WiFi",      # Giữ "WiFi" (gặp đầu tiên)
#     "pool": "Pool",      # Giữ "Pool" (gặp đầu tiên)
#     "gym": "Gym",
#     "parking": "Parking"
# }
# Kết quả: ["WiFi", "Pool", "Gym", "Parking"]
```

---

#### 4.3. Static Method `_merge_images()`

```python
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
                existing.description = HotelsService._best_string(
                    existing.description, img.description
                )
    return list(unique_map.values())
```

**Mục đích:** Merge images, loại trùng theo link, giữ description tốt nhất

**Logic:**

##### Bước 1: Gộp lists
```python
combined = (imgs1 or []) + (imgs2 or [])
```

##### Bước 2: Lặp qua từng ảnh
```python
for img in combined:
    if img and img.link:  # Đảm bảo img không None và có link
```

##### Bước 3: Check trùng lặp
```python
if img.link not in unique_map:
    unique_map[img.link] = img  # Lần đầu gặp → lưu
```

##### Bước 4: Nếu trùng → merge description
```python
else:
    existing = unique_map[img.link]
    existing.description = HotelsService._best_string(
        existing.description, img.description
    )
```

**Ví dụ:**
```python
imgs1 = [
    Image(link="a.jpg", description="Room"),
    Image(link="b.jpg", description="Nice view")
]
imgs2 = [
    Image(link="a.jpg", description="Deluxe Room with balcony"),
    Image(link="c.jpg", description="Pool")
]

_merge_images(imgs1, imgs2)
# Kết quả:
# [
#   Image(link="a.jpg", description="Deluxe Room with balcony"),  # Chọn description dài hơn
#   Image(link="b.jpg", description="Nice view"),
#   Image(link="c.jpg", description="Pool")
# ]
```

---

#### 4.4. Method `merge_and_save()`

```python
def merge_and_save(self, new_hotels: List[Hotel]):
    for incoming in new_hotels:
        if not incoming or not incoming.id:
            continue
        
        if incoming.id not in self.hotels:
            self.hotels[incoming.id] = incoming
        else:
            existing = self.hotels[incoming.id]
            # ... merge logic
```

**Mục đích:** Thêm hotels mới hoặc merge với data hiện có

**Phân tích từng phần:**

##### Kiểm tra hợp lệ
```python
if not incoming or not incoming.id:
    continue
```
- Bỏ qua hotel None hoặc không có ID
- Defensive programming: Tránh lỗi runtime

##### Trường hợp 1: Hotel mới
```python
if incoming.id not in self.hotels:
    self.hotels[incoming.id] = incoming
```
- Thêm thẳng vào storage

##### Trường hợp 2: Hotel đã tồn tại → MERGE
```python
else:
    existing = self.hotels[incoming.id]
```

###### Merge các trường string
```python
existing.name = self._best_string(existing.name, incoming.name)
existing.description = self._best_string(existing.description, incoming.description)
```
- Chọn string dài hơn

###### Merge các trường số
```python
existing.destination_id = existing.destination_id or incoming.destination_id
```
- Nếu existing None → dùng incoming
- Nếu existing có giá trị → giữ nguyên
- Logic: "Giữ giá trị đầu tiên không None"

###### Merge Location
```python
existing.location.lat = existing.location.lat or incoming.location.lat
existing.location.lng = existing.location.lng or incoming.location.lng
existing.location.address = self._best_string(existing.location.address, incoming.location.address)
existing.location.city = self._best_string(existing.location.city, incoming.location.city)
existing.location.country = self._best_string(existing.location.country, incoming.location.country)
```
- Merge từng field của Location object

###### Merge Amenities
```python
existing.amenities.general = self._merge_arrays(
    existing.amenities.general, incoming.amenities.general
)
existing.amenities.room = self._merge_arrays(
    existing.amenities.room, incoming.amenities.room
)
```
- Dùng `_merge_arrays()` để gộp list và loại trùng thông minh

###### Merge Images
```python
existing.images.rooms = self._merge_images(
    existing.images.rooms, incoming.images.rooms
)
existing.images.site = self._merge_images(
    existing.images.site, incoming.images.site
)
existing.images.amenities = self._merge_images(
    existing.images.amenities, incoming.images.amenities
)
```
- Dùng `_merge_images()` để gộp ảnh, giữ description tốt nhất

###### Merge Booking Conditions
```python
existing.booking_conditions = self._merge_arrays(
    existing.booking_conditions, incoming.booking_conditions
)
```

**Ví dụ merge hoàn chỉnh:**

```python
# Existing hotel (từ Acme)
{
    "id": "iJhz",
    "name": "Beach Villas",
    "location": {"lat": 1.264751, "lng": 103.824006},
    "amenities": {"general": ["Pool", "WiFi"]},
    "images": {"rooms": []}
}

# Incoming hotel (từ Patagonia)
{
    "id": "iJhz",
    "name": "Beach Villas Singapore",
    "location": {"address": "8 Sentosa Gateway"},
    "amenities": {"room": ["TV", "Aircon"]},
    "images": {"rooms": [Image(link="a.jpg", description="Room")]}
}

# Sau khi merge:
{
    "id": "iJhz",
    "name": "Beach Villas Singapore",  # Dài hơn
    "location": {
        "lat": 1.264751,               # Từ existing
        "lng": 103.824006,             # Từ existing
        "address": "8 Sentosa Gateway" # Từ incoming
    },
    "amenities": {
        "general": ["Pool", "WiFi"],    # Từ existing
        "room": ["TV", "Aircon"]        # Từ incoming
    },
    "images": {
        "rooms": [Image(link="a.jpg", description="Room")]  # Từ incoming
    }
}
```

---

#### 4.5. Method `find()`

```python
def find(self, hotel_ids: List[str], destination_ids: List[int]) -> List[dict]:
    results = []
    
    valid_h_ids = {str(h) for h in hotel_ids if str(h).lower() != 'none'} if hotel_ids else set()
    valid_d_ids = {int(d) for d in destination_ids if str(d).lower() != 'none'} if destination_ids else set()
    
    for h in self.hotels.values():
        match_h = (not valid_h_ids) or (str(h.id) in valid_h_ids)
        match_d = (not valid_d_ids) or (int(h.destination_id) in valid_d_ids)
        
        if match_h and match_d:
            hotel_dict = asdict(h)
            results.append(hotel_dict)
            
    return results
```

**Mục đích:** Lọc hotels theo hotel_ids và destination_ids

**Phân tích từng bước:**

##### Bước 1: Tạo filter sets
```python
valid_h_ids = {str(h) for h in hotel_ids if str(h).lower() != 'none'} if hotel_ids else set()
```

**Giải thích:**
- **Set comprehension:** Tạo set (loại trùng tự động)
- `str(h)`: Convert về string (đồng nhất kiểu)
- `if str(h).lower() != 'none'`: Loại bỏ "none", "None", "NONE"
- `if hotel_ids else set()`: Nếu hotel_ids là None/empty → dùng set rỗng

**Ví dụ:**
```python
hotel_ids = ["iJhz", "SjyX", "none", "iJhz"]
valid_h_ids = {"iJhz", "SjyX"}  # Loại "none" và trùng lặp
```

##### Bước 2: Lặp qua tất cả hotels
```python
for h in self.hotels.values():
```
- `.values()`: Lấy Hotel objects (không cần key)

##### Bước 3: Kiểm tra điều kiện lọc
```python
match_h = (not valid_h_ids) or (str(h.id) in valid_h_ids)
```

**Logic table:**

| valid_h_ids | h.id in valid_h_ids | match_h | Ý nghĩa |
|-------------|---------------------|---------|---------|
| {} (rỗng)   | -                   | True    | Không filter → Match tất cả |
| {"iJhz"}    | True                | True    | ID khớp → Match |
| {"iJhz"}    | False               | False   | ID không khớp → Không match |

**Tương tự với destination:**
```python
match_d = (not valid_d_ids) or (int(h.destination_id) in valid_d_ids)
```

##### Bước 4: Thêm vào results nếu khớp CẢ HAI điều kiện
```python
if match_h and match_d:
    hotel_dict = asdict(h)
    results.append(hotel_dict)
```

- `asdict(h)`: Convert dataclass → dictionary
- Vì API cần trả về JSON, không phải object

**Ví dụ:**

```python
# Storage:
hotels = {
    "iJhz": Hotel(id="iJhz", destination_id=5432, ...),
    "SjyX": Hotel(id="SjyX", destination_id=5432, ...),
    "f8c9": Hotel(id="f8c9", destination_id=1122, ...),
}

# Query 1: Tất cả hotels
find([], []) → [iJhz, SjyX, f8c9]

# Query 2: Hotels có ID = iJhz hoặc SjyX
find(["iJhz", "SjyX"], []) → [iJhz, SjyX]

# Query 3: Hotels ở destination 5432
find([], [5432]) → [iJhz, SjyX]

# Query 4: Hotel iJhz ở destination 5432
find(["iJhz"], [5432]) → [iJhz]

# Query 5: Hotel iJhz ở destination 1122 (không khớp)
find(["iJhz"], [1122]) → []
```

---

### PHẦN 5: Main Function

```python
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
    
    return json.dumps(filtered, indent=2)
```

**Luồng xử lý:**

#### Bước 1: Tạo suppliers
```python
suppliers = [Acme(), Paperflies(), Patagonia()]
```
- Tạo instances của các supplier classes
- Dễ thêm supplier mới: `suppliers.append(NewSupplier())`

#### Bước 2: Fetch data từ tất cả suppliers
```python
all_supplier_data = []
for supp in suppliers:
    all_supplier_data.extend(supp.fetch())
```

- `supp.fetch()`: Trả về `List[Hotel]`
- `.extend()`: Thêm tất cả items vào list (không phải nested list)

**extend vs append:**
```python
# extend
list1 = [1, 2]
list1.extend([3, 4])  # [1, 2, 3, 4]

# append
list2 = [1, 2]
list2.append([3, 4])  # [1, 2, [3, 4]]
```

#### Bước 3: Merge data
```python
svc = HotelsService()
svc.merge_and_save(all_supplier_data)
```
- Tạo service instance
- Merge tất cả hotels vào storage

#### Bước 4: Filter
```python
filtered = svc.find(hotel_ids, destination_ids)
```
- Lọc theo yêu cầu
- Trả về `List[dict]`

#### Bước 5: Convert to JSON
```python
return json.dumps(filtered, indent=2)
```
- `json.dumps()`: Dict → JSON string
- `indent=2`: Format đẹp (dễ đọc)

**Output ví dụ:**
```json
[
  {
    "id": "iJhz",
    "destination_id": 5432,
    "name": "Beach Villas Singapore",
    "location": {
      "lat": 1.264751,
      "lng": 103.824006,
      "address": "8 Sentosa Gateway",
      "city": "Singapore",
      "country": "SG"
    },
    ...
  }
]
```

---

### PHẦN 6: Entry Point

```python
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
```

**Giải thích:**

```python
if __name__ == '__main__':
```
- Chỉ chạy khi file được execute trực tiếp
- Không chạy khi được import

```python
fptr = open(os.environ['OUTPUT_PATH'], 'w')
```
- HackerRank format: Output ghi ra file
- `OUTPUT_PATH`: Biến môi trường

```python
hotel_ids_count = int(input().strip())
```
- Đọc số lượng hotel IDs
- `.strip()`: Xóa whitespace

```python
for _ in range(hotel_ids_count):
    hotel_ids_item = input()
    hotel_ids.append(hotel_ids_item)
```
- `_`: Variable không dùng (convention)
- Đọc từng ID từ input

**Input format ví dụ:**
```
2          ← hotel_ids_count
iJhz       ← hotel_ids[0]
SjyX       ← hotel_ids[1]
1          ← destination_ids_count
5432       ← destination_ids[0]
```

---

## 🔄 Luồng Xử Lý Logic Tổng Thể

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    START: fetchHotels()                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Tạo danh sách suppliers: [Acme, Paperflies, Patagonia]    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────┴───────────────┐
         │   For each supplier:          │
         │   1. Call endpoint()          │
         │   2. GET request to API       │
         │   3. Parse JSON response      │
         │   4. Call parse() for each    │
         │   5. Return List[Hotel]       │
         └───────────────┬───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│        Gộp tất cả data: all_supplier_data                   │
│        (Có thể có hotel trùng từ nhiều nguồn)               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           Tạo HotelsService instance                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────┴────────────────┐
         │  merge_and_save():             │
         │  For each hotel:               │
         │    - Nếu mới → Thêm vào        │
         │    - Nếu trùng → Merge data    │
         │      • Best string             │
         │      • Merge arrays            │
         │      • Merge images            │
         └───────────────┬────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│             hotels storage (Dict[str, Hotel])               │
│             Mỗi ID chỉ có 1 Hotel với data đầy đủ nhất      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────┴────────────────┐
         │  find():                       │
         │  Filter by hotel_ids AND       │
         │             destination_ids    │
         │  Convert to List[dict]         │
         └───────────────┬────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           json.dumps() → JSON string                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    RETURN result                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Design Patterns Được Sử Dụng

### 1. **Template Method Pattern**

#### Định nghĩa
Base class định nghĩa skeleton của algorithm, subclass override các bước cụ thể.

#### Trong code:
```python
class BaseSupplier:
    def fetch(self):  # Template method (không đổi)
        resp = requests.get(self.endpoint())  # Bước 1: Gọi API
        return [self.parse(dto) for dto in resp.json()]  # Bước 2: Parse
    
    def endpoint(self):  # Hook method (override)
        pass
    
    def parse(self, dto):  # Hook method (override)
        pass

class Acme(BaseSupplier):
    def endpoint(self):  # Override
        return 'https://...acme'
    
    def parse(self, dto):  # Override
        return Hotel(...)
```

#### Lợi ích:
- ✅ Tránh duplicate code
- ✅ Dễ thêm supplier mới
- ✅ Logic fetch giống nhau, chỉ endpoint và parse khác

---

### 2. **Strategy Pattern**

#### Định nghĩa
Định nghĩa family of algorithms, encapsulate từng cái, làm chúng interchangeable.

#### Trong code:
```python
# Mỗi supplier là một strategy để parse data
suppliers = [Acme(), Patagonia(), Paperflies()]

for supp in suppliers:
    supp.fetch()  # Cùng interface, khác implementation
```

#### Lợi ích:
- ✅ Dễ thêm/bớt suppliers
- ✅ Không cần sửa code hiện tại

---

### 3. **Repository Pattern**

#### Định nghĩa
Tách logic truy cập dữ liệu khỏi business logic.

#### Trong code:
```python
class HotelsService:
    def __init__(self):
        self.hotels = {}  # Data storage
    
    def merge_and_save(self, hotels):  # Save
        ...
    
    def find(self, ids):  # Query
        ...
```

#### Lợi ích:
- ✅ Business logic không quan tâm storage là gì (Dict, DB, File)
- ✅ Dễ test và maintain

---

### 4. **Data Transfer Object (DTO)**

#### Định nghĩa
Object chỉ chứa data, không có behavior.

#### Trong code:
```python
@dataclass
class Hotel:
    id: str
    name: str
    # ... chỉ có attributes, không có methods
```

#### Lợi ích:
- ✅ Rõ ràng, dễ hiểu
- ✅ Dễ serialize/deserialize
- ✅ Type-safe với type hints

---

## 📊 Bảng So Sánh Suppliers

| Aspect | Acme | Patagonia | Paperflies |
|--------|------|-----------|------------|
| **ID field** | `Id` | `id` | `hotel_id` |
| **Destination** | `DestinationId` | `destination` | `destination_id` |
| **Name** | `Name` | `name` | `hotel_name` |
| **Description** | `Description` | `info` | `details` |
| **Coordinates** | `Latitude`, `Longitude` | `lat`, `lng` | ❌ Không có |
| **Address** | `Address` + `PostalCode` | `address` | `location.address` |
| **City** | `City` | ❌ Không có | ❌ Không có |
| **Country** | `Country` | ❌ Không có | `location.country` |
| **General Amenities** | `Facilities` | ❌ Không có | `amenities.general` |
| **Room Amenities** | ❌ Không có | `amenities` | `amenities.room` |
| **Room Images** | ❌ Không có | `images.rooms` | `images.rooms` |
| **Site Images** | ❌ Không có | ❌ Không có | `images.site` |
| **Amenities Images** | ❌ Không có | `images.amenities` | ❌ Không có |
| **Booking Conditions** | ❌ Không có | ❌ Không có | `booking_conditions` |

**Nhận xét:**
- Không supplier nào có đầy đủ data
- Cần merge để có dataset hoàn chỉnh
- Mỗi supplier có điểm mạnh riêng

---

## 💡 Kỹ Thuật Lập Trình Đáng Chú Ý

### 1. Defensive Programming
```python
# Luôn check None
s1 = (s1 or "").strip()

# Safe dict access
dto.get('key', default)

# Validate before process
if not incoming or not incoming.id:
    continue
```

### 2. List Comprehension
```python
# Thay vì:
result = []
for item in items:
    if condition:
        result.append(transform(item))

# Dùng:
result = [transform(item) for item in items if condition]
```

### 3. Set Comprehension
```python
# Loại trùng và filter trong 1 dòng
valid_ids = {str(h) for h in hotel_ids if str(h).lower() != 'none'}
```

### 4. Dictionary for Deduplication
```python
# Thay vì check trùng với list (O(n))
unique_map = {}
for item in items:
    if item not in unique_map:  # O(1)
        unique_map[item] = item
```

### 5. Type Hints
```python
def parse(self, dto: dict) -> Hotel:
    ...

def find(self, hotel_ids: List[str]) -> List[dict]:
    ...
```
- Giúp IDE autocomplete
- Giúp catch bug sớm
- Documentation tự động

### 6. Dataclass với Field
```python
@dataclass
class Images:
    rooms: List[Image] = field(default_factory=list)
```
- Tránh mutable default arguments bug

### 7. Static Methods
```python
@staticmethod
def _best_string(s1: str, s2: str) -> str:
```
- Utility methods không cần instance
- Có thể test riêng

---

## 🧪 Test Cases (Ví dụ)

### Test 1: Merge cùng hotel từ 2 sources
```python
# Acme trả về:
Hotel(id="iJhz", name="Beach Villas", lat=1.264, amenities.general=["Pool"])

# Patagonia trả về:
Hotel(id="iJhz", name="Beach Villas Singapore", amenities.room=["TV"])

# Sau merge:
Hotel(
    id="iJhz",
    name="Beach Villas Singapore",  # Dài hơn
    lat=1.264,                      # Từ Acme
    amenities={
        "general": ["Pool"],        # Từ Acme
        "room": ["TV"]              # Từ Patagonia
    }
)
```

### Test 2: Filter logic
```python
# Storage:
hotels = {
    "A": Hotel(id="A", dest=1),
    "B": Hotel(id="B", dest=2),
    "C": Hotel(id="C", dest=1)
}

# Test cases:
find([], []) → [A, B, C]                    # Tất cả
find(["A"], []) → [A]                       # Chỉ A
find([], [1]) → [A, C]                      # Destination 1
find(["A", "B"], [1]) → [A]                 # A có dest=1, B có dest=2
find(["A"], [2]) → []                       # A không có dest=2
```

### Test 3: Merge arrays (loại trùng thông minh)
```python
arr1 = ["WiFi", "Pool"]
arr2 = ["Wi-Fi", "pool", "Gym"]

_merge_arrays(arr1, arr2)
# → ["WiFi", "Pool", "Gym"]  # "Wi-Fi" và "wifi" coi như trùng
```

---

## 📚 Các Khái Niệm Python Quan Trọng

### 1. `or` operator với default values
```python
value = dto.get('key') or "default"
```
**Logic:**
- Nếu `dto.get('key')` trả về None, "", [], 0 → Dùng "default"
- Các giá trị "falsy" trong Python: None, False, 0, "", [], {}, set()

### 2. `is` vs `==`
```python
a == b  # So sánh giá trị
a is b  # So sánh địa chỉ bộ nhớ (cùng object?)
```

### 3. String formatting
```python
# f-string (Python 3.6+)
f"{addr} {postal}".strip()

# Tương đương:
"{} {}".format(addr, postal).strip()
```

### 4. `*args` vs `**kwargs`
```python
def func(*args):      # args là tuple
    print(args)       # (1, 2, 3)

func(1, 2, 3)

def func(**kwargs):   # kwargs là dict
    print(kwargs)     # {'a': 1, 'b': 2}

func(a=1, b=2)
```

### 5. List methods
```python
list.append(item)      # Thêm 1 item
list.extend(items)     # Thêm nhiều items
list.insert(i, item)   # Thêm vào vị trí i
list.remove(item)      # Xóa item đầu tiên
list.pop()             # Xóa và trả về item cuối
```

### 6. Dict methods
```python
dict.get(key, default)        # Lấy value, nếu không có dùng default
dict.setdefault(key, default) # Như get nhưng set luôn nếu chưa có
dict.values()                 # Lấy tất cả values
dict.keys()                   # Lấy tất cả keys
dict.items()                  # Lấy (key, value) pairs
```

---

## ⚡ Performance Considerations

### 1. Time Complexity

| Operation | Complexity | Giải thích |
|-----------|------------|-----------|
| `dict[key]` | O(1) | Hash table lookup |
| `key in dict` | O(1) | Hash table check |
| `list.append()` | O(1) | Thêm vào cuối |
| `key in list` | O(n) | Phải duyệt toàn bộ |
| `set.add()` | O(1) | Hash table |
| `key in set` | O(1) | Hash table |

**Vì sao dùng Dict cho storage:**
```python
# ❌ Chậm - O(n) cho mỗi lookup
hotels = []  # List
for h in hotels:
    if h.id == target_id:
        return h

# ✅ Nhanh - O(1) cho mỗi lookup
hotels = {}  # Dict
return hotels.get(target_id)
```

### 2. Memory Usage

**Trade-off:**
- Dict: Dùng nhiều memory hơn (hash table overhead)
- List: Ít memory hơn
- **Decision:** Chọn Dict vì speed quan trọng hơn trong case này

---

## 🔍 Error Handling

### 1. Network Errors
```python
try:
    resp = requests.get(self.endpoint(), timeout=10)
except Exception:
    pass
return []
```
- Bắt tất cả errors
- Trả về empty list (fail gracefully)
- Không crash cả hệ thống vì 1 supplier lỗi

### 2. Data Validation
```python
if not incoming or not incoming.id:
    continue
```
- Skip invalid data
- Không raise exception

### 3. Safe Dict Access
```python
dto.get('key', default)  # Không KeyError
```

---

## 🚀 Cách Mở Rộng

### 1. Thêm Supplier Mới
```python
class NewSupplier(BaseSupplier):
    def endpoint(self):
        return 'https://new-api.com/hotels'
    
    def parse(self, dto: dict) -> Hotel:
        return Hotel(
            id=dto['hotel_id'],
            # ... mapping logic
        )

# Thêm vào danh sách
suppliers = [Acme(), Patagonia(), Paperflies(), NewSupplier()]
```

### 2. Thêm Field Mới
```python
@dataclass
class Hotel:
    # ... existing fields
    rating: float = 0.0  # Field mới
    reviews_count: int = 0

# Update merge logic
existing.rating = max(existing.rating, incoming.rating)
```

### 3. Thay Đổi Storage
```python
# Thay vì Dict, dùng Database
class HotelsService:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def merge_and_save(self, hotels):
        for hotel in hotels:
            self.db.save(hotel)  # ORM hoặc SQL
```

---

## 🎓 Bài Học Quan Trọng

### 1. Clean Code Principles
- ✅ Single Responsibility: Mỗi class làm 1 việc
- ✅ DRY (Don't Repeat Yourself): `_merge_arrays()` dùng chung
- ✅ KISS (Keep It Simple): Logic đơn giản, dễ hiểu
- ✅ Meaningful names: `_best_string()` thay vì `_merge()`

### 2. OOP Best Practices
- ✅ Inheritance để tái sử dụng code
- ✅ Polymorphism để linh hoạt
- ✅ Encapsulation để bảo vệ data
- ✅ Composition (Hotel chứa Location, Amenities)

### 3. Data Processing
- ✅ Normalize data (lowercase, trim)
- ✅ Handle None/empty values
- ✅ Deduplicate intelligently
- ✅ Merge strategies (best string, union arrays)

### 4. API Design
- ✅ Clear function signatures với type hints
- ✅ Consistent return types
- ✅ Fail gracefully (không crash)
- ✅ Flexible filtering

---

## 📝 Tổng Kết

### Kiến Trúc Tổng Thể
```
Input (hotel_ids, dest_ids)
    ↓
Fetch từ 3 suppliers (parallel)
    ↓
Parse data thành Hotel objects
    ↓
Merge vào HotelsService storage
    ↓
Filter theo điều kiện
    ↓
Convert to JSON
    ↓
Output
```

### Điểm Mạnh của Code
1. **Modularity:** Mỗi component độc lập
2. **Extensibility:** Dễ thêm suppliers mới
3. **Maintainability:** Code rõ ràng, dễ đọc
4. **Robustness:** Handle errors tốt
5. **Performance:** Dùng Dict cho O(1) lookup

### Công Nghệ Sử Dụng
- **Python 3.7+** (dataclasses)
- **requests** library (HTTP)
- **typing** module (type hints)
- **json** module (serialization)
- **OOP principles** (inheritance, encapsulation)
- **Design patterns** (Template Method, Strategy, Repository)

### Skills Học Được
1. ✅ Làm việc với APIs
2. ✅ Data merging strategies
3. ✅ OOP design
4. ✅ Error handling
5. ✅ Code organization
6. ✅ Python advanced features (dataclasses, comprehensions)

---

## 🎯 Câu Hỏi Ôn Tập

1. **Tại sao dùng dataclass thay vì class thông thường?**
   - Ngắn gọn, tự động sinh `__init__`, có type hints

2. **Tại sao `BaseSupplier.fetch()` không phải abstract method?**
   - Vì logic chung cho tất cả suppliers, chỉ `endpoint()` và `parse()` khác nhau

3. **Tại sao merge lại chọn string dài hơn?**
   - Giả định string dài = chi tiết hơn = chất lượng tốt hơn

4. **Tại sao dùng Dict thay vì List cho storage?**
   - Lookup O(1) vs O(n), tự động loại trùng

5. **Tại sao cần normalize key trong `_merge_arrays()`?**
   - Để "WiFi", "Wi-Fi", "wifi" được coi là giống nhau

6. **Match logic trong `find()` hoạt động thế nào?**
   - Empty filter = match tất cả, có filter = phải khớp

7. **Tại sao dùng `or []` nhiều lần?**
   - Handle None để tránh TypeError khi iterate

8. **Design pattern nào được dùng?**
   - Template Method, Strategy, Repository, DTO

---

*Tài liệu này phân tích chi tiết toàn bộ code main.py, giải thích từng dòng code, khái niệm OOP, logic xử lý, và design patterns được sử dụng. Hy vọng giúp bạn hiểu sâu về cấu trúc và cách hoạt động của hệ thống!*

**Ngày tạo:** 2 tháng 3, 2026  
**Phiên bản:** 1.0
