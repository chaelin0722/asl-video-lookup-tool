const express = require("express");
const cors = require('cors');
const multer = require("multer");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");
//const path = require("path");

const app = express();

// to show local files to local host webpage
const gifFolderPath = "path to gifs";
app.use('/gifs', express.static(gifFolderPath));
// save webm -> mp4 files to here
app.use('/tmp', express.static("absolute directory to where recorded file created"));

// Enable CORS
app.use(cors());

// Enable Cross-Origin Isolation for SharedArrayBuffer support
app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Cross-Origin-Opener-Policy", "same-origin");
  res.setHeader("Cross-Origin-Embedder-Policy", "require-corp");
  next();
});


const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, "absolute directory to where recorded file created"); // directory for save files
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + "-" + Math.round(Math.random() * 1e9);
    const originalName = file.originalname; // file name
    const extension = originalName.substring(originalName.lastIndexOf(".")); // get file format
    cb(null, `${file.fieldname}-${uniqueSuffix}${extension}`); // file name
  },
});

const upload = multer({ storage: storage });





// convert recorded webm file to mp4 file
app.post("/convert-video", upload.single("video"), async (req, res) => {
  const inputPath = req.file.path;
  const pythonProcess = spawn("python3", [
    "absolute direcory to/sl-wrapper-main/recognition_mod/convert_webm_to_mp4.py",
    inputPath,
  ]);

  let convertedPath = "";
  pythonProcess.stdout.on("data", (data) => {
    convertedPath += data.toString();
  });
  //  send converted mp4 to process on UI
  const outputPath = inputPath.replace(".webm", ".mp4");
  pythonProcess.on("close", (code) => {
    if (code !== 0) {
      return res.status(500).json({ error: "Conversion failed" });
    } 
    res.sendFile(outputPath); 

  });
});



// endpoint for processing video
app.post("/process-video", upload.single("video"), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: "No video uploaded." });
  }

  console.log("File uploaded successfully:", req.file);
  const videoPath = req.file.path;  


  // JSON 파일 경로 생성 (같은 tmp 디렉토리에 저장)
  const path = require("path"); // path 모듈 사용
  const jsonPath = path.join(
  path.dirname(videoPath), // 비디오 파일의 디렉토리 경로
  `${path.basename(videoPath, path.extname(videoPath))}.json`
);


  // Run Python Script
  let pythonProcess;
  if (req.body.scriptName === "submit") {
      pythonProcess = spawn("python3", [
        "absolute directory to/sl-wrapper-main/segmentation_mod/e2e_seg2rec.py",
        "--video",
        videoPath,
      ]);

  } else if (req.body.scriptName === "find-a-sign") {
    console.log("start recognition! find-a-sign");
    const videoPath = req.file.path; // uploaded video path
    const start = parseFloat(req.body.start);
    const end = parseFloat(req.body.end);

    const output_file = path.join(
    path.dirname(videoPath),
    path.basename(videoPath, path.extname(videoPath)) + '.txt'
    );


    // create segment.txt
    const txtContent = `Start: ${start.toFixed(3)} sec, End: ${end.toFixed(3)} sec\n`;
    fs.writeFileSync(output_file, txtContent);

    console.log(`Created file: ${output_file}`);


    pythonProcess = spawn("python3", [
      "absolute directory to/sl-wrapper-main/recognition_mod/e2e_recognition_stgcn.py",
      "--input_segtxt", output_file,
      "--video", videoPath]);

  } else {
    return res.status(400).json({ error: "Invalid scriptName provided." });
  }


  // handle python process exit
  pythonProcess.on("close", (code) => {
    if (code !== 0) {
      return res
        .status(500)
        .json({ error: "Python script failed to process the video." });
    }

    console.log(`Attempting to read JSON file at: ${jsonPath}`);
    // JSON 결과 읽기
    fs.readFile(jsonPath, "utf8", (err, data) => {
      if (err) {
        console.error("Error Reading JSON File:", err);
        return res
          .status(500)
          .json({ error: "Failed to read the output JSON file." });

      }else{
        console.log("JSON File Data:", data);
      }
      res.json(JSON.parse(data)); // return results
    });

  });
});


// to check the root url
app.get("/", (req, res) => {
  res.send("Server is running and ready to receive requests!");
});
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
