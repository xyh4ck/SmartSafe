#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Celery Flower 管理脚本
# 用法: ./celery_flower.sh {start|stop|status|restart}
# ============================================================

# Resolve backend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}"

# PID 文件路径
PID_FILE="${BACKEND_DIR}/celery_flower.pid"
LOG_FILE="${BACKEND_DIR}/logs/celery_flower.log"

# Allow overriding via environment variables
: "${CELERY_APP:=app.core.celery_app:celery_app}"
: "${FLOWER_ADDRESS:=0.0.0.0}"
: "${FLOWER_PORT:=5555}"
: "${FLOWER_BASIC_AUTH:=}"
: "${FLOWER_EXTRA_ARGS:=}"

# 确保日志目录存在
mkdir -p "$(dirname "${LOG_FILE}")"

# 获取 flower 进程 PID
get_pid() {
    if [[ -f "${PID_FILE}" ]]; then
        cat "${PID_FILE}"
    else
        echo ""
    fi
}

# 检查进程是否运行
is_running() {
    local pid
    pid=$(get_pid)
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# 启动 flower
do_start() {
    if is_running; then
        echo "[celery_flower] Flower 已在运行中 (PID: $(get_pid))"
        return 0
    fi

    echo "[celery_flower] 启动 Celery Flower..."
    echo "[celery_flower] BACKEND_DIR=${BACKEND_DIR}"
    echo "[celery_flower] CELERY_APP=${CELERY_APP}"
    echo "[celery_flower] FLOWER_ADDRESS=${FLOWER_ADDRESS}"
    echo "[celery_flower] FLOWER_PORT=${FLOWER_PORT}"

    cd "${BACKEND_DIR}"

    # 构建认证参数
    AUTH_ARGS=""
    if [[ -n "${FLOWER_BASIC_AUTH}" ]]; then
        AUTH_ARGS="--basic_auth=${FLOWER_BASIC_AUTH}"
    fi

    # 后台启动 flower
    nohup celery -A "${CELERY_APP}" flower \
        --address="${FLOWER_ADDRESS}" \
        --port="${FLOWER_PORT}" \
        ${AUTH_ARGS} \
        ${FLOWER_EXTRA_ARGS} \
        >> "${LOG_FILE}" 2>&1 &

    local pid=$!
    echo "${pid}" > "${PID_FILE}"
    
    # 等待一小段时间检查是否启动成功
    sleep 2
    if is_running; then
        echo "[celery_flower] Flower 启动成功 (PID: ${pid})"
        echo "[celery_flower] 访问地址: http://${FLOWER_ADDRESS}:${FLOWER_PORT}"
        echo "[celery_flower] 日志文件: ${LOG_FILE}"
    else
        echo "[celery_flower] Flower 启动失败，请检查日志: ${LOG_FILE}"
        rm -f "${PID_FILE}"
        return 1
    fi
}

# 停止 flower
do_stop() {
    if ! is_running; then
        echo "[celery_flower] Flower 未在运行"
        rm -f "${PID_FILE}"
        return 0
    fi

    local pid
    pid=$(get_pid)
    echo "[celery_flower] 停止 Celery Flower (PID: ${pid})..."

    # 发送 SIGTERM 信号
    kill -TERM "${pid}" 2>/dev/null

    # 等待进程退出（最多等待 10 秒）
    local count=0
    while is_running && [[ ${count} -lt 10 ]]; do
        sleep 1
        ((count++))
        echo -n "."
    done
    echo ""

    if is_running; then
        echo "[celery_flower] Flower 未能优雅退出，强制终止..."
        kill -9 "${pid}" 2>/dev/null
        sleep 1
    fi

    rm -f "${PID_FILE}"
    echo "[celery_flower] Flower 已停止"
}

# 查看状态
do_status() {
    if is_running; then
        echo "[celery_flower] Flower 正在运行 (PID: $(get_pid))"
        echo "[celery_flower] 访问地址: http://${FLOWER_ADDRESS}:${FLOWER_PORT}"
        return 0
    else
        echo "[celery_flower] Flower 未在运行"
        return 1
    fi
}

# 重启 flower
do_restart() {
    echo "[celery_flower] 重启 Celery Flower..."
    do_stop
    sleep 2
    do_start
}

# 显示帮助
show_usage() {
    echo "用法: $0 {start|stop|status|restart}"
    echo ""
    echo "命令:"
    echo "  start   - 启动 Celery Flower"
    echo "  stop    - 停止 Celery Flower"
    echo "  status  - 查看 Flower 运行状态"
    echo "  restart - 重启 Celery Flower"
    echo ""
    echo "环境变量:"
    echo "  CELERY_APP         - Celery 应用路径 (默认: app.core.celery_app:celery_app)"
    echo "  FLOWER_ADDRESS     - 监听地址 (默认: 0.0.0.0)"
    echo "  FLOWER_PORT        - 监听端口 (默认: 5555)"
    echo "  FLOWER_BASIC_AUTH  - Basic Auth 认证 (格式: user:pass)"
}

# 主入口
case "${1:-}" in
    start)
        do_start
        ;;
    stop)
        do_stop
        ;;
    status)
        do_status
        ;;
    restart)
        do_restart
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
