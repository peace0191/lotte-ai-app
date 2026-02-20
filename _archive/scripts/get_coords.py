
import sys
import os

# 현재 디렉토리를 sys.path에 추가하여 services 모듈을 찾을 수 있게 함
sys.path.append(os.getcwd())

from services.geocode import geocode_nominatim

addresses = [
    "서울특별시 강남구 삼성로51길 37",
    "서울특별시 강남구 양재천로 363",
    "서울특별시 강남구 선릉로 209"
]

print("--- Coordinates Start ---")
for addr in addresses:
    coords = geocode_nominatim(addr)
    if coords:
        print(f"{addr} -> {coords[0]}, {coords[1]}")
    else:
        print(f"{addr} -> Not Found")
print("--- Coordinates End ---")
