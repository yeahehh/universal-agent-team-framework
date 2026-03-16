"""
插件系统测试脚本

测试所有插件的创建、初始化、执行功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_base_plugin():
    """测试插件基类"""
    print("=" * 60)
    print("测试插件基类")
    print("=" * 60)
    
    from plugins.base_plugin import PluginStatus, PluginType, PluginContext, BasePlugin
    
    # 测试枚举
    assert PluginStatus.ACTIVE.value == "active"
    assert PluginType.DATA.value == "data"
    print("✓ 枚举测试通过")
    
    # 测试上下文
    context = PluginContext(
        task_id="test-123",
        agent_id="agent-456",
        input_data={"key": "value"}
    )
    assert context.task_id == "test-123"
    assert context.plugin_id is not None
    print("✓ PluginContext 测试通过")
    
    print("✅ 插件基类测试通过\n")

def test_data_plugins():
    """测试数据类插件"""
    print("=" * 60)
    print("测试数据类插件")
    print("=" * 60)
    
    from plugins.data_plugins import DatabasePlugin, FilePlugin, ApiPlugin
    from plugins.base_plugin import PluginContext
    
    # 测试 FilePlugin
    file_plugin = FilePlugin("TestFile", {"base_dir": ".", "encoding": "utf-8"})
    assert file_plugin.plugin_name == "TestFile"
    assert file_plugin.plugin_type.value == "data"
    print("✓ FilePlugin 创建成功")
    
    # 测试 ApiPlugin
    api_plugin = ApiPlugin("TestApi", {"base_url": "https://api.example.com", "timeout": 30})
    assert api_plugin.base_url == "https://api.example.com"
    print("✓ ApiPlugin 创建成功")
    
    print("✅ 数据类插件测试通过\n")

def test_llm_plugins():
    """测试 LLM 类插件"""
    print("=" * 60)
    print("测试 LLM 类插件")
    print("=" * 60)
    
    from plugins.llm_plugins import ChatPlugin, EmbeddingPlugin
    
    # 测试 ChatPlugin（不初始化 API）
    chat_plugin = ChatPlugin("TestChat", {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7
    })
    assert chat_plugin.model == "gpt-3.5-turbo"
    print("✓ ChatPlugin 创建成功")
    
    # 测试 EmbeddingPlugin
    embedding_plugin = EmbeddingPlugin("TestEmbed", {
        "embedding_model": "text-embedding-ada-002"
    })
    assert embedding_plugin.embedding_model == "text-embedding-ada-002"
    print("✓ EmbeddingPlugin 创建成功")
    
    print("✅ LLM 类插件测试通过\n")

def test_tool_plugins():
    """测试工具类插件"""
    print("=" * 60)
    print("测试工具类插件")
    print("=" * 60)
    
    from plugins.tool_plugins import SearchPlugin, CalculatorPlugin, CodePlugin
    from plugins.base_plugin import PluginContext
    
    # 测试 CalculatorPlugin
    calc_plugin = CalculatorPlugin("TestCalc")
    calc_plugin.initialize()
    
    context = PluginContext(input_data={"expression": "1 + 2 * 3"})
    result = calc_plugin.execute_with_context(context)
    assert result == 7
    print("✓ CalculatorPlugin 计算正确：1 + 2 * 3 = 7")
    
    # 测试 CodePlugin
    code_plugin = CodePlugin("TestCode", {"timeout": 5, "max_output": 1000})
    code_plugin.initialize()
    
    context = PluginContext(input_data={
        "code": "result = 10 + 20",
        "globals": {},
        "locals": {}
    })
    result = code_plugin.execute_with_context(context)
    assert result["success"] == True
    print("✓ CodePlugin 执行成功")
    
    print("✅ 工具类插件测试通过\n")

def test_custom_plugins():
    """测试自定义插件"""
    print("=" * 60)
    print("测试自定义插件")
    print("=" * 60)
    
    from plugins.custom_plugins import ExamplePlugin
    from plugins.base_plugin import PluginContext
    
    example_plugin = ExamplePlugin("TestExample", {"custom_param": "test_value"})
    example_plugin.initialize()
    
    context = PluginContext(input_data={
        "action": "process",
        "data": {"key": "value"}
    })
    result = example_plugin.execute_with_context(context)
    assert result["status"] == "success"
    print("✓ ExamplePlugin 执行成功")
    
    print("✅ 自定义插件测试通过\n")

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始插件系统测试")
    print("=" * 60 + "\n")
    
    try:
        test_base_plugin()
        test_data_plugins()
        test_llm_plugins()
        test_tool_plugins()
        test_custom_plugins()
        
        print("=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        return True
    except Exception as e:
        print("=" * 60)
        print(f"❌ 测试失败：{str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)