 # Installation Guide

This guide provides instructions for setting up the necessary dependencies for `dt2civitai.py` on macOS, including installing `exiftool` and Pillow for Python via Homebrew. If you already have these installed and working, you can skip this section.

## Prerequisites

Before proceeding, ensure you have the following:

- macOS operating system
- Internet connection

## Installing Homebrew

Homebrew is a package manager for macOS. If you already have Homebrew installed, skip to the next section. Otherwise, follow these steps to install it:

1. Open Terminal (you can find it using Spotlight search or navigate to `Applications -> Utilities -> Terminal`).
2. Paste the following command and press Enter:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Follow the prompts to complete the installation.

## Installing exiftool with Homebrew

`exiftool` is a powerful tool for reading, writing, and editing meta-information in various files. Follow these steps to install it using Homebrew:

1. Open Terminal.
2. Run the following command:
   ```bash
   brew install exiftool
   ```
3. Once the installation is complete, verify it by running:
   ```bash
   exiftool -ver
   ```

## Installing Pillow for Python

Pillow is a Python Imaging Library that adds image processing capabilities to your Python interpreter. To install Pillow, follow these steps:

1. Ensure you have Python3 installed. Check by running:
   ```bash
   python3 --version
   ```
2. If Python3 is not installed, download and install it with Homebrew:
   ```bash
   brew install python3
   ```
3. Open Terminal.
4. Run the following command to install Pillow using Homebrew:
   ```bash
   brew install pillow
   ```
5. Verify the installation by running a Python script that imports Pillow:
   ```python
   python3 -c "import PIL"
   ```

## Conclusion

You've successfully installed `exiftool` with Homebrew and Pillow for Python on your macOS system. You are now ready to use these tools in your Python scripts. For more information on using exiftool and Pillow, refer to their respective documentation.

# Important Caveats

- `dt2civitai.py` may request permission from MacOS to access data from other apps while reading Draw Things' models directory. Please grant it permission.
- If you use an external models directory, uncomment the relevant line in the script and modify the path accordingly.
- The shebang in the script assumes Python3 was installed with Homebrew. Modify the path if needed.

## Usage

The `dt2civitai.py` script can be used in various ways:

- Process an individual image:
  ```bash
  python3 dt2civitai.py input_image.png output_folder
  ```
- Process a folder of images:
  ```bash
  python3 dt2civitai.py /path/to/image/folder/ /destination/folder/
  ```
- Process all Draw Things images in the current directory:
  ```bash
  python3 dt2civitai.py
  ```
