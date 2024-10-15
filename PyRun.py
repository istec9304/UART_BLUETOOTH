import asyncio
from bleak import BleakScanner, BleakClient

# 전송할 데이터
data_to_send = 'AAA'.encode('utf-8')  # UTF-8 인코딩된 바이트 배열

# BLE 장치 UUID
device_name = "uart1"
characteristic_uuid = "0000ffe1-0000-1000-8000-00805f9b34fb"

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
            await print_services(client)
            await send_data(client)
    else:
        print(f"{device_name} 장치를 찾을 수 없습니다.")

async def print_services(client):
    services = client.services  # get_services() 대신 사용
    print("Services and characteristics:")
    for service in services:
        print(f"  Service UUID: {service.uuid}")
        for char in service.characteristics:
            print(f"    Characteristic UUID: {char.uuid}, Properties: {char.properties}")

async def send_data(client):
    retry_count = 3
    for attempt in range(retry_count):
        try:
            if not client.is_connected:
                print("장치가 연결되어 있지 않습니다. 재연결 시도 중...")
                await client.connect()  # 연결 재시도
            await client.write_gatt_char(characteristic_uuid, data_to_send)
            print("데이터 전송 성공!")
            break  # 성공 시 루프 종료
        except Exception as e:
            print(f"데이터 전송 중 오류 발생: {e}")
            await asyncio.sleep(1)  # 잠시 대기 후 재시도
            if attempt == retry_count - 1:
                print("최대 재시도 횟수 도달, 실패했습니다.")

if __name__ == "__main__":
    asyncio.run(scan_and_connect())
