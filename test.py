import random
import time
from collections import defaultdict


def generate_chars(loop_count):
    # 基础字符和初始权重（权重递减：a最高，f初始0）
    chars = ['a', 'b', 'c', 'd', 'e', 'f']
    base_weights = [5, 4, 3, 2, 1, 0]

    # 前10回合只出现a
    if loop_count < 10:
        return ['a']

    # 计算当前解锁的字符
    unlocked_count = min(6, 1 + loop_count // 10)
    unlocked_chars = chars[:unlocked_count]

    # 计算字符f的出现概率
    f_prob = 0
    if 'f' in unlocked_chars and loop_count >= 50:
        # 从第50回合开始增长，每回合增加0.1%，上限40%
        f_prob = min(0.2, 0.001 * (loop_count - 50))

    # 确定本次生成的字符数量
    char_count = random.randint(1, 3)

    # 当需要生成多个字符时，排除f（因为f只能单独出现）
    if char_count > 1:
        # 从解锁字符中移除f
        available_chars = [c for c in unlocked_chars if c != 'f']
        # 构建权重列表（排除f）
        weights = [base_weights[chars.index(c)] for c in available_chars]
        return random.choices(available_chars, weights=weights, k=char_count)

    # 处理只生成一个字符的情况（可能包含f）
    # 计算非f字符的总权重
    non_f_chars = [c for c in unlocked_chars if c != 'f']
    total_base = sum(base_weights[chars.index(c)] for c in non_f_chars) or 1

    # 构建权重列表（包含f概率）
    weights = []
    for c in unlocked_chars:
        if c == 'f':
            weights.append(f_prob)
        else:
            # 非f字符的权重按比例压缩
            char_weight = base_weights[chars.index(c)]
            weights.append(char_weight * (1 - f_prob) / total_base)
    print(f'weights==>{weights}')
    # 随机选择一个字符
    return random.choices(unlocked_chars, weights=weights, k=1)


# 统计各字符出现次数
char_counts = defaultdict(int)
total_chars = 0
f_occurrences = 0

try:
    for loop_count in range(200):  # 模拟200回合
        # 生成字符
        chars = generate_chars(loop_count)

        # 更新统计
        for char in chars:
            char_counts[char] += 1
            total_chars += 1
            if char == 'f':
                f_occurrences += 1

        # 打印当前结果
        print(f"回合 {loop_count:>3}: {chars}  ", end="")

        # 每10回合打印解锁状态
        if loop_count % 10 == 9 or loop_count == 0:
            unlocked_count = min(6, 1 + loop_count // 10)
            unlocked_chars = "".join(chars[:unlocked_count])
            print(f"  解锁: {unlocked_chars}")
        else:
            print()

        time.sleep(0.1)  # 控制输出速度

    # 打印统计信息
    print("\n===== 统计信息 =====")
    for char in "abcdef":
        count = char_counts[char]
        if total_chars:
            percent = 100 * count / total_chars
            print(f"{char}: {count}次 ({percent:.1f}%)", end=" | ")

    if f_occurrences:
        print(f"\n字符f出现时单独出现的概率: {100 * char_counts['f'] / f_occurrences:.0f}%")
except KeyboardInterrupt:
    print("\n程序已中断")
