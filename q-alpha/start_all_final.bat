@echo off
chcp 65001 >nul
color 0A
title Q-Alpha 量化系统 - 一键启动

echo.
echo ==============================================
echo          Q-Alpha 量化系统 - 一键启动
echo ==============================================
echo.

:: 启动后端（带日志输出）
start "【后端】API 服务运行中" cmd /k ^
cd /d "D:\qalpha\q-alpha-v2-complete\q-alpha\backend" ^
& if not exist venv (py -m venv venv) ^
& call venv\Scripts\activate.bat ^
& pip install -r requirements.txt ^
& if not exist .env (copy .env.example .env >nul 2>&1) ^
& echo 后端已启动 http://localhost:8000 ^
& py main.py > backend.log 2>&1

timeout /t 3 /nobreak >nul

:: 启动前端
start "【前端】页面服务运行中" cmd /k ^
cd /d "D:\qalpha\q-alpha-v2-complete\q-alpha\frontend" ^
& npm install ^
& echo 前端已启动 http://localhost:3000 ^
& npm run dev > frontend.log 2>&1

timeout /t 2 /nobreak >nul

:: 后端日志监听（修复版，先创建空日志文件）
start "【后端日志实时监听】" cmd /k ^
cd /d "D:\qalpha\q-alpha-v2-complete\q-alpha\backend" ^
& if not exist backend.log (type nul > backend.log) ^
& echo 实时查看后端日志 ^
& powershell "Get-Content backend.log -Wait -Encoding UTF8"

:: 前端日志监听（修复版）
start "【前端日志实时监听】" cmd /k ^
cd /d "D:\qalpha\q-alpha-v2-complete\q-alpha\frontend" ^
& if not exist frontend.log (type nul > frontend.log) ^
& echo 实时查看前端日志 ^
& powershell "Get-Content frontend.log -Wait -Encoding UTF8"

echo.
echo ==============================================
echo           启动完成！
echo 后端：http://localhost:8000
echo 前端：http://localhost:3000
echo ==============================================
echo.
pause >nul