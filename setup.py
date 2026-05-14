"""
QuantPilot 安装配置文件

轻量级终端AI量化策略回测引擎CLI工具。
纯Python标准库实现，零外部依赖。
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="quantpilot",
    version="1.0.0",
    description="轻量级终端AI量化策略回测引擎CLI工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="QuantPilot Team",
    license="MIT",
    python_requires=">=3.6",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "quantpilot=quantpilot.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
    ],
)
