# SL Processing Wrapper

This wrapper repository includes sign segmentation and recognition functionality. Our goal is to connect these two modules into a joint pipeline.

## Segmentation

The interface is implemented in `segmentation_mod/segmentation.py`. In this script, an example use of the `segment_into_sign()` function is provided. This function takes in a path to an mp4 video and provides you an EAF representation of the segmented signs.

> [!NOTE]  
> Running this script in an IDE and inspecting the x variable can be very helpful! You will immediately see the representation of segmented timestamps.

## Recognition

The interface is implemented in `recognition_mod/recognition.py`. In this script, an example use of the `recognize_sign()` function is provided. This function takes in a path to an mp4 video and provides you a list of predicted signs, as well as their likelihood.

> [!NOTE]  
> Our current recogniton model supoorts 100 signs. Once we retrain it on the new datasets, an update will have to be made to the repo to support its vocab.

## Environment Setup

**1.** Clone the repo and locate the directory in Terminal.
**2.** Create a Conda environment:

```bash
conda create -n sl-wrapper python=3.8
```

**3.** Go into the environment:

```bash
conda activate sl-wrapper
```

**4.** Install dependencies for the segmentation module.

```bash
pip install git+https://github.com/sign-language-processing/transcription
```

**5.** Install dependencies for the recognition module.

```bash
pip install -r requirements.txt
```

**6.** Download the recognition model from [here](https://drive.google.com/file/d/1Fs_Ilo916kHznlrt-dUK2cwbuyl1HGTx/view?usp=sharing) and place it into the `recognition_mod` folder.

**7.** If you are using a Mac with Apple Silicon (M1/M2/M3 chip), complete an additional step below. If you are a PC or a Linux user, or if you use an Intel-based Mac, you are done!

<details>
  <summary>Click to see additional step</summary>
  <br>
  <b>6a.</b> Because of messy versioning on the side of PyTorch and version requirements of the segmenation and recognition repositories, you will need to change some files down in Conda. Pace yourself!
  <br>
  <b>6b.</b> First, locate the folder with the PyTorch (torch) library in your Conda environment. This path can look like `/Users/yourusernamehere/anaconda3/envs/sl-wrapper-2/lib/python3.8/site-packages/torch/`, but can also differ based on your macOS version.
  <br>
  <b>6c.</b> Locate the folder `nn/modules` within the `torch` folder.
  <br>
  <b>6d.</b> Take the files located in this repository's `apple-silicon-torch-fix` folder and copy them over into `nn/modules`. Note that you are replacing existing files -- that is intended.
  
</details>
