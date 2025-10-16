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
#aircraft_name = 'F16'  # 飞机名称
initial_rcs = 0.5  # 初始 RCS 值 (dBsm)，从 0.5 开始
frequencies = list(range(1, 13))  # [1, 2, 3, ..., 12] 1.0-12.0 GHz，步长 1 GHz（共12个频率点）
polarizations = ['HH', 'VV']
azimuths = range(-90, 181, 90)  # -90到180度，步长90
elevations = range(-90, 91, 90)  # -90到90度，步长90

filepath = "D:/demo/RCS/simRCS/OutPut/sim/"
air_names = ['F22','F35']
fre = [1, 2,3,4,5,6,7,8,9,10,11,12]

def insert_rcs_data():
    try:
        # 建立数据库连接
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()

        # 准备批量插入SQL
        sql = """
              INSERT INTO rcs_data
                  (aircraft_name, frequency, polarization, azimuth, elevation, rcs_value, equipID)
              VALUES (%s, %s, %s, %s, %s, %s, 0) ON DUPLICATE KEY 
              UPDATE rcs_value = 
              VALUES (rcs_value) \
              """

        for aircraft_name in air_names:
            print(f"开始处理飞机型号: {aircraft_name}")
            # 生成所有参数组合
            params = []
            current_rcs = initial_rcs  # 初始化 current_rcs 为 0.5

            for freq, pol, az, el in itertools.product(frequencies, polarizations, azimuths, elevations):
                params.append((aircraft_name, freq, pol, az, el, current_rcs))
                current_rcs += random.uniform(0, 1)  # 每次递增 0~1 之间的随机值

            # 批量插入（每1000条提交一次）
            batch_size = 1000
            for i in range(0, len(params), batch_size):
                batch = params[i:i + batch_size]
                cursor.executemany(sql, batch)
                connection.commit()
                print(f"  {aircraft_name} - 已插入 {min(i + batch_size, len(params))}/{len(params)} 条记录")

            print(f"最终 RCS 值: {current_rcs:.2f} dBsm")  # 打印最终 RCS 值

        print("所有数据插入完成！")


    except Exception as e:
        print(f"发生错误: {e}")
        connection.rollback()
    finally:
        if connection:
            connection.close()


def parse_rcs_data_to_dict(filename):
    """
    解析RCS数据文件并返回字典结构

    参数:
        filename: 数据文件名

    返回:
        rcs_dict: 二维字典，可通过rcs_dict[azimuth][elevation]访问RCS值
    """

    # 读取文件
    with open(filename, 'r') as file:
        lines = file.readlines()

    # 跳过前5行标题信息
    data_lines = lines[5:]

    # 解析俯仰角度 (第6行)
    elevation_angles = list(map(float, data_lines[0].strip().split()))

    # 创建二维字典
    rcs_dict = {}

    # 解析方位角和对应的RCS数据
    for line in data_lines[1:]:
        if line.strip():  # 跳过空行
            values = list(map(float, line.strip().split()))
            azimuth = values[0]  # 第一个值是方位角
            rcs_values = values[1:]  # 剩余的是该方位角下的RCS值

            # 为每个方位角创建子字典
            rcs_dict[azimuth] = {}

            # 将俯仰角与对应的RCS值配对
            for i, elevation in enumerate(elevation_angles):
                rcs_dict[azimuth][elevation] = rcs_values[i]

    return rcs_dict


def update_rcs_value(rcs_pattern_data,HH_OR_VV,freq,name):
    """
        根据aircraft_name, frequency, polarization, azimuth, elevation的值判断并更新rcs_value
    """
    try:
        # 建立数据库连接
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()

        # 使用参数化查询（安全且正确）
        select_sql = """
                     SELECT id, aircraft_name, frequency, polarization, azimuth, elevation, rcs_value
                     FROM rcs_data
                     WHERE aircraft_name = %s
                       AND frequency = %s
                       AND polarization = %s
                       AND azimuth IS NOT NULL
                       AND elevation IS NOT NULL \
                     """

        # 正确传递参数
        cursor.execute(select_sql, (name, freq, HH_OR_VV))
        records = cursor.fetchall()

        print(f"找到 {len(records)} 条需要处理的记录")

        # 准备更新SQL
        update_sql = """
                     UPDATE rcs_data
                     SET rcs_value = %s
                     WHERE id = %s \
                     """

        # 批量更新参数
        update_params = []
        updated_count = 0

        for record in records:
            record_id, aircraft_name, frequency, polarization, azimuth, elevation, current_rcs = record

            if not rcs_pattern_data:
                new_rcs = 0  #剔除对应的5，7，9，11，先设为0
            else:
                new_rcs = rcs_pattern_data[azimuth][elevation]


            # 如果新值与原值不同，则添加到更新列表
            if new_rcs != current_rcs:
                update_params.append((new_rcs, record_id))
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


def line_value_lose_data():
    try:
        # 建立数据库连接
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()

        # 使用参数化查询（安全且正确）
        select_sql = """
                     SELECT id, aircraft_name, frequency, polarization, azimuth, elevation, rcs_value
                     FROM rcs_data
                     WHERE rcs_value = 0 \
                     """

        # 正确传递参数
        cursor.execute(select_sql)
        records = cursor.fetchall()

        print(f"找到 {len(records)} 条loss的记录")

        # 准备更新SQL
        update_sql = """
                     UPDATE rcs_data
                     SET rcs_value = %s
                     WHERE id = %s \
                     """

        # 准备更新SQL
        chaXun_sql = """
                     SELECT rcs_value
                     FROM rcs_data
                     WHERE aircraft_name = %s 
                     AND frequency = %s
                     AND polarization = %s
                     AND azimuth = %s
                     AND elevation = %s \
                     """



        # 批量更新参数
        update_params = []
        updated_count = 0

        for record in records:
            record_id, aircraft_name, frequency, polarization, azimuth, elevation, current_rcs = record

            if current_rcs == 0:
                # 正确传递参数
                min_value = 0
                max_value = 0
                cursor.execute(chaXun_sql, (aircraft_name, frequency - 1, polarization, azimuth, elevation))
                chaXun_records = cursor.fetchall()
                for chaXun_record in chaXun_records:
                    min_value = chaXun_record[0]
                    break
                cursor.execute(chaXun_sql, (aircraft_name, frequency + 1, polarization, azimuth, elevation))
                chaXun_records = cursor.fetchall()
                for chaXun_record in chaXun_records:
                    max_value = chaXun_record[0]
                    break
                new_rcs = round((min_value + max_value)/2, 2)
                # 0值替换
                if 1:
                    update_params.append((new_rcs, record_id))
                    updated_count += 1



        # 批量更新（每1000条提交一次）
        batch_size = 1000
        for i in range(0, len(update_params), batch_size):
            batch = update_params[i:i + batch_size]
            cursor.executemany(update_sql, batch)
            connection.commit()
            print(f"插值丢失的 {min(i + batch_size, len(update_params))}/{len(update_params)} 条记录")

        print(f"所有 0 数据插值完成！共更新了 {updated_count} 条记录")

    except Exception as e:
        print(f"发生错误: {e}")
        if 'connection' in locals():
            connection.rollback()
    finally:
        if 'connection' in locals() and connection:
            connection.close()


def update_rcs_data():
    # 从本地加载数据
    empty_Value = []
    for i in air_names:
        for j in fre:
            if j == 9 or j == 11 or j == 5 or j == 7:
                update_rcs_value(empty_Value, 'HH', j, i)
                update_rcs_value(empty_Value, 'VV', j, i)
                continue
            HH_rcs_pattern_data = parse_rcs_data_to_dict(
                filepath + i + "/" + i + "_0001_" + str(j) + "GHz_" + polarizations[0] + ".txt")
            VV_rcs_pattern_data = parse_rcs_data_to_dict(
                filepath + i + "/" + i + "_0001_" + str(j) + "GHz_" + polarizations[1] + ".txt")
            update_rcs_value(HH_rcs_pattern_data, 'HH', j, i)
            update_rcs_value(VV_rcs_pattern_data, 'VV', j, i)
    line_value_lose_data()


if __name__ == "__main__":
    # 计算总记录数并确认
    total = len(frequencies) * len(polarizations) * len(azimuths) * len(elevations)
    print(f"将插入 {total} 条记录")
    confirm = input("确认插入？(y/n): ")
    if confirm.lower() == 'y':
        insert_rcs_data()
    else:
        print("操作已取消")

    update_rcs_data()





