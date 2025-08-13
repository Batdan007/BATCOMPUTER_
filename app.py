import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# wan2.2-main/gradio_ti2v.py
import gradio as gr
import torch
from huggingface_hub import snapshot_download
from PIL import Image
import random
import numpy as np
import spaces

import wan
from wan.configs import WAN_CONFIGS, SIZE_CONFIGS, MAX_AREA_CONFIGS, SUPPORTED_SIZES
from wan.utils.utils import cache_video

import gc

# --- 1. Global Setup and Model Loading ---

print("Starting Gradio App for Wan 2.2 TI2V-5B...")

# Download model snapshots from Hugging Face Hub
repo_id = "Wan-AI/Wan2.2-TI2V-5B"
print(f"Downloading/loading checkpoints for {repo_id}...")
ckpt_dir = snapshot_download(repo_id, local_dir_use_symlinks=False)
print(f"Using checkpoints from {ckpt_dir}")

# Load the model configuration
TASK_NAME = 'ti2v-5B'
cfg = WAN_CONFIGS[TASK_NAME]
FIXED_FPS = 24
MIN_FRAMES_MODEL = 8
MAX_FRAMES_MODEL = 121 

# Dimension calculation constants
MOD_VALUE = 32
DEFAULT_H_SLIDER_VALUE = 704
DEFAULT_W_SLIDER_VALUE = 1280
NEW_FORMULA_MAX_AREA = 1280.0 * 704.0

SLIDER_MIN_H, SLIDER_MAX_H = 128, 1280
SLIDER_MIN_W, SLIDER_MAX_W = 128, 1280

# Instantiate the pipeline in the global scope
print("Initializing WanTI2V pipeline...")
device = "cuda" if torch.cuda.is_available() else "cpu"
device_id = 0 if torch.cuda.is_available() else -1
pipeline = wan.WanTI2V(
    config=cfg,
    checkpoint_dir=ckpt_dir,
    device_id=device_id,
    rank=0,
    t5_fsdp=False,
    dit_fsdp=False,
    use_sp=False,
    t5_cpu=False,
    init_on_cpu=False,
    convert_model_dtype=True,
)
print("Pipeline initialized and ready.")

# --- Helper Functions (from Wan 2.1 Fast demo) ---
def _calculate_new_dimensions_wan(pil_image, mod_val, calculation_max_area,
                                 min_slider_h, max_slider_h,
                                 min_slider_w, max_slider_w,
                                 default_h, default_w):
    orig_w, orig_h = pil_image.size
    if orig_w <= 0 or orig_h <= 0:
        return default_h, default_w

    aspect_ratio = orig_h / orig_w
    
    calc_h = round(np.sqrt(calculation_max_area * aspect_ratio))
    calc_w = round(np.sqrt(calculation_max_area / aspect_ratio))

    calc_h = max(mod_val, (calc_h // mod_val) * mod_val)
    calc_w = max(mod_val, (calc_w // mod_val) * mod_val)
    
    new_h = int(np.clip(calc_h, min_slider_h, (max_slider_h // mod_val) * mod_val))
    new_w = int(np.clip(calc_w, min_slider_w, (max_slider_w // mod_val) * mod_val))
    
    return new_h, new_w

def handle_image_upload_for_dims_wan(uploaded_pil_image, current_h_val, current_w_val):
    """
    Handle image upload and calculate appropriate dimensions for video generation.
    
    Args:
        uploaded_pil_image: The uploaded image (PIL Image or numpy array)
        current_h_val: Current height slider value
        current_w_val: Current width slider value
        
    Returns:
        Tuple of gr.update objects for height and width sliders
    """
    if uploaded_pil_image is None:
        return gr.update(value=DEFAULT_H_SLIDER_VALUE), gr.update(value=DEFAULT_W_SLIDER_VALUE)
    try:
        # Convert numpy array to PIL Image if needed
        if hasattr(uploaded_pil_image, 'shape'):  # numpy array
            pil_image = Image.fromarray(uploaded_pil_image).convert("RGB")
        else:  # already PIL Image
            pil_image = uploaded_pil_image
            
        new_h, new_w = _calculate_new_dimensions_wan(
            pil_image, MOD_VALUE, NEW_FORMULA_MAX_AREA,
            SLIDER_MIN_H, SLIDER_MAX_H, SLIDER_MIN_W, SLIDER_MAX_W,
            DEFAULT_H_SLIDER_VALUE, DEFAULT_W_SLIDER_VALUE
        )
        return gr.update(value=new_h), gr.update(value=new_w)
    except Exception as e:
        gr.Warning("Error attempting to calculate new dimensions")
        return gr.update(value=DEFAULT_H_SLIDER_VALUE), gr.update(value=DEFAULT_W_SLIDER_VALUE)

def get_duration(image, 
                 prompt, 
                 height,
                 width,
                 duration_seconds, 
                 sampling_steps, 
                 guide_scale, 
                 shift, 
                 seed,
                 progress):
    """Calculate dynamic GPU duration based on parameters."""
    return sampling_steps * 15

# --- 2. Gradio Inference Function ---
@spaces.GPU(duration=get_duration)
def generate_video(
    image,
    prompt,
    height,
    width,
    duration_seconds,
    sampling_steps=38,
    guide_scale=cfg.sample_guide_scale,
    shift=cfg.sample_shift,
    seed=42,
    progress=gr.Progress(track_tqdm=True)
):
    """
    Generate a video from text prompt and optional image using the Wan 2.2 TI2V model.
    
    Args:
        image: Optional input image (numpy array) for image-to-video generation
        prompt: Text prompt describing the desired video
        height: Target video height in pixels
        width: Target video width in pixels
        duration_seconds: Desired video duration in seconds
        sampling_steps: Number of denoising steps for video generation
        guide_scale: Guidance scale for classifier-free guidance
        shift: Sample shift parameter for the model
        seed: Random seed for reproducibility (-1 for random)
        progress: Gradio progress tracker
        
    Returns:
        Path to the generated video file
    """
    if seed == -1:
        seed = random.randint(0, sys.maxsize)

    # Ensure dimensions are multiples of MOD_VALUE
    target_h = max(MOD_VALUE, (int(height) // MOD_VALUE) * MOD_VALUE)
    target_w = max(MOD_VALUE, (int(width) // MOD_VALUE) * MOD_VALUE)

    input_image = None
    if image is not None:
        input_image = Image.fromarray(image).convert("RGB")
        # Resize image to match target dimensions
        input_image = input_image.resize((target_w, target_h))
    
    # Calculate number of frames based on duration
    num_frames = np.clip(int(round(duration_seconds * FIXED_FPS)), MIN_FRAMES_MODEL, MAX_FRAMES_MODEL)

    # Create size string for the pipeline
    size_str = f"{target_h}*{target_w}"

    video_tensor = pipeline.generate(
        input_prompt=prompt,
        img=input_image,  # Pass None for T2V, Image for I2V
        size=SIZE_CONFIGS.get(size_str, (target_h, target_w)),
        max_area=MAX_AREA_CONFIGS.get(size_str, target_h * target_w),
        frame_num=num_frames,  # Use calculated frames instead of cfg.frame_num
        shift=shift,
        sample_solver='unipc',
        sampling_steps=int(sampling_steps),
        guide_scale=guide_scale,
        seed=seed,
        offload_model=True
    )

    # Save the video to a temporary file
    video_path = cache_video(
        tensor=video_tensor[None],  # Add a batch dimension
        save_file=None,  # cache_video will create a temp file
        fps=cfg.sample_fps,
        normalize=True,
        value_range=(-1, 1)
    )
    del video_tensor
    gc.collect()
    return video_path


# --- 3. Gradio Interface ---
css = ".gradio-container {max-width: 1100px !important; margin: 0 auto} #output_video {height: 500px;} #input_image {height: 500px;}"

with gr.Blocks(css=css, theme=gr.themes.Soft(), delete_cache=(60, 900)) as demo:
    gr.Markdown("# Wan 2.2 TI2V 5B")
    gr.Markdown("generate high quality videos using **Wan 2.2 5B Text-Image-to-Video model**,[[model]](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B),[[paper]](https://arxiv.org/abs/2503.20314)")

    with gr.Row():
        with gr.Column(scale=2):
            image_input = gr.Image(type="numpy", label="Optional (blank = text-to-image)", elem_id="input_image")
            prompt_input = gr.Textbox(label="Prompt", value="A beautiful waterfall in a lush jungle, cinematic.", lines=3)
            duration_input = gr.Slider(
                minimum=round(MIN_FRAMES_MODEL/FIXED_FPS, 1), 
                maximum=round(MAX_FRAMES_MODEL/FIXED_FPS, 1), 
                step=0.1, 
                value=2.0, 
                label="Duration (seconds)", 
                info=f"Clamped to model's {MIN_FRAMES_MODEL}-{MAX_FRAMES_MODEL} frames at {FIXED_FPS}fps."
            )
            
            with gr.Accordion("Advanced Settings", open=False):
                with gr.Row():
                    height_input = gr.Slider(minimum=SLIDER_MIN_H, maximum=SLIDER_MAX_H, step=MOD_VALUE, value=DEFAULT_H_SLIDER_VALUE, label=f"Output Height (multiple of {MOD_VALUE})")
                    width_input = gr.Slider(minimum=SLIDER_MIN_W, maximum=SLIDER_MAX_W, step=MOD_VALUE, value=DEFAULT_W_SLIDER_VALUE, label=f"Output Width (multiple of {MOD_VALUE})")
                steps_input = gr.Slider(label="Sampling Steps", minimum=10, maximum=50, value=38, step=1)
                scale_input = gr.Slider(label="Guidance Scale", minimum=1.0, maximum=10.0, value=cfg.sample_guide_scale, step=0.1)
                shift_input = gr.Slider(label="Sample Shift", minimum=1.0, maximum=20.0, value=cfg.sample_shift, step=0.1)
                seed_input = gr.Number(label="Seed (-1 for random)", value=-1, precision=0)

        with gr.Column(scale=2):
            video_output = gr.Video(label="Generated Video", elem_id="output_video")
            run_button = gr.Button("Generate Video", variant="primary")
            
    # Add image upload handler
    image_input.upload(
        fn=handle_image_upload_for_dims_wan,
        inputs=[image_input, height_input, width_input],
        outputs=[height_input, width_input]
    )
    
    image_input.clear(
        fn=handle_image_upload_for_dims_wan,
        inputs=[image_input, height_input, width_input],
        outputs=[height_input, width_input]
    )

    example_image_path = os.path.join(os.path.dirname(__file__), "examples/i2v_input.JPG")
    gr.Examples(
        examples=[
            [example_image_path, "The cat removes the glasses from its eyes.", 1088, 800, 1.5],
            [None, "A cinematic shot of a boat sailing on a calm sea at sunset.", 704, 1280, 2.0],
            [None, "Drone footage flying over a futuristic city with flying cars.", 704, 1280, 2.0],
        ],
        inputs=[image_input, prompt_input, height_input, width_input, duration_input],
        outputs=video_output,
        fn=generate_video,
        cache_examples="lazy",
    )

    run_button.click(
        fn=generate_video,
        inputs=[image_input, prompt_input, height_input, width_input, duration_input, steps_input, scale_input, shift_input, seed_input],
        outputs=video_output
    )

if __name__ == "__main__":
    demo.launch(mcp_server=True)