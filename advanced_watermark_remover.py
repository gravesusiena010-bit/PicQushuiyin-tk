##########advanced_watermark_remover.py: 高级图片去水印工具 ##################
# 变更记录: [2024-12-19] @李祥光 [创建高级去水印工具，支持批量处理和多种算法]########
# 输入: [图片文件路径或目录] | 输出: [去水印后的图片文件]###############


###########################文件下的所有函数###########################
"""
main：主程序入口，支持单张和批量处理
process_single_image：处理单张图片
process_batch_images：批量处理图片
load_image_safe：安全加载图片文件
mouse_callback_advanced：高级鼠标回调，支持多种选择模式
remove_watermark_telea：使用TELEA算法去水印
remove_watermark_ns：使用Navier-Stokes算法去水印
preview_result：预览处理结果
save_result_with_options：保存结果，支持多种选项
setup_logging：设置日志系统
show_advanced_help：显示高级帮助信息
"""
###########################文件下的所有函数###########################

#########mermaid格式说明所有函数的调用关系说明开始#########
"""
flowchart TD
    A[程序启动] --> B[main函数]
    B --> C{检查参数类型}
    C -->|单张图片| D[process_single_image]
    C -->|目录| E[process_batch_images]
    D --> F[load_image_safe]
    E --> G[遍历目录]
    G --> F
    F --> H[mouse_callback_advanced]
    H --> I{选择算法}
    I -->|TELEA| J[remove_watermark_telea]
    I -->|NS| K[remove_watermark_ns]
    J --> L[preview_result]
    K --> L
    L --> M[save_result_with_options]
    M --> N[记录日志]
    B --> O[show_advanced_help]
"""
#########mermaid格式说明所有函数的调用关系说明结束#########

import cv2
import numpy as np
import os
import sys
import argparse
import logging
import time
from datetime import datetime
from typing import Tuple, List, Optional
from pathlib import Path

# 全局变量
drawing = False
ix, iy = -1, -1
mask = None
original_img = None
current_img = None
brush_size = 5
selection_mode = 'brush'  # 'brush' or 'rectangle'
rect_start = None
rect_end = None

def setup_logging():
    """
    setup_logging 功能说明:
    # 设置日志系统，记录程序运行状态和错误信息
    # 输入: [无] | 输出: [配置日志记录器]
    """
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    log_filename = f"watermark_removal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = log_dir / log_filename
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logging.info("高级图片去水印工具启动")
    return logging.getLogger(__name__)

def mouse_callback_advanced(event, x, y, flags, param):
    """
    mouse_callback_advanced 功能说明:
    # 高级鼠标回调函数，支持画笔和矩形两种选择模式
    # 输入: [鼠标事件参数] | 输出: [更新全局mask和显示变量]
    """
    global ix, iy, drawing, mask, current_img, brush_size, selection_mode
    global rect_start, rect_end
    
    if selection_mode == 'brush':
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            ix, iy = x, y
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                cv2.circle(mask, (x, y), brush_size, 255, -1)
                cv2.circle(current_img, (x, y), brush_size, (0, 0, 255), -1)
                cv2.imshow('高级去水印工具 - 按ESC确认', current_img)
        
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            cv2.circle(mask, (x, y), brush_size, 255, -1)
            cv2.circle(current_img, (x, y), brush_size, (0, 0, 255), -1)
            cv2.imshow('高级去水印工具 - 按ESC确认', current_img)
    
    elif selection_mode == 'rectangle':
        if event == cv2.EVENT_LBUTTONDOWN:
            rect_start = (x, y)
        
        elif event == cv2.EVENT_LBUTTONUP:
            if rect_start:
                rect_end = (x, y)
                # 绘制矩形区域到mask
                cv2.rectangle(mask, rect_start, rect_end, 255, -1)
                cv2.rectangle(current_img, rect_start, rect_end, (0, 0, 255), 2)
                cv2.imshow('高级去水印工具 - 按ESC确认', current_img)
                rect_start = None

def load_image_safe(image_path: str) -> Optional[np.ndarray]:
    """
    load_image_safe 功能说明:
    # 安全加载图片文件，包含详细的错误处理和日志记录
    # 输入: [图片文件路径] | 输出: [numpy数组格式的图片数据或None]
    """
    try:
        if not os.path.exists(image_path):
            logging.error(f"图片文件不存在: {image_path}")
            return None
        
        img = cv2.imread(image_path)
        if img is None:
            logging.error(f"无法读取图片文件: {image_path}")
            return None
        
        logging.info(f"成功加载图片: {image_path}, 尺寸: {img.shape[1]}x{img.shape[0]}")
        return img
        
    except Exception as e:
        logging.error(f"加载图片时发生错误: {str(e)}")
        return None

def remove_watermark_telea(img: np.ndarray, mask: np.ndarray, radius: int = 3) -> np.ndarray:
    """
    remove_watermark_telea 功能说明:
    # 使用TELEA算法进行图像修复
    # 输入: [原始图片, 水印区域mask, 修复半径] | 输出: [修复后的图片]
    """
    start_time = time.time()
    result = cv2.inpaint(img, mask, radius, cv2.INPAINT_TELEA)
    end_time = time.time()
    
    logging.info(f"TELEA算法处理完成，耗时: {end_time - start_time:.2f}秒")
    return result

def remove_watermark_ns(img: np.ndarray, mask: np.ndarray, radius: int = 3) -> np.ndarray:
    """
    remove_watermark_ns 功能说明:
    # 使用Navier-Stokes算法进行图像修复
    # 输入: [原始图片, 水印区域mask, 修复半径] | 输出: [修复后的图片]
    """
    start_time = time.time()
    result = cv2.inpaint(img, mask, radius, cv2.INPAINT_NS)
    end_time = time.time()
    
    logging.info(f"Navier-Stokes算法处理完成，耗时: {end_time - start_time:.2f}秒")
    return result

def preview_result(original: np.ndarray, result: np.ndarray) -> bool:
    """
    preview_result 功能说明:
    # 预览处理结果，支持对比显示
    # 输入: [原始图片, 处理结果] | 输出: [用户是否确认保存]
    """
    # 创建对比显示
    h, w = original.shape[:2]
    comparison = np.zeros((h, w * 2, 3), dtype=np.uint8)
    comparison[:, :w] = original
    comparison[:, w:] = result
    
    # 添加分割线和标签
    cv2.line(comparison, (w, 0), (w, h), (255, 255, 255), 2)
    cv2.putText(comparison, 'Original', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(comparison, 'Result', (w + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    cv2.imshow('处理结果预览 - 按S保存，按Q取消', comparison)
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s') or key == ord('S'):
            cv2.destroyWindow('处理结果预览 - 按S保存，按Q取消')
            return True
        elif key == ord('q') or key == ord('Q'):
            cv2.destroyWindow('处理结果预览 - 按S保存，按Q取消')
            return False

def save_result_with_options(img: np.ndarray, original_path: str, 
                           suffix: str = '_no_watermark', 
                           quality: int = 95) -> Optional[str]:
    """
    save_result_with_options 功能说明:
    # 保存处理结果，支持自定义后缀和质量设置
    # 输入: [处理后图片, 原始路径, 文件后缀, 图片质量] | 输出: [保存的文件路径]
    """
    try:
        base_name = os.path.splitext(original_path)[0]
        extension = os.path.splitext(original_path)[1].lower()
        output_path = f"{base_name}{suffix}{extension}"
        
        # 根据文件格式设置保存参数
        if extension in ['.jpg', '.jpeg']:
            cv2.imwrite(output_path, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
        elif extension == '.png':
            cv2.imwrite(output_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        else:
            cv2.imwrite(output_path, img)
        
        logging.info(f"结果已保存到: {output_path}")
        return output_path
        
    except Exception as e:
        logging.error(f"保存文件时发生错误: {str(e)}")
        return None

def process_single_image(image_path: str, algorithm: str = 'telea', 
                        radius: int = 3) -> bool:
    """
    process_single_image 功能说明:
    # 处理单张图片的完整流程
    # 输入: [图片路径, 算法类型, 修复半径] | 输出: [处理是否成功]
    """
    global mask, original_img, current_img, selection_mode, brush_size
    
    # 加载图片
    original_img = load_image_safe(image_path)
    if original_img is None:
        return False
    
    current_img = original_img.copy()
    mask = np.zeros(original_img.shape[:2], np.uint8)
    
    # 创建窗口
    cv2.namedWindow('高级去水印工具 - 按ESC确认', cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback('高级去水印工具 - 按ESC确认', mouse_callback_advanced)
    
    cv2.imshow('高级去水印工具 - 按ESC确认', current_img)
    
    print(f"\n当前模式: {selection_mode}")
    print(f"画笔大小: {brush_size}")
    print("快捷键: ESC-确认 | R-重置 | B-画笔模式 | T-矩形模式 | +/-调整画笔 | Q-退出")
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC键
            if np.sum(mask) == 0:
                print("警告: 未选择任何区域")
                continue
            
            print(f"开始使用{algorithm.upper()}算法去除水印...")
            
            if algorithm.lower() == 'telea':
                result = remove_watermark_telea(original_img, mask, radius)
            else:
                result = remove_watermark_ns(original_img, mask, radius)
            
            # 预览结果
            if preview_result(original_img, result):
                output_path = save_result_with_options(result, image_path)
                if output_path:
                    print(f"处理完成！结果保存在: {output_path}")
                    cv2.destroyAllWindows()
                    return True
            
        elif key == ord('r') or key == ord('R'):  # 重置
            mask = np.zeros(original_img.shape[:2], np.uint8)
            current_img = original_img.copy()
            cv2.imshow('高级去水印工具 - 按ESC确认', current_img)
            print("已重置选择区域")
            
        elif key == ord('b') or key == ord('B'):  # 画笔模式
            selection_mode = 'brush'
            print(f"切换到画笔模式，画笔大小: {brush_size}")
            
        elif key == ord('t') or key == ord('T'):  # 矩形模式
            selection_mode = 'rectangle'
            print("切换到矩形选择模式")
            
        elif key == ord('+') or key == ord('='):  # 增大画笔
            brush_size = min(brush_size + 2, 20)
            print(f"画笔大小: {brush_size}")
            
        elif key == ord('-') or key == ord('_'):  # 减小画笔
            brush_size = max(brush_size - 2, 1)
            print(f"画笔大小: {brush_size}")
            
        elif key == ord('q') or key == ord('Q'):  # 退出
            print("用户取消操作")
            break
    
    cv2.destroyAllWindows()
    return False

def process_batch_images(directory: str, algorithm: str = 'telea', 
                        radius: int = 3) -> int:
    """
    process_batch_images 功能说明:
    # 批量处理目录中的所有图片文件
    # 输入: [目录路径, 算法类型, 修复半径] | 输出: [成功处理的文件数量]
    """
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    processed_count = 0
    
    image_files = []
    for file_path in Path(directory).rglob('*'):
        if file_path.suffix.lower() in supported_formats:
            image_files.append(str(file_path))
    
    if not image_files:
        print(f"在目录 {directory} 中未找到支持的图片文件")
        return 0
    
    print(f"找到 {len(image_files)} 个图片文件，开始批量处理...")
    
    for i, image_path in enumerate(image_files, 1):
        print(f"\n处理第 {i}/{len(image_files)} 个文件: {os.path.basename(image_path)}")
        
        if process_single_image(image_path, algorithm, radius):
            processed_count += 1
        else:
            print(f"跳过文件: {image_path}")
    
    logging.info(f"批量处理完成，成功处理 {processed_count}/{len(image_files)} 个文件")
    return processed_count

def show_advanced_help():
    """
    show_advanced_help 功能说明:
    # 显示高级工具的详细帮助信息
    # 输入: [无] | 输出: [打印帮助信息]
    """
    help_text = """
    ========================================
    高级图片去水印工具使用说明
    ========================================
    
    使用方法:
    python advanced_watermark_remover.py [选项] <图片路径或目录>
    
    选项:
    -a, --algorithm    选择算法 (telea/ns) [默认: telea]
    -r, --radius       修复半径 (1-10) [默认: 3]
    -b, --batch        批量处理模式
    -h, --help         显示帮助信息
    
    示例:
    # 处理单张图片
    python advanced_watermark_remover.py photo.jpg
    
    # 使用NS算法处理
    python advanced_watermark_remover.py -a ns photo.jpg
    
    # 批量处理目录
    python advanced_watermark_remover.py -b ./images/
    
    交互操作:
    - 鼠标左键: 选择水印区域
    - ESC: 确认选择并开始处理
    - R: 重新选择区域
    - B: 切换到画笔模式
    - T: 切换到矩形选择模式
    - +/-: 调整画笔大小
    - Q: 退出程序
    
    算法说明:
    - TELEA: 快速行进方法，适合简单水印
    - NS: Navier-Stokes方法，适合复杂纹理
    
    ========================================
    """
    print(help_text)

def main():
    """
    main 功能说明:
    # 高级工具主程序入口，支持命令行参数解析和多种处理模式
    # 输入: [命令行参数] | 输出: [处理结果]
    """
    # 设置日志
    logger = setup_logging()
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='高级图片去水印工具')
    parser.add_argument('path', nargs='?', help='图片文件路径或目录')
    parser.add_argument('-a', '--algorithm', choices=['telea', 'ns'], 
                       default='telea', help='选择修复算法')
    parser.add_argument('-r', '--radius', type=int, default=3, 
                       help='修复半径 (1-10)')
    parser.add_argument('-b', '--batch', action='store_true', 
                       help='批量处理模式')
    
    args = parser.parse_args()
    
    # 显示帮助
    if not args.path:
        show_advanced_help()
        return
    
    # 验证参数
    if not os.path.exists(args.path):
        print(f"错误: 路径不存在 - {args.path}")
        return
    
    if not 1 <= args.radius <= 10:
        print("错误: 修复半径必须在1-10之间")
        return
    
    try:
        if args.batch or os.path.isdir(args.path):
            # 批量处理模式
            processed = process_batch_images(args.path, args.algorithm, args.radius)
            print(f"\n批量处理完成，成功处理 {processed} 个文件")
        else:
            # 单文件处理模式
            success = process_single_image(args.path, args.algorithm, args.radius)
            if success:
                print("\n处理完成！")
            else:
                print("\n处理取消或失败")
                
    except KeyboardInterrupt:
        print("\n用户中断操作")
        logging.info("用户中断操作")
    except Exception as e:
        print(f"程序运行时发生错误: {str(e)}")
        logging.error(f"程序运行时发生错误: {str(e)}")

if __name__ == "__main__":
    main()