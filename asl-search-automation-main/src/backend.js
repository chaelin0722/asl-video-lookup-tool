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
  // Python 스크립트 실행
  const pythonProcess = spawn("python3", [
    "/Users/zzenninkim/Documents/Research/sl-wrapper-main/segmentation_mod/e2e_seg2rec.py",
    "--video",
    videoPath,
  ]);


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
