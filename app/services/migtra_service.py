# import httpx


async def send_gps_data_to_migtra(gps_data: list) -> bool:
    print("[MIGTRA] Sending GPS data to Migtra")
    print(gps_data)
    return True

    # url = "https://migtra.example.com/api/gps"
    # headers = {"Content-Type": "application/json"}
    # try:
    #     async with httpx.AsyncClient() as client:
    #         response = await client.post(url,
    #   json={"data": gps_data}, headers=headers)
    #         response.raise_for_status()
    #     return True
    # except httpx.HTTPError as e:
    #     print(f"Error sending to Migtra: {e}")
    #     return False
