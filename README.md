
# ASL Video Lookup Tool (`asl-video-lookup-tool`)

This project is the official implementation of the system presented at the **ACM ASSETS 2026** conference.

It is an AI-powered tool that allows users to upload and record a long ASL (American Sign Language) video and automatically:

- Segment the video into individual signs
- Recognize each sign
- Return the gloss (English meaning) for each recognized sign

<img width="861" height="377" alt="Overview_UI" src="https://github.com/user-attachments/assets/d885c328-9cc6-412f-a78e-7ea3f5b7f53e" />


## 📂 Project Structure

- `asl-search-automation-main/`: Contains the frontend files and UI logic
- `sl-wrapper-main/`: Backend modules for segmentation and recognition


## ⚙️ Installation & Execution

### 1. Environment Setup

Install the required YAML environment and activate it:
```
conda env create -f environment.yml
conda activate SLD-2025
```

### 2. Run the frontend
```
cd ~ asl-video-lookup-tool/asl-search-automation-main/src/
npm install
npm run build
npm run serve 
```

### 3. Run the backend
```
cd ~ asl-video-lookup-tool/asl-search-automation-main/src/
node backend.js
```

## ⚠️ Configuration Notes
Make sure that you update all absolute paths in the following files to match your local directory structure.

✅ asl-search-automation-main/src/backend.js:
	
 • Line 13: gifFolderPath → Path to the folder where your GIFs are stored
 • Lines 15, 31, 51, 94, 119: Update these to your repository’s absolute path

Example:

```
const gifFolderPath = "/Users/yourname/Downloads/gifs/gifs/";
```

✅ sl-wrapper-main/recognition_mod/e2e_recognition_stgcn.py:

 • Line 165: Update with your local absolute path


✅ sl-wrapper-main/segmentation_mod/e2e_seg2rec.py:

 • Lines 29, 40, 41, 84: Update with your local absolute paths

## Pretrained Weights

1. Download the pretrained weights from [Google Drive](https://drive.google.com/file/d/1CXX6YrH3sJvxLaUMg-KCjUZCTsvcABfY/view?usp=sharing).
2. Place the downloaded file into the following directory:
   ```bash
   ./recognition_mod/STGCN/ALL_weights/
	```


### 🚀 Features

🎥 Upload or record long ASL videos via the web interface

✂️ Automatically segment videos into individual signs

🧠 Recognize 991 sign classes using an ST-GCN-based model

🔍 View top gloss predictions for each sign, with matching GIFs for visual reference



## 📝 Publication & Citation

If you use this tool, the dataset, or the underlying methodology in your research, please cite our paper:

> **Design and Evaluation of an AI-Based American Sign Language Video Comprehension Tool: Exploring the Benefits and Use of Automatic Segmentation and Sign Lookup**
> Chaelin Kim, Denise Crochet, Maty Bohacek, and Saad Hassan. 2026. In *Proceedings of the 28th International ACM SIGACCESS Conference on Computers and Accessibility (ASSETS ’26)*. Association for Computing Machinery, New York, NY, USA.

### BibTeX
```bibtex
@inproceedings{kim2026design,
  author    = {Kim, Chaelin and Crochet, Denise and Bohacek, Maty and Hassan, Saad},
  title     = {Design and Evaluation of an AI-Based American Sign Language Video Comprehension Tool: Exploring the Benefits and Use of Automatic Segmentation and Sign Lookup},
  booktitle = {Proceedings of the 28th International ACM SIGACCESS Conference on Computers and Accessibility (ASSETS '26)},
  year      = {2026},
  location  = {Porto, Portugal},
  publisher = {ACM},
  address   = {New York, NY, USA}
}






