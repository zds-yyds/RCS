import pymysql
from pymysql import Error


def enhanced_db_test():
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'zds_test_rcs',
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor  # 关键修复：指定返回字典格式
    }

    try:
        print("\n正在测试连接...")
        with pymysql.connect(**config) as conn:
            with conn.cursor() as cursor:
                # 测试基本查询
                cursor.execute("SELECT 1+1 AS result")
                row = cursor.fetchone()
                assert row['result'] == 2, f"基础查询测试失败，得到: {row}"

                # 测试表结构
                cursor.execute("DESCRIBE rcs_data")
                columns = {col['Field'] for col in cursor.fetchall()}
                expected_columns = {'id', 'aircraft_name', 'frequency', 'polarization',
                                    'azimuth', 'elevation', 'rcs_value'}
                assert columns == expected_columns, f"表结构不匹配，缺少: {expected_columns - columns}"

                # 测试写入权限（可选）
                test_id = 999999
                cursor.execute(
                    "INSERT INTO rcs_data VALUES (%s, 'test', 1.0, 'HH', 0, 0, 1.0)",
                    (test_id,)
                )
                cursor.execute("DELETE FROM rcs_data WHERE id = %s", (test_id,))
                conn.commit()

        print("✔ 所有测试通过！")
        return True

    except AssertionError as e:
        print(f"✖ 验证失败: {e}")
        return False
    except Error as e:
        print(f"✖ 数据库错误: {e}")
        return False


if __name__ == "__main__":
    print("=== 数据库连接测试工具 ===")
    if enhanced_db_test():
        print("\n✅ 数据库完全可用")
    else:
        print("\n❌ 存在配置问题，请检查:")
        print("1. 数据库服务是否运行")
        print("2. 用户名/密码是否正确")
        print("3. 网络连接是否正常")
        print("4. 用户是否有足够权限")