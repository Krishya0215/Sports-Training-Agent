"""
多模态功能环境检查脚本
检查所有必要的依赖和配置是否正确
"""
import os
import sys
from pathlib import Path


def check_dependencies():
    """检查Python依赖"""
    print("\n" + "="*60)
    print("检查Python依赖")
    print("="*60)
    
    required_packages = {
        "dashscope": "阿里云DashScope SDK",
        "fitz": "PyMuPDF (图像提取)",
        "PIL": "Pillow (图像处理)",
        "markitdown": "MarkItDown (PDF转换)",
        "langchain": "LangChain核心库",
        "chromadb": "ChromaDB向量数据库"
    }
    
    missing = []
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {package:15s} - {description}")
        except ImportError:
            print(f"❌ {package:15s} - {description} (未安装)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  缺少 {len(missing)} 个依赖包")
        print("请运行: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ 所有依赖已安装")
        return True


def check_api_key():
    """检查API密钥配置"""
    print("\n" + "="*60)
    print("检查API密钥")
    print("="*60)
    
    env_file = Path("model/.env")
    
    if not env_file.exists():
        print(f"❌ 环境变量文件不存在: {env_file}")
        print("请创建 model/.env 文件并添加:")
        print("DASHSCOPE_API_KEY=your_api_key_here")
        return False
    
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    api_key = os.getenv("DASHSCOPE_API_KEY")
    
    if not api_key:
        print("❌ DASHSCOPE_API_KEY 未设置")
        return False
    
    if api_key.startswith("sk-") and len(api_key) > 20:
        print(f"✅ API密钥已配置: {api_key[:10]}...{api_key[-5:]}")
        return True
    else:
        print("⚠️  API密钥格式可能不正确")
        return False


def check_configuration():
    """检查配置文件"""
    print("\n" + "="*60)
    print("检查配置文件")
    print("="*60)
    
    config_files = {
        "config/chroma.yml": "ChromaDB配置",
        "config/agent.yml": "Agent配置",
        "config/rag.yml": "RAG配置"
    }
    
    all_ok = True
    for file_path, description in config_files.items():
        if Path(file_path).exists():
            print(f"✅ {file_path:25s} - {description}")
        else:
            print(f"❌ {file_path:25s} - {description} (不存在)")
            all_ok = False
    
    # 检查多模态配置
    try:
        import yaml
        with open("config/chroma.yml", "r", encoding="utf-8") as f:
            chroma_config = yaml.safe_load(f)
        
        doc_processing = chroma_config.get("document_processing", {})
        
        print("\n多模态配置:")
        print(f"  use_markitdown: {doc_processing.get('use_markitdown', False)}")
        print(f"  extract_images: {doc_processing.get('extract_images', False)}")
        print(f"  image_description_enabled: {doc_processing.get('image_description_enabled', False)}")
        
        if doc_processing.get("image_description_enabled"):
            print("✅ 多模态功能已启用")
        else:
            print("⚠️  多模态功能未启用")
            print("请在 config/chroma.yml 中设置 image_description_enabled: true")
    
    except Exception as e:
        print(f"❌ 读取配置失败: {e}")
        all_ok = False
    
    return all_ok


def check_directories():
    """检查必要的目录"""
    print("\n" + "="*60)
    print("检查目录结构")
    print("="*60)
    
    required_dirs = [
        "data",
        "data/extracted_images",
        "rag/chroma_db",
        "logs",
        "model",
        "memory"
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"⚠️  {dir_path} (不存在，将自动创建)")
            path.mkdir(parents=True, exist_ok=True)
    
    return True


def test_multimodal_model():
    """测试多模态模型连接"""
    print("\n" + "="*60)
    print("测试多模态模型")
    print("="*60)
    
    try:
        from model.multimodal_model import multimodal_llm
        print("✅ 多模态模型模块加载成功")
        
        # 检查是否有测试图像
        test_images = list(Path("data/extracted_images").rglob("*.jpg")) + \
                      list(Path("data/extracted_images").rglob("*.png"))
        
        if test_images:
            print(f"✅ 找到 {len(test_images)} 张测试图像")
            print("\n可以运行以下命令测试:")
            print("python test_multimodal.py")
        else:
            print("⚠️  未找到测试图像")
            print("请先处理PDF文档以提取图像")
        
        return True
        
    except Exception as e:
        print(f"❌ 多模态模型测试失败: {e}")
        return False


def check_pdf_files():
    """检查PDF文件"""
    print("\n" + "="*60)
    print("检查PDF文件")
    print("="*60)
    
    pdf_files = list(Path("data").glob("*.pdf"))
    
    if pdf_files:
        print(f"✅ 找到 {len(pdf_files)} 个PDF文件:")
        for pdf in pdf_files:
            size_mb = pdf.stat().st_size / (1024 * 1024)
            print(f"   - {pdf.name} ({size_mb:.2f} MB)")
        return True
    else:
        print("⚠️  未找到PDF文件")
        print("请将PDF文件放入 data/ 目录")
        return False


def main():
    """运行所有检查"""
    print("\n" + "="*70)
    print("多模态功能环境检查")
    print("="*70)
    
    checks = [
        ("Python依赖", check_dependencies),
        ("API密钥", check_api_key),
        ("配置文件", check_configuration),
        ("目录结构", check_directories),
        ("PDF文件", check_pdf_files),
        ("多模态模型", test_multimodal_model)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "="*70)
    print("检查结果总结")
    print("="*70)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:20s}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("\n🎉 环境配置完成！可以开始使用多模态功能")
        print("\n下一步:")
        print("1. 运行测试: python test_multimodal.py")
        print("2. 查看示例: python examples/multimodal_example.py")
        print("3. 阅读文档: 多模态功能使用指南.md")
    else:
        print("\n⚠️  请解决上述问题后再使用多模态功能")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
