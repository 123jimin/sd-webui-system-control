import modules.scripts as scripts
import gradio as gr
import gc, os, sys, tracemalloc, psutil

from modules import shared, script_callbacks

class Script(scripts.Script):
    def __init__(self):
        super().__init__()

    def title(self):
        return "System Control"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        return ()

def get_memory_info() -> str:
    info = psutil.virtual_memory()
    GiB = 1024 ** 3
    return f"using {psutil.Process().memory_info().rss/GiB:.3f} GiB | {info.available/GiB:.3f} / {info.total/GiB:.3f} GiB free"

def get_disk_info() -> str:
    info = psutil.disk_usage(os.getcwd())
    GB = 1000 ** 3
    return f"{info.free/GB:.3f} / {info.total/GB:.3f} GB free"

def get_system_info() -> str:
    uname = os.uname()
    
    infos = []
    infos.append(f"Node: {uname.nodename}")
    infos.append(f"OS: {uname.sysname} {uname.release} {uname.version}")
    infos.append(f"Working Directory: {os.getcwd()}")
    infos.append(f"User ID: {os.getuid()} / Process ID: {os.getpid()}")

    infos.append("")

    infos.append(f"CPU: {uname.machine}, {psutil.cpu_count()} logical cores")

    load_1, load_5, load_15 = psutil.getloadavg()
    infos.append(f"- load: {load_1}% (1 min) / {load_5}% (5 min) / {load_15}% (15 min)")

    infos.append(f"Memory: {get_memory_info()}")
    infos.append(f"Disk: {get_disk_info()}")

    return "\n".join(infos)

def create_system_info_ui():
    with gr.Box(elem_classes="ch_box"):
        text_system_info = gr.Textbox(label="System Info", interactive=False, value=get_system_info)
        gr.Button(value="Refresh").click(get_system_info, outputs=text_system_info)

def create_system_control_ui():
    def do_garbage_collect():
        gc.collect()

    def do_start_tracemalloc():
        tracemalloc.start(6)

    def do_snapshot_tracemalloc():
        tracemalloc.take_snapshot().dump("tracemalloc.bin")

    def do_shutdown():
        shared.state.server_command = 'stop'
    
    def do_restart():
        shared.state.server_command = 'restart'

    with gr.Box(elem_classes="ch_box"):
        with gr.Row():
            gr.Button(value="Collect garbages").click(do_garbage_collect)
            gr.Button(value="Start tracemalloc").click(do_start_tracemalloc)
            gr.Button(value="Take tracemalloc snapshot").click(do_snapshot_tracemalloc)
        with gr.Row():
            gr.Button(value="Shutdown", variant="primary").click(do_shutdown)
            gr.Button(value="Restart", variant="primary").click(do_restart)

def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as system_control_tab:
        create_system_info_ui()
        create_system_control_ui()
    return [(system_control_tab, "System Control", "system_control")]

script_callbacks.on_ui_tabs(on_ui_tabs)
