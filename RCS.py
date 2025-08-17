import pymysql
import itertools

# 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'test_rcs',
    'charset': 'utf8mb4'
}

# 固定参数
aircraft_name = 'F-16'  # 飞机名称
fixed_rcs = 2.0  # 固定RCS值(dBsm)
frequencies = list(range(1, 11))  # [1, 2, 3, ..., 10] 1.0-10.0 GHz，步长 1 GHz（共10个频率点）
polarizations = ['HH', 'VV']
azimuths = range(-180, 181, 30)  # -180到180度，步长30
elevations = range(-90, 91, 30)  # -90到90度，步长30


def insert_rcs_data():
    try:
        # 建立数据库连接
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()

        # 准备批量插入SQL
        sql = """
              INSERT INTO rcs_data
                  (aircraft_name, frequency, polarization, azimuth, elevation, rcs_value)
              VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY \
              UPDATE rcs_value = \
              VALUES (rcs_value) \
              """

        # 生成所有参数组合
        params = []
        for freq, pol, az, el in itertools.product(frequencies, polarizations, azimuths, elevations):
            params.append((aircraft_name, freq, pol, az, el, fixed_rcs))

        # 批量插入（每1000条提交一次）
        batch_size = 1000
        for i in range(0, len(params), batch_size):
            batch = params[i:i + batch_size]
            cursor.executemany(sql, batch)
            connection.commit()
            print(f"已插入 {min(i + batch_size, len(params))}/{len(params)} 条记录")

        print("所有数据插入完成！")

    except Exception as e:
        print(f"发生错误: {e}")
        connection.rollback()
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    # 计算总记录数并确认
    total = len(frequencies) * len(polarizations) * len(azimuths) * len(elevations)
    print(f"将插入 {total} 条记录")
    confirm = input("确认插入？(y/n): ")
    if confirm.lower() == 'y':
        insert_rcs_data()
    else:
        print("操作已取消")