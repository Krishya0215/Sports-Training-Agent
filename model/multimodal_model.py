"""
多模态模型服务 - 支持图像理解和描述生成
"""
import os
import base64
from typing import Optional, Dict, Any
from pathlib import Path
import dashscope
from dashscope import MultiModalConversation
from utils.logger_handler import logger
from dotenv import load_dotenv

load_dotenv()

# 设置API Key
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")


class MultiModalLLM:
    """多模态大语言模型服务"""
    
    def __init__(self, model_name: str = "qwen-vl-max"):
        """
        初始化多模态模型
        
        Args:
            model_name: 模型名称，可选 qwen-vl-plus, qwen-vl-max
        """
        self.model_name = model_name
        logger.info(f"多模态模型初始化: {model_name}")
    
    def generate_image_description(
        self, 
        image_path: str, 
        prompt: Optional[str] = None,
        detail_level: str = "detailed"
    ) -> Dict[str, Any]:
        """
        为图像生成文本描述
        
        Args:
            image_path: 图像文件路径
            prompt: 自定义提示词，如果为None则使用默认提示
            detail_level: 描述详细程度 (brief/detailed/comprehensive)
            
        Returns:
            包含描述文本和元数据的字典
        """
        if not os.path.exists(image_path):
            logger.error(f"图像文件不存在: {image_path}")
            return {"description": "", "success": False, "error": "文件不存在"}
        
        # 根据详细程度设置提示词
        if prompt is None:
            prompt = self._get_default_prompt(detail_level)
        
        try:
            # 构建消息
            messages = [{
                'role': 'user',
                'content': [
                    {'image': f'file://{os.path.abspath(image_path)}'},
                    {'text': prompt}
                ]
            }]
            
            # 调用多模态模型
            response = MultiModalConversation.call(
                model=self.model_name,
                messages=messages
            )
            
            if response.status_code == 200:
                description = response.output.choices[0].message.content[0]['text']
                logger.info(f"图像描述生成成功: {Path(image_path).name}")
                
                return {
                    "description": description,
                    "success": True,
                    "image_path": image_path,
                    "model": self.model_name,
                    "detail_level": detail_level
                }
            else:
                logger.error(f"多模态模型调用失败: {response.message}")
                return {
                    "description": "",
                    "success": False,
                    "error": response.message
                }
                
        except Exception as e:
            logger.error(f"生成图像描述失败: {e}")
            return {
                "description": "",
                "success": False,
                "error": str(e)
            }
    
    def _get_default_prompt(self, detail_level: str) -> str:
        """获取默认提示词"""
        prompts = {
            "brief": "请简要描述这张图片的主要内容（50字以内）。",
            "detailed": """请详细描述这张图片中的运动训练相关内容，包括：
1. 主要动作或训练项目
2. 关键技术要点
3. 姿势和动作细节
4. 相关的训练目标或效果
请用专业的运动训练术语进行描述。""",
            "comprehensive": """请全面分析这张图片中的运动训练内容：
1. 训练项目和动作名称
2. 动作的标准姿势和技术要领
3. 涉及的主要肌肉群和身体部位
4. 常见错误和注意事项
5. 适用人群和训练目标
6. 与其他训练动作的关联
请提供专业、详细的分析。"""
        }
        return prompts.get(detail_level, prompts["detailed"])
    
    def batch_generate_descriptions(
        self, 
        image_paths: list[str],
        prompt: Optional[str] = None
    ) -> list[Dict[str, Any]]:
        """
        批量生成图像描述
        
        Args:
            image_paths: 图像文件路径列表
            prompt: 自定义提示词
            
        Returns:
            描述结果列表
        """
        results = []
        for image_path in image_paths:
            result = self.generate_image_description(image_path, prompt)
            results.append(result)
        
        logger.info(f"批量生成完成: {len(results)} 张图像")
        return results


# 创建全局实例
multimodal_llm = MultiModalLLM()


if __name__ == "__main__":
    # 测试代码
    test_image = "data/test_image.jpg"
    if os.path.exists(test_image):
        result = multimodal_llm.generate_image_description(test_image)
        print(f"描述: {result['description']}")
    else:
        print("测试图像不存在")
