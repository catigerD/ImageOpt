import os
from .file_processor import FileProcessor


class DirectoryWalker:
    def __init__(self):
        self.processor = FileProcessor()

    def walk_and_process(self, directory):
        """递归处理目录中的所有图片"""
        processed_count = 0
        total_opt_size = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                opt_size = self.processor.optimize_image(file_path)
                if opt_size >= 0:
                    processed_count += 1
                    total_opt_size += opt_size
        return processed_count, total_opt_size


def main():
    import sys
    if len(sys.argv) < 2:
        print("请提供要处理的目录路径作为参数")
        sys.exit(1)

    target_directory = sys.argv[1]
    if not os.path.isdir(target_directory):
        print(f"错误: {target_directory} 不是有效目录")
        sys.exit(1)

    print(f"开始处理目录: {target_directory}")
    walker = DirectoryWalker()
    total_processed, total_opt_size = walker.walk_and_process(target_directory)
    print(f"\n处理完成! 共处理了 {total_processed} 个图片文件, 节省 {total_opt_size} bytes")


if __name__ == "__main__":
    main()
