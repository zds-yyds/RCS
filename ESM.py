import pymysql
import itertools
import random

# 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'test_rcs',
    'charset': 'utf8mb4'
}

# 多个飞机型号
aircraft_names = ['F-16', 'F-22']

# 系统类型及其合法模式映射
system_types = ['RADAR', 'COMM']
valid_mode_map = {
    'RADAR': ['搜索', '跟踪'],
    'COMM': ['应答', '静默']
}

# 固定参数
power_dbm = 200000.0  # 200 kW ≈ 83 dBm
frequency_ghz = 8.0
bandwidth_mhz = 1.0
beam_number = 1
angle_config = {
    "minAz": -30,
    "maxAz": 30,
    "minEle": -60,
    "maxEle": 60
}
max_range_km = 200.0

def insert_esm_data():
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()

        sql = """
            INSERT INTO esm_data (
                aircraft_name, system_type, mode_name,
                power, frequency, bandwidth,
                pulse_width, pri, beam_number,
                minAz, maxAz, minEle, maxEle, max_range
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                power = VALUES(power),
                frequency = VALUES(frequency),
                bandwidth = VALUES(bandwidth),
                pulse_width = VALUES(pulse_width),
                pri = VALUES(pri),
                beam_number = VALUES(beam_number),
                minAz = VALUES(minAz),
                maxAz = VALUES(maxAz),
                minEle = VALUES(minEle),
                maxEle = VALUES(maxEle),
                max_range = VALUES(max_range)
        """

        params = []

        for aircraft_name, system_type in itertools.product(aircraft_names, system_types):
            for mode_name in valid_mode_map[system_type]:
                if system_type == 'RADAR':
                    pulse_width = round(random.uniform(0.5, 10.0), 2)
                    pri = round(random.uniform(100, 1000), 2)
                    min_az = angle_config["minAz"]
                    max_az = angle_config["maxAz"]
                    min_el = angle_config["minEle"]
                    max_el = angle_config["maxEle"]
                    beam = beam_number
                else:
                    pulse_width = None
                    pri = None
                    min_az = None
                    max_az = None
                    min_el = None
                    max_el = None
                    beam = None

                params.append((
                    aircraft_name,
                    system_type,
                    mode_name,
                    power_dbm,
                    frequency_ghz,
                    bandwidth_mhz,
                    pulse_width,
                    pri,
                    beam,
                    min_az,
                    max_az,
                    min_el,
                    max_el,
                    max_range_km
                ))

        cursor.executemany(sql, params)
        connection.commit()
        print(f"成功插入 {len(params)} 条 ESM 数据！")

    except Exception as e:
        print(f"发生错误: {e}")
        connection.rollback()
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    total = len(aircraft_names) * sum(len(modes) for modes in valid_mode_map.values())
    print(f"将插入 {total} 条合法 ESM 记录")
    confirm = input("确认插入？(y/n): ")
    if confirm.lower() == 'y':
        insert_esm_data()
    else:
        print("操作已取消")
