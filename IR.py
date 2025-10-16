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
filepath = "D:/demo/RCS/simRCS/OutPut/sim/"
air_names = ['F22','F35']
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
                (aircraft_name, thrust_state, env_temperature, azimuth, elevation, ir_value, equipID)
            VALUES (%s, %s, %s, %s, %s, %s, 0)
            ON DUPLICATE KEY UPDATE
                ir_value = VALUES(ir_value)
        """

        for aircraft_name in air_names:
            print(f"开始处理飞机型号: {aircraft_name}")
            # 生成所有参数组合
            params = []
            current_ir = 0.5

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
                print(f"  {aircraft_name} - 已插入 {min(i + batch_size, len(params))}/{len(params)} 条记录")
            print(f"最终 IR 值: {current_ir:.2f} W/sr")

        print("IR 数据插入完成！")


    except Exception as e:
        print(f"发生错误: {e}")
        connection.rollback()
    finally:
        if connection:
            connection.close()


def parse_ir_data_to_dict(filename):
    """
    解析IR数据文件并返回字典结构

    参数:
        filename: 数据文件名

    返回:
        ir_dict: 二维字典，可通过ir_dict[azimuth][elevation]访问ir值
    """

    # 读取文件
    with open(filename, 'r') as file:
        lines = file.readlines()

    # 跳过前2行标题信息
    data_lines = lines[2:]

    # 解析俯仰角度 (第3行)
    elevation_angles = list(map(float, data_lines[0].strip().split()))

    # 创建二维字典
    ir_dict = {}

    # 解析方位角和对应的ir数据
    for line in data_lines[1:]:
        if line.strip():  # 跳过空行
            values = list(map(float, line.strip().split()))
            azimuth = values[0]  # 第一个值是方位角
            ir_values = values[1:]  # 剩余的是该方位角下的ir值

            # 为每个方位角创建子字典
            ir_dict[azimuth] = {}

            # 将俯仰角与对应的ir值配对
            for i, elevation in enumerate(elevation_angles):
                ir_dict[azimuth][elevation] = ir_values[i]

    return ir_dict


def update_ir_value(ir_pattern_data,MIL_OR_AB,temp,name):
    """
        根据aircraft_name, thrust_state, env_temperature, azimuth, elevation的值判断并更新rcs_value
    """
    try:
        # 建立数据库连接
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()

        # 使用参数化查询（安全且正确）
        select_sql = """
                     SELECT id, aircraft_name, thrust_state, env_temperature, azimuth, elevation, ir_value
                     FROM ir_data
                     WHERE aircraft_name = %s
                       AND thrust_state = %s
                       AND env_temperature = %s
                       AND azimuth IS NOT NULL
                       AND elevation IS NOT NULL \
                     """

        # 正确传递参数
        cursor.execute(select_sql, (name, MIL_OR_AB, temp))
        records = cursor.fetchall()

        print(f"找到 {len(records)} 条需要处理的记录")

        # 准备更新SQL
        update_sql = """
                     UPDATE ir_data
                     SET ir_value = %s
                     WHERE id = %s \
                     """

        # 批量更新参数
        update_params = []
        updated_count = 0

        for record in records:
            record_id, aircraft_name, thrust_state, env_temperature, azimuth, elevation, current_ir = record

            if MIL_OR_AB == 'AB':
                if ir_pattern_data[azimuth][elevation] > 0.001:
                    new_ir = ir_pattern_data[azimuth][elevation] + random.uniform(2, 5)
                else:
                    new_ir = ir_pattern_data[azimuth][elevation]
            else:
                new_ir = ir_pattern_data[azimuth][elevation]



            # 如果新值与原值不同，则添加到更新列表
            if new_ir != current_ir:
                update_params.append((new_ir, record_id))
                updated_count += 1

        # 批量更新（每1000条提交一次）
        batch_size = 1000
        for i in range(0, len(update_params), batch_size):
            batch = update_params[i:i + batch_size]
            cursor.executemany(update_sql, batch)
            connection.commit()
            print(f"已更新 {min(i + batch_size, len(update_params))}/{len(update_params)} 条记录")

        print(f"所有数据更新完成！共更新了 {updated_count} 条记录")

    except Exception as e:
        print(f"发生错误: {e}")
        if 'connection' in locals():
            connection.rollback()
    finally:
        if 'connection' in locals() and connection:
            connection.close()


def update_ir_data():
    # 从本地加载数据
    ir_pattern_data = parse_ir_data_to_dict(filepath)
    for i in air_names:
        for j in env_temperatures:

            update_ir_value(ir_pattern_data, 'MIL', j, i)
            update_ir_value(ir_pattern_data, 'AB', j, i)



if __name__ == "__main__":
    # total = len(thrust_states) * len(env_temperatures) * len(azimuths) * len(elevations)
    # print(f"将插入 {total} 条 IR 记录")
    # confirm = input("确认插入？(y/n): ")
    # if confirm.lower() == 'y':
    #     insert_ir_data()
    # else:
    #     print("操作已取消")
    update_ir_data()
    pass