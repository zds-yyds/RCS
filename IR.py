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

# 固定参数
aircraft_name = 'F-16'
thrust_states = ['MIL', 'AB']
env_temperatures = [-20, -10, 0, 10, 20, 30, 40]
azimuths = list(range(-90, 181, 90))  # 排除 -180，避免与 180 重复
elevations = list(range(-90, 91, 90))  # -90 到 90 步长 30

def insert_ir_data():
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()

        sql = """
            INSERT INTO ir_data
                (aircraft_name, thrust_state, env_temperature, azimuth, elevation, ir_value)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                ir_value = VALUES(ir_value)
        """

        params = []
        current_ir = 0.0

        # 生成所有参数组合
        for combo in itertools.product(thrust_states, env_temperatures, azimuths, elevations):
            thrust_state, temp, az, el = combo
            params.append((aircraft_name, thrust_state, temp, az, el, current_ir))
            current_ir += random.uniform(0, 0.5)

        # 批量插入
        batch_size = 1000
        for i in range(0, len(params), batch_size):
            batch = params[i:i + batch_size]
            cursor.executemany(sql, batch)
            connection.commit()
            print(f"已插入 {min(i + batch_size, len(params))}/{len(params)} 条记录")

        print("IR 数据插入完成！")
        print(f"最终 IR 值: {current_ir:.2f} W/sr")

    except Exception as e:
        print(f"发生错误: {e}")
        connection.rollback()
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    total = len(thrust_states) * len(env_temperatures) * len(azimuths) * len(elevations)
    print(f"将插入 {total} 条 IR 记录")
    confirm = input("确认插入？(y/n): ")
    if confirm.lower() == 'y':
        insert_ir_data()
    else:
        print("操作已取消")
