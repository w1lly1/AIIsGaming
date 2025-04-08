# 在文件顶部新增导入
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
import os
import json
# from transformers.models.qwen_vl import QwenVLImageProcessor
# from transformers.models.qwen_vl.image_processing_qwen_vl import QwenVLImageProcessor
from transformers import Qwen2VLImageProcessor  # 使用专用图像处理器


class CardAnalyzer:
    def __init__(self):
        # 新增大模型初始化
        self.model_path = r"E:\huggingFace\downloads\Qwen\Qwen2.5-VL-7B-Instruct"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            device_map="auto",
            torch_dtype=torch.bfloat16,  # 显存优化
            trust_remote_code=True
        )

    def analyze_card(self, img_path):
        """使用大模型分析的核心函数"""
        try:
            prompt = """分析这张炉石传说卡牌,返回JSON格式结果。需要包含:
            - type(随从/法术）
            - cost(铸币消耗）
            - name(卡牌名称）
            - attack(攻击力，仅随从）
            - health(生命值，仅随从）
            - effect(效果描述）
            - attributes(属性列表）
            卡牌图片："""
            
            response = self.query_model(img_path, prompt)
            return self.parse_response(response)
        except Exception as e:
            return {"error": str(e)}

    def query_model(self, img_path, prompt):
        """与大模型交互的核心方法"""
        # 修复图像模式警告
        image = Image.open(img_path).convert('RGB')  # 确保转换为RGB模式

        # 初始化专用处理器
        image_processor = Qwen2VLImageProcessor.from_pretrained(self.model_path)
        tokenizer = AutoTokenizer.from_pretrained(self.model_path)

        # 构建模型输入
        inputs = tokenizer(
            prompt,
            return_tensors='pt',
            padding=True
        ).to(self.model.device)

        # 处理图像
        image_tensor = image_processor(images=image, return_tensors="pt")['pixel_values'].to(self.model.device)

        # 生成响应
        outputs = self.model.generate(
            **inputs,
            image=image_tensor,
            max_new_tokens=1024,
            temperature=0.2
        )
        return tokenizer.decode(outputs[0], skip_special_tokens=True)

    def parse_response(self, response):
        """解析大模型返回的响应"""
        import re
        import json

        # 使用正则表达式提取JSON部分
        json_match = re.search(r'```json(.*?)```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                return {"error": "JSON解析失败"}
        return {"error": "未找到有效响应"}

def main():
    analyzer = CardAnalyzer()
    card_dir = "Cache/Test"
    results = []
    
    if not os.path.exists(card_dir):
        print(f"目录不存在: {card_dir}")
        return

    for filename in os.listdir(card_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                print(f"正在分析: {filename}")
                result = analyzer.analyze_card(os.path.join(card_dir, filename))
                results.append({
                    "filename": filename,
                    "data": result
                })
            except Exception as e:
                print(f"分析 {filename} 时出错: {str(e)}")
    
    # 保存分析结果
    output_path = "Cache/card_analysis.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"分析完成！结果已保存至: {output_path}")

if __name__ == "__main__":
    main()