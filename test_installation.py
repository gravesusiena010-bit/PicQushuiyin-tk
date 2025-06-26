##########test_installation.py: 安装测试脚本 ##################
# 变更记录: [2025-06-26] @李祥光 [创建安装测试脚本，验证环境配置]########
# 输入: [无] | 输出: [测试结果报告]###############


###########################文件下的所有函数###########################
"""
test_python_version：测试Python版本
test_required_packages：测试必需包安装
test_optional_packages：测试可选包安装
test_file_permissions：测试文件权限
test_demo_processing：测试演示图片处理
run_all_tests：运行所有测试
print_test_result：打印测试结果
generate_test_report：生成测试报告
"""
###########################文件下的所有函数###########################

#########mermaid格式说明所有函数的调用关系说明开始#########
"""
flowchart TD
    A[程序启动] --> B[run_all_tests]
    B --> C[test_python_version]
    B --> D[test_required_packages]
    B --> E[test_optional_packages]
    B --> F[test_file_permissions]
    B --> G[test_demo_processing]
    C --> H[print_test_result]
    D --> H
    E --> H
    F --> H
    G --> H
    H --> I[generate_test_report]
    I --> J[显示最终结果]
"""
#########mermaid格式说明所有函数的调用关系说明结束#########

import sys
import os
import subprocess
import importlib
import tempfile
import time
from pathlib import Path
from datetime import datetime

class InstallationTester:
    """
    InstallationTester 功能说明:
    # 安装测试类，验证环境配置和依赖包安装
    # 输入: [无] | 输出: [详细的测试报告]
    """
    
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        
    def print_header(self):
        """
        print_header 功能说明:
        # 打印测试开始的标题信息
        # 输入: [无] | 输出: [打印标题]
        """
        print("="*60)
        print("🔧 高级图片去水印工具 - 安装测试")
        print("="*60)
        print(f"测试时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Python版本: {sys.version}")
        print(f"操作系统: {os.name}")
        print("="*60)
        print()
    
    def test_python_version(self):
        """
        test_python_version 功能说明:
        # 测试Python版本是否满足要求
        # 输入: [无] | 输出: [版本测试结果]
        """
        print("📋 测试 1: Python版本检查")
        
        try:
            version = sys.version_info
            version_str = f"{version.major}.{version.minor}.{version.micro}"
            
            if version >= (3, 8):
                self.test_results.append(("Python版本", "✅ 通过", f"版本 {version_str} 满足要求 (>=3.8)"))
                print(f"   ✅ Python版本: {version_str} (满足要求)")
                return True
            else:
                self.test_results.append(("Python版本", "❌ 失败", f"版本 {version_str} 不满足要求 (需要>=3.8)"))
                print(f"   ❌ Python版本: {version_str} (需要 >= 3.8)")
                return False
                
        except Exception as e:
            self.test_results.append(("Python版本", "❌ 错误", str(e)))
            print(f"   ❌ 版本检查失败: {e}")
            return False
    
    def test_required_packages(self):
        """
        test_required_packages 功能说明:
        # 测试必需的Python包是否已安装
        # 输入: [无] | 输出: [包安装测试结果]
        """
        print("\n📦 测试 2: 必需包安装检查")
        
        required_packages = {
            'cv2': 'opencv-python',
            'numpy': 'numpy',
            'PIL': 'Pillow',
            'tkinter': 'tkinter (内置)',
            'tkinterdnd2': 'tkinterdnd2'
        }
        
        all_passed = True
        
        for module_name, package_name in required_packages.items():
            try:
                if module_name == 'tkinter':
                    import tkinter
                    version = tkinter.TkVersion
                else:
                    module = importlib.import_module(module_name)
                    version = getattr(module, '__version__', '未知版本')
                
                self.test_results.append((f"包: {package_name}", "✅ 已安装", f"版本: {version}"))
                print(f"   ✅ {package_name}: 已安装 (版本: {version})")
                
            except ImportError:
                self.test_results.append((f"包: {package_name}", "❌ 未安装", "需要安装"))
                print(f"   ❌ {package_name}: 未安装")
                all_passed = False
            except Exception as e:
                self.test_results.append((f"包: {package_name}", "⚠️ 警告", str(e)))
                print(f"   ⚠️ {package_name}: 检查异常 - {e}")
        
        return all_passed
    
    def test_optional_packages(self):
        """
        test_optional_packages 功能说明:
        # 测试可选的Python包安装情况
        # 输入: [无] | 输出: [可选包测试结果]
        """
        print("\n🔧 测试 3: 可选包检查")
        
        optional_packages = {
            'pathlib': 'pathlib (内置)',
            'logging': 'logging (内置)',
            'threading': 'threading (内置)',
            'argparse': 'argparse (内置)'
        }
        
        for module_name, package_name in optional_packages.items():
            try:
                importlib.import_module(module_name)
                self.test_results.append((f"可选包: {package_name}", "✅ 可用", "正常"))
                print(f"   ✅ {package_name}: 可用")
            except ImportError:
                self.test_results.append((f"可选包: {package_name}", "❌ 不可用", "可能影响功能"))
                print(f"   ❌ {package_name}: 不可用")
    
    def test_file_permissions(self):
        """
        test_file_permissions 功能说明:
        # 测试文件读写权限
        # 输入: [无] | 输出: [权限测试结果]
        """
        print("\n📁 测试 4: 文件权限检查")
        
        try:
            # 测试当前目录写权限
            test_file = "test_write_permission.tmp"
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            
            self.test_results.append(("当前目录写权限", "✅ 正常", "可以创建和删除文件"))
            print("   ✅ 当前目录写权限: 正常")
            
            # 测试logs目录
            logs_dir = Path("logs")
            if not logs_dir.exists():
                logs_dir.mkdir(exist_ok=True)
                self.test_results.append(("logs目录", "✅ 已创建", "日志目录创建成功"))
                print("   ✅ logs目录: 已创建")
            else:
                self.test_results.append(("logs目录", "✅ 存在", "日志目录已存在"))
                print("   ✅ logs目录: 已存在")
            
            return True
            
        except Exception as e:
            self.test_results.append(("文件权限", "❌ 错误", str(e)))
            print(f"   ❌ 文件权限测试失败: {e}")
            return False
    
    def test_demo_processing(self):
        """
        test_demo_processing 功能说明:
        # 测试基本的图像处理功能
        # 输入: [无] | 输出: [图像处理测试结果]
        """
        print("\n🖼️ 测试 5: 图像处理功能")
        
        try:
            import cv2
            import numpy as np
            
            # 创建测试图像
            test_img = np.zeros((100, 100, 3), dtype=np.uint8)
            test_img[:] = (255, 255, 255)  # 白色背景
            
            # 添加一些内容
            cv2.rectangle(test_img, (20, 20), (80, 80), (0, 0, 255), -1)
            
            # 创建测试mask
            mask = np.zeros((100, 100), dtype=np.uint8)
            cv2.rectangle(mask, (30, 30), (70, 70), 255, -1)
            
            # 测试TELEA算法
            result_telea = cv2.inpaint(test_img, mask, 3, cv2.INPAINT_TELEA)
            self.test_results.append(("TELEA算法", "✅ 正常", "图像修复功能正常"))
            print("   ✅ TELEA算法: 正常")
            
            # 测试NS算法
            result_ns = cv2.inpaint(test_img, mask, 3, cv2.INPAINT_NS)
            self.test_results.append(("NS算法", "✅ 正常", "图像修复功能正常"))
            print("   ✅ NS算法: 正常")
            
            # 测试图像保存
            temp_file = "test_output.jpg"
            cv2.imwrite(temp_file, result_telea)
            if os.path.exists(temp_file):
                os.remove(temp_file)
                self.test_results.append(("图像保存", "✅ 正常", "可以保存处理结果"))
                print("   ✅ 图像保存: 正常")
            
            return True
            
        except Exception as e:
            self.test_results.append(("图像处理", "❌ 错误", str(e)))
            print(f"   ❌ 图像处理测试失败: {e}")
            return False
    
    def test_gui_components(self):
        """
        test_gui_components 功能说明:
        # 测试GUI组件是否可以正常创建
        # 输入: [无] | 输出: [GUI测试结果]
        """
        print("\n🖥️ 测试 6: GUI组件检查")
        
        try:
            import tkinter as tk
            from tkinter import ttk
            
            # 创建测试窗口
            root = tk.Tk()
            root.withdraw()  # 隐藏窗口
            
            # 测试基本组件
            frame = ttk.Frame(root)
            button = ttk.Button(frame, text="测试")
            label = ttk.Label(frame, text="测试标签")
            
            self.test_results.append(("tkinter基本组件", "✅ 正常", "可以创建GUI组件"))
            print("   ✅ tkinter基本组件: 正常")
            
            # 测试拖拽组件
            try:
                import tkinterdnd2
                self.test_results.append(("拖拽功能", "✅ 可用", "支持文件拖拽"))
                print("   ✅ 拖拽功能: 可用")
            except ImportError:
                self.test_results.append(("拖拽功能", "❌ 不可用", "tkinterdnd2未安装"))
                print("   ❌ 拖拽功能: 不可用")
            
            root.destroy()
            return True
            
        except Exception as e:
            self.test_results.append(("GUI组件", "❌ 错误", str(e)))
            print(f"   ❌ GUI组件测试失败: {e}")
            return False
    
    def generate_test_report(self):
        """
        generate_test_report 功能说明:
        # 生成详细的测试报告
        # 输入: [测试结果] | 输出: [格式化的测试报告]
        """
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "="*60)
        print("📊 测试报告汇总")
        print("="*60)
        
        # 统计结果
        passed = sum(1 for _, status, _ in self.test_results if "✅" in status)
        failed = sum(1 for _, status, _ in self.test_results if "❌" in status)
        warnings = sum(1 for _, status, _ in self.test_results if "⚠️" in status)
        total = len(self.test_results)
        
        print(f"总测试项: {total}")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        print(f"警告: {warnings} ⚠️")
        print(f"测试耗时: {duration.total_seconds():.2f} 秒")
        print()
        
        # 详细结果
        print("详细结果:")
        print("-" * 60)
        for test_name, status, details in self.test_results:
            print(f"{test_name:<25} {status:<10} {details}")
        
        print("\n" + "="*60)
        
        # 总体评估
        if failed == 0:
            print("🎉 恭喜！所有测试通过，环境配置正确！")
            print("✨ 您可以正常使用高级图片去水印工具")
        elif failed <= 2:
            print("⚠️ 大部分测试通过，但有少量问题需要解决")
            print("💡 建议检查失败的项目并重新安装相关依赖")
        else:
            print("❌ 多个测试失败，环境配置存在问题")
            print("🔧 请按照README.md重新配置环境")
        
        print("\n📖 如需帮助，请查看README.md或联系技术支持")
        print("="*60)
        
        # 保存报告到文件
        try:
            report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(f"高级图片去水印工具 - 安装测试报告\n")
                f.write(f"测试时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"测试耗时: {duration.total_seconds():.2f} 秒\n\n")
                
                f.write(f"统计结果:\n")
                f.write(f"总测试项: {total}\n")
                f.write(f"通过: {passed}\n")
                f.write(f"失败: {failed}\n")
                f.write(f"警告: {warnings}\n\n")
                
                f.write("详细结果:\n")
                for test_name, status, details in self.test_results:
                    f.write(f"{test_name}: {status} - {details}\n")
            
            print(f"\n📄 测试报告已保存到: {report_file}")
            
        except Exception as e:
            print(f"\n⚠️ 无法保存测试报告: {e}")
    
    def run_all_tests(self):
        """
        run_all_tests 功能说明:
        # 运行所有测试项目
        # 输入: [无] | 输出: [完整的测试流程]
        """
        self.print_header()
        
        # 运行所有测试
        tests = [
            self.test_python_version,
            self.test_required_packages,
            self.test_optional_packages,
            self.test_file_permissions,
            self.test_demo_processing,
            self.test_gui_components
        ]
        
        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"   ❌ 测试执行异常: {e}")
                self.test_results.append(("测试执行", "❌ 异常", str(e)))
        
        # 生成报告
        self.generate_test_report()

def main():
    """
    main 功能说明:
    # 主程序入口，启动安装测试
    # 输入: [无] | 输出: [运行完整测试流程]
    """
    tester = InstallationTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()