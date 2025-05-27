import requests
import math
import time

# --- Configuration ---
APP_KEY = "YOUR_TMAP_APPKEY"  # Replace with your actual AppKey
CNT_BUFF = 10  # Buffer points for smooth matching
SPLIT_VALUE = 20  # Max points per API request
REQ_LIMIT_PER_SEC = 1  # API request limit per second

# --- Data ---
# Flat list of longitude, latitude pairs
ALL_POINTS_RAW = [
    126.95042955033101, 37.39952907832974,
    126.95100890747277, 37.39935861417968,
    126.95184575668353, 37.399171103167795,
    126.95238219849246, 37.39836991446609,
    126.95221053711612, 37.39727892033366,
    126.95343362442138, 37.39680160540712,
    126.95515023819372, 37.397790325810476,
    126.95680247894435, 37.397994887024126,
    126.95695268264977, 37.39847219435172,
    126.95695268264977, 37.39956317111266,
    126.95645915619167, 37.400790500985025,
    126.95703851334244, 37.40133597447641,
    126.95800410858769, 37.40179621464611,
    126.95937739959838, 37.40169393929715,
    126.96064340225449, 37.40106323822738,
    126.96074264399483, 37.4001811001235,
    126.96189062945639, 37.39907308586036,
    126.96211593503247, 37.398126999177244,
    126.96302788610492, 37.39865118381423,
    126.9626470124259, 37.398114214139916
]

# --- Global State (similar to DrawLine object) ---
tot_distance = 0
tot_point_count = 0
arr_matched_id = []
last_matched_location = None
cnt_req_api = 0


# --- Helper Functions ---
def log_message(msg):
    print(msg)


def deg2rad(deg):
    return deg * math.pi / 180


def rad2deg(rad):
    return rad * 180 / math.pi


def calculate_distance(lon1, lat1, lon2, lat2):
    if lon1 == lon2 and lat1 == lat2:
        return 0

    theta = lon1 - lon2
    dist = math.sin(deg2rad(lat1)) * math.sin(deg2rad(lat2)) + \
           math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * math.cos(deg2rad(theta))
    dist = math.acos(dist)
    dist = rad2deg(dist)

    dist = dist * 60 * 1.1515
    dist = dist * 1.609344  # miles to km
    dist = dist * 1000.0  # km to m

    return round(dist, 2)


def req_load_api(point_string, app_key):
    url = 'https://apis.openapi.sk.com/tmap/road/matchToRoads500?version=1'
    headers = {"appKey": app_key}
    data = {
        "responseType": "1",
        "coords": point_string
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        log_message(f"API request failed: {e}")
        return None


def process_points():
    global tot_distance, tot_point_count, arr_matched_id, last_matched_location, cnt_req_api

    current_index = 0
    cnt_all_point = len(ALL_POINTS_RAW)

    log_message("- LoadApi 요청 작업 시작 -")
    log_message('------------------------------------------')

    while current_index < cnt_all_point:
        point_string_parts = []
        points_in_current_chunk = 0
        start_chunk_index = current_index

        # Adjust start_chunk_index for buffer
        if cnt_req_api > 0:  # If it's not the first request, include buffer from previous chunk
            start_chunk_index = max(0, current_index - CNT_BUFF * 2)

        # Build point string for the current API call
        for i in range(start_chunk_index, cnt_all_point, 2):
            if points_in_current_chunk >= SPLIT_VALUE + CNT_BUFF and (current_index + SPLIT_VALUE * 2) < cnt_all_point:
                # If we've reached the split value plus buffer, and there's more data to come, break
                break

            point_string_parts.append(f"{ALL_POINTS_RAW[i]},{ALL_POINTS_RAW[i + 1]}")
            points_in_current_chunk += 1

            if points_in_current_chunk == SPLIT_VALUE and (i + 2) < cnt_all_point:
                # If we've hit the split value and there are still points, break for next API call
                break

        point_string = '|'.join(point_string_parts)

        if not point_string:
            break  # No more points to process

        response = req_load_api(point_string, APP_KEY)
        cnt_req_api += 1

        if response and response.get('resultData', {}).get('matchedPoints'):
            matched_points = response['resultData']['matchedPoints']
            arr_point_for_cal_distance = []

            # This complex buffer logic needs to be carefully translated.
            # The JavaScript logic for "less drawing" based on buffer size is for map visualization.
            # For distance calculation, we'll focus on the *actual* matched points.

            # If there was a last matched location from the previous API call, prepend it
            if last_matched_location:
                arr_point_for_cal_distance.append(last_matched_location)
                last_matched_location = None  # Reset after use

            for j, matched_obj in enumerate(matched_points):
                obj_matched_location = matched_obj.get('matchedLocation')
                obj_source_location = matched_obj.get('sourceLocation')

                # 1. Matched ID
                matched_id = f"{matched_obj['linkId']}_{matched_obj['idxName']}"
                if matched_id not in arr_matched_id:
                    arr_matched_id.append(matched_id)

                # 2. Distance Calculation points
                if obj_matched_location:
                    arr_point_for_cal_distance.append({
                        'longitude': obj_matched_location['longitude'],
                        'latitude': obj_matched_location['latitude']
                    })

            # Store the last matched location for the next API call's buffer
            if arr_point_for_cal_distance:
                last_matched_location = arr_point_for_cal_distance[-1]

            # 4. Calculate distance
            for k in range(len(arr_point_for_cal_distance) - 1):
                p1 = arr_point_for_cal_distance[k]
                p2 = arr_point_for_cal_distance[k + 1]
                tot_distance += calculate_distance(p1['longitude'], p1['latitude'], p2['longitude'], p2['latitude'])

            # 5. Count matched points
            # The JS logic for counting points with buffer is a bit tricky.
            # We'll just count the unique matched points for simplicity here.
            tot_point_count += len(arr_point_for_cal_distance)
            if cnt_req_api > 1 and len(arr_point_for_cal_distance) >= 1:
                tot_point_count -= 1  # Adjust for overlapping buffer point if included from previous call
        else:
            log_message("No matched points in response.")

        log_message(f"총 거리 : {tot_distance:.2f}m")
        log_message(f"매칭된 링크의 개수 : {len(arr_matched_id)}개")
        log_message(f"총 좌표의 개수 : {tot_point_count}개")
        log_message('------------------------------------------')

        current_index += points_in_current_chunk * 2  # Move to the next set of points

        if current_index < cnt_all_point:
            time.sleep(1 / REQ_LIMIT_PER_SEC)  # Apply rate limiting

    log_message("- LoadApi 요청 작업 완료 -")


# --- Main execution ---
if __name__ == "__main__":
    if len(ALL_POINTS_RAW) <= (CNT_BUFF * 2) or SPLIT_VALUE <= CNT_BUFF or SPLIT_VALUE > 500:
        print(
            "Error: Resource point data count must exceed buffer size, and 'SPLIT_VALUE' must exceed buffer size and be less than or equal to 500.")
    else:
        process_points()
