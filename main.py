import os
import requests
import gradio as gr
from gradio_imageslider import ImageSlider

from subprocess import check_call

def download_model(url, dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    file_name = url.split('/')[-1]  
    file_path = os.path.join(dirpath, file_name)
    if os.path.exists(file_path):
        return
    with requests.get(url, stream=True) as r:
        r.raise_for_status()  # 检查响应状态，如果不是200，则抛出异常
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
image_upscale_models = [
    'https://github.com/GeeMoose/Image-Upscale/releases/download/v0.0.2/RealESRGAN_General_x4_v3.bin',
    'https://github.com/GeeMoose/Image-Upscale/releases/download/v0.0.3/RealESRGAN_General_x4_v3.param',
    'https://github.com/GeeMoose/Image-Upscale/releases/download/v0.0.2/ultramix_balanced.bin',
    'https://github.com/GeeMoose/Image-Upscale/releases/download/v0.0.3/ultramix_balanced.param',
    'https://github.com/GeeMoose/Image-Upscale/releases/download/v0.0.2/ultrasharp.bin',
    'https://github.com/GeeMoose/Image-Upscale/releases/download/v0.0.3/ultrasharp.param'
]

for model_url in image_upscale_models:
    download_model(model_url, 'models')

def upscaled_arg(filePath, outFile, modelsPath, model, scale, gpuid, saveImageAs):
    return [
        "-i",
        filePath,
        "-o",
        outFile,
        "-s",
        scale,
        "-m",
        modelsPath,
        "-n",
        model,
        "-g",
        gpuid,
        "-f",
        saveImageAs,
    ]

def spawnUpscaling(commands, arguments):
    args = ','.join([arg for arg in arguments])
    executor = commands + ',' + args
    return executor.split(',')

def upscale_image(fullfileName, scale, model,gpuid=""):
    arguments = upscaled_arg(
        fullfileName, "./output.png", 'models', model, str(scale), gpuid, 'png')
    print(arguments)
    ret = check_call(spawnUpscaling('./bin/upscaling-realesrgan', arguments))
    return './output.png'
    
# upscale_image('image1.png', 'output.png', 'ultramix_balanced', '2', '')

# Define the Gradio interface
iface = gr.Interface(
    fn=upscale_image,
    inputs=[
        gr.Image(label="Input Image", type="filepath"),
        gr.Slider(minimum=1, maximum=4, step=1, value=2, label="Scale Factor"),
        gr.Dropdown(choices=["RealESRGAN_General_x4_v3","ultramix_balanced", "ultrasharp"], label="Model",value="RealESRGAN_General_x4_v3")
    ],
    outputs = ImageSlider(label="Before / After"),
    title="Image Upscaling",
    description="Upload an image to upscale it using Real-ESRGAN."
)


iface.launch(debug=True)