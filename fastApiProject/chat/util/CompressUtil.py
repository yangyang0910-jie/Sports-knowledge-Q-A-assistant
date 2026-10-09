import tiktoken
from chat.util import CompressModelUtil
from chat.dao import CompressDao
from users.util import RedisUtil

THRESHOLD = 3000      # 总Token阈值，超过此值才触发压缩
KEEP_TOKENS = 2000    # 动态保留预算：始终保留最近约2000 tokens的消息不压缩


def compress_history(session_id):
    """
    检查并压缩历史记录（在对话保存入库之后调用）。
    session_id = 会话ID（即会话第一行的 dialogue_id，后续行 current_id 指向它）。
    消息来源：数据库中 is_compressed=0 的未压缩消息。
    """
    # 防护：新对话（0）或非法id绝不压缩，防止污染compress表
    if not session_id or int(session_id) <= 0:
        return None

    session_id = int(session_id)

    # 1. 从数据库取未压缩消息（自带 is_compressed=0 过滤，且含会话第一行）
    db_messages = CompressDao.get_uncompressed_messages_dao(session_id)
    if not db_messages:
        return None   # 全部已压缩，无事可做

    # 2. 组装成 history：一行记录展开为 user + assistant 两条（answer 不丢失）
    history = []
    for m in db_messages:
        if m['question']:
            history.append({
                "role": "user",
                "content": m['question'],
                "round_number": int(m['round_number']) if m['round_number'] else 0,
            })
        if m['answer']:
            history.append({
                "role": "assistant",
                "content": m['answer'],
                "round_number": int(m['round_number']) if m['round_number'] else 0,
            })

    if not history:
        return None

    # 3. 计算总Token
    try:
        enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")   # 网络拉取失败时的兜底

    total_tokens = sum(len(enc.encode(msg['content'])) for msg in history)

    print(f"【压缩观测】会话{session_id} | 待处理消息数: {len(history)} | Token数: {total_tokens}")

    if total_tokens <= THRESHOLD:
        return None

    print(f">>> 触发压缩机制 (>{THRESHOLD} tokens)")

    # 4. 获取锁，防止并发重复压缩
    redis = RedisUtil.get_redis_conn()
    lock_key = f"lock:compress:{session_id}"
    if not redis.set(lock_key, "1", nx=True, ex=60):
        print("当前会话正在压缩中，跳过本次触发")
        return None

    try:
        # 5. 动态保留边界：从最新往前累计，保留约 KEEP_TOKENS 不压缩
        keep_from_index = len(history)
        accumulated_tokens = 0

        for i in range(len(history) - 1, -1, -1):
            msg_tokens = len(enc.encode(history[i]['content']))
            if accumulated_tokens + msg_tokens > KEEP_TOKENS:
                break
            accumulated_tokens += msg_tokens
            keep_from_index = i

        messages_to_compress = history[:keep_from_index]#压缩区

        if not messages_to_compress:
            print(f"扣除保留消息(约{accumulated_tokens} tokens)后无内容可压缩")
            return None

        # 6. 压缩边界 = 被压缩部分最后一轮，必须有效（round 为 NULL 的旧数据不会进来）
        lastround = messages_to_compress[-1].get('round_number') or 0
        if lastround <= 0:
            print("无法确定压缩边界(lastround)，放弃本次压缩")
            return None

        # 7. 读取老摘要进行增量更新
        old_summary = CompressDao.get_summary_from_db(session_id)
        if not old_summary:
            old_summary = "暂无历史摘要"

        new_messages_text = "\n".join(
            f"{m['role']}: {m['content']}" for m in messages_to_compress
        )

        prompt = (
            "你是一个对话记录管理员。请根据提供的[历史摘要]和[新增对话]，生成一份更新后的、简洁的[全量摘要]。\n\n"
            "要求：\n"
            "1. 必须保留[历史摘要]中的关键背景信息。\n"
            "2. 将[新增对话]中的新信息融入摘要中。\n"
            "3. 去除寒暄和无关细节，保持精简。\n\n"
            f"【历史摘要】：\n{old_summary}\n\n"
            f"【新增对话】：\n{new_messages_text}\n\n"
            "请输出更新后的全量摘要："
        )

        # 8. 调用模型生成新摘要
        llm = CompressModelUtil.Compress_Model()
        digest = llm.invoke(prompt)
        new_summary = digest.content if hasattr(digest, 'content') else str(digest)

        if not new_summary or not new_summary.strip():
            print("压缩模型返回了空摘要，放弃本次压缩")
            return None

        # 9. 先存摘要，成功才标记（防止摘要丢了但消息被标记已压缩）
        if CompressDao.compress_save_dao(new_summary, session_id, lastround) != 200:
            print("摘要保存失败，本次压缩作废，不标记 is_compressed")
            return None
        CompressDao.compress_dao(lastround, session_id)

        print(f"会话 {session_id} 压缩完成。摘要长度: {len(new_summary)}字符, 覆盖至第{lastround}轮")
        return new_summary

    except Exception as e:
        print(f"压缩失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        redis.delete(lock_key)
