@echo off
REM 本地一键运行：抓取 + 总结（如果有 key）+ 生成网站
REM Usage: run.bat

setlocal

cd /d "%~dp0"

if not defined DEEPSEEK_API_KEY (
    echo [WARN] DEEPSEEK_API_KEY 未设置
    echo 将跳过 AI 总结，仅抓取 RSS + 显示原文
    echo.
    set "SKIP_SUMMARY=1"
)

echo === 1/3 抓取 RSS ===
python scripts\fetch_rss.py
if errorlevel 1 goto :err

if defined SKIP_SUMMARY goto :build

echo.
echo === 2/3 AI 总结 ===
python scripts\summarize.py
if errorlevel 1 (
    echo [WARN] 总结失败，继续生成网站
)

:build
echo.
echo === 3/3 生成网站 ===
python scripts\build_site.py
if errorlevel 1 goto :err

echo.
echo === 全部完成 ===
echo 网站文件: site\index.html
echo 可以用浏览器直接打开: site\index.html
echo 或运行本地预览: python -m http.server --directory site 8000
exit /b 0

:err
echo.
echo [ERROR] 执行失败
exit /b 1
