import asyncio
from bleak import BleakScanner, BleakClient

# BLE 장치 UUID
device_name = "uart1"

async def scan_and_connect():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()
    target_device = None

    for device in devices:
        print(f"Found device: {device.name} - {device.address}")
        if device.name == device_name:
            target_device = device
            break

    if target_device:
        print(f"Found target device: {target_device.name} ({target_device.address})")
        async with BleakClient(target_device) as client:
            print(f"{target_device.name}에 성공적으로 연결되었습니다.")
            await keep_connection(client)  # 연결 유지
    else:
        print(f"{device_name} 장치를 찾을 수 없습니다.")

async def keep_connection(client):
    try:
        count = 0
        reconnect_attempts = 0  # 재연결 시도 횟수
        while count < 30:  # 총 30초 동안 유지
            if client.is_connected:
                print(f"장치가 연결되어 있습니다. 연결 유지 중... (초: {count + 1})")
                reconnect_attempts = 0  # 연결이 유지되면 시도 횟수 초기화
            else:
                reconnect_attempts += 1
                print("장치가 연결되어 있지 않습니다. 재연결을 시도합니다...")
                try:
                    await client.connect()  # 연결 시도
                    if client.is_connected:
                        print("장치에 성공적으로 재연결되었습니다.")
                        reconnect_attempts = 0  # 성공적으로 재연결되면 시도 횟수 초기화
                    else:
                        print("재연결에 실패했습니다.")
                except Exception as e:
                    print(f"재연결 중 오류 발생: {e}")

            count += 1
            await asyncio.sleep(1)  # 1초마다 카운트 증가

            # 재연결 시도가 여러 번 실패한 경우 대기
            if reconnect_attempts >= 5:
                print("재연결 시도가 5회 실패했습니다. 잠시 대기 후 다시 시도합니다...")
                await asyncio.sleep(5)  # 5초 대기 후 재연결 시도
                reconnect_attempts = 0  # 시도 횟수 초기화
    except Exception as e:
        print(f"연결 유지 중 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(scan_and_connect())
