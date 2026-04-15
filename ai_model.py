import os
import uuid
import warnings
import numpy as np
import nibabel as nib
import tensorflow as tf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=UserWarning)

PATCH = 32
RESULT_DIR = "static/results"
MODEL_PATH = "brain_tumor_3DUNet.keras"

os.makedirs(RESULT_DIR, exist_ok=True)

model = None
MODEL_OUTPUT_CLASSES = None

try:
    model = tf.keras.models.load_model(
        MODEL_PATH,
        compile=False,
        safe_mode=True
    )
    model_output_shape = model.output_shape
    if isinstance(model_output_shape, list):
        model_output_shape = model_output_shape[0]
    MODEL_OUTPUT_CLASSES = int(model_output_shape[-1])
except Exception:
    model = None
    MODEL_OUTPUT_CLASSES = None


def normalize_channel(channel):
    channel = channel.astype(np.float32)
    cmin = np.min(channel)
    cmax = np.max(channel)

    if cmax - cmin < 1e-8:
        return np.zeros_like(channel, dtype=np.float32)

    return (channel - cmin) / (cmax - cmin)


def normalize_volume(vol):
    vol = vol.astype(np.float32)
    out = np.zeros_like(vol, dtype=np.float32)

    for i in range(vol.shape[-1]):
        out[..., i] = normalize_channel(vol[..., i])

    return out


def load_nifti(path):
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"NIfTI file not found: {path}")

    img = nib.load(path)
    data = img.get_fdata(dtype=np.float32)

    if data.ndim != 3:
        raise ValueError(f"Expected 3D NIfTI volume, got shape {data.shape} for {path}")

    return img, data


def load_modalities(t1, t1ce, flair, t2):
    t1_img, t1_data = load_nifti(t1)
    t1ce_img, t1ce_data = load_nifti(t1ce)
    flair_img, flair_data = load_nifti(flair)
    t2_img, t2_data = load_nifti(t2)

    shapes = {t1_data.shape, t1ce_data.shape, flair_data.shape, t2_data.shape}
    if len(shapes) != 1:
        raise ValueError(f"Input MRI shapes do not match: {shapes}")

    vol = np.stack([flair_data, t1_data, t1ce_data, t2_data], axis=-1)
    vol = normalize_volume(vol)

    meta = {
        "base_img": flair_img,
        "shape": vol.shape
    }
    return vol, meta


def compute_padding(shape3d, patch_size):
    d, h, w = shape3d
    pd = (patch_size - (d % patch_size)) % patch_size
    ph = (patch_size - (h % patch_size)) % patch_size
    pw = (patch_size - (w % patch_size)) % patch_size
    return [(0, pd), (0, ph), (0, pw), (0, 0)]


def remap_to_brats_labels(raw):
    raw = raw.astype(np.uint8)

    if MODEL_OUTPUT_CLASSES == 4:
        return raw

    if MODEL_OUTPUT_CLASSES == 5:
        mapping = np.array([0, 1, 2, 4, 4], dtype=np.uint8)
        return mapping[raw]

    if MODEL_OUTPUT_CLASSES == 3:
        mapping = np.array([1, 2, 4], dtype=np.uint8)
        return mapping[raw]

    unique_vals = np.unique(raw)
    if set(unique_vals.tolist()).issubset({0, 1, 2, 4}):
        return raw

    return raw


def decode_prediction(probs):
    if probs.ndim != 4:
        raise ValueError(f"Unexpected model output shape: {probs.shape}")

    raw = np.argmax(probs, axis=-1).astype(np.uint8)
    pred_patch = remap_to_brats_labels(raw)
    conf_patch = np.max(probs, axis=-1).astype(np.float32)

    return pred_patch, conf_patch


def predict_volume(vol):
    d, h, w, c = vol.shape
    if c != 4:
        raise ValueError(f"Expected 4 MRI channels, got {c}")

    if model is None:
        pred = np.zeros((d, h, w), dtype=np.uint8)
        conf = np.zeros((d, h, w), dtype=np.float32)
        return pred, conf

    pad = compute_padding((d, h, w), PATCH)
    v = np.pad(vol, pad, mode="constant", constant_values=0)

    pred_out = np.zeros(v.shape[:3], dtype=np.uint8)
    conf_out = np.zeros(v.shape[:3], dtype=np.float32)

    for z in range(0, v.shape[0], PATCH):
        for y in range(0, v.shape[1], PATCH):
            for x in range(0, v.shape[2], PATCH):
                patch = v[z:z + PATCH, y:y + PATCH, x:x + PATCH]

                if patch.shape != (PATCH, PATCH, PATCH, 4):
                    continue

                probs = model.predict(patch[None, ...], verbose=0)[0]
                pred_patch, conf_patch = decode_prediction(probs)

                pred_out[z:z + PATCH, y:y + PATCH, x:x + PATCH] = pred_patch
                conf_out[z:z + PATCH, y:y + PATCH, x:x + PATCH] = conf_patch

    return pred_out[:d, :h, :w], conf_out[:d, :h, :w]


def normalize_slice_for_display(slice_2d):
    s = slice_2d.astype(np.float32)
    smin = np.min(s)
    smax = np.max(s)

    if smax - smin < 1e-8:
        return np.zeros_like(s, dtype=np.float32)

    return (s - smin) / (smax - smin)


def save_slice_graph(pred, run_id):
    slice_tumor = [int(np.sum(pred[z] > 0)) for z in range(pred.shape[0])]
    graph_path = os.path.join(RESULT_DIR, f"slice_graph_{run_id}.png")

    plt.figure(figsize=(8, 4))
    plt.plot(slice_tumor, color="blue", linewidth=2)
    plt.title("Tumor Area per Slice")
    plt.xlabel("Slice Index")
    plt.ylabel("Tumor Voxels")
    plt.tight_layout()
    plt.savefig(graph_path, dpi=150, bbox_inches="tight")
    plt.close()

    return graph_path, slice_tumor


def save_overlays(vol, pred, run_id):
    overlay_paths = []
    d = pred.shape[0]

    tumor_slices = [i for i in range(d) if np.sum(pred[i] > 0) > 0]

    if tumor_slices:
        center_idx = tumor_slices[len(tumor_slices) // 2]
        start = max(0, center_idx - 5)
        end = min(d, center_idx + 5)
    else:
        mid = d // 2
        start = max(0, mid - 5)
        end = min(d, mid + 5)

    for i in range(start, end):
        path = os.path.join(RESULT_DIR, f"overlay_{run_id}_{i}.png")
        base_slice = normalize_slice_for_display(vol[i, :, :, 0])

        plt.figure(figsize=(5, 5))
        plt.imshow(base_slice, cmap="gray")

        masked_pred = np.ma.masked_where(pred[i] == 0, pred[i])
        plt.imshow(masked_pred, cmap="jet", alpha=0.4, interpolation="nearest")

        plt.title(f"Overlay Slice {i}")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(path, dpi=150, bbox_inches="tight", pad_inches=0)
        plt.close()

        overlay_paths.append(path)

    return overlay_paths


def save_confidence_map(conf, pred, run_id):
    if pred is not None and np.any(pred > 0):
        slice_scores = [np.sum(pred[i] > 0) for i in range(pred.shape[0])]
        mid = int(np.argmax(slice_scores))
    else:
        mid = conf.shape[0] // 2

    conf_path = os.path.join(RESULT_DIR, f"confidence_{run_id}.png")

    plt.figure(figsize=(5, 5))
    plt.imshow(conf[mid], cmap="hot")
    plt.colorbar()
    plt.title(f"Confidence Map - Slice {mid}")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(conf_path, dpi=150, bbox_inches="tight")
    plt.close()

    return conf_path


def to_web_path(path):
    return path.replace("\\", "/")


def predict_all(t1, t1ce, flair, t2):
    run_id = uuid.uuid4().hex[:12]

    vol, meta = load_modalities(t1, t1ce, flair, t2)
    pred, conf = predict_volume(vol)

    base_img = meta["base_img"]
    pred_img = nib.Nifti1Image(
        pred.astype(np.uint8),
        affine=base_img.affine,
        header=base_img.header
    )
    pred_mask_path = os.path.join(RESULT_DIR, f"pred_mask_{run_id}.nii.gz")
    nib.save(pred_img, pred_mask_path)

    type_map = {
        1: "NET/NCR",
        2: "ED",
        4: "ET"
    }

    labels = np.unique(pred).astype(int).tolist()
    present = [type_map[l] for l in labels if l in type_map]

    tumor_voxels = int(np.sum(pred > 0))
    total_voxels = int(np.prod(pred.shape))
    tumor_percent = round((tumor_voxels / total_voxels) * 100, 4) if total_voxels > 0 else 0.0

    graph_path, slice_tumor = save_slice_graph(pred, run_id)
    overlay_paths = save_overlays(vol, pred, run_id)
    conf_path = save_confidence_map(conf, pred, run_id)

    mean_conf = float(np.mean(conf[pred > 0])) if tumor_voxels > 0 else 0.0
    max_conf = float(np.max(conf)) if conf.size > 0 else 0.0

    return {
        "pred_mask": to_web_path(pred_mask_path),
        "overlays": [to_web_path(p) for p in overlay_paths],
        "graph": to_web_path(graph_path),
        "confidence_map": to_web_path(conf_path),
        "types": present,
        "labels_found": labels,
        "tumor_voxels": tumor_voxels,
        "tumor_percent": tumor_percent,
        "max_confidence": round(max_conf, 4),
        "mean_confidence": round(mean_conf, 4),
        "confidence": f"{mean_conf * 100:.2f}%",
        "prediction": "Tumor Detected" if tumor_voxels > 0 else "No Tumor Found",
        "slice_tumor_counts": slice_tumor,
        "volume_shape": list(pred.shape)
    }
