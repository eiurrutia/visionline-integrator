# import httpx


async def send_gps_data_to_gauss_control(gps_data: list) -> bool:
    print("[MIGTRA] Sending GPS data to Migtra")
    print(gps_data)
    return True

    # url = "https://gausscontrol.example.com/api/alarms"
    # headers = {"Content-Type": "application/json"}
    # try:
    #     async with httpx.AsyncClient() as client:
    #         response = await client.post(
    #      url, json={"data": alarm_data}, headers=headers)
    #         response.raise_for_status()
    #     return True
    # except httpx.HTTPError as e:
    #     print(f"Error sending to Gauss Control: {e}")
    #     return False
