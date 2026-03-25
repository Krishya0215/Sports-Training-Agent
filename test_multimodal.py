"""
多模态功能测试脚本
测试图像描述生成和感知记忆功能
"""
import os
from pathlib import Path
from model.multimodal_model import multimodal_llm
from rag.document_processor import DocumentProcessor
from memory.memory_manager import MemoryManager
from utils.logger_handler import logger


def test_image_description():
    """测试单张图像描述生成"""
    print("\n" + "="*50)
    print("测试1: 单张图像描述生成")
    print("="*50)
    
    # 查找测试图像
    test_images = list(Path("data/extracted_images").rglob("*.jpg")) + \
                  list(Path("data/extracted_images").rglob("*.png"))
    
    if not test_images:
        print("❌ 未找到测试图像，请先处理PDF文档")
        return False
    
    test_image = str(test_images[0])
    print(f"测试图像: {test_image}")
    
    # 生成描述
    result = multimodal_llm.generate_image_description(
        test_image,
        detail_level="detailed"
    )
    
    if result["success"]:
        print(f"✅ 图像描述生成成功")
        print(f"描述内容:\n{result['description']}")
        print(f"使用模型: {result['model']}")
        return True
    else:
        print(f"❌ 图像描述生成失败: {result.get('error')}")
        return False


def test_pdf_processing_with_images():
    """测试PDF处理和图像提取"""
    print("\n" + "="*50)
    print("测试2: PDF多模态处理")
    print("="*50)
    
    # 查找PDF文件
    pdf_files = list(Path("data").glob("*.pdf"))
    
    if not pdf_files:
        print("❌ 未找到PDF文件")
        return False
    
    pdf_file = str(pdf_files[0])
    print(f"处理PDF: {pdf_file}")
    
    # 处理PDF
    processor = DocumentProcessor()
    documents = processor.process_pdf(pdf_file)
    
    # 统计文档类型
    text_docs = [d for d in documents if d.metadata.get("content_type") != "image_description"]
    image_docs = [d for d in documents if d.metadata.get("content_type") == "image_description"]
    
    print(f"✅ PDF处理完成")
    print(f"  - 文本块: {len(text_docs)} 个")
    print(f"  - 图像描述: {len(image_docs)} 个")
    
    if image_docs:
        print(f"\n示例图像描述:")
        for i, doc in enumerate(image_docs[:2], 1):
            print(f"\n图像 {i}:")
            print(f"  文件名: {doc.metadata.get('image_filename')}")
            print(f"  页码: {doc.metadata.get('page_number')}")
            print(f"  描述: {doc.page_content[:200]}...")
    
    return len(image_docs) > 0


def test_perceptual_memory():
    """测试感知记忆功能"""
    print("\n" + "="*50)
    print("测试3: 感知记忆")
    print("="*50)
    
    memory_manager = MemoryManager()
    
    # 添加测试图像描述
    test_data = [
        {
            "image_id": "test_img_1.jpg",
            "description": "运动员正在进行深蹲训练，双脚与肩同宽，膝盖不超过脚尖",
            "metadata": {
                "source": "data/运动训练基础理论.pdf",
                "page_number": 1,
                "model": "qwen-vl-max"
            }
        },
        {
            "image_id": "test_img_2.jpg",
            "description": "标准的俯卧撑姿势示意图，身体保持一条直线",
            "metadata": {
                "source": "data/运动训练基础理论.pdf",
                "page_number": 2,
                "model": "qwen-vl-max"
            }
        }
    ]
    
    # 添加到感知记忆
    for data in test_data:
        memory_manager.perceptual_memory.add_image_description(
            image_id=data["image_id"],
            description=data["description"],
            metadata=data["metadata"]
        )
    
    print(f"✅ 添加了 {len(test_data)} 个图像描述到感知记忆")
    
    # 测试检索
    all_descriptions = memory_manager.perceptual_memory.get_all_image_descriptions()
    print(f"✅ 感知记忆中共有 {len(all_descriptions)} 个图像描述")
    
    # 测试按来源搜索
    source_images = memory_manager.perceptual_memory.search_images_by_source(
        "data/运动训练基础理论.pdf"
    )
    print(f"✅ 从指定文档检索到 {len(source_images)} 个图像")
    
    # 显示记忆摘要
    summary = memory_manager.summarize_memory()
    print(f"\n记忆系统摘要:")
    for key, value in summary.items():
        print(f"  - {key}: {value}")
    
    return True


def test_full_workflow():
    """测试完整工作流"""
    print("\n" + "="*50)
    print("测试4: 完整多模态工作流")
    print("="*50)
    
    # 1. 处理PDF
    processor = DocumentProcessor()
    pdf_files = list(Path("data").glob("*.pdf"))
    
    if not pdf_files:
        print("❌ 未找到PDF文件")
        return False
    
    pdf_file = str(pdf_files[0])
    documents = processor.process_pdf(pdf_file)
    
    # 2. 提取图像描述文档
    image_docs = [d for d in documents if d.metadata.get("content_type") == "image_description"]
    
    # 3. 存入感知记忆
    memory_manager = MemoryManager()
    for doc in image_docs:
        memory_manager.perceptual_memory.add_image_description(
            image_id=doc.metadata.get("image_filename", "unknown"),
            description=doc.page_content,
            metadata=doc.metadata
        )
    
    print(f"✅ 完整工作流测试完成")
    print(f"  - 处理文档: {len(documents)} 个块")
    print(f"  - 图像描述: {len(image_docs)} 个")
    print(f"  - 感知记忆: {len(memory_manager.perceptual_memory.image_descriptions)} 个图像")
    
    return True


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("多模态功能测试套件")
    print("="*60)
    
    tests = [
        ("图像描述生成", test_image_description),
        ("PDF多模态处理", test_pdf_processing_with_images),
        ("感知记忆", test_perceptual_memory),
        ("完整工作流", test_full_workflow)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            logger.error(f"测试 {test_name} 失败: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\n总计: {passed}/{total} 测试通过")


if __name__ == "__main__":
    main()
