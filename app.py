import os
import sys
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import gradio as gr

UPSTREAM_DIR = Path(os.environ.get("UPSTREAM_DIR", "/opt/watermarks-remover"))
SCRIPTS = UPSTREAM_DIR / "skills" / "remove-ai-marks" / "scripts"

ALLOWED_EXTS = {".txt", ".md", ".html", ".htm", ".svg", ".png", ".jpg", ".jpeg", ".pdf", ".docx", ".odt"}

def _ensure_upstream():
    if not SCRIPTS.exists():
        raise RuntimeError("Không tìm thấy watermarks-remover upstream trong container.")

def _run(args, timeout=60):
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    # Keep the public service conservative.
    env.setdefault("WATERMARKS_MAX_INPUT_BYTES", str(64 * 1024 * 1024))
    p = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=timeout,
        env=env,
        cwd=str(UPSTREAM_DIR),
    )
    return p.returncode, p.stdout

def clean_text_ui(text, consent):
    if not consent:
        return "", "Bạn cần xác nhận quyền sở hữu/quyền xử lý trước khi sử dụng."
    if not text:
        return "", "Không có nội dung để xử lý."
    _ensure_upstream()
    with tempfile.TemporaryDirectory(prefix="wmr_") as td:
        src = Path(td) / "input.txt"
        dst = Path(td) / "output.txt"
        src.write_text(text, encoding="utf-8")
        code, out = _run([
            sys.executable, str(SCRIPTS / "clean_text.py"),
            str(src), "-o", str(dst), "--stats"
        ])
        if code != 0 or not dst.exists():
            return "", f"Xử lý thất bại:\n{out}"
        cleaned = dst.read_text(encoding="utf-8", errors="replace")
        return cleaned, (
            "Đã chạy Layer A (Unicode/edit-based hygiene).\n"
            "Lưu ý: kết quả này KHÔNG chứng minh rằng nội dung sẽ vượt qua detector của nhà cung cấp.\n\n"
            + out[-4000:]
        )

def inspect_text_ui(text, consent):
    if not consent:
        return "Bạn cần xác nhận quyền sở hữu/quyền xử lý trước khi sử dụng."
    if not text:
        return "Không có nội dung để kiểm tra."
    _ensure_upstream()
    with tempfile.TemporaryDirectory(prefix="wmr_") as td:
        src = Path(td) / "input.txt"
        src.write_text(text, encoding="utf-8")
        code, out = _run([sys.executable, str(SCRIPTS / "inspect_text.py"), str(src)])
        return out if out else f"Exit code: {code}"

def clean_file_ui(file_path, consent):
    if not consent:
        return None, "Bạn cần xác nhận quyền sở hữu/quyền xử lý trước khi sử dụng."
    if not file_path:
        return None, "Chưa chọn file."
    _ensure_upstream()

    src_path = Path(file_path)
    ext = src_path.suffix.lower()
    if ext not in ALLOWED_EXTS:
        return None, f"Định dạng {ext or '(không có đuôi)'} chưa được bật trên bản public."

    with tempfile.TemporaryDirectory(prefix="wmr_") as td:
        src = Path(td) / ("input" + ext)
        dst = Path(td) / ("cleaned" + ext)
        shutil.copy2(src_path, src)

        code, inspect_out = _run([sys.executable, str(SCRIPTS / "inspect_file.py"), str(src)])
        code2, clean_out = _run([
            sys.executable, str(SCRIPTS / "clean_file.py"),
            str(src), "-o", str(dst)
        ])

        if code2 != 0 or not dst.exists():
            return None, f"Xử lý thất bại:\n{clean_out}"

        # Gradio needs a persistent temporary result long enough for download.
        exported = Path(tempfile.gettempdir()) / f"watermarks-remover-cleaned-{os.getpid()}{ext}"
        shutil.copy2(dst, exported)

        report = (
            "KIỂM TRA TRƯỚC:\n" + inspect_out[-5000:] +
            "\n\nKẾT QUẢ LÀM SẠCH:\n" + clean_out[-5000:] +
            "\n\nGiới hạn: công cụ chỉ báo cáo phần có thể kiểm chứng và best-effort; "
            "không cam kết xóa pixel watermark/soft binding hoặc làm detector chính thức thất bại."
        )
        return str(exported), report

TITLE = "Watermarks Remover — Privacy & Hygiene"
DESCRIPTION = """
Bản web community được xây dựng từ dự án MIT
**guillaumemeyer/watermarks-remover** để làm sạch metadata/provenance và ký tự ẩn
trên **nội dung bạn sở hữu hoặc được phép xử lý**.

**Không dùng cho gian lận học thuật, giả mạo nguồn gốc, hoặc tuyên bố sai rằng nội dung AI là “do con người viết”.**
Dịch vụ không cam kết “undetectable” và không chứng nhận rằng detector của nhà cung cấp sẽ thất bại.
"""

with gr.Blocks(title=TITLE, theme=gr.themes.Soft()) as demo:
    gr.Markdown(f"# {TITLE}\n{DESCRIPTION}")

    consent = gr.Checkbox(
        label="Tôi xác nhận mình sở hữu nội dung này hoặc có quyền hợp pháp để xử lý nội dung này.",
        value=False
    )

    with gr.Tabs():
        with gr.Tab("Văn bản"):
            text_in = gr.Textbox(lines=14, label="Nội dung")
            with gr.Row():
                inspect_btn = gr.Button("Kiểm tra")
                clean_btn = gr.Button("Làm sạch Layer A", variant="primary")
            text_out = gr.Textbox(lines=14, label="Kết quả")
            text_report = gr.Textbox(lines=10, label="Báo cáo")
            inspect_btn.click(inspect_text_ui, [text_in, consent], [text_report], queue=False)
            clean_btn.click(clean_text_ui, [text_in, consent], [text_out, text_report], queue=False)

        with gr.Tab("File"):
            gr.Markdown("Hỗ trợ public: TXT/MD/HTML/SVG/PNG/JPEG/PDF/DOCX/ODT theo core upstream.")
            file_in = gr.File(label="Chọn file", type="filepath")
            file_btn = gr.Button("Kiểm tra & làm sạch", variant="primary")
            file_out = gr.File(label="Tải file đã xử lý")
            file_report = gr.Textbox(lines=16, label="Báo cáo")
            file_btn.click(clean_file_ui, [file_in, consent], [file_out, file_report], queue=False)

        with gr.Tab("Giới hạn & đạo đức"):
            gr.Markdown("""
### Phạm vi
- Layer A: ký tự Unicode ẩn, bidi, tag characters, exotic spaces…
- File metadata/provenance: C2PA/EXIF/XMP/doc properties theo định dạng upstream hỗ trợ.
- Layer B rewrite: **không bật trên public demo mặc định** vì cần model/backend và không thể bảo đảm detector.
- Pixel-domain watermark removal: **ngoài phạm vi** core.
- reverse-SynthID: chỉ là scorer/detection bên ngoài, không bundle vào website này.
- CtrlRegen/noai-watermark: không bundle vào bản public này; phải tuân thủ license/dependency riêng của upstream liên quan.

### Quy tắc sử dụng
- Chỉ xử lý nội dung bạn sở hữu hoặc có quyền.
- Không dùng để gian lận học thuật hoặc giả mạo tác giả/nguồn gốc.
- Không quảng cáo hay hiểu kết quả là “AI-undetectable”.
- Không có bảo đảm rằng soft binding, pixel watermark hoặc detector riêng của vendor đã bị vô hiệu hóa.

### Quyền riêng tư
File được xử lý trong thư mục tạm thời của container. Ứng dụng không chủ động lưu lịch sử nội dung.
Hosting provider vẫn có thể có log/hạ tầng riêng theo chính sách của họ.
""")

        with gr.Tab("License"):
            gr.Markdown("""
Dự án upstream: **guillaumemeyer/watermarks-remover** — MIT License.

Copyright (c) 2026 watermarks-remover contributors.

Bản web này giữ nguyên attribution/license notice theo yêu cầu MIT. Các dự án phụ/optional
như reverse-SynthID hoặc noai-watermark có thể có điều khoản riêng và không được coi là MIT
chỉ vì website này dùng core MIT.
""")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", "80")), show_error=True)
