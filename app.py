import sys
import os
import warnings

# Fix 'NoneType object has no attribute write' error in PyInstaller --windowed mode
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

# Suppress non-critical PyTorch / Torchvision deprecation warnings
warnings.filterwarnings("ignore")

import torchvision.transforms.functional as F

# Fix for torchvision >= 0.15 compatibility with BasicSR / GFPGAN
try:
    import torchvision.transforms.functional_tensor
except ImportError:
    sys.modules['torchvision.transforms.functional_tensor'] = F

import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image, ImageTk
import torch

# ==============================================================================
# 🎨 بخش تنظیمات رنگ‌ها و شخصی‌سازی دکمه‌ها (COLOR THEME CONFIGURATION)
# ==============================================================================
# کد رنگ‌ها به صورت هگزادسیپال (مثلاً '#27ae60') هستند.
# می‌توانید کد رنگ دلخواه خود را جایگزین کنید.
# ------------------------------------------------------------------------------

COLOR_THEME = {
    # ۱. دکمه‌های عمومی (مانند «انتخاب تصویر» و «ذخیره تصویر»)
    "PRIMARY_BTN": {
        "fg_color": "#1f538d",  # رنگ دکمه در حالت عادی (قبل از کلیک)
        "hover_color": "#14375e",  # رنگ دکمه وقتی موس روی آن می‌رود
        "text_color": "#ffffff",  # رنگ متن روی دکمه
        "text_color_disabled": "#2a2929"  # رنگ متن وقتی دکمه غیرفعال است (Disabled)
    },

    # ۲. دکمه اصلی عملیات (دکمه «شروع پردازش»)
    "ACTION_BTN": {
        "fg_color": "#27ae60",  # رنگ دکمه در حالت عادی (سبز)
        "hover_color": "#0f6533",  # رنگ دکمه موقع هاور (سبز پررنگ‌تر)
        "text_color": "#ffffff",  # رنگ متن روی دکمه
        "text_color_disabled": "#454949"  # رنگ متن دکمه در حالت غیرفعال
    },

    # ۳. عناصر جانبی (منوهای کشویی، اسلایدرها و کلیدها)
    "WIDGETS": {
        "button_color": "#1f538d",  # رنگ اصلی دستگیره اسلایدر / منوها
        "button_hover_color": "#14375e",  # رنگ هاور دستگیره اسلایدر
        "progress_color": "#27ae60",  # رنگ نوار پیشرفت (Progress Bar)
        "switch_color": "#27ae60"  # رنگ سوئیتچ در حالت فعال
    }
}

# ==============================================================================


# UI Theme Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ZoomableCanvas(ctk.CTkFrame):
    """Custom Image Viewer widget supporting Zoom, Scrollbars, and Click-and-Drag Panning."""

    def __init__(self, master, placeholder_text="No image loaded.", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder_text = placeholder_text

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Dark Canvas for displaying image
        self.canvas = tk.Canvas(self, bg="#1a1a1a", highlightthickness=0, bd=0)

        # Scrollbars
        self.v_scroll = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.h_scroll = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)

        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.pil_img = None
        self.tk_img = None
        self.zoom_level = 1.0

        # Mouse Bindings for Zoom
        self.canvas.bind("<MouseWheel>", self._on_zoom)
        self.canvas.bind("<Button-4>", self._on_zoom)
        self.canvas.bind("<Button-5>", self._on_zoom)

        # Mouse Bindings for Panning / Dragging
        self.canvas.bind("<ButtonPress-1>", self._start_pan)
        self.canvas.bind("<B1-Motion>", self._pan)

        # Canvas resize binding
        self.canvas.bind("<Configure>", self._on_configure)

        self._show_placeholder()

    def _show_placeholder(self):
        self.canvas.delete("all")
        cw = max(self.canvas.winfo_width() // 2, 200)
        ch = max(self.canvas.winfo_height() // 2, 200)
        self.canvas.create_text(
            cw, ch,
            text=self.placeholder_text,
            fill="#777777",
            font=("Arial", 14),
            tags="placeholder"
        )

    def set_image(self, cv_bgr_img):
        if cv_bgr_img is None:
            return
        rgb = cv2.cvtColor(cv_bgr_img, cv2.COLOR_BGR2RGB)
        self.pil_img = Image.fromarray(rgb)
        self.zoom_level = 1.0
        self.update_view()

    def _calc_fit_size(self):
        if not self.pil_img:
            return (100, 100)
        w, h = self.pil_img.size
        c_w = max(self.canvas.winfo_width() - 20, 300)
        c_h = max(self.canvas.winfo_height() - 20, 300)
        scale = min(c_w / w, c_h / h)
        return (max(1, int(w * scale)), max(1, int(h * scale)))

    def _on_zoom(self, event):
        if self.pil_img is None:
            return
        if event.num == 4 or event.delta > 0:
            zoom_factor = 1.15  # Zoom In
        else:
            zoom_factor = 0.85  # Zoom Out

        self.zoom_level = max(0.2, min(10.0, self.zoom_level * zoom_factor))
        self.update_view()

    def update_view(self):
        if self.pil_img is None:
            self._show_placeholder()
            return

        base_w, base_h = self._calc_fit_size()
        new_w = int(base_w * self.zoom_level)
        new_h = int(base_h * self.zoom_level)

        resized = self.pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(resized)

        self.canvas.delete("all")

        c_w = self.canvas.winfo_width()
        c_h = self.canvas.winfo_height()

        # Center image if smaller than canvas space
        pos_x = max(0, (c_w - new_w) // 2) if c_w > new_w else 0
        pos_y = max(0, (c_h - new_h) // 2) if c_h > new_h else 0

        self.canvas.create_image(pos_x, pos_y, anchor="nw", image=self.tk_img)

        # Update scrollregion so scrollbars work according to image size
        scroll_w = max(c_w, pos_x + new_w)
        scroll_h = max(c_h, pos_y + new_h)
        self.canvas.config(scrollregion=(0, 0, scroll_w, scroll_h))

    def _on_configure(self, event):
        if self.pil_img is None:
            self._show_placeholder()
        elif self.zoom_level == 1.0:
            self.update_view()

    def _start_pan(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def _pan(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)


class AIRestorerEngine:
    """Handles AI Model loading and processing pipelines (Real-ESRGAN + GFPGAN)."""

    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else
                                   ('mps' if torch.backends.mps.is_available() else 'cpu'))
        self.upscaler = None
        self.face_enhancer = None

    def load_models(self, model_name="RealESRGAN_x4plus", scale=4, tile_size=0):
        from realesrgan import RealESRGANer
        from basicsr.archs.rrdbnet_arch import RRDBNet
        from gfpgan import GFPGANer

        # 1. Initialize Real-ESRGAN for General Upscaling (Body, Clothing, Background)
        if model_name == "RealESRGAN_x4plus":
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
            model_url = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
        elif model_name == "RealESRGAN_x4plus_anime_6B":
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
            model_url = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth'

        self.upscaler = RealESRGANer(
            scale=scale,
            model_path=model_url,
            dni_weight=None,
            model=model,
            tile=tile_size,
            tile_pad=10,
            pre_pad=0,
            half=(self.device.type == 'cuda'),
            device=self.device
        )

        # 2. Initialize GFPGAN for Face Repair & Detail Restoration
        self.face_enhancer = GFPGANer(
            model_path='https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth',
            upscale=scale,
            arch='clean',
            channel_multiplier=2,
            bg_upsampler=self.upscaler,
            device=self.device
        )

    def process_image(self, input_bgr, enable_face_restore=True, weight=0.5):
        """Processes the input BGR image array through the pipeline."""
        if enable_face_restore and self.face_enhancer is not None:
            _, _, restored_img = self.face_enhancer.enhance(
                input_bgr,
                has_aligned=False,
                only_center_face=False,
                paste_back=True,
                weight=weight
            )
        else:
            restored_img, _ = self.upscaler.enhance(input_bgr, outscale=self.upscaler.scale)

        return restored_img


class AIRestorerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Photo Upscaler & Face Restorer Pro")
        self.geometry("1200x800")
        self.minsize(900, 600)

        self.engine = AIRestorerEngine()
        self.input_path = None
        self.original_image_cv = None
        self.processed_image_cv = None

        self._build_ui()

    def _build_ui(self):
        # Grid Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= LEFT CONTROL PANEL =================
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="Control Center", font=ctk.CTkFont(size=20, weight="bold")).pack(padx=20,
                                                                                                         pady=(20, 10))

        # Hardware Info Badge
        device_str = f"Hardware: {self.engine.device.type.upper()}"
        device_color = "#2fa572" if self.engine.device.type == 'cuda' else "#e58e26"
        ctk.CTkLabel(self.sidebar, text=device_str, text_color=device_color, font=ctk.CTkFont(weight="bold")).pack(
            pady=(0, 15))

        # File Selection Button
        self.btn_load = ctk.CTkButton(
            self.sidebar,
            text="📁 Open Image",
            fg_color=COLOR_THEME["PRIMARY_BTN"]["fg_color"],
            hover_color=COLOR_THEME["PRIMARY_BTN"]["hover_color"],
            text_color=COLOR_THEME["PRIMARY_BTN"]["text_color"],
            text_color_disabled=COLOR_THEME["PRIMARY_BTN"]["text_color_disabled"],
            command=self.load_image
        )
        self.btn_load.pack(padx=20, pady=10, fill="x")

        # Model Selector
        ctk.CTkLabel(self.sidebar, text="Upscale Model Target:").pack(anchor="w", padx=20, pady=(10, 0))
        self.combo_model = ctk.CTkOptionMenu(
            self.sidebar,
            values=["RealESRGAN_x4plus (Photos/Real)", "RealESRGAN_x4plus_anime_6B (Anime/Art)"],
            button_color=COLOR_THEME["WIDGETS"]["button_color"],
            button_hover_color=COLOR_THEME["WIDGETS"]["button_hover_color"]
        )
        self.combo_model.pack(padx=20, pady=5, fill="x")

        # Upscale Scale Selector
        ctk.CTkLabel(self.sidebar, text="Enlarge Factor:").pack(anchor="w", padx=20, pady=(10, 0))
        self.combo_scale = ctk.CTkOptionMenu(
            self.sidebar,
            values=["2x", "4x"],
            button_color=COLOR_THEME["WIDGETS"]["button_color"],
            button_hover_color=COLOR_THEME["WIDGETS"]["button_hover_color"]
        )
        self.combo_scale.set("4x")
        self.combo_scale.pack(padx=20, pady=5, fill="x")

        # Face Restoration Toggle
        self.switch_face = ctk.CTkSwitch(
            self.sidebar,
            text="Restore & Repair Faces",
            progress_color=COLOR_THEME["WIDGETS"]["switch_color"],
            command=self._toggle_face_slider
        )
        self.switch_face.pack(anchor="w", padx=20, pady=15)
        self.switch_face.select()

        # Face Restoration Weight Slider
        self.lbl_weight = ctk.CTkLabel(self.sidebar, text="Face Restoration Fidelity (0.5):")
        self.lbl_weight.pack(anchor="w", padx=20, pady=(5, 0))
        self.slider_weight = ctk.CTkSlider(
            self.sidebar,
            from_=0.1,
            to=1.0,
            number_of_steps=18,
            button_color=COLOR_THEME["WIDGETS"]["button_color"],
            button_hover_color=COLOR_THEME["WIDGETS"]["button_hover_color"],
            command=self._update_weight_label
        )
        self.slider_weight.set(0.5)
        self.slider_weight.pack(padx=20, pady=5, fill="x")

        # Low VRAM / Tiling Option
        ctk.CTkLabel(self.sidebar, text="Tile Size (Lower if out of VRAM):").pack(anchor="w", padx=20, pady=(10, 0))
        self.combo_tile = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Auto (0)", "512 (Recommended)", "256 (Low VRAM)"],
            button_color=COLOR_THEME["WIDGETS"]["button_color"],
            button_hover_color=COLOR_THEME["WIDGETS"]["button_hover_color"]
        )
        self.combo_tile.pack(padx=20, pady=5, fill="x")

        # Process Button
        self.btn_process = ctk.CTkButton(
            self.sidebar,
            text="✨ Enhance & Upscale",
            fg_color=COLOR_THEME["ACTION_BTN"]["fg_color"],
            hover_color=COLOR_THEME["ACTION_BTN"]["hover_color"],
            text_color=COLOR_THEME["ACTION_BTN"]["text_color"],
            text_color_disabled=COLOR_THEME["ACTION_BTN"]["text_color_disabled"],
            font=ctk.CTkFont(weight="bold"),
            command=self.start_processing
        )
        self.btn_process.pack(padx=20, pady=(20, 10), fill="x")

        # Progress Bar & Status
        self.progress = ctk.CTkProgressBar(self.sidebar, progress_color=COLOR_THEME["WIDGETS"]["progress_color"])
        self.progress.pack(padx=20, pady=5, fill="x")
        self.progress.set(0)

        self.lbl_status = ctk.CTkLabel(self.sidebar, text="Status: Ready", font=ctk.CTkFont(size=12))
        self.lbl_status.pack(pady=5)

        # Save Button
        self.btn_save = ctk.CTkButton(
            self.sidebar,
            text="💾 Save Result",
            fg_color=COLOR_THEME["PRIMARY_BTN"]["fg_color"],
            hover_color=COLOR_THEME["PRIMARY_BTN"]["hover_color"],
            text_color=COLOR_THEME["PRIMARY_BTN"]["text_color"],
            text_color_disabled=COLOR_THEME["PRIMARY_BTN"]["text_color_disabled"],
            state="disabled",
            command=self.save_image
        )
        self.btn_save.pack(padx=20, pady=(10, 20), fill="x")

        # ================= RIGHT PREVIEW PANEL =================
        self.preview_frame = ctk.CTkTabview(self)
        self.preview_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.tab_original = self.preview_frame.add("Original Image")
        self.tab_enhanced = self.preview_frame.add("Enhanced Result")

        # Scrollable + Zoomable Canvas Viewers
        self.view_orig = ZoomableCanvas(self.tab_original, placeholder_text="No image loaded.")
        self.view_orig.pack(expand=True, fill="both")

        self.view_enh = ZoomableCanvas(self.tab_enhanced,
                                       placeholder_text="Process an image to view the enhanced result.")
        self.view_enh.pack(expand=True, fill="both")

    def _toggle_face_slider(self):
        state = "normal" if self.switch_face.get() else "disabled"
        self.slider_weight.configure(state=state)

    def _update_weight_label(self, val):
        self.lbl_weight.configure(text=f"Face Restoration Fidelity ({val:.2f}):")

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if file_path:
            self.input_path = file_path
            self.original_image_cv = cv2.imread(file_path)
            self.view_orig.set_image(self.original_image_cv)
            self.lbl_status.configure(text="Image loaded successfully.")
            self.btn_save.configure(state="disabled")

    def start_processing(self):
        if self.original_image_cv is None:
            messagebox.showwarning("Warning", "Please open an image first!")
            return

        self.btn_process.configure(state="disabled")
        self.btn_load.configure(state="disabled")
        self.progress.configure(mode="indefinite")
        self.progress.start()
        self.lbl_status.configure(text="Processing AI Models... Please wait.")

        # Run process in background thread to avoid freezing GUI
        threading.Thread(target=self._process_worker, daemon=True).start()

    def _process_worker(self):
        try:
            model_key = "RealESRGAN_x4plus" if "RealESRGAN_x4plus (" in self.combo_model.get() else "RealESRGAN_x4plus_anime_6B"
            scale_val = int(self.combo_scale.get().replace("x", ""))

            tile_map = {"Auto (0)": 0, "512 (Recommended)": 512, "256 (Low VRAM)": 256}
            tile_val = tile_map[self.combo_tile.get()]

            # Load models
            self.engine.load_models(model_name=model_key, scale=scale_val, tile_size=tile_val)

            # Process image
            face_restore = bool(self.switch_face.get())
            weight_val = float(self.slider_weight.get())

            self.processed_image_cv = self.engine.process_image(
                self.original_image_cv,
                enable_face_restore=face_restore,
                weight=weight_val
            )

            # Update UI on main thread
            self.after(0, self._on_processing_complete)

        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda msg=err_msg: self._on_processing_error(msg))

    def _on_processing_complete(self):
        self.progress.stop()
        self.progress.set(1.0)
        self.btn_process.configure(state="normal")
        self.btn_load.configure(state="normal")
        self.btn_save.configure(state="normal")
        self.lbl_status.configure(text="Enhancement Complete!")

        # Display Enhanced Result & Reset zoom view
        self.view_enh.set_image(self.processed_image_cv)

        # Switch to Enhanced Tab
        self.preview_frame.set("Enhanced Result")

    def _on_processing_error(self, err_msg):
        self.progress.stop()
        self.progress.set(0)
        self.btn_process.configure(state="normal")
        self.btn_load.configure(state="normal")
        self.lbl_status.configure(text="Processing Error!")
        messagebox.showerror("Error during enhancement", f"An error occurred:\n{err_msg}")

    def save_image(self):
        if self.processed_image_cv is None:
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("WebP Image", "*.webp")]
        )
        if save_path:
            cv2.imwrite(save_path, self.processed_image_cv)
            messagebox.showinfo("Saved", f"Image saved successfully to:\n{save_path}")


if __name__ == "__main__":
    app = AIRestorerApp()
    app.mainloop()