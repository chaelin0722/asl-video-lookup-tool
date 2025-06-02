# ASL Segmentation & Recognition Automation

This project is an AI-powered sign language dictionary tool.  
It allows users to upload and record a long ASL (American Sign Language) video and automatically:

- Segment the video into individual signs
- Recognize each sign
- Return the gloss (English meaning) for each recognized sign


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
cd ~ Asl_seg_rec/asl-search-automation-main/src/
Npm install
npm run build
npm run serve 
```

### 3. Run the backend
```
cd ~ Asl_seg_rec/asl-search-automation-main/src/
node backend.js
```

## ⚠️ Configuration Notes
Make sure to update all absolute paths in the following files to match your local directory structure.

✅ backend.js:
	•	Line 13: gifFolderPath → Path to the folder where your GIFs are stored
	•	Lines 15, 31, 51, 94, 119: Update these to your repository’s absolute path

Example:
```
const gifFolderPath = "/Users/yourname/Downloads/gifs/gifs/";
```
✅ sl-wrapper-main/recognition_mod/e2e_recognition_stgcn.py:
	•	Line 165: Update with your local absolute path

✅ sl-wrapper-main/segmentation_mod/e2e_seg2rec.py:
	•	Lines 29, 40, 41, 84: Update with your local absolute paths

### 🚀 Features
	•	🎥 Upload or record long ASL videos via the web interface
	•	✂️ Automatically segment videos into individual signs
	•	🧠 Recognize 991 sign classes using an ST-GCN-based model
	•	🔍 View top gloss predictions for each sign, with matching GIFs for visual reference






