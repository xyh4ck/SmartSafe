#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Celery Worker 管理脚本
# 用法: ./celery_worker.sh {start|stop|status|restart|log}
# ============================================================

# Resolve backend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}"

# PID 文件路径
PID_FILE="${BACKEND_DIR}/celery_worker.pid"
LOG_FILE="${BACKEND_DIR}/logs/celery_worker.log"

# Allow overriding via environment variables
: "${CELERY_APP:=app.core.celery_app:celery_app}"
: "${CELERY_LOGLEVEL:=info}"
: "${CELERY_QUEUES:=evaltask,default}"
: "${CELERY_CONCURRENCY:=4}"
: "${CELERY_POOL:=prefork}"
: "${CELERY_EXTRA_ARGS:=}"

# 确保日志目录存在
mkdir -p "$(dirname "${LOG_FILE}")"

# 获取 worker 进程 PID
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

# 启动 worker
do_start() {
    if is_running; then
        echo "[celery_worker] Worker 已在运行中 (PID: $(get_pid))"
        return 0
    fi

    echo "[celery_worker] 启动 Celery Worker..."
    echo "[celery_worker] BACKEND_DIR=${BACKEND_DIR}"
    echo "[celery_worker] CELERY_APP=${CELERY_APP}"
    echo "[celery_worker] CELERY_QUEUES=${CELERY_QUEUES}"
    echo "[celery_worker] CELERY_CONCURRENCY=${CELERY_CONCURRENCY}"

    cd "${BACKEND_DIR}"

    # 后台启动 celery worker
    nohup celery -A "${CELERY_APP}" worker \
        -l "${CELERY_LOGLEVEL}" \
        -Q "${CELERY_QUEUES}" \
        --concurrency "${CELERY_CONCURRENCY}" \
        --pool "${CELERY_POOL}" \
        ${CELERY_EXTRA_ARGS} \
        >> "${LOG_FILE}" 2>&1 &

    local pid=$!
    echo "${pid}" > "${PID_FILE}"
    
    # 等待一小段时间检查是否启动成功
    sleep 2
    if is_running; then
        echo "[celery_worker] Worker 启动成功 (PID: ${pid})"
        echo "[celery_worker] 日志文件: ${LOG_FILE}"
    else
        echo "[celery_worker] Worker 启动失败，请检查日志: ${LOG_FILE}"
        rm -f "${PID_FILE}"
        return 1
    fi
}

# 停止 worker
do_stop() {
    if ! is_running; then
        echo "[celery_worker] Worker 未在运行"
        rm -f "${PID_FILE}"
        return 0
    fi

    local pid
    pid=$(get_pid)
    echo "[celery_worker] 停止 Celery Worker (PID: ${pid})..."

    # 发送 SIGTERM 信号，让 worker 优雅退出
    kill -TERM "${pid}" 2>/dev/null

    # 等待进程退出（最多等待 30 秒）
    local count=0
    while is_running && [[ ${count} -lt 30 ]]; do
        sleep 1
        ((count++))
        echo -n "."
    done
    echo ""

    if is_running; then
        echo "[celery_worker] Worker 未能优雅退出，强制终止..."
        kill -9 "${pid}" 2>/dev/null
        sleep 1
    fi

    rm -f "${PID_FILE}"
    echo "[celery_worker] Worker 已停止"
}

# 查看状态
do_status() {
    if is_running; then
        echo "[celery_worker] Worker 正在运行 (PID: $(get_pid))"
        return 0
    else
        echo "[celery_worker] Worker 未在运行"
        return 1
    fi
}

# 重启 worker
do_restart() {
    echo "[celery_worker] 重启 Celery Worker..."
    do_stop
    sleep 2
    do_start
}

# 查看日志
do_log() {
    if [[ ! -f "${LOG_FILE}" ]]; then
        echo "[celery_worker] 日志文件不存在: ${LOG_FILE}"
        echo "[celery_worker] 请先执行: $0 start"
        return 1
    fi

    echo "[celery_worker] 查看日志: ${LOG_FILE}"
    tail -n 200 -f "${LOG_FILE}"
}

# 显示帮助
show_usage() {
    echo "用法: $0 {start|stop|status|restart|log}"
    echo ""
    echo "命令:"
    echo "  start   - 启动 Celery Worker"
    echo "  stop    - 停止 Celery Worker"
    echo "  status  - 查看 Worker 运行状态"
    echo "  restart - 重启 Celery Worker"
    echo "  log     - 查看并跟随日志 (tail -n 200 -f)"
    echo ""
    echo "环境变量:"
    echo "  CELERY_APP         - Celery 应用路径 (默认: app.core.celery_app:celery_app)"
    echo "  CELERY_LOGLEVEL    - 日志级别 (默认: info)"
    echo "  CELERY_QUEUES      - 监听队列 (默认: evaltask,default)"
    echo "  CELERY_CONCURRENCY - 并发数 (默认: 4)"
    echo "  CELERY_POOL        - 进程池类型 (默认: prefork)"
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
    log)
        do_log
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
