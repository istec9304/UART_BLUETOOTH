import asyncio
from bleak import BleakScanner, BleakClient

# BLE 장치 UUID
device_name = "HMSoft"  # 도움말 https://m.cafe.daum.net/smhan/darS/26
# GATT characteristic UUID to which the data will be sent
characteristic_uuid = "0000ffe1-0000-1000-8000-00805f9b34fb"  # Replace with your valid characteristic UUID

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
        while True:  # 무한 루프를 통해 재연결 시도
            try:
                async with BleakClient(target_device, timeout=10.0) as client:
                    print(f"{target_device.name}에 성공적으로 연결되었습니다.")
                    # Register the notification handler
                    await client.start_notify(characteristic_uuid, notification_handler)
                    await counter_for_10_seconds(client)  # 10초 동안 카운터 출력
                    await client.stop_notify(characteristic_uuid)  # Stop notifications after use
                    break  # 카운터가 끝나면 루프 종료
            except Exception as e:
                print(f"연결 실패: {e}")
                print("재연결을 시도합니다...")
                await asyncio.sleep(2)  # 2초 대기 후 재시도
    else:
        print(f"{device_name} 장치를 찾을 수 없습니다.")

async def counter_for_10_seconds(client):
    try:
        for count in range(10):
            if client.is_connected:
                print(f"연결 유지 중... (초: {count + 1})")
                await send_data(client, "AAA")  # 문자열 AAA 전송
            else:
                print("장치가 연결되어 있지 않습니다. 연결이 끊겼습니다.")
                return  # 연결이 끊기면 함수 종료

            await asyncio.sleep(1)  # 1초 대기
    except Exception as e:
        print(f"카운터 중 오류 발생: {e}")

async def send_data(client, data):
    try:
        # Convert the string to bytes
        byte_data = data.encode('utf-8')
        await client.write_gatt_char(characteristic_uuid, byte_data)
        print(f"전송된 데이터: {data}")
    except Exception as e:
        print(f"데이터 전송 중 오류 발생: {e}")

def notification_handler(sender, data):
    """Handler for received notifications."""
    # Convert the received data from bytes to string or hex
    received_data = data.decode('utf-8')  # Or you could use `data.hex()` for hex format
    print(f"수신된 데이터: {received_data}")

if __name__ == "__main__":
    asyncio.run(scan_and_connect())
