import cv2
import numpy as np
import mss
import time
import os
import threading
from datetime import datetime
from pynput import keyboard

# ── 配置 ──────────────────────────────────────────────
THRESHOLD = 8.0
CHECK_INTERVAL = 2
OBSIDIAN_VAULT = ""  # 留空则保存在脚本同目录下的 sessions 文件夹
# ───────────────────────────────────────────────────────

STATUS_PAUSED = 0
STATUS_MONITORING = 1
STATUS_QUIT = 2

status = STATUS_PAUSED
status_lock = threading.Lock()
output_queue = []
queue_lock = threading.Lock()
writer_running = True

session_dir = None
index_path = None

# ── 创建会话文件夹 ────────────────────────────────────
def create_session_folder():
    global session_dir, index_path
    session_name = datetime.now().strftime("Meeting_%Y%m%d_%H%M")
    if os.path.isdir(OBSIDIAN_VAULT):
        base_dir = OBSIDIAN_VAULT
    else:
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")
    session_dir = os.path.join(base_dir, session_name)
    os.makedirs(session_dir, exist_ok=True)
    index_path = os.path.join(session_dir, "slides_index.md")
    return session_name, base_dir

# ── YAML 头部 ─────────────────────────────────────────
def write_yaml_header(session_name):
    today = datetime.now().strftime("%Y-%m-%d")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write("tags: #meeting_slides\n")
        f.write(f"date: {today}\n")
        f.write(f"session: {session_name}\n")
        f.write("---\n\n")

# ── 异步写入线程 ──────────────────────────────────────
def async_writer():
    global writer_running
    while writer_running:
        time.sleep(0.5)
        with queue_lock:
            batch = output_queue[:]
            output_queue.clear()
        if batch:
            with open(index_path, "a", encoding="utf-8") as f:
                for filename in batch:
                    f.write(f"![[{filename}]]\n")

# ── 状态切换 ──────────────────────────────────────────
def set_status(new_status):
    global status
    with status_lock:
        status = new_status
    if new_status == STATUS_PAUSED:
        print("\n[PAUSED]  已暂停 — 按 F9 恢复监控")
    elif new_status == STATUS_MONITORING:
        print("\n[RUNNING] 监控中 — 按 F10 暂停，Esc 退出")
    elif new_status == STATUS_QUIT:
        print("\n[EXIT]    正在退出...")

def on_press(key):
    try:
        if key == keyboard.Key.f9:
            set_status(STATUS_MONITORING)
        elif key == keyboard.Key.f10:
            set_status(STATUS_PAUSED)
        elif key == keyboard.Key.esc:
            set_status(STATUS_QUIT)
            return False
    except Exception:
        pass

# ── 截图并存档 ────────────────────────────────────────
def capture_and_save(sct, monitor):
    img = np.array(sct.grab(monitor))
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)   # BGRA → RGB
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"Slide_{timestamp}.jpg"
    filepath = os.path.join(session_dir, filename)
    from PIL import Image
    Image.fromarray(img).save(filepath, "JPEG", quality=92)
    with queue_lock:
        output_queue.append(filename)
    print(f"   [SAVED]  {filename}")

# ── 主循环 ────────────────────────────────────────────
def main():
    global writer_running

    session_name, base_dir = create_session_folder()
    write_yaml_header(session_name)

    writer_thread = threading.Thread(target=async_writer, daemon=True)
    writer_thread.start()

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    print("=" * 56)
    print("  PPT Grabber — 会议截图助手")
    print(f"  输出: {base_dir}")
    print(f"  会话: {session_name}")
    print("  F9 = 开始监控  |  F10 = 暂停  |  Esc = 退出")
    print("=" * 56)
    set_status(STATUS_PAUSED)

    sct = mss.MSS()
    monitors = sct.monitors
    monitor = monitors[1] if len(monitors) > 1 else monitors[0]

    prev_gray = None

    while True:
        with status_lock:
            current_status = status

        if current_status == STATUS_QUIT:
            break

        if current_status == STATUS_PAUSED:
            time.sleep(0.5)
            continue

        try:
            frame = np.array(sct.grab(monitor))
            small = cv2.resize(frame, (128, 128))
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

            if prev_gray is not None:
                diff = cv2.absdiff(gray, prev_gray)
                mean_diff = np.mean(diff)

                if mean_diff > THRESHOLD:
                    print(f"\n[TRIGGER] 翻页检测 (差异: {mean_diff:.2f})")
                    capture_and_save(sct, monitor)
                else:
                    print(f"\r[RUNNING] 监控中 (差异: {mean_diff:.2f})", end="", flush=True)

            prev_gray = gray

        except Exception as e:
            print(f"\n[ERROR] 截图出错: {e}")

        time.sleep(CHECK_INTERVAL)

    # ── 安全退出 ──
    listener.stop()
    sct.close()
    writer_running = False
    time.sleep(0.6)

    with queue_lock:
        if output_queue:
            with open(index_path, "a", encoding="utf-8") as f:
                for filename in output_queue:
                    f.write(f"![[{filename}]]\n")
            output_queue.clear()

    print(f"\n[DONE] 程序已退出。所有文件保存在: {session_dir}")
    print(f"       {len(os.listdir(session_dir)) - 1} 张截图  +  slides_index.md")

if __name__ == "__main__":
    main()
