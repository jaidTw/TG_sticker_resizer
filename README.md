# TG Sticker Resizer

Resize images to fit the sticker format required by Telegram

This script basically does following:
1. Use Pillow to fix the alpha channel of original images in case of sometimes they're wrong and could lead to bugs in waifu2x.
2. Use [nihui / waifu2x-ncnn-vulkan](https://github.com/nihui/waifu2x-ncnn-vulkan) to pre-scale images. (Optional)
3. Use OpenCV to adjust the image size.

## Requirement
* `pip install opencv-python`
* `pip install pillow`

## Usage

```
./resize.py [-f] [-h] [-w] <input_directory>
```
* `input_directory`: Directory of images to be processed
* `-f`: Force overwrite. The script would prompt for overwriting if the file to be written is already exists without this option specified.
* `-h`: Show help messages.
* `-w`: Use waifu2x to pre-scale the image. You should also configure the path of the `waifu2x-ncnn-vulkan` binary at the beginning of this script.

Processed images would be saved into `<input_directory>/out`


