#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import json

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

import mtts

def test_cache_rule_matcher():
    """测试缓存规则匹配器"""

    # 获取 cache_rules.json 的路径
    base_dir = os.path.dirname(__file__)
    rules_path = os.path.join(base_dir, "..", "Submods", "MAICA_MTTSubmod", "cache_rules.json")

    print("Rules path: {}".format(rules_path))
    print("Rules file exists: {}".format(os.path.exists(rules_path)))

    if not os.path.exists(rules_path):
        print("ERROR: cache_rules.json not found!")
        return False

    # 创建规则匹配器
    matcher = mtts.RuleMatcher(rules_path)

    print("\n=== 规则加载测试 ===")
    print("加载的规则数: {}".format(len(matcher.rules)))
    print("默认action: {}".format(matcher.default_action))

    # 测试用例
    test_cases = [
        {
            "text": "不过跟[player]打肯定不一样吧",
            "label": "test_label",
            "expected_rule": "regex_text",
            "description": "测试包含方括号的字符串"
        },
        {
            "text": "这是一个普通字符串",
            "label": "maica_talking",
            "expected_rule": "regex_label",
            "description": "测试完全匹配 maica_talking 标签"
        },
        {
            "text": "短",
            "label": "test_label",
            "expected_rule": "default",
            "description": "测试文本过短（少于3个非符号字符）"
        },
        {
            "text": "这是一个普通字符串",
            "label": "other_label",
            "expected_rule": "default",
            "description": "测试不匹配任何规则，使用默认action"
        }
    ]

    print("\n=== 规则匹配测试 ===")
    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        text = test_case["text"]
        label = test_case["label"]
        description = test_case["description"]
        expected = test_case["expected_rule"]

        rule = matcher.match_cache_rule(text, label)
        action = matcher.get_action(text, label)

        # 计算非符号字符数
        content_chars = matcher._count_content_chars(text)

        print("\n测试 {}: {}".format(i, description))
        print("  文本: '{}'".format(text))
        print("  标签: '{}'".format(label))
        print("  非符号字符数: {}".format(content_chars))
        print("  匹配规则: {}".format(rule))
        print("  Action: {}".format(action))

        # 验证结果
        if expected == "regex_text":
            if rule.get('regex_text') and not rule.get('is_default'):
                print("  ✓ 通过: 成功匹配 regex_text 规则")
            else:
                print("  ✗ 失败: 应该匹配 regex_text 规则")
                all_passed = False
        elif expected == "regex_label":
            if rule.get('regex_label') and not rule.get('is_default'):
                print("  ✓ 通过: 成功匹配 regex_label 规则")
            else:
                print("  ✗ 失败: 应该匹配 regex_label 规则")
                all_passed = False
        elif expected == "default":
            if rule.get('is_default'):
                print("  ✓ 通过: 使用默认 action")
            else:
                print("  ✗ 失败: 应该使用默认 action")
                all_passed = False

    print("\n=== 字符串替换规则测试 ===")
    print("加载的替换规则数: {}".format(len(matcher.replace_rules)))

    # 测试替换规则
    replace_test_cases = [
        {
            "text": "I love you <3",
            "expected": "I love you ",
            "description": "测试 <3 替换为空"
        },
        {
            "text": "Multiple <3 <3 hearts",
            "expected": "Multiple   hearts",
            "description": "测试多个 <3 替换"
        },
        {
            "text": "No special chars here",
            "expected": "No special chars here",
            "description": "测试无替换的文本"
        }
    ]

    for i, test_case in enumerate(replace_test_cases, 1):
        text = test_case["text"]
        expected = test_case["expected"]
        description = test_case["description"]

        result = matcher.apply_replace_rules(text)

        print("\n替换测试 {}: {}".format(i, description))
        print("  原文本: '{}'".format(text))
        print("  期望结果: '{}'".format(expected))
        print("  实际结果: '{}'".format(result))

        if result == expected:
            print("  ✓ 通过")
        else:
            print("  ✗ 失败")
            all_passed = False

    print("\n=== 测试总结 ===")
    if all_passed:
        print("✓ 所有测试通过!")
        return True
    else:
        print("✗ 部分测试失败")
        return False

if __name__ == "__main__":
    success = test_cache_rule_matcher()
    sys.exit(0 if success else 1)
