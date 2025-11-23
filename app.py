import streamlit as st
import os
import subprocess
from pathlib import Path

# --- Config ---
st.set_page_config(page_title="JAV TH - Auto Burner", page_icon="🎬", layout="wide")

UPLOAD_DIR = "/tmp/uploads"
OUTPUT_DIR = "/tmp/outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- UI ---
col1, col2 = st.columns([1, 6])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=100)
    else:
        st.write("🎬")

with col2:
    st.title("Cloud Video Burner (FFmpeg)")
    st.write("เครื่องมือฝังซับไตเติลสำหรับไฟล์ขนาดใหญ่")

st.info("💡 หมายเหตุ: การอัปโหลดและประมวลผลไฟล์ 10GB บน Cloud ฟรี อาจใช้เวลานานมาก (แนะนำให้ใช้เน็ตแรงๆ)")

# --- Inputs ---
video_file = st.file_uploader("1. เลือกไฟล์วิดีโอ (MP4)", type=["mp4"])
sub_file = st.file_uploader("2. เลือกไฟล์ซับไตเติล", type=["srt", "vtt", "ass"])

col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    fps = st.selectbox("Frame Rate", ["Original", "24", "30", "60"])
with col_opt2:
    preset = st.selectbox("ความเร็ว (Preset)", ["ultrafast", "superfast", "veryfast", "medium"], index=1, help="Ultrafast เร็วสุดแต่ไฟล์ใหญ่, Medium ช้าแต่ภาพสวย")

# --- Process ---
if st.button("🚀 เริ่ม Burn Subtitle", type="primary"):
    if video_file and sub_file:
        v_path = os.path.join(UPLOAD_DIR, video_file.name)
        s_path = os.path.join(UPLOAD_DIR, sub_file.name)
        out_name = f"burned_{video_file.name}"
        out_path = os.path.join(OUTPUT_DIR, out_name)

        # 1. Save Files
        with st.status("📦 กำลังอัปโหลดไฟล์เข้า Server...", expanded=True) as status:
            with open(v_path, "wb") as f: f.write(video_file.getbuffer())
            with open(s_path, "wb") as f: f.write(sub_file.getbuffer())
            status.write("✅ อัปโหลดเสร็จสิ้น! กำลังเริ่ม FFmpeg...")

            # 2. Command
            # Escape path เพื่อป้องกัน error
            abs_s_path = os.path.abspath(s_path).replace(":", "\\:")
            
            cmd = [
                'ffmpeg', '-y',
                '-i', v_path,
                '-vf', f"subtitles='{abs_s_path}'",
                '-c:v', 'libx264', '-preset', preset,
                '-c:a', 'copy'
            ]
            if fps != "Original":
                cmd.extend(['-r', fps])
            cmd.append(out_path)

            # 3. Run
            process = subprocess.run(cmd, capture_output=True, text=True)

            if process.returncode == 0:
                status.update(label="✅ เสร็จสมบูรณ์!", state="complete", expanded=False)
                st.success(f"ทำรายการสำเร็จ! ({out_name})")
                
                # Download
                with open(out_path, "rb") as f:
                    st.download_button(
                        label="⬇️ ดาวน์โหลดไฟล์ผลลัพธ์",
                        data=f,
                        file_name=out_name,
                        mime="video/mp4"
                    )
                
                # Cleanup
                os.remove(v_path)
                os.remove(s_path)
                os.remove(out_path)
            else:
                status.update(label="❌ ผิดพลาด", state="error")
                st.error("เกิดข้อผิดพลาดในการแปลงไฟล์")
                st.code(process.stderr)
    else:
        st.warning("กรุณาเลือกไฟล์ให้ครบ")
