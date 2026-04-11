import os
import numpy as np
import nibabel as nib
import tensorflow as tf
import matplotlib.pyplot as plt

PATCH = 32
RESULT_DIR = "static/results"
os.makedirs(RESULT_DIR, exist_ok=True)

# -------- LOAD MODEL --------
model = tf.keras.models.load_model("brain_tumor_3DUNet.keras", compile=False)

# -------- LOAD 4 MRI MODALITIES --------
def load_modalities(t1, t1ce, flair, t2):
    t1 = nib.load(t1).get_fdata()
    t1ce = nib.load(t1ce).get_fdata()
    flair = nib.load(flair).get_fdata()
    t2 = nib.load(t2).get_fdata()

    vol = np.stack([flair, t1, t1ce, t2], -1).astype("float32")
    vol = (vol - vol.min()) / (vol.max() - vol.min() + 1e-8)
    return vol

# -------- FULL VOLUME PREDICTION --------
def predict_volume(vol):
    D, H, W, _ = vol.shape

    pad = [
        (0, PATCH - (D % PATCH)),
        (0, PATCH - (H % PATCH)),
        (0, PATCH - (W % PATCH)),
        (0, 0)
    ]

    v = np.pad(vol, pad)
    out = np.zeros(v.shape[:3])
    conf_out = np.zeros(v.shape[:3])

    for z in range(0, v.shape[0], PATCH):
        for y in range(0, v.shape[1], PATCH):
            for x in range(0, v.shape[2], PATCH):
                patch = v[z:z+PATCH, y:y+PATCH, x:x+PATCH]
                if patch.shape != (PATCH, PATCH, PATCH, 4):
                    continue
                probs = model.predict(patch[None], verbose=0)[0]
                out[z:z+PATCH, y:y+PATCH, x:x+PATCH] = np.argmax(probs, -1)
                conf_out[z:z+PATCH, y:y+PATCH, x:x+PATCH] = np.max(probs, -1)

    return out[:D,:H,:W], conf_out[:D,:H,:W]

# -------- MAIN FUNCTION USED BY FLASK --------
def predict_all(t1, t1ce, flair, t2):

    vol = load_modalities(t1, t1ce, flair, t2)
    pred, conf = predict_volume(vol)

    nib.save(nib.Nifti1Image(pred, np.eye(4)), f"{RESULT_DIR}/pred_mask.nii.gz")

    type_map = {1:"NET", 2:"ED", 4:"ET"}
    labels = np.unique(pred)
    present = [type_map[l] for l in labels if l in type_map]

    tumor_voxels = int(np.sum(pred > 0))
    tumor_percent = round((tumor_voxels / np.prod(pred.shape)) * 100, 4)

    # ---- SLICE GRAPH ----
    slice_tumor = [int(np.sum(pred[z] > 0)) for z in range(pred.shape[0])]
    graph_path = f"{RESULT_DIR}/slice_graph.png"

    plt.figure()
    plt.plot(slice_tumor)
    plt.title("Tumor Area per Slice")
    plt.savefig(graph_path)
    plt.close()

    # ---- OVERLAYS ----
    overlay_paths = []
    mid = pred.shape[0] // 2

    for i in range(mid-5, mid+5):
        path = f"{RESULT_DIR}/overlay_{i}.png"
        plt.figure(figsize=(5,5))
        plt.imshow(vol[i,:,:,0], cmap="gray")
        plt.imshow(pred[i], cmap="jet", alpha=0.4)
        plt.axis("off")
        plt.savefig(path)
        plt.close()
        overlay_paths.append(path)

    # ---- CONFIDENCE MAP ----
    conf_path = f"{RESULT_DIR}/confidence.png"
    plt.figure(figsize=(5,5))
    plt.imshow(conf[mid], cmap="hot")
    plt.colorbar()
    plt.title("Confidence Map")
    plt.savefig(conf_path)
    plt.close()

    return {
        "overlays": overlay_paths,
        "graph": graph_path,
        "confidence": conf_path,
        "types": present,
        "tumor_voxels": tumor_voxels,
        "tumor_percent": tumor_percent
    }
