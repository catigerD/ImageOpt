import os
import re
import sys
import tinify
from PIL import Image

# 配置你的 TinyPNG API 密钥
TINYPNG_API_KEY = "DFY2dxk82bXZPj07cNtT1R21vrXc0fZN"

webp_block_regex_list = [
    r'.*app/src/main/assets/.*'
]


class FileProcessor:
    def __init__(self):
        apiKey = get_tinypng_key()
        if apiKey is None:
            apiKey = TINYPNG_API_KEY
        self.tinypng_api_key = apiKey
        self.supported_formats = ('.png', '.jpg', '.jpeg')

    def compress_with_tinypng(self, input_path, output_path):
        """使用 TinyPNG 压缩图片"""
        try:
            tinify.key = self.tinypng_api_key
            source = tinify.from_file(input_path)
            source.to_file(output_path)
            return os.path.getsize(output_path)
        except Exception as e:
            print(f"TinyPNG 压缩失败: {e}")
            return float('inf')

    def convert_to_webp(self, input_path, output_path, quality=80):
        """将图片转换为 WebP 格式"""
        try:
            for regex in webp_block_regex_list:
                if re.search(regex, input_path):
                    print(f"WebP 转换失败: 命中黑名单")
                    return float('inf')

            with Image.open(input_path) as img:
                img.save(output_path, 'webp', quality=quality)
            return os.path.getsize(output_path)
        except Exception as e:
            print(f"WebP 转换失败: {e}")
            return float('inf')

    def optimize_image(self, image_path):
        """优化图片并选择最佳方案"""
        if not os.path.isfile(image_path):
            print(f"文件不存在: {image_path}")
            return -1

        # 只处理支持的图片格式
        if not image_path.lower().endswith(self.supported_formats):
            print(f"不支持的图片格式: {image_path}")
            return -1

        print(f"\n正在处理图片: {image_path}")

        # 准备临时文件
        base_name = os.path.splitext(image_path)[0]
        ext = os.path.splitext(image_path)[1].lower()
        compressed_path = f"{base_name}_compressed{ext}"
        webp_path = f"{base_name}.webp"

        # 获取原始文件大小
        original_size = os.path.getsize(image_path)
        print(f"原始文件大小: {original_size} bytes")

        # 处理图片
        compressed_size = self.compress_with_tinypng(image_path, compressed_path)
        webp_size = self.convert_to_webp(image_path, webp_path)

        print(f"压缩后大小: {compressed_size} bytes | WebP大小: {webp_size} bytes")

        # 比较结果并选择最佳方案
        best_option = None
        if compressed_size < original_size and compressed_size <= webp_size:
            best_option = 'compressed'
        elif webp_size < original_size and webp_size <= compressed_size:
            best_option = 'webp'

        # 应用最佳方案
        opt_size = 0
        if best_option == 'compressed':
            os.replace(compressed_path, image_path)
            if os.path.exists(webp_path):
                os.remove(webp_path)
            opt_size = original_size - compressed_size
            print(f"✅ 选择压缩方案: 节省 {opt_size} bytes")
        elif best_option == 'webp':
            os.remove(image_path)
            if os.path.exists(compressed_path):
                os.remove(compressed_path)
            opt_size = original_size - webp_size
            print(f"✅ 选择WebP方案: 节省 {opt_size} bytes")
        else:
            if os.path.exists(compressed_path):
                os.remove(compressed_path)
            if os.path.exists(webp_path):
                os.remove(webp_path)
            print("ℹ️ 原始文件已是最佳，无需优化")

        return opt_size


def get_tinypng_key():
    """
    从 local.properties 读取 TinyPNG API Key
    :return: API Key 字符串，如果找不到返回 None
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prop_file = os.path.join(project_root, 'local.properties')

    if not os.path.exists(prop_file):
        return None

    with open(prop_file, 'r') as f:
        content = f.read()

    # 使用正则表达式匹配 key
    match = re.search(r'TinyPNG\.API\.Key\s*=\s*(.+)', content)
    return match.group(1).strip() if match else None

def main():
    if len(sys.argv) < 2:
        print("请提供图片路径作为参数")
        sys.exit(1)

    processor = FileProcessor()
    for image_path in sys.argv[1:]:
        processor.optimize_image(image_path)

if __name__ == "__main__":
    import sys
    main()
