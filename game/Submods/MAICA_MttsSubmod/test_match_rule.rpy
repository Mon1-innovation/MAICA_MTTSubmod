label test_match_rule:

    python:
        # 获取匹配器
        matcher = store.mtts.matcher

        # 测试用例定义
        test_cases = [
            {
                "text": "不过跟[player]打肯定不一样吧",
                "label": "test_label",
                "expected_rule": "regex_text",
                "description": "测试包含方括号的字符串（匹配regex_text）"
            },
            {
                "text": "这是一个普通字符串",
                "label": "maica_talking",
                "expected_rule": "regex_label",
                "description": "测试完全匹配 maica_talking 标签（匹配regex_label）"
            },
            {
                "text": "短",
                "label": "test_label",
                "expected_rule": "default",
                "description": "测试文本过短（少于3个非符号字符，使用默认action）"
            },
            {
                "text": "这是一个普通字符串",
                "label": "other_label",
                "expected_rule": "general_text",
                "description": "测试不匹配特定规则，匹配General text规则"
            },
            {
                "text": "Hello world 123",
                "label": "any_label",
                "expected_rule": "general_text",
                "description": "测试英文和数字文本"
            }
        ]

        all_passed = True
        test_results = []

        for i, test_case in enumerate(test_cases, 1):
            text = test_case["text"]
            label = test_case["label"]
            description = test_case["description"]
            expected = test_case["expected_rule"]

            rule = matcher.match_rule(text, label)
            content_chars = matcher._count_content_chars(text)

            # 对方括号进行转义，避免Ren'Py解析
            escaped_text = text.replace('[', '(').replace(']', ')')
            escaped_label = label.replace('[', '(').replace(']', ')')
            escaped_action = str(rule.get('action', [])).replace('[', '(').replace(']', ')')

            result_text = "测试 {}: {}\n".format(i, description)
            result_text += "  文本: '{}'\n".format(escaped_text)
            result_text += "  标签: '{}'\n".format(escaped_label)
            result_text += "  非符号字符数: {}\n".format(content_chars)
            result_text += "  匹配规则名称: {}\n".format(rule.get('name', 'N/A'))
            result_text += "  Action: {}\n".format(escaped_action)
            result_text += "  是否默认规则: {}".format(rule.get('is_default', False))

            # 验证结果
            passed = False
            if expected == "regex_text":
                if rule.get('regex_text') and not rule.get('is_default'):
                    result_text += "\n  ✓ 通过: 成功匹配 regex_text 规则"
                    passed = True
                else:
                    result_text += "\n  ✗ 失败: 应该匹配 regex_text 规则"
            elif expected == "regex_label":
                if rule.get('regex_label') and not rule.get('is_default'):
                    result_text += "\n  ✓ 通过: 成功匹配 regex_label 规则"
                    passed = True
                else:
                    result_text += "\n  ✗ 失败: 应该匹配 regex_label 规则"
            elif expected == "general_text":
                if rule.get('name') == 'General text' and not rule.get('is_default'):
                    result_text += "\n  ✓ 通过: 成功匹配 General text 规则"
                    passed = True
                else:
                    result_text += "\n  ✗ 失败: 应该匹配 General text 规则"
            elif expected == "default":
                if rule.get('is_default'):
                    result_text += "\n  ✓ 通过: 使用默认 action"
                    passed = True
                else:
                    result_text += "\n  ✗ 失败: 应该使用默认 action"

            test_results.append(result_text)
            if not passed:
                all_passed = False

    $ test_output = "\n\n".join(test_results)

    $ renpy.say(m, "=== store.mtts.matcher.match_rule 测试 ===\n\n加载的规则数: {}\n默认action: {}\n\n=== 规则匹配测试 ===\n\n{}".format(len(matcher.rules), matcher.default_action, test_output))

    python:
        if all_passed:
            final_msg = "\n\n=== 测试总结 ===\n✓ 所有测试通过!"
        else:
            final_msg = "\n\n=== 测试总结 ===\n✗ 部分测试失败"

    m "[final_msg]"

    return
