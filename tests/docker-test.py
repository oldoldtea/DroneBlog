#!/usr/bin/env python3
"""Docker 容器内 MCP Server 测试脚本"""

import asyncio
import json
import sys

sys.path.insert(0, '/app/droneblog_mcp/src')

from droneblog_mcp.server import create_server

async def run_tests():
    print("=" * 60)
    print("DroneBlog MCP Server - Docker 容器内测试")
    print("=" * 60)
    
    mcp = create_server()
    passed = 0
    failed = 0
    
    # 测试 1: 工具列表
    print("\n[1/8] 工具列表...")
    try:
        tools = await mcp.list_tools()
        tool_names = [t.name for t in tools]
        expected = ['blog_generate', 'blog_list', 'blog_read', 'blog_edit', 
                   'blog_delete', 'config_get', 'config_set', 'build', 
                   'deploy', 'pipeline_status', 'pipeline_run']
        missing = [t for t in expected if t not in tool_names]
        if missing:
            print(f"  ✗ 缺少工具: {missing}")
            failed += 1
        else:
            print(f"  ✓ 所有 {len(expected)} 个工具已注册")
            passed += 1
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        failed += 1
    
    # 测试 2: blog_list
    print("\n[2/8] blog_list...")
    try:
        result = await mcp.call_tool('blog_list', {'limit': 3})
        posts = [json.loads(item.text) for item in result[0]]
        print(f"  ✓ 返回 {len(posts)} 篇文章")
        for post in posts:
            print(f"    - {post['title'][:40]}...")
        passed += 1
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        failed += 1
    
    # 测试 3: blog_read
    print("\n[3/8] blog_read...")
    try:
        result = await mcp.call_tool('blog_read', {'slug': 'tokio-async-runtime'})
        data = json.loads(result[0].text)
        if data['status'] == 'success':
            print(f"  ✓ 读取成功: {data['post']['title']}")
            passed += 1
        else:
            print(f"  ✗ 读取失败: {data['message']}")
            failed += 1
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        failed += 1
    
    # 测试 4: config_get
    print("\n[4/8] config_get...")
    try:
        result = await mcp.call_tool('config_get', {'scope': 'site'})
        data = json.loads(result[0].text)
        if data['status'] == 'success':
            print(f"  ✓ 配置读取成功: {data['config']['title']}")
            passed += 1
        else:
            print(f"  ✗ 配置读取失败")
            failed += 1
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        failed += 1
    
    # 测试 5: build
    print("\n[5/8] build...")
    try:
        result = await mcp.call_tool('build', {})
        data = json.loads(result[0].text)
        if data['status'] == 'success':
            print(f"  ✓ 构建成功: {data['message']}")
            passed += 1
        else:
            print(f"  ✗ 构建失败: {data['message']}")
            failed += 1
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        failed += 1
    
    # 测试 6: pipeline_status
    print("\n[6/8] pipeline_status...")
    try:
        result = await mcp.call_tool('pipeline_status', {})
        data = json.loads(result[0].text)
        if data['status'] == 'success':
            print(f"  ✓ 流水线状态: {len(data['stages'])} 个阶段")
            passed += 1
        else:
            print(f"  ✗ 状态查询失败")
            failed += 1
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        failed += 1
    
    # 测试 7: Resources
    print("\n[7/8] Resources...")
    try:
        result = await mcp.read_resource('blog://list')
        content = result[0].content
        if len(content) > 100:
            print(f"  ✓ blog://list 资源可读 ({len(content)} 字符)")
            passed += 1
        else:
            print(f"  ✗ 资源内容太短")
            failed += 1
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        failed += 1
    
    # 测试 8: Prompts
    print("\n[8/8] Prompts...")
    try:
        result = await mcp.get_prompt('blog_writing')
        if result.messages and len(result.messages[0].content.text) > 100:
            print(f"  ✓ blog_writing Prompt 可用")
            passed += 1
        else:
            print(f"  ✗ Prompt 内容太短")
            failed += 1
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        failed += 1
    
    # 总结
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0

if __name__ == '__main__':
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
