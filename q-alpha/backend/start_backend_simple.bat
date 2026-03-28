@echo off
chcp 65001 >nul
title 后端服务 - 极简启动

:: 直接进入你的后端目录
cd /d D:\qalpha\q-alpha-v2-complete\q-alpha\backend

:: 1. 检查并创建虚拟环境
if not exist "venv" (
    echo [1/4] 正在创建虚拟环境...
    py -m venv venv
)

:: 2. 激活虚拟环境
echo [2/4] 正在激活虚拟环境...
call venv\Scripts\activate.bat

:: 3. 安装依赖
echo [3/4] 正在安装依赖...
pip install -r requirements.txt

:: 4. 检查并创建 .env
if not exist ".env" (
    echo [4/4] 自动生成 .env 配置文件
    copy .env.example .env >nul 2>&1
)

:: 启动服务
echo.
echo ========================================
echo ✅ 后端启动完成！访问地址：http://localhost:8000
echo ========================================
echo.
py main.py

pause