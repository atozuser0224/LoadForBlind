import requests
import json

# T-map API 키 (본인의 API 키로 변경하세요)
TMAP_APP_KEY = "YOUR_TMAP_APP_KEY"


def get_walking_route(start_lat, start_lon, end_lat, end_lon):
    """
    T-map API를 이용하여 도보 경로 데이터를 가져오는 함수

    :param start_lat: 출발지 위도
    :param start_lon: 출발지 경도
    :param end_lat: 도착지 위도
    :param end_lon: 도착지 경도
    :return: 도보 경로 데이터 (JSON 형식) 또는 None
    """
    url = "https://apis.openapi.sk.com/tmap/routes/pedestrian"
    headers = {
        "appKey": TMAP_APP_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "startX": str(start_lon),  # 경도
        "startY": str(start_lat),  # 위도
        "endX": str(end_lon),
        "endY": str(end_lat),
        "reqCoordType": "WGS84GEO",  # 요청 좌표계 (위도/경도)
        "resCoordType": "WGS84GEO",  # 결과 좌표계 (위도/경도)
        "startName": "출발지",
        "endName": "도착지"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # HTTP 오류가 발생하면 예외 발생
        route_data = response.json()
        return route_data
    except requests.exceptions.RequestException as e:
        print(f"API 요청 오류: {e}")
        return None


def parse_route_data(route_data):
    """
    T-map 도보 경로 데이터에서 좌표만 추출하는 함수
    """
    if not route_data or "features" not in route_data:
        return []

    path_coords = []
    total_distance = 0
    total_time = 0

    for feature in route_data["features"]:
        if feature["geometry"]["type"] == "Point":
            # 포인트 정보 (예: 출발지, 도착지, 교차점)
            pass
        elif feature["geometry"]["type"] == "LineString":
            # 경로 선 정보
            for coord in feature["geometry"]["coordinates"]:
                path_coords.append((coord[1], coord[0]))  # 위도, 경도 순으로 저장

        # 경로 요약 정보 (첫 번째 feature의 properties에서 추출)
        if feature["properties"].get("totalDistance"):
            total_distance = feature["properties"]["totalDistance"]
        if feature["properties"].get("totalTime"):
            total_time = feature["properties"]["totalTime"]

    return path_coords, total_distance, total_time


if __name__ == "__main__":
    # 예시: 서울역에서 남산타워까지 도보 경로
    start_latitude = 37.55627233898953  # 서울역 위도
    start_longitude = 126.97216664972583  # 서울역 경도

    end_latitude = 37.55106199464528  # 남산타워 위도
    end_longitude = 126.99120612458428  # 남산타워 경도

    # 도보 경로 데이터 가져오기
    route_info = get_walking_route(start_latitude, start_longitude, end_latitude, end_longitude)

    if route_info:
        path, dist, time = parse_route_data(route_info)
        print("--- 도보 경로 정보 ---")
        print(f"총 거리: {dist} 미터")
        print(f"예상 소요 시간: {time // 60}분 {time % 60}초")
        print("경로 좌표 (위도, 경도):")
        for lat, lon in path:
            print(f"  ({lat}, {lon})")

        # 이 경로 좌표를 웹 지도에 표시하거나 다른 용도로 활용할 수 있습니다.
        # 예를 들어, folium 라이브러리를 사용하여 파이썬에서 지도에 그릴 수도 있습니다.
        # import folium
        # m = folium.Map(location=[(start_latitude + end_latitude) / 2, (start_longitude + end_longitude) / 2], zoom_start=14)
        # folium.PolyLine(path, color="red", weight=2.5, opacity=1).add_to(m)
        # folium.Marker([start_latitude, start_longitude], popup="출발").add_to(m)
        # folium.Marker([end_latitude, end_longitude], popup="도착").add_to(m)
        # m.save("walking_route.html")
        # print("\n'walking_route.html' 파일이 생성되었습니다. 웹 브라우저에서 열어보세요.")
    else:
        print("도보 경로 정보를 가져오는 데 실패했습니다.")
