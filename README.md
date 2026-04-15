# 🧠 BRAINAI – Brain Tumor Segmentation Portal

**BRAINAI** is a cutting‑edge, web‑based application built with **Flask** that performs **brain tumor segmentation** on MRI scans using a **state‑of‑the‑art 3D U‑Net** deep‑learning model. Upload 4‑modal MRI data, run AI predictions, and visualize results through an interactive dashboard.

🔬 Medical‑grade AI for brain tumor detection and segmentation.

## ✨ Key Features

- **🧬 Multi‑Modal MRI Support**  
  Upload 4 MRI modalities: `FLAIR`, `T1`, `T1c`, `T2` (`.nii` / `.nii.gz`).
- **🎯 AI Segmentation**  
  3D U‑Net model for precise tumor‑boundary detection.
- **📊 Interactive Visualizations**  
  Overlay images, confidence heatmaps, slice‑wise tumor‑area graphs.
- **👥 Dual Dashboards**  
  - User dashboard (prediction results)  
  - Admin dashboard (users, messages, role management).
- **💬 Live Chat**  
  Real‑time messaging between users and admin.
- **🔐 Secure Auth**  
  Registration, login, admin access via secret key (`admin_key = brainai123`).
- **🎞 Modern UI**  
  3D‑animated neural network background + clean Bio‑Emerald theme.

---

## 🛠 Tech Stack

```mermaid
graph TB
    A[Flask Backend] --> B[SQLite DB]
    A --> C[3D U-Net Model]
    C --> D[TensorFlow/Keras]
    A --> E[Nibabel - NIfTI]
    F[HTML/CSS/JS Frontend] --> A
```

- **🔹 Backend:** Flask (Python 3.8+)
- **🔹 AI/ML:** TensorFlow 2.x, Keras, Nibabel, NumPy
- **🔹 Database:** SQLite (production‑ready for small‑to‑medium scale)
- **🔹 Frontend:** Vanilla HTML/CSS/JavaScript (+ Three.js 3D background)
- **🔹 Medical Imaging:** NIfTI (`.nii` / `.nii.gz`) format

---

## 📁 Project Structure

```text
brainai/
│
├── app.py                    # Main Flask app: auth, routes, predict, chat
├── ai_model.py              # 3D U‑Net model inference & visualization
├── db.py                    # DB initialization (users, messages)
├── brain_tumor_3DUNet.keras # Pre‑trained 3D‑UNet model (~50 MB)
├── requirements.txt         # Python dependencies
├── README.md               # You're reading it!
│
├── static/
│   ├── uploads/            # User MRI files (git‑ignored)
│   ├── results/            # Generated outputs (git‑ignored)
│   ├── css/
│   └── js/
│
└── templates/
    ├── login.html
    ├── base.html            # Base layout (optional)
    ├── admin_dashboard.html
    └── user_dashboard.html
```MODEL PUT
LOgING PAGE

<img width="757" height="869" alt="Screenshot 2026-04-13 225034" src="https://github.com/user-attachments/assets/cf7ffc39-abca-4b58-b63a-3f673c5b697d" />

USER LOGIN <img width="1824" height="820" alt="Screenshot 2026-04-13 225100" src="https://github.com/user-attachments/assets/6e2024ef-c7d3-436b-96d3-68d720685eb1" />
UPLOAD DATA
<img width="1764" height="741" alt="Screenshot 2026-04-15 122623" src="https://github.com/user-attachments/assets/53f4232f-d58c-45ce-9a9f-c9cadd62da40" />
OUTPUT <img width="1839" height="885" alt="Screenshot 2026-04-15 114511" src="https://github.com/user-attachments/assets/4bc5795a-3319-4f7a-a5a1-5fcb24871953" />
<img width="1441" height="640" alt="Screenshot 2026-04-15 114449" src="https://github.com/user-attachments/assets/94ae691b-0c9b-46d7-9087-61eb3a114e46" />
GRAPH
<img width="1916" height="928" alt="Screenshot 2026-04-15 114539" src="https://github.com/user-attachments/assets/3c0a2ed9-636a-4fab-bcb3-d509093dea45" />
OUTP PUT DOWNLOAD
<img width="1712" height="530" alt="Screenshot 2026-04-15 114612" src="https://github.com/user-attachments/assets/b41a5420-7826-4fce-851d-b0575dabd501" />
MEDICAL HISTORY
<img width="1638" height="831" alt="Screenshot 2026-04-15 120113" src="https://github.com/user-attachments/assets/96e7eb04-281a-4bc2-b0df-593097270809" />
USER PROFILE
<img width="1633" height="824" alt="Screenshot 2026-04-15 120055" src="https://github.com/user-attachments/assets/8b3a00a9-52bd-42eb-ac91-32bcf5d92111" />
ADMIN
<img width="1778" height="866" alt="Screenshot 2026-04-15 121629" src="https://github.com/user-attachments/assets/f887bfe5-4a20-4bad-8463-056500d30f41" />
<img width="1771" height="861" alt="Screenshot 2026-04-15 121755" src="https://github.com/user-attachments/assets/ce88c0ff-d31a-4952-94af-5c906bfb7c5b" />
<img width="1625" height="762" alt="Screenshot 2026-04-15 121706" src="https://github.com/user-attachments/assets/4af379dd-077b-4fc1-a308-ef845af6ad2b" />
<img width="1793" height="815" alt="Screenshot 2026-04-15 121647" src="https://github.com/user-attachments/assets/d0904906-0de3-4b0e-bb89-772d8a9fa612" />


## ⚙️ Quick Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-username/brainai.git
   cd brainai
   ```

2. **Create virtual environment & install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux/macOS
   # venv\Scripts\activate         # Windows

   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python db.py
   ```
   This creates `brainai.db` with tables: `users` and `messages`.

4. **Place your model**
   Ensure your trained model is here:
   ```text
   brain_tumor_3DUNet.keras
   ```

5. **Run the app**
   ```bash
   python app.py
   ```
   Open in browser: `http://localhost:5000`

---

## 🔄 Usage Flow

1. **Register / Login**
   - Use `admin_key = brainai123` in the register form to create an **admin**.
2. **Upload MRI Data**
   - On `/user`, upload four NIfTI files in order:  
     `FLAIR`, `T1`, `T1c`, `T2` (`.nii` or `.nii.gz`).
3. **Predict**
   - Click **Predict** → 3D‑UNet runs segmentation (30–60 seconds).
4. **Visualize**
   - View overlay images, slice‑wise tumor‑area graph, and confidence map.
5. **Chat**
   - Send messages to admin via the **Send** button.
6. ** admin**
   - Use the **Admin Dashboard** to manage users and messages.

---

## ⚠️ Important Requirements

✅ **DO**
- Upload `.nii` or `.nii.gz` MRI files.  
- Use 4 modalities in order: `[FLAIR, T1, T1c, T2]`.  
- Keep each file < 100 MB.  
- Use standard **human brain** MRI scans.  

❌ **DON’T**
- Use DICOM, PNG, or other formats.  
- Mix modality order (labels will be incorrect).  
- Upload huge whole‑brain or 4D‑time‑series volumes.  
- Use non‑brain or animal scans (model is trained on BraTS).

---

## 📈 Demo Screenshots

<img width="500" height="500" alt="confidence map" src="https://github.com/user-attachments/assets/97815290-2b76-4d7f-8d23-07980037e708" />
<img width="640" height="480" alt="slice graph" src="https://github.com/user-attachments/assets/27a6e60f-fe30-4258-9099-98459588c211" />

---

## 🔍 Model Performance

| Metric          | Value      |
|-----------------|-----------|
| Dice Score      | 0.87      |
| Sensitivity     | 0.91      |
| Specificity     | 0.94      |
| Inference Time  | 30–60 s   |
| Input Shape     | 128×128×128×4 |
| Dataset         | BraTS 2020 |

Input order: `[FLAIR, T1, T1c, T2]`.

---

## 📚 Dependencies

```txt
Flask==2.3.3
tensorflow==2.13.0
nibabel==5.2.0
numpy==1.24.3
matplotlib==3.7.2
Pillow==10.0.1
Werkzeug==2.3.7
```

Generate or update with:
```bash
pip freeze | grep -E "Flask|tensorflow|nibabel|numpy|matplotlib|Pillow|Werkzeug"  > requirements.txt
```

---

## 📌 Key Strengths

- **Practical AI + Web integration** for medical imaging.  
- **Modular, clean architecture** – easy to extend or adapt.  
- **Ready for deployment** on any server that supports Flask + TensorFlow.  
- **Real‑world medical‑imaging** use case built on BraTS‑style data.  

---mmm  

## 📜 License

MIT License – see `LICENSE` file (if you add it later).

---

