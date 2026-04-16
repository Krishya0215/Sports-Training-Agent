"""
记忆数据快速概览

显示所有用户的记忆数据摘要，无需指定 user_id
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import db


def show_all_users_summary():
    """显示所有用户的记忆数据摘要"""
    print("\n" + "="*70)
    print("  记忆数据概览 - 所有用户")
    print("="*70)

    # 获取所有用户
    conn = db._get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, email FROM users ORDER BY id")
    users = cursor.fetchall()

    if not users:
        print("\n  没有用户")
        conn.close()
        return

    print(f"\n共 {len(users)} 个用户:\n")

    for user in users:
        user_id = user["id"]
        username = user["username"]

        print("-" * 70)
        print(f"用户 #{user_id}: {username}")
        print("-" * 70)

        # 用户画像
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
        profile = cursor.fetchone()

        if profile:
            print(f"  画像:")
            print(f"    目标: {profile['goal'] if profile['goal'] else 'N/A'}")
            print(f"    水平: {profile['fitness_level'] if profile['fitness_level'] else 'N/A'}")
            print(f"    方法: {profile['preferred_method'] if profile['preferred_method'] else 'N/A'}")
            print(f"    每周天数: {profile['weekly_days'] if profile['weekly_days'] else 'N/A'}")
            print(f"    强度: {profile['intensity_level'] if profile['intensity_level'] else 'N/A'}")
        else:
            print("  画像: 无")

        # 语义记忆统计
        cursor.execute("""
            SELECT fact_category, COUNT(*) as count
            FROM memory_semantic_facts
            WHERE user_id = ? AND is_active = 1
            GROUP BY fact_category
            ORDER BY count DESC
        """, (user_id,))
        semantic_stats = cursor.fetchall()

        if semantic_stats:
            print(f"  语义记忆: {sum(s['count'] for s in semantic_stats)} 条")
            for stat in semantic_stats:
                print(f"    - {stat['fact_category']:15} {stat['count']} 条")
        else:
            print("  语义记忆: 无")

        # 情景记忆统计
        cursor.execute("""
            SELECT event_type, COUNT(*) as count
            FROM memory_episodic_events
            WHERE user_id = ?
            GROUP BY event_type
            ORDER BY count DESC
        """, (user_id,))
        episodic_stats = cursor.fetchall()

        if episodic_stats:
            print(f"  情景记忆: {sum(e['count'] for e in episodic_stats)} 条")
            for stat in episodic_stats:
                print(f"    - {stat['event_type']:30} {stat['count']} 条")
        else:
            print("  情景记忆: 无")

        # 训练计划统计
        cursor.execute("SELECT COUNT(*) as count FROM training_plans WHERE user_id = ?", (user_id,))
        plan_count = cursor.fetchone()["count"]
        print(f"  训练计划: {plan_count} 个")

        # 训练记录统计
        cursor.execute("SELECT COUNT(*) as count FROM training_records WHERE user_id = ?", (user_id,))
        record_count = cursor.fetchone()["count"]
        print(f"  训练记录: {record_count} 条")

        # 训练类型分布
        cursor.execute("""
            SELECT training_type, COUNT(*) as count
            FROM training_records
            WHERE user_id = ?
            GROUP BY training_type
            ORDER BY count DESC
            LIMIT 5
        """, (user_id,))
        type_stats = cursor.fetchall()

        if type_stats:
            print(f"  训练类型分布:")
            for stat in type_stats:
                print(f"    - {stat['training_type']:20} {stat['count']} 次")

        print()

    conn.close()

    print("="*70)
    print("\n提示:")
    print("  - 使用 python tools/check_memory_db.py --users 查看用户ID列表")
    print("  - 使用 python tools/check_memory_db.py --user <id> 查看详细数据")
    print("  - 使用 python tools/check_memory_db.py --export <id> 导出JSON")
    print("="*70 + "\n")


if __name__ == "__main__":
    show_all_users_summary()
