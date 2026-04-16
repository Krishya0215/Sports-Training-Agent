"""
记忆数据库检查工具

使用方法：
    python tools/check_memory_db.py              # 查看所有表概览
    python tools/check_memory_db.py --user <id>  # 查看指定用户的所有记忆数据
    python tools/check_memory_db.py --semantic     # 查看语义记忆
    python tools/check_memory_db.py --episodic    # 查看情景记忆
"""
import sys
from pathlib import Path
import argparse
import sqlite3
import json

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import DB_PATH


class MemoryDBChecker:
    """记忆数据库检查工具"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)

    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def show_all_tables(self):
        """显示所有表概览"""
        print("\n" + "="*60)
        print("  数据库表概览")
        print("="*60)

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()

        print(f"\n共有 {len(tables)} 张表:\n")

        for table in tables:
            table_name = table["name"]
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()["count"]

            print(f"  {table_name:40} {count:10} 条记录")

        conn.close()

    def show_table_schema(self, table_name: str):
        """显示表结构"""
        print(f"\n{'='*60}")
        print(f"  表: {table_name}")
        print(f"{'='*60}\n")

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        print(f"{'字段名':<30} {'类型':<15} {'说明'}")
        print("-"*60)

        for col in columns:
            name = col["name"]
            type = col["type"]
            nullable = "可为空" if col["notnull"] == 0 else "非空"
            pk = "主键" if col["pk"] > 0 else ""
            note = f"{nullable} {pk}".strip()
            print(f"{name:<30} {type:<15} {note}")

        conn.close()

    def show_semantic_memory(self, user_id: int = None, limit: int = 20):
        """显示语义记忆"""
        print(f"\n{'='*60}")
        print("  语义记忆 (memory_semantic_facts)")
        print(f"{'='*60}\n")

        conn = self._get_connection()
        cursor = conn.cursor()

        if user_id:
            cursor.execute("""
                SELECT * FROM memory_semantic_facts
                WHERE user_id = ? AND is_active = 1
                ORDER BY updated_at DESC
                LIMIT ?
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM memory_semantic_facts
                WHERE is_active = 1
                ORDER BY updated_at DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()

        if not rows:
            print("  暂无数据")
            conn.close()
            return

        print(f"{'ID':<6} {'用户ID':<8} {'类别':<15} {'键':<25} {'值':<30} {'置信度'}")
        print("-"*100)

        for row in rows:
            print(f"{row['id']:<6} {row['user_id']:<8} {row['fact_category']:<15} "
                  f"{row['fact_key']:<25} {str(row['fact_value']):<30} {row['confidence']}")

        conn.close()

    def show_episodic_memory(self, user_id: int = None, limit: int = 10):
        """显示情景记忆"""
        print(f"\n{'='*60}")
        print("  情景记忆 (memory_episodic_events)")
        print(f"{'='*60}\n")

        conn = self._get_connection()
        cursor = conn.cursor()

        if user_id:
            cursor.execute("""
                SELECT id, user_id, event_type, event_time, event_summary, importance_score
                FROM memory_episodic_events
                WHERE user_id = ?
                ORDER BY event_time DESC
                LIMIT ?
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT id, user_id, event_type, event_time, event_summary, importance_score
                FROM memory_episodic_events
                ORDER BY event_time DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()

        if not rows:
            print("  暂无数据")
            conn.close()
            return

        print(f"{'ID':<6} {'用户ID':<8} {'类型':<20} {'时间':<20} {'摘要'} {'重要性'}")
        print("-"*100)

        for row in rows:
            summary = row['event_summary'][:40] + "..." if len(str(row['event_summary'])) > 40 else row['event_summary']
            time_str = row['event_time'][:19] if row['event_time'] else "N/A"
            print(f"{row['id']:<6} {row['user_id']:<8} {row['event_type']:<20} {time_str:<20} "
                  f"{summary:<40} {row['importance_score']}")

        conn.close()

    def show_working_memory(self, user_id: int = None, limit: int = 10):
        """显示工作记忆"""
        print(f"\n{'='*60}")
        print("  工作记忆 (memory_working_sessions + messages)")
        print(f"{'='*60}\n")

        conn = self._get_connection()
        cursor = conn.cursor()

        # 先显示会话
        if user_id:
            cursor.execute("""
                SELECT s.id, s.conversation_id, s.status, s.created_at,
                       COUNT(m.id) as message_count
                FROM memory_working_sessions s
                LEFT JOIN memory_working_messages m ON s.id = m.session_id
                WHERE s.user_id = ?
                GROUP BY s.id
                ORDER BY s.updated_at DESC
                LIMIT ?
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT s.id, s.conversation_id, s.status, s.created_at,
                       COUNT(m.id) as message_count
                FROM memory_working_sessions s
                LEFT JOIN memory_working_messages m ON s.id = m.session_id
                GROUP BY s.id
                ORDER BY s.updated_at DESC
                LIMIT ?
            """, (limit,))

        sessions = cursor.fetchall()

        if not sessions:
            print("  暂无工作记忆会话")
            conn.close()
            return

        print(f"{'会话ID':<10} {'对话ID':<30} {'状态':<10} {'消息数':<10} {'创建时间'}")
        print("-"*80)

        for session in sessions:
            conv_id = session['conversation_id'][:28] + "..." if session['conversation_id'] and len(session['conversation_id']) > 28 else (session['conversation_id'] or "N/A")
            print(f"{session['id']:<10} {conv_id:<30} {session['status']:<10} {session['message_count']:<10} "
                  f"{session['created_at'][:19] if session['created_at'] else 'N/A'}")

        # 显示消息
        if sessions:
            cursor.execute("""
                SELECT session_id, role, content, created_at
                FROM memory_working_messages
                WHERE session_id IN ({})
                ORDER BY session_id, sequence_no
                LIMIT ?
            """.format(','.join(str(s['id']) for s in sessions[:5]), limit * 2))

            messages = cursor.fetchall()

            if messages:
                print(f"\n  消息 (最近{len(messages)}条):")
                print(f"  {'会话ID':<10} {'角色':<10} {'内容':<50} {'时间'}")
                print("  " + "-"*80)

                for msg in messages:
                    content = msg['content'][:47] + "..." if len(str(msg['content'])) > 47 else msg['content']
                    print(f"  {msg['session_id']:<10} {msg['role']:<10} {content:<50} "
                          f"{msg['created_at'][:19] if msg['created_at'] else 'N/A'}")

        conn.close()

    def show_user_profile(self, user_id: int = None):
        """显示用户画像"""
        print(f"\n{'='*60}")
        print("  用户画像 (user_profiles)")
        print(f"{'='*60}\n")

        conn = self._get_connection()
        cursor = conn.cursor()

        if user_id:
            cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
        else:
            cursor.execute("SELECT * FROM user_profiles LIMIT 5")

        rows = cursor.fetchall()

        if not rows:
            print("  暂无数据")
            conn.close()
            return

        for row in rows:
            print(f"用户ID: {row['user_id']}")
            print(f"目标: {row.get('goal', 'N/A')}")
            print(f"训练方法: {row.get('preferred_method', 'N/A')}")
            print(f"每周训练天数: {row.get('weekly_days', 'N/A')}")
            print(f"每日时长(分钟): {row.get('daily_duration', 'N/A')}")
            print(f"强度级别: {row.get('intensity_level', 'N/A')}")
            print(f"伤病状态: {row.get('injury_status', 'N/A')}")
            print(f"健身水平: {row.get('fitness_level', 'N/A')}")
            print(f"更新时间: {row.get('updated_at', 'N/A')}")
            print()

        conn.close()

    def show_training_plans(self, user_id: int = None, limit: int = 5):
        """显示训练计划"""
        print(f"\n{'='*60}")
        print("  训练计划 (training_plans)")
        print(f"{'='*60}\n")

        conn = self._get_connection()
        cursor = conn.cursor()

        if user_id:
            cursor.execute("""
                SELECT * FROM training_plans
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM training_plans
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()

        if not rows:
            print("  暂无数据")
            conn.close()
            return

        print(f"{'ID':<6} {'用户ID':<8} {'标题':<25} {'目标':<15} {'基于记忆':<10} {'创建时间'}")
        print("-"*90)

        for row in rows:
            title = row['title'][:23] + "..." if len(str(row['title'])) > 23 else row['title']
            print(f"{row['id']:<6} {row['user_id']:<8} {title:<25} "
                  f"{str(row['goal'])[:15]:<15} {'是' if row['based_on_memory'] else '否':<10} "
                  f"{row['created_at'][:19] if row['created_at'] else 'N/A'}")

        conn.close()

    def show_training_records(self, user_id: int = None, limit: int = 10):
        """显示训练记录"""
        print(f"\n{'='*60}")
        print("  训练记录 (training_records)")
        print(f"{'='*60}\n")

        conn = self._get_connection()
        cursor = conn.cursor()

        if user_id:
            cursor.execute("""
                SELECT id, user_id, date, training_type, duration, fatigue_level,
                       pain_level, completion_status, notes
                FROM training_records
                WHERE user_id = ?
                ORDER BY date DESC
                LIMIT ?
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT id, user_id, date, training_type, duration, fatigue_level,
                       pain_level, completion_status, notes
                FROM training_records
                ORDER BY date DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()

        if not rows:
            print("  暂无数据")
            conn.close()
            return

        print(f"{'ID':<6} {'用户ID':<8} {'日期':<12} {'类型':<15} {'时长':<6} {'疲劳':<6} {'疼痛':<6} {'状态':<10}")
        print("-"*80)

        for row in rows:
            print(f"{row['id']:<6} {row['user_id']:<8} {row['date']:<12} "
                  f"{str(row['training_type'])[:15]:<15} {row['duration'] or 0:<6} "
                  f"{row['fatigue_level'] or '-':<6} {row['pain_level'] or '-':<6} "
                  f"{(row['completion_status'] or '')[:10]:<10}")

        conn.close()

    def show_user_info(self):
        """显示用户信息"""
        print(f"\n{'='*60}")
        print("  用户列表 (users)")
        print(f"{'='*60}\n")

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, username, email, is_first_login, profile_completed FROM users")
        rows = cursor.fetchall()

        print(f"{'ID':<6} {'用户名':<20} {'邮箱':<30} {'首次登录':<10} {'画像完成':<10}")
        print("-"*80)

        for row in rows:
            print(f"{row['id']:<6} {row['username']:<20} {row['email']:<30} "
                  f"{'是' if row['is_first_login'] else '否':<10} "
                  f"{'是' if row['profile_completed'] else '否':<10}")

        conn.close()

    def export_user_memory(self, user_id: int, output_file: str = None):
        """导出用户所有记忆数据到JSON"""
        conn = self._get_connection()
        cursor = conn.cursor()

        data = {
            "user_id": user_id,
            "export_time": str(datetime.now()),
            "user_profile": None,
            "semantic_memory": [],
            "episodic_memory": [],
            "training_plans": [],
            "training_records": []
        }

        # 用户画像
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
        profile = cursor.fetchone()
        if profile:
            data["user_profile"] = dict(profile)

        # 语义记忆
        cursor.execute("""
            SELECT * FROM memory_semantic_facts
            WHERE user_id = ? AND is_active = 1
            ORDER BY updated_at DESC
        """, (user_id,))
        data["semantic_memory"] = [dict(row) for row in cursor.fetchall()]

        # 情景记忆
        cursor.execute("""
            SELECT * FROM memory_episodic_events
            WHERE user_id = ?
            ORDER BY event_time DESC
        """, (user_id,))
        data["episodic_memory"] = [dict(row) for row in cursor.fetchall()]

        # 训练计划
        cursor.execute("""
            SELECT * FROM training_plans
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        data["training_plans"] = [dict(row) for row in cursor.fetchall()]

        # 训练记录
        cursor.execute("""
            SELECT * FROM training_records
            WHERE user_id = ?
            ORDER BY date DESC
        """, (user_id,))
        data["training_records"] = [dict(row) for row in cursor.fetchall()]

        conn.close()

        # 输出
        if output_file is None:
            output_file = f"memory_export_user_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        print(f"\n✅ 导出完成: {output_file}")
        print(f"   - 用户画像: {'有' if data['user_profile'] else '无'}")
        print(f"   - 语义记忆: {len(data['semantic_memory'])} 条")
        print(f"   - 情景记忆: {len(data['episodic_memory'])} 条")
        print(f"   - 训练计划: {len(data['training_plans'])} 个")
        print(f"   - 训练记录: {len(data['training_records'])} 条")


def main():
    parser = argparse.ArgumentParser(description='记忆数据库检查工具')
    parser.add_argument('--db', help='数据库文件路径')
    parser.add_argument('--user', type=int, help='用户ID')
    parser.add_argument('--tables', action='store_true', help='显示所有表概览')
    parser.add_argument('--schema', help='显示指定表的结构')
    parser.add_argument('--semantic', action='store_true', help='显示语义记忆')
    parser.add_argument('--episodic', action='store_true', help='显示情景记忆')
    parser.add_argument('--working', action='store_true', help='显示工作记忆')
    parser.add_argument('--profile', action='store_true', help='显示用户画像')
    parser.add_argument('--plans', action='store_true', help='显示训练计划')
    parser.add_argument('--records', action='store_true', help='显示训练记录')
    parser.add_argument('--users', action='store_true', help='显示用户列表')
    parser.add_argument('--export', type=int, metavar='USER_ID', help='导出用户记忆数据到JSON')
    parser.add_argument('--limit', type=int, default=10, help='显示记录数量限制')

    args = parser.parse_args()

    checker = MemoryDBChecker(args.db)

    # 默认显示所有表
    if not any([args.schema, args.semantic, args.episodic, args.working,
                args.profile, args.plans, args.records, args.users, args.export]):
        checker.show_all_tables()
        print("\n提示: 使用 --user <id> 查看指定用户的数据")
        return

    # 处理各选项
    if args.schema:
        checker.show_table_schema(args.schema)

    if args.semantic:
        checker.show_semantic_memory(args.user, args.limit)

    if args.episodic:
        checker.show_episodic_memory(args.user, args.limit)

    if args.working:
        checker.show_working_memory(args.user, args.limit)

    if args.profile:
        checker.show_user_profile(args.user)

    if args.plans:
        checker.show_training_plans(args.user, args.limit)

    if args.records:
        checker.show_training_records(args.user, args.limit)

    if args.users:
        checker.show_user_info()

    if args.export:
        checker.export_user_memory(args.export)


if __name__ == "__main__":
    from datetime import datetime
    main()
