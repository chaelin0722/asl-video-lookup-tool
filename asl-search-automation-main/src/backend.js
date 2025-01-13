const express = require("express");
const cors = require('cors');
const multer = require("multer");
const { spawn } = require("child_process");
const fs = require("fs");
//const path = require("path");

const app = express();

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, "/Users/zzenninkim/Documents/Research/asl-search-automation-main/src/tmp/"); // 저장할 디렉토리
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + "-" + Math.round(Math.random() * 1e9);
    const originalName = file.originalname; // 원래 파일 이름
    const extension = originalName.substring(originalName.lastIndexOf(".")); // 확장자 추출
    cb(null, `${file.fieldname}-${uniqueSuffix}${extension}`); // 커스터마이즈된 파일 이름
  },
});

const upload = multer({ storage: storage });


// Enable CORS
app.use(cors());
// 비디오 처리 엔드포인트
app.post("/process-video", upload.single("video"), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: "No video uploaded." });
  }

  console.log("File uploaded successfully:", req.file);
  const videoPath = req.file.path; // 임시 경로에 저장된 파일

  // JSON 파일 경로 생성 (같은 tmp 디렉토리에 저장)
  const path = require("path"); // path 모듈 사용
  const jsonPath = path.join(
  path.dirname(videoPath), // 비디오 파일의 디렉토리 경로
  `${path.basename(videoPath, path.extname(videoPath))}.json`
);

  /*
  const outputJsonPath = path.join(
    "results",
    `${path.basename(req.file.originalname, path.extname(req.file.originalname))}.json`
  );
*/
  // Run Python Script
  // 실행할 Python 스크립트 경로 설정
  let pythonProcess;
  if (req.body.scriptName === "submit") {
    /*    pythonProcess = spawn("python3", [
          "/Users/zzenninkim/Documents/Research/sign-segmentation/demo/e2e_newseg2rec.py",
          "--video_path",
          videoPath,
          "--save_path",
          "/Users/zzenninkim/Documents/Research/sign-segmentation/demo/results"ßß,
          "--save_segments"

      ]);*/
      pythonProcess = spawn("python3", [
    "/Users/zzenninkim/Documents/Research/sl-wrapper-main/segmentation_mod/e2e_seg2rec.py",
    "--video",
    videoPath,
  ]);

  } else if (req.body.scriptName === "find-a-sign") {
    console.log("start recognition! find-a-sign");
    const videoPath = req.file.path; // 업로드된 비디오 경로
    const start = parseFloat(req.body.start); // 선택된 시작 시간
    const end = parseFloat(req.body.end); // 선택된 종료 시간

    const output_file = path.join(
    path.dirname(videoPath),
    path.basename(videoPath, path.extname(videoPath)) + '.txt'
    );


    // create segment.txt
    const txtContent = `Start: ${start.toFixed(3)} sec, End: ${end.toFixed(3)} sec\n`;
    fs.writeFileSync(output_file, txtContent);

    console.log(`Created file: ${output_file}`);


    pythonProcess = spawn("python3", [
      "/Users/zzenninkim/Documents/Research/sl-wrapper-main/recognition_mod/e2e_recognition.py",
      "--input_segtxt", output_file,
      "--video", videoPath]);

  } else {
    return res.status(400).json({ error: "Invalid scriptName provided." });
  }





  /*
  * python demo/demo.py
  * --video_path /Users/zzenninkim/dataset/How2Sign/Video_test_for_analysis/G3FhmHz_7hs_15-10-rgb_front.mp4
  * --slowdown_factor 1 --save_segments --viz
  * */


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
      res.json(JSON.parse(data)); // 결과 반환
    });

    // 임시 파일 삭제
    /*
    fs.unlink(videoPath, (err) => {
      if (err) console.error("Failed to delete uploaded file:", err);
    });*/
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