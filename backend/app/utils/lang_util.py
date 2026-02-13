# -*- coding: utf-8 -*-
"""语言检测工具"""

import re
from typing import Literal


def judge_language(text: str) -> Literal["chinese", "english", "mixed", "unknown"]:
    """
    判断文本的主要语言类型
    
    Args:
        text: 待检测的文本
        
    Returns:
        - "chinese": 主要是中文（中文字符占比 >= 30%）
        - "english": 主要是英文（英文字符占比 >= 50% 且中文占比 < 10%）
        - "mixed": 中英混合
        - "unknown": 无法判断（文本过短或无有效字符）
    """
    if not text or not isinstance(text, str):
        return "unknown"
    
    # 移除空白字符和标点符号，只保留有效字符
    text = text.strip()
    if not text:
        return "unknown"
    
    # 统计各类字符
    chinese_count = 0
    english_count = 0
    total_valid = 0
    
    for char in text:
        # 中文字符范围（基本汉字）
        if '\u4e00' <= char <= '\u9fff':
            chinese_count += 1
            total_valid += 1
        # 英文字母
        elif char.isalpha() and char.isascii():
            english_count += 1
            total_valid += 1
        # 数字也算有效字符
        elif char.isdigit():
            total_valid += 1
    
    if total_valid == 0:
        return "unknown"
    
    chinese_ratio = chinese_count / total_valid
    english_ratio = english_count / total_valid
    
    # 判断逻辑
    if chinese_ratio >= 0.3:
        return "chinese"
    elif english_ratio >= 0.5 and chinese_ratio < 0.1:
        return "english"
    elif chinese_count > 0 and english_count > 0:
        return "mixed"
    elif english_ratio >= 0.3:
        return "english"
    else:
        return "unknown"
