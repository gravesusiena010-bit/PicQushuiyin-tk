##########watermark_remover_gui.py: 图片去水印工具GUI界面 ##################
# 变更记录: [2025-06-26] @李祥光 [创建现代化tkinter界面，支持拖拽、预览和批量处理]########
# 输入: [用户交互操作] | 输出: [去水印后的图片文件]###############


###########################文件下的所有函数###########################
"""
WatermarkRemoverGUI：主界面类，管理所有GUI组件和交互
create_widgets：创建界面组件
setup_styles：设置界面样式
select_single_file：选择单个文件
select_batch_folder：选择批量处理文件夹
start_processing：开始处理图片
process_image_with_gui：带GUI的图片处理
update_progress：更新进度条
show_preview：显示预览窗口
reset_interface：重置界面
show_help：显示帮助信息
on_drop：拖拽文件处理
"""
###########################文件下的所有函数###########################

#########mermaid格式说明所有函数的调用关系说明开始#########
"""
flowchart TD
    A[程序启动] --> B[WatermarkRemoverGUI初始化]
    B --> C[create_widgets]
    C --> D[setup_styles]
    D --> E[界面显示]
    E --> F{用户操作}
    F -->|选择文件| G[select_single_file]
    F -->|选择文件夹| H[select_batch_folder]
    F -->|拖拽文件| I[on_drop]
    F -->|开始处理| J[start_processing]
    J --> K[process_image_with_gui]
    K --> L[update_progress]
    L --> M[show_preview]
    M --> N[保存结果]
    F -->|重置| O[reset_interface]
    F -->|帮助| P[show_help]
"""
#########mermaid格式说明所有函数的调用关系说明结束#########

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import tkinter.font as tkFont
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import threading
import time
from pathlib import Path
import logging
from datetime import datetime
from tkinterdnd2 import DND_FILES, TkinterDnD

# 导入原有的处理函数
from advanced_watermark_remover import (
    load_image_safe, remove_watermark_telea, remove_watermark_ns,
    save_result_with_options, setup_logging
)

class WatermarkRemoverGUI:
    """
    WatermarkRemoverGUI 功能说明:
    # 图片去水印工具的现代化GUI界面，提供直观的用户体验
    # 输入: [用户交互操作] | 输出: [处理后的图片和界面反馈]
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("高级图片去水印工具 v2.0")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # 设置图标和样式
        self.setup_styles()
        
        # 初始化变量
        self.selected_files = []
        self.current_image = None
        self.current_image_path = None
        self.mask = None
        self.processed_image = None
        self.is_processing = False
        self.drawing = False
        self.rect_start = None
        self.selection_mode = 'rectangle'
        
        # 算法选择变量
        self.algorithm_var = tk.StringVar(value="telea")
        self.radius_var = tk.IntVar(value=3)
        self.quality_var = tk.IntVar(value=95)
        self.batch_mode_var = tk.BooleanVar(value=False)
        
        # 创建界面组件
        self.create_widgets()
        
        # 设置日志
        self.logger = setup_logging()
        
        # 启用拖拽功能
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)
    
    def setup_styles(self):
        """
        setup_styles 功能说明:
        # 设置现代化的界面样式和主题
        # 输入: [无] | 输出: [配置ttk样式]
        """
        style = ttk.Style()
        style.theme_use('clam')
        
        # 自定义样式
        style.configure('Title.TLabel', font=('Microsoft YaHei', 16, 'bold'), 
                       foreground='#2c3e50', background='#f0f0f0')
        style.configure('Subtitle.TLabel', font=('Microsoft YaHei', 10), 
                       foreground='#34495e', background='#f0f0f0')
        style.configure('Custom.TButton', font=('Microsoft YaHei', 9))
        style.configure('Success.TLabel', foreground='#27ae60', background='#f0f0f0')
        style.configure('Error.TLabel', foreground='#e74c3c', background='#f0f0f0')
        
        # 进度条样式
        style.configure('Custom.Horizontal.TProgressbar', 
                       background='#3498db', troughcolor='#ecf0f1')
    
    def create_widgets(self):
        """
        create_widgets 功能说明:
        # 创建所有GUI组件，包括文件选择、参数设置、预览等区域
        # 输入: [无] | 输出: [创建完整的用户界面]
        """
        # 主标题
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        ttk.Label(title_frame, text="🎨 高级图片去水印工具", 
                 style='Title.TLabel').pack(side='left')
        ttk.Label(title_frame, text="支持拖拽文件 | 实时预览 | 批量处理", 
                 style='Subtitle.TLabel').pack(side='right')
        
        # 创建主要内容区域
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 左侧控制面板
        self.create_control_panel(main_frame)
        
        # 右侧预览面板
        self.create_preview_panel(main_frame)
        
        # 底部状态栏
        self.create_status_bar()
    
    def create_control_panel(self, parent):
        """
        create_control_panel 功能说明:
        # 创建左侧控制面板，包含文件选择、参数设置等
        # 输入: [父容器] | 输出: [控制面板组件]
        """
        self.control_frame = ttk.LabelFrame(parent, text="📁 控制面板", padding=15)
        self.control_frame.pack(side='left', fill='y', padx=(0, 10))
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(self.control_frame, text="文件选择", padding=10)
        file_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Button(file_frame, text="📄 选择单个文件", 
                  command=self.select_single_file, 
                  style='Custom.TButton').pack(fill='x', pady=2)
        
        ttk.Button(file_frame, text="📁 选择文件夹(批量)", 
                  command=self.select_batch_folder, 
                  style='Custom.TButton').pack(fill='x', pady=2)
        
        # 拖拽提示
        drag_label = ttk.Label(file_frame, text="💡 或直接拖拽文件到此窗口", 
                              style='Subtitle.TLabel')
        drag_label.pack(pady=5)
        
        # 算法选择区域
        algo_frame = ttk.LabelFrame(self.control_frame, text="算法设置", padding=10)
        algo_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(algo_frame, text="修复算法:").pack(anchor='w')
        algo_radio_frame = ttk.Frame(algo_frame)
        algo_radio_frame.pack(fill='x', pady=5)
        
        ttk.Radiobutton(algo_radio_frame, text="TELEA (快速)", 
                       variable=self.algorithm_var, value="telea").pack(anchor='w')
        ttk.Radiobutton(algo_radio_frame, text="Navier-Stokes (精细)", 
                       variable=self.algorithm_var, value="ns").pack(anchor='w')
        
        # 参数调整
        ttk.Label(algo_frame, text="修复半径:").pack(anchor='w', pady=(10, 0))
        radius_frame = ttk.Frame(algo_frame)
        radius_frame.pack(fill='x', pady=5)
        
        ttk.Scale(radius_frame, from_=1, to=10, variable=self.radius_var, 
                 orient='horizontal').pack(side='left', fill='x', expand=True)
        ttk.Label(radius_frame, textvariable=self.radius_var, width=3).pack(side='right')
        
        ttk.Label(algo_frame, text="输出质量:").pack(anchor='w', pady=(10, 0))
        quality_frame = ttk.Frame(algo_frame)
        quality_frame.pack(fill='x', pady=5)
        
        ttk.Scale(quality_frame, from_=50, to=100, variable=self.quality_var, 
                 orient='horizontal').pack(side='left', fill='x', expand=True)
        ttk.Label(quality_frame, textvariable=self.quality_var, width=3).pack(side='right')
        
        # 处理选项
        option_frame = ttk.LabelFrame(self.control_frame, text="处理选项", padding=10)
        option_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Checkbutton(option_frame, text="批量处理模式", 
                       variable=self.batch_mode_var).pack(anchor='w')
        
        # 操作按钮
        button_frame = ttk.Frame(self.control_frame)
        button_frame.pack(fill='x', pady=(0, 15))
        
        self.process_btn = ttk.Button(button_frame, text="🚀 开始处理", 
                                     command=self.start_processing, 
                                     style='Custom.TButton')
        self.process_btn.pack(fill='x', pady=2)
        
        ttk.Button(button_frame, text="🔄 重置", 
                  command=self.reset_interface, 
                  style='Custom.TButton').pack(fill='x', pady=2)
        
        ttk.Button(button_frame, text="❓ 帮助", 
                  command=self.show_help, 
                  style='Custom.TButton').pack(fill='x', pady=2)
        
        # 进度条
        self.progress = ttk.Progressbar(self.control_frame, 
                                       style='Custom.Horizontal.TProgressbar')
        self.progress.pack(fill='x', pady=(0, 10))
        
        # 文件列表
        list_frame = ttk.LabelFrame(self.control_frame, text="选中的文件", padding=10)
        list_frame.pack(fill='both', expand=True)
        
        self.file_listbox = tk.Listbox(list_frame, height=8, 
                                      font=('Microsoft YaHei', 9))
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', 
                                 command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.file_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def create_preview_panel(self, parent):
        """
        create_preview_panel 功能说明:
        # 创建右侧预览面板，显示原图和处理结果
        # 输入: [父容器] | 输出: [预览面板组件]
        """
        preview_frame = ttk.LabelFrame(parent, text="🖼️ 预览面板", padding=15)
        preview_frame.pack(side='right', fill='both', expand=True)
        
        # 预览标签页
        self.notebook = ttk.Notebook(preview_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # 原图标签页
        self.original_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.original_frame, text="原图")
        
        self.original_canvas = tk.Canvas(self.original_frame, bg='white', 
                                        relief='sunken', bd=2)
        self.original_canvas.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 处理结果标签页
        self.result_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.result_frame, text="处理结果")
        
        self.result_canvas = tk.Canvas(self.result_frame, bg='white', 
                                      relief='sunken', bd=2)
        self.result_canvas.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 对比视图标签页
        self.compare_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.compare_frame, text="对比视图")
        
        self.compare_canvas = tk.Canvas(self.compare_frame, bg='white', 
                                       relief='sunken', bd=2)
        self.compare_canvas.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_status_bar(self):
        """
        create_status_bar 功能说明:
        # 创建底部状态栏，显示当前状态和提示信息
        # 输入: [无] | 输出: [状态栏组件]
        """
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill='x', side='bottom', padx=20, pady=(0, 20))
        
        self.status_label = ttk.Label(status_frame, text="就绪 - 请选择要处理的图片文件", 
                                     style='Subtitle.TLabel')
        self.status_label.pack(side='left')
        
        # 时间显示
        self.time_label = ttk.Label(status_frame, text="", style='Subtitle.TLabel')
        self.time_label.pack(side='right')
        self.update_time()
    
    def update_time(self):
        """
        update_time 功能说明:
        # 更新状态栏的时间显示
        # 输入: [无] | 输出: [更新时间显示]
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def select_single_file(self):
        """
        select_single_file 功能说明:
        # 选择单个图片文件进行处理
        # 输入: [用户文件选择] | 输出: [更新文件列表和预览]
        """
        file_types = [
            ('图片文件', '*.jpg *.jpeg *.png *.bmp *.tiff *.tif'),
            ('JPEG文件', '*.jpg *.jpeg'),
            ('PNG文件', '*.png'),
            ('所有文件', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=file_types
        )
        
        if filename:
            self.selected_files = [filename]
            self.update_file_list()
            self.load_preview(filename)
            self.status_label.config(text=f"已选择文件: {os.path.basename(filename)}")
    
    def select_batch_folder(self):
        """
        select_batch_folder 功能说明:
        # 选择文件夹进行批量处理
        # 输入: [用户文件夹选择] | 输出: [更新文件列表]
        """
        folder = filedialog.askdirectory(title="选择包含图片的文件夹")
        
        if folder:
            supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
            image_files = []
            
            for file_path in Path(folder).rglob('*'):
                if file_path.suffix.lower() in supported_formats:
                    image_files.append(str(file_path))
            
            if image_files:
                self.selected_files = image_files
                self.batch_mode_var.set(True)
                self.update_file_list()
                self.status_label.config(text=f"已选择 {len(image_files)} 个图片文件")
                
                if image_files:
                    self.load_preview(image_files[0])
            else:
                messagebox.showwarning("警告", "所选文件夹中没有找到支持的图片文件")
    
    def on_drop(self, event):
        """
        on_drop 功能说明:
        # 处理拖拽文件事件
        # 输入: [拖拽事件] | 输出: [更新文件列表]
        """
        files = self.root.tk.splitlist(event.data)
        image_files = []
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        
        for file_path in files:
            if os.path.isfile(file_path):
                if Path(file_path).suffix.lower() in supported_formats:
                    image_files.append(file_path)
            elif os.path.isdir(file_path):
                for img_file in Path(file_path).rglob('*'):
                    if img_file.suffix.lower() in supported_formats:
                        image_files.append(str(img_file))
        
        if image_files:
            self.selected_files = image_files
            if len(image_files) > 1:
                self.batch_mode_var.set(True)
            self.update_file_list()
            self.load_preview(image_files[0])
            self.status_label.config(text=f"已拖拽 {len(image_files)} 个图片文件")
        else:
            messagebox.showwarning("警告", "拖拽的文件中没有支持的图片格式")
    
    def update_file_list(self):
        """
        update_file_list 功能说明:
        # 更新文件列表显示
        # 输入: [无] | 输出: [更新界面文件列表]
        """
        self.file_listbox.delete(0, tk.END)
        for file_path in self.selected_files:
            self.file_listbox.insert(tk.END, os.path.basename(file_path))
    
    def load_preview(self, image_path):
        """
        load_preview 功能说明:
        # 加载图片预览到界面
        # 输入: [图片路径] | 输出: [显示图片预览]
        """
        try:
            # 使用PIL加载图片
            pil_image = Image.open(image_path)
            
            # 计算合适的显示尺寸
            canvas_width = self.original_canvas.winfo_width()
            canvas_height = self.original_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 400, 300
            
            # 保持宽高比缩放
            img_ratio = pil_image.width / pil_image.height
            canvas_ratio = canvas_width / canvas_height
            
            if img_ratio > canvas_ratio:
                new_width = canvas_width - 20
                new_height = int(new_width / img_ratio)
            else:
                new_height = canvas_height - 20
                new_width = int(new_height * img_ratio)
            
            # 缩放图片
            resized_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(resized_image)
            
            # 显示在画布上
            self.original_canvas.delete("all")
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.original_canvas.create_image(x, y, anchor='nw', image=self.photo)
            
            # 保存当前图片信息
            self.current_image = cv2.imread(image_path)
            self.current_image_path = image_path
            self.mask = np.zeros(self.current_image.shape[:2], np.uint8)
            
            # 绑定鼠标事件用于水印区域选择
            self.setup_mouse_events()
            
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片预览: {str(e)}")
    
    def setup_mouse_events(self):
        """
        setup_mouse_events 功能说明:
        # 设置鼠标事件处理，支持手动选择水印区域
        # 输入: [无] | 输出: [绑定鼠标事件]
        """
        self.drawing = False
        self.rect_start = None
        self.selection_mode = 'rectangle'  # 'rectangle' 或 'brush'
        
        # 绑定鼠标事件
        self.original_canvas.bind('<Button-1>', self.on_mouse_down)
        self.original_canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.original_canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.original_canvas.bind('<Button-3>', self.clear_selection)  # 右键清除选择
        
        # 添加选择模式切换按钮
        self.add_selection_controls()
    
    def add_selection_controls(self):
        """
        add_selection_controls 功能说明:
        # 添加水印选择控制按钮
        # 输入: [无] | 输出: [创建选择控制界面]
        """
        # 在控制面板中添加选择模式控件
        # 找到算法设置框架
        algo_frame = None
        for child in self.control_frame.winfo_children():
            if isinstance(child, ttk.LabelFrame) and child.cget('text') == '算法设置':
                algo_frame = child
                break
        
        if algo_frame is None:
            # 如果找不到算法框架，创建一个新的
            algo_frame = self.control_frame
        
        selection_frame = ttk.LabelFrame(algo_frame, text="水印选择", padding=10)
        selection_frame.pack(fill='x', pady=(0, 10))
        
        self.selection_mode_var = tk.StringVar(value='rectangle')
        
        ttk.Radiobutton(selection_frame, text="矩形选择", 
                       variable=self.selection_mode_var, value='rectangle',
                       command=self.change_selection_mode).pack(anchor='w')
        
        ttk.Radiobutton(selection_frame, text="画笔选择", 
                       variable=self.selection_mode_var, value='brush',
                       command=self.change_selection_mode).pack(anchor='w')
        
        # 画笔大小控制
        brush_frame = ttk.Frame(selection_frame)
        brush_frame.pack(fill='x', pady=5)
        
        ttk.Label(brush_frame, text="画笔大小:").pack(side='left')
        self.brush_size_var = tk.IntVar(value=10)
        ttk.Scale(brush_frame, from_=5, to=50, variable=self.brush_size_var, 
                 orient='horizontal', length=100).pack(side='left', padx=5)
        ttk.Label(brush_frame, textvariable=self.brush_size_var, width=3).pack(side='left')
        
        # 清除选择按钮
        ttk.Button(selection_frame, text="清除选择", 
                  command=self.clear_selection).pack(fill='x', pady=5)
    
    def change_selection_mode(self):
        """
        change_selection_mode 功能说明:
        # 切换水印选择模式
        # 输入: [用户选择] | 输出: [更新选择模式]
        """
        self.selection_mode = self.selection_mode_var.get()
        self.status_label.config(text=f"选择模式: {self.selection_mode} - 在图片上{'拖拽矩形' if self.selection_mode == 'rectangle' else '画笔涂抹'}选择水印区域")
    
    def on_mouse_down(self, event):
        """
        on_mouse_down 功能说明:
        # 处理鼠标按下事件
        # 输入: [鼠标事件] | 输出: [开始选择操作]
        """
        if self.current_image is None:
            return
        
        # 转换画布坐标到图片坐标
        img_x, img_y = self.canvas_to_image_coords(event.x, event.y)
        if img_x is None or img_y is None:
            return
        
        if self.selection_mode == 'rectangle':
            self.rect_start = (img_x, img_y)
            self.drawing = True
        elif self.selection_mode == 'brush':
            self.drawing = True
            brush_size = self.brush_size_var.get()
            cv2.circle(self.mask, (img_x, img_y), brush_size, 255, -1)
            self.update_preview_with_mask()
    
    def on_mouse_drag(self, event):
        """
        on_mouse_drag 功能说明:
        # 处理鼠标拖拽事件
        # 输入: [鼠标事件] | 输出: [更新选择区域]
        """
        if not self.drawing or self.current_image is None:
            return
        
        img_x, img_y = self.canvas_to_image_coords(event.x, event.y)
        if img_x is None or img_y is None:
            return
        
        if self.selection_mode == 'brush':
            brush_size = self.brush_size_var.get()
            cv2.circle(self.mask, (img_x, img_y), brush_size, 255, -1)
            self.update_preview_with_mask()
    
    def on_mouse_up(self, event):
        """
        on_mouse_up 功能说明:
        # 处理鼠标释放事件
        # 输入: [鼠标事件] | 输出: [完成选择操作]
        """
        if not self.drawing or self.current_image is None:
            return
        
        img_x, img_y = self.canvas_to_image_coords(event.x, event.y)
        if img_x is None or img_y is None:
            return
        
        if self.selection_mode == 'rectangle' and self.rect_start:
            # 绘制矩形到mask
            cv2.rectangle(self.mask, self.rect_start, (img_x, img_y), 255, -1)
            self.update_preview_with_mask()
            self.rect_start = None
        
        self.drawing = False
    
    def canvas_to_image_coords(self, canvas_x, canvas_y):
        """
        canvas_to_image_coords 功能说明:
        # 将画布坐标转换为图片坐标
        # 输入: [画布坐标] | 输出: [图片坐标]
        """
        if self.current_image is None:
            return None, None
        
        # 获取画布和图片尺寸
        canvas_width = self.original_canvas.winfo_width()
        canvas_height = self.original_canvas.winfo_height()
        img_height, img_width = self.current_image.shape[:2]
        
        # 计算图片在画布中的显示尺寸和位置
        img_ratio = img_width / img_height
        canvas_ratio = canvas_width / canvas_height
        
        if img_ratio > canvas_ratio:
            display_width = canvas_width - 20
            display_height = int(display_width / img_ratio)
        else:
            display_height = canvas_height - 20
            display_width = int(display_height * img_ratio)
        
        # 图片在画布中的偏移
        offset_x = (canvas_width - display_width) // 2
        offset_y = (canvas_height - display_height) // 2
        
        # 检查点击是否在图片区域内
        if (canvas_x < offset_x or canvas_x > offset_x + display_width or
            canvas_y < offset_y or canvas_y > offset_y + display_height):
            return None, None
        
        # 转换为图片坐标
        relative_x = canvas_x - offset_x
        relative_y = canvas_y - offset_y
        
        img_x = int((relative_x / display_width) * img_width)
        img_y = int((relative_y / display_height) * img_height)
        
        # 确保坐标在图片范围内
        img_x = max(0, min(img_x, img_width - 1))
        img_y = max(0, min(img_y, img_height - 1))
        
        return img_x, img_y
    
    def update_preview_with_mask(self):
        """
        update_preview_with_mask 功能说明:
        # 更新预览图片，显示选中的水印区域
        # 输入: [无] | 输出: [更新预览显示]
        """
        if self.current_image is None:
            return
        
        # 创建带有mask覆盖的预览图片
        preview_img = self.current_image.copy()
        
        # 在选中区域添加红色半透明覆盖
        mask_colored = cv2.cvtColor(self.mask, cv2.COLOR_GRAY2BGR)
        mask_colored[:, :, 0] = 0  # 移除蓝色通道
        mask_colored[:, :, 1] = 0  # 移除绿色通道
        
        # 应用半透明覆盖
        alpha = 0.3
        preview_img = cv2.addWeighted(preview_img, 1-alpha, mask_colored, alpha, 0)
        
        # 转换为PIL格式并显示
        preview_rgb = cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB)
        pil_preview = Image.fromarray(preview_rgb)
        
        # 计算显示尺寸（与load_preview中的逻辑相同）
        canvas_width = self.original_canvas.winfo_width()
        canvas_height = self.original_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = 400, 300
        
        img_ratio = pil_preview.width / pil_preview.height
        canvas_ratio = canvas_width / canvas_height
        
        if img_ratio > canvas_ratio:
            new_width = canvas_width - 20
            new_height = int(new_width / img_ratio)
        else:
            new_height = canvas_height - 20
            new_width = int(new_height * img_ratio)
        
        resized_preview = pil_preview.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_preview)
        
        # 更新画布显示
        self.original_canvas.delete("all")
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        self.original_canvas.create_image(x, y, anchor='nw', image=self.photo)
    
    def clear_selection(self, event=None):
        """
        clear_selection 功能说明:
        # 清除当前的水印选择
        # 输入: [事件(可选)] | 输出: [清除mask并更新预览]
        """
        if self.current_image is not None:
            self.mask = np.zeros(self.current_image.shape[:2], np.uint8)
            self.load_preview(self.current_image_path)  # 重新加载原始预览
            self.status_label.config(text="已清除水印选择")
    
    def start_processing(self):
        """
        start_processing 功能说明:
        # 开始处理选中的图片文件
        # 输入: [用户操作] | 输出: [启动处理线程]
        """
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择要处理的图片文件")
            return
        
        if self.is_processing:
            messagebox.showinfo("提示", "正在处理中，请稍候...")
            return
        
        # 在新线程中处理，避免界面卡顿
        self.is_processing = True
        self.process_btn.config(state='disabled', text="处理中...")
        
        processing_thread = threading.Thread(target=self.process_images_thread)
        processing_thread.daemon = True
        processing_thread.start()
    
    def process_images_thread(self):
        """
        process_images_thread 功能说明:
        # 在后台线程中处理图片，避免界面冻结
        # 输入: [无] | 输出: [处理图片并更新界面]
        """
        try:
            total_files = len(self.selected_files)
            processed_count = 0
            
            for i, file_path in enumerate(self.selected_files):
                # 更新进度
                progress = (i / total_files) * 100
                self.root.after(0, lambda p=progress: self.update_progress(p))
                
                # 更新状态
                filename = os.path.basename(file_path)
                self.root.after(0, lambda f=filename: 
                               self.status_label.config(text=f"正在处理: {f}"))
                
                # 处理图片
                success = self.process_single_image_gui(file_path)
                if success:
                    processed_count += 1
                
                time.sleep(0.1)  # 短暂延迟，让界面更新
            
            # 处理完成
            self.root.after(0, lambda: self.update_progress(100))
            self.root.after(0, lambda: 
                           self.status_label.config(text=f"处理完成: {processed_count}/{total_files} 个文件"))
            
        except Exception as e:
            self.root.after(0, lambda: 
                           messagebox.showerror("错误", f"处理过程中发生错误: {str(e)}"))
        finally:
            self.root.after(0, self.processing_finished)
    
    def process_single_image_gui(self, image_path):
        """
        process_single_image_gui 功能说明:
        # 处理单张图片的GUI版本，使用用户选择的水印区域
        # 输入: [图片路径] | 输出: [处理是否成功]
        """
        try:
            # 加载图片
            img = load_image_safe(image_path)
            if img is None:
                return False
            
            # 使用用户选择的mask或自动检测
            if image_path == self.current_image_path and np.sum(self.mask) > 0:
                # 使用用户手动选择的区域
                mask = self.mask.copy()
                self.logger.info(f"使用手动选择的水印区域，面积: {np.sum(mask > 0)} 像素")
            else:
                # 自动检测水印区域（用于批量处理或未选择区域的情况）
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                
                mask = np.zeros(gray.shape, np.uint8)
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if 100 < area < 5000:
                        cv2.fillPoly(mask, [contour], 255)
                
                if np.sum(mask) == 0:
                    h, w = mask.shape
                    cv2.rectangle(mask, (w-100, h-50), (w-10, h-10), 255, -1)
                
                self.logger.info(f"使用自动检测的水印区域，面积: {np.sum(mask > 0)} 像素")
            
            # 应用选择的算法
            algorithm = self.algorithm_var.get()
            radius = self.radius_var.get()
            
            if algorithm == 'telea':
                result = remove_watermark_telea(img, mask, radius)
            else:
                result = remove_watermark_ns(img, mask, radius)
            
            # 保存结果
            quality = self.quality_var.get()
            output_path = save_result_with_options(result, image_path, 
                                                 '_no_watermark', quality)
            
            if output_path:
                # 更新预览（仅对第一张图片）
                if image_path == self.selected_files[0]:
                    self.root.after(0, lambda: self.show_result_preview(result))
                return True
            
        except Exception as e:
            self.logger.error(f"处理图片时发生错误: {str(e)}")
            return False
        
        return False
    
    def show_result_preview(self, result_image):
        """
        show_result_preview 功能说明:
        # 显示处理结果预览
        # 输入: [处理后的图片] | 输出: [更新预览界面]
        """
        try:
            # 转换为PIL格式
            result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
            pil_result = Image.fromarray(result_rgb)
            
            # 计算显示尺寸
            canvas_width = self.result_canvas.winfo_width()
            canvas_height = self.result_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 400, 300
            
            # 缩放图片
            img_ratio = pil_result.width / pil_result.height
            canvas_ratio = canvas_width / canvas_height
            
            if img_ratio > canvas_ratio:
                new_width = canvas_width - 20
                new_height = int(new_width / img_ratio)
            else:
                new_height = canvas_height - 20
                new_width = int(new_height * img_ratio)
            
            resized_result = pil_result.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.result_photo = ImageTk.PhotoImage(resized_result)
            
            # 显示结果
            self.result_canvas.delete("all")
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.result_canvas.create_image(x, y, anchor='nw', image=self.result_photo)
            
            # 切换到结果标签页
            self.notebook.select(1)
            
        except Exception as e:
            messagebox.showerror("错误", f"无法显示结果预览: {str(e)}")
    
    def update_progress(self, value):
        """
        update_progress 功能说明:
        # 更新进度条显示
        # 输入: [进度值] | 输出: [更新进度条]
        """
        self.progress['value'] = value
        self.root.update_idletasks()
    
    def processing_finished(self):
        """
        processing_finished 功能说明:
        # 处理完成后的清理工作
        # 输入: [无] | 输出: [重置界面状态]
        """
        self.is_processing = False
        self.process_btn.config(state='normal', text="🚀 开始处理")
        self.progress['value'] = 0
    
    def reset_interface(self):
        """
        reset_interface 功能说明:
        # 重置界面到初始状态
        # 输入: [用户操作] | 输出: [清空所有选择和预览]
        """
        self.selected_files = []
        self.current_image = None
        self.processed_image = None
        
        self.file_listbox.delete(0, tk.END)
        self.original_canvas.delete("all")
        self.result_canvas.delete("all")
        self.compare_canvas.delete("all")
        
        self.progress['value'] = 0
        self.batch_mode_var.set(False)
        self.status_label.config(text="就绪 - 请选择要处理的图片文件")
        
        # 切换回原图标签页
        self.notebook.select(0)
    
    def show_help(self):
        """
        show_help 功能说明:
        # 显示帮助信息窗口
        # 输入: [用户操作] | 输出: [弹出帮助窗口]
        """
        help_window = tk.Toplevel(self.root)
        help_window.title("使用帮助")
        help_window.geometry("600x500")
        help_window.configure(bg='#f0f0f0')
        
        # 创建滚动文本框
        text_frame = ttk.Frame(help_window)
        text_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        help_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                             font=('Microsoft YaHei', 10))
        help_text.pack(fill='both', expand=True)
        
        help_content = """
🎨 高级图片去水印工具使用指南

📁 文件选择:
• 点击"选择单个文件"处理单张图片
• 点击"选择文件夹(批量)"批量处理整个文件夹
• 直接拖拽文件或文件夹到窗口中

⚙️ 算法设置:
• TELEA算法: 快速处理，适合简单水印
• Navier-Stokes算法: 精细处理，适合复杂纹理
• 修复半径: 控制修复区域大小(1-10)
• 输出质量: 控制保存图片的质量(50-100)

🖼️ 预览功能:
• 原图标签页: 显示原始图片
• 处理结果标签页: 显示去水印后的效果
• 对比视图标签页: 并排对比原图和结果

💡 使用技巧:
• 支持JPG、PNG、BMP、TIFF等常见格式
• 批量处理时会自动检测水印区域
• 处理后的文件会保存在原文件同目录
• 文件名会自动添加"_no_watermark"后缀

⚠️ 注意事项:
• 处理大文件时请耐心等待
• 建议先用单张图片测试效果
• 复杂水印可能需要手动调整参数
• 处理过程中请勿关闭程序

🔧 快捷操作:
• 拖拽文件: 快速添加文件
• 重置按钮: 清空所有选择
• 进度条: 显示处理进度
• 状态栏: 显示当前操作状态

📞 技术支持:
如遇问题请查看日志文件或联系技术支持。
        """
        
        help_text.insert('1.0', help_content)
        help_text.config(state='disabled')

def main():
    """
    main 功能说明:
    # 程序主入口，初始化GUI界面
    # 输入: [无] | 输出: [启动GUI应用程序]
    """
    # 创建支持拖拽的根窗口
    root = TkinterDnD.Tk()
    
    # 设置窗口图标（如果有的话）
    try:
        root.iconbitmap('icon.ico')
    except:
        pass  # 如果没有图标文件就忽略
    
    # 创建应用程序
    app = WatermarkRemoverGUI(root)
    
    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
    main()