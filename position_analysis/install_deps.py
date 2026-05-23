#!/usr/bin/env python3
"""
安装持仓分析系统依赖包
解决架构兼容性问题
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """运行命令并显示进度"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            check=True
        )
        print(f"✅ {description}成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败")
        print(f"错误输出: {e.stderr}")
        return False

def main():
    print("=" * 60)
    print("持仓分析系统依赖安装")
    print("=" * 60)
    
    # 检查Python版本
    python_version = sys.version
    print(f"Python版本: {python_version}")
    
    # 检查架构
    import platform
    arch = platform.machine()
    print(f"系统架构: {arch}")
    
    # 安装核心依赖（不包含matplotlib）
    core_deps = [
        "pandas>=1.5.0",
        "numpy>=1.24.0", 
        "openpyxl>=3.1.0",
        "Jinja2>=3.1.0",
        "markdown>=3.4.0",
        "requests>=2.28.0"
    ]
    
    success_count = 0
    total_count = len(core_deps)
    
    for dep in core_deps:
        cmd = f"{sys.executable} -m pip install '{dep}' --quiet"
        if run_command(cmd, f"安装 {dep}"):
            success_count += 1
    
    print(f"\n📊 安装统计: {success_count}/{total_count} 个依赖包安装成功")
    
    # 尝试安装matplotlib（可选）
    print("\n🖼️ 尝试安装matplotlib（图表功能）...")
    try:
        # 先尝试直接安装
        cmd = f"{sys.executable} -m pip install 'matplotlib>=3.7.0' --quiet"
        if run_command(cmd, "安装matplotlib"):
            # 测试matplotlib是否可用
            import matplotlib
            print(f"✅ matplotlib版本: {matplotlib.__version__}")
            
            # 尝试安装seaborn
            cmd = f"{sys.executable} -m pip install 'seaborn>=0.12.0' --quiet"
            run_command(cmd, "安装seaborn")
    except Exception as e:
        print(f"⚠️ matplotlib安装失败: {e}")
        print("提示: 图表功能将受限，但文本报告功能仍可用")
    
    # 验证安装
    print("\n🔍 验证安装结果...")
    test_modules = [
        ("pandas", "pd"),
        ("numpy", "np"),
        ("openpyxl", ""),
        ("jinja2", "Jinja2"),
        ("markdown", ""),
        ("requests", "")
    ]
    
    for module_name, alias in test_modules:
        try:
            if alias:
                exec(f"import {module_name} as {alias}")
            else:
                exec(f"import {module_name}")
            print(f"✅ {module_name} 导入成功")
        except ImportError as e:
            print(f"❌ {module_name} 导入失败: {e}")
    
    print("\n" + "=" * 60)
    print("安装完成！")
    print("=" * 60)
    
    if success_count == total_count:
        print("🎉 所有核心依赖包安装成功！")
        print("系统可以生成文本报告，图表功能取决于matplotlib安装状态")
    else:
        print("⚠️ 部分依赖包安装失败")
        print("建议: 手动安装缺失的依赖包")
    
    print(f"\nPython路径: {sys.executable}")
    print(f"当前目录: {os.getcwd()}")
    print(f"运行命令: {sys.executable} src/main.py data/sample_portfolio.csv")

if __name__ == "__main__":
    main()