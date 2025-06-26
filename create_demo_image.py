##########create_demo_image.py: [创建演示图片] ##################
# 变更记录: [2025-06-26] @李祥光 [创建演示图片生成脚本]########
# 输入: [无] | 输出: [生成demo.jpg演示图片]###############

import cv2
import numpy as np
from pathlib import Path

def create_demo_image():
    """
    create_demo_image 功能说明:
    # 创建一个带有水印的演示图片，用于测试去水印功能
    # 输入: [无] | 输出: [保存demo.jpg文件]
    """
    # 创建一个500x400的蓝色背景图片
    img = np.zeros((400, 500, 3), dtype=np.uint8)
    img[:] = (200, 150, 100)  # BGR格式的浅蓝色
    
    # 添加一些图案
    cv2.rectangle(img, (50, 50), (200, 150), (255, 255, 255), -1)
    cv2.circle(img, (350, 200), 80, (0, 255, 0), -1)
    cv2.ellipse(img, (250, 300), (100, 50), 0, 0, 360, (0, 0, 255), -1)
    
    # 添加文字作为"水印"
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, 'WATERMARK', (150, 250), font, 1.5, (0, 0, 0), 3)
    cv2.putText(img, 'DEMO', (300, 100), font, 1, (128, 128, 128), 2)
    
    # 保存图片
    output_path = Path('demo.jpg')
    cv2.imwrite(str(output_path), img)
    print(f"演示图片已创建: {output_path.absolute()}")
    
    return str(output_path.absolute())

if __name__ == "__main__":
    create_demo_image()