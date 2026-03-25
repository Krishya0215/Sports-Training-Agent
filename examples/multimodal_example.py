"""
多模态功能使用示例
演示如何使用图像描述和感知记忆功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from model.multimodal_model import multimodal_llm
from rag.document_processor import DocumentProcessor
from rag.vector_store import VectorStoreService
from memory.memory_manager import MemoryManager
from utils.logger_handler import logger


def example_1_generate_image_description():
    """示例1: 生成单张图像的描述"""
    print("\n" + "="*60)
    print("示例1: 生成图像描述")
    print("="*60)
    
    # 假设有一张训练图像
    image_path = "data/extracted_images/sample_image.jpg"
    
    # 生成简要描述
    result = multimodal_llm.generate_image_description(
        image_path=image_path,
        detail_level="brief"
    )
    
    if result["success"]:
        print(f"✅ 简要描述: {result['description']}")
    
    # 生成详细描述
    result = multimodal_llm.generate_image_description(
        image_path=image_path,
        detail_level="detailed"
    )
    
    if result["success"]:
        print(f"✅ 详细描述: {result['description']}")


def example_2_process_pdf_with_images():
    """示例2: 处理包含图像的PDF文档"""
    print("\n" + "="*60)
    print("示例2: 处理多模态PDF")
    print("="*60)
    
    # 初始化文档处理器
    processor = DocumentProcessor()
    
    # 处理PDF文档
    pdf_path = "data/运动训练基础理论.pdf"
    documents = processor.process_pdf(pdf_path)
    
    # 分类文档
    text_docs = [d for d in documents if d.metadata.get("content_type") != "image_description"]
    image_docs = [d for d in documents if d.metadata.get("content_type") == "image_description"]
    
    print(f"✅ 处理完成:")
    print(f"   - 文本块: {len(text_docs)}")
    print(f"   - 图像描述: {len(image_docs)}")
    
    # 显示第一个图像描述
    if image_docs:
        first_image = image_docs[0]
        print(f"\n示例图像描述:")
        print(f"   文件: {first_image.metadata.get('image_filename')}")
        print(f"   页码: {first_image.metadata.get('page_number')}")
        print(f"   内容: {first_image.page_content[:150]}...")
    
    return documents


def example_3_store_and_retrieve():
    """示例3: 存储和检索多模态文档"""
    print("\n" + "="*60)
    print("示例3: 多模态文档检索")
    print("="*60)
    
    # 处理文档
    processor = DocumentProcessor()
    documents = processor.process_pdf("data/运动训练基础理论.pdf")
    
    # 存入向量库
    vector_store = VectorStoreService()
    vector_store.add_documents(documents)
    print(f"✅ 已存储 {len(documents)} 个文档块")
    
    # 检索测试
    retriever = vector_store.get_retriever()
    
    # 查询1: 可能匹配文本
    query1 = "深蹲的标准动作"
    results1 = retriever.invoke(query1)
    print(f"\n查询: '{query1}'")
    print(f"检索到 {len(results1)} 个结果")
    
    for i, doc in enumerate(results1[:3], 1):
        content_type = doc.metadata.get("content_type", "text")
        print(f"\n结果 {i} ({content_type}):")
        print(f"   {doc.page_content[:100]}...")
    
    # 查询2: 可能匹配图像描述
    query2 = "训练姿势示意图"
    results2 = retriever.invoke(query2)
    print(f"\n查询: '{query2}'")
    print(f"检索到 {len(results2)} 个结果")
    
    # 统计结果类型
    text_results = sum(1 for d in results2 if d.metadata.get("content_type") != "image_description")
    image_results = sum(1 for d in results2 if d.metadata.get("content_type") == "image_description")
    print(f"   - 文本结果: {text_results}")
    print(f"   - 图像描述: {image_results}")


def example_4_perceptual_memory():
    """示例4: 使用感知记忆"""
    print("\n" + "="*60)
    print("示例4: 感知记忆系统")
    print("="*60)
    
    # 初始化记忆管理器
    memory = MemoryManager()
    
    # 模拟添加图像描述
    image_data = [
        {
            "id": "squat_demo.jpg",
            "description": "运动员展示标准深蹲姿势：双脚与肩同宽，膝盖不超过脚尖，背部保持挺直",
            "metadata": {
                "source": "training_guide.pdf",
                "page_number": 12,
                "exercise_type": "力量训练"
            }
        },
        {
            "id": "pushup_demo.jpg",
            "description": "标准俯卧撑姿势：身体保持一条直线，手臂与肩同宽，核心收紧",
            "metadata": {
                "source": "training_guide.pdf",
                "page_number": 15,
                "exercise_type": "力量训练"
            }
        },
        {
            "id": "running_form.jpg",
            "description": "正确的跑步姿势：上身微微前倾，手臂自然摆动，脚掌中部着地",
            "metadata": {
                "source": "cardio_guide.pdf",
                "page_number": 8,
                "exercise_type": "有氧训练"
            }
        }
    ]
    
    # 添加到感知记忆
    for img in image_data:
        memory.perceptual_memory.add_image_description(
            image_id=img["id"],
            description=img["description"],
            metadata=img["metadata"]
        )
    
    print(f"✅ 已添加 {len(image_data)} 个图像描述到感知记忆")
    
    # 检索所有图像
    all_images = memory.perceptual_memory.get_all_image_descriptions()
    print(f"\n感知记忆中的图像: {len(all_images)} 个")
    
    # 按来源搜索
    training_guide_images = memory.perceptual_memory.search_images_by_source("training_guide.pdf")
    print(f"\n来自 'training_guide.pdf' 的图像: {len(training_guide_images)} 个")
    
    for img in training_guide_images:
        print(f"   - {img['image_id']}: {img['description'][:50]}...")
    
    # 显示记忆摘要
    summary = memory.summarize_memory()
    print(f"\n记忆系统摘要:")
    for key, value in summary.items():
        print(f"   {key}: {value}")


def example_5_integrated_workflow():
    """示例5: 完整的多模态工作流"""
    print("\n" + "="*60)
    print("示例5: 完整多模态工作流")
    print("="*60)
    
    # 1. 处理PDF文档
    print("\n步骤1: 处理PDF文档")
    processor = DocumentProcessor()
    documents = processor.process_pdf("data/运动训练基础理论.pdf")
    print(f"✅ 生成 {len(documents)} 个文档块")
    
    # 2. 存入向量库
    print("\n步骤2: 存入向量库")
    vector_store = VectorStoreService()
    vector_store.add_documents(documents)
    print(f"✅ 文档已存储")
    
    # 3. 提取图像描述并存入感知记忆
    print("\n步骤3: 更新感知记忆")
    memory = MemoryManager()
    image_docs = [d for d in documents if d.metadata.get("content_type") == "image_description"]
    
    for doc in image_docs:
        memory.perceptual_memory.add_image_description(
            image_id=doc.metadata.get("image_filename", "unknown"),
            description=doc.page_content,
            metadata=doc.metadata
        )
    
    print(f"✅ 感知记忆已更新，包含 {len(image_docs)} 个图像")
    
    # 4. 执行检索
    print("\n步骤4: 执行多模态检索")
    retriever = vector_store.get_retriever()
    query = "训练动作的正确姿势"
    results = retriever.invoke(query)
    
    print(f"✅ 查询: '{query}'")
    print(f"✅ 检索到 {len(results)} 个结果")
    
    # 分析结果
    for i, doc in enumerate(results[:5], 1):
        content_type = doc.metadata.get("content_type", "text")
        source = doc.metadata.get("file_name", "unknown")
        
        if content_type == "image_description":
            print(f"\n结果 {i} [图像描述] - {source}")
            print(f"   页码: {doc.metadata.get('page_number')}")
            print(f"   内容: {doc.page_content[:100]}...")
        else:
            print(f"\n结果 {i} [文本] - {source}")
            print(f"   内容: {doc.page_content[:100]}...")
    
    # 5. 记录交互
    print("\n步骤5: 记录到记忆系统")
    memory.record_interaction(
        question=query,
        answer="基于检索结果生成的答案...",
        retrieved_docs=[doc.metadata.get("source") for doc in results],
        metadata={
            "image_descriptions": [
                {
                    "image_id": doc.metadata.get("image_filename"),
                    "description": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in results if doc.metadata.get("content_type") == "image_description"
            ]
        }
    )
    
    print(f"✅ 交互已记录")
    
    # 显示最终状态
    summary = memory.summarize_memory()
    print(f"\n最终记忆状态:")
    for key, value in summary.items():
        print(f"   {key}: {value}")


def main():
    """运行所有示例"""
    print("\n" + "="*70)
    print("多模态功能使用示例")
    print("="*70)
    
    examples = [
        ("生成图像描述", example_1_generate_image_description),
        ("处理多模态PDF", example_2_process_pdf_with_images),
        ("多模态检索", example_3_store_and_retrieve),
        ("感知记忆", example_4_perceptual_memory),
        ("完整工作流", example_5_integrated_workflow)
    ]
    
    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print("0. 运行所有示例")
    
    choice = input("\n请选择要运行的示例 (0-5): ").strip()
    
    if choice == "0":
        for name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"❌ 示例 '{name}' 运行失败: {e}")
                logger.error(f"示例失败: {e}")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        name, func = examples[int(choice) - 1]
        try:
            func()
        except Exception as e:
            print(f"❌ 示例运行失败: {e}")
            logger.error(f"示例失败: {e}")
    else:
        print("无效的选择")


if __name__ == "__main__":
    main()
