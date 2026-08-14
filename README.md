# 📸 AI Photo Upscaler & Face Restorer Pro

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/downloads/release/python-31011/)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Real-ESRGAN](https://img.shields.io/badge/Model-Real--ESRGAN-orange.svg)](https://github.com/xinntao/Real-ESRGAN)
[![GFPGAN](https://img.shields.io/badge/Model-GFPGAN-green.svg)](https://github.com/TencentARC/GFPGAN)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)]()

A modern, high-performance desktop application for **4x image upscaling** and **deep facial restoration**, powered by **Real-ESRGAN** and **GFPGAN v1.4**.

---

## 📥 Download Standalone App (No Python Required)

For Windows users who just want to run the program without installing Python or setting up an environment:

👉 **[Download Latest Windows Release (.zip)](https://github.com/alivahab2025/AI-Photo-Enhancer/releases/latest)**

1. Download and extract the `.zip` archive.
2. Run `AIPhotoEnhancer.exe`.

---

## ✨ Features

* **⚡ 2-Stage Neural Enhancement Pipeline:**
  * **Real-ESRGAN (`RealESRGAN_x4plus` & `Anime_6B`):** Reconstructs background details, hair, clothing textures, and removes compression artifacts.
  * **GFPGAN v1.4:** Reconstructs photorealistic facial details (eyes, skin, teeth) with zero blur.
* **🔍 Interactive Canvas:**
  * **Zoom In / Out:** Seamless mouse wheel zooming.
  * **Pan & Drag:** Click and drag to navigate through high-resolution images.
  * **Scrollbars:** Built-in dark-themed scrollbars for easy navigation.
* **⚙️ Advanced Controls:**
  * **Face Restoration Fidelity Slider:** Fine-tune facial generation vs identity preservation ($0.1 - 1.0$).
  * **VRAM Tiling Support:** Process ultra-high-resolution images on low-VRAM GPUs without Out-Of-Memory errors.
  * **GPU Acceleration:** Automatic CUDA / CPU detection with FP16 half-precision support.
* **🎨 Customizable UI:** Easily customize theme colors, buttons, and hover states directly from the configuration dictionary in `app.py`.

---

## 🧠 AI Pipeline Overview

| Component | AI Architecture | Target Areas |
| :--- | :--- | :--- |
| **Upscaler** | `RealESRGAN_x4plus` / `RRDBNet` | Clothing, Body, Background, Textures |
| **Upscaler (Anime)** | `RealESRGAN_x4plus_anime_6B` | Digital art, Anime, Vector/Flat graphics |
| **Face Enhancer** | `GFPGAN v1.4` (Clean Arch) | Eyes, Facial skin, Mouth, Teeth, Facial hair |

---

## 🚀 Running from Source

### Option 1: Automatic One-Click Launch (Recommended)
Simply double-click the **`run_app.bat`** file. It will automatically:
1. Detect Python 3.10.
2. Create and activate an isolated virtual environment (`.venv`).
3. Install PyTorch with CUDA acceleration and required dependencies.
4. Launch the application.

### Option 2: Manual Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/alivahab2025/AI-Photo-Enhancer.git](https://github.com/alivahab2025/AI-Photo-Enhancer.git)
   cd AI-Photo-Enhancer