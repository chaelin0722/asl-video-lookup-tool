<!-- 이 코드는 각 버튼들이 실행해야 할 동작들을 정리해둔 곳! -->
<template>
  <div id="span-selection">
    <header>

<!--<div id="next-video">
        <custom-button size="small" :has-border="true" @clicked="advanceStep()"
          >{{ nextStepText }}
        </custom-button>
      </div>-->
    </header>
    <div id="video-container">
      <video ref="videoPlayer" class="video-js"></video>
    </div>
    <div id="scratchpad">
      <textarea
        v-model="scratchpad"
        placeholder="Write the video's translation here..."
      ></textarea>
    </div>
    <div id="timeline-container">
      <timeline
        :position="videoPosition"
        :playing="playing"
        :duration="duration"
        :frame-base-name="frameBaseName"
        :frame-number="frameNumber"
        ref="timeline"
        @change="updateSelection($event)"
        @change-position="changeTick"
      />
    </div>
    <div id="video-controls-container">
      <video-controls
        :playing="playing"
        :playingSelection="playingSelection"
        :currentTime="currentTime"
        :duration="duration"
        @general-play="generalPlay()"
        @selection-play="selectionPlay()"
        @upload-video="uploadVideo()"
        @execute-model="executePythonScript()"
        @execute-recognition="executeRecPythonScript()"
        @record-video="Recording()"
      />
      <custom-button
      size="small"
      :has-border="true"
      @clicked="uploadVideo()"
      >Upload Video</custom-button
      >
    </div>
    <!--Add upload video button-->

    <div id="search-panel">
      <search
        ref="search"
        :selection="timelineSelection"
        :duration="duration"
        :currentStep="currentStep"
        :signs="signs"
      />
    </div>
  </div>
</template>

<script>
import videojs from 'video.js';
import Timeline from '../components/Timeline.vue';
import VideoControls from '../components/VideoControls.vue';
import Search from '../components/Search.vue';
import CustomButton from '../components/CustomButton.vue';
//import runPythonScript from "../backend.js";
import axios from "axios";

export default {
  name: 'SpanSelection',
  components: {Timeline, VideoControls, Search, CustomButton},
  props: {
    options: {
      type: Object,
      default() {
        return {
          autoplay: false,
          controls: false,
          fill: true,
          sources: [],
        };
      },
    },
  },
  data() {
    return {
      playing: false,
      showResults: false,
      interval: null,
      timelineSelection: {start: 0, end: 1},
      player: null,
      stopAtSelection: false,
      videoPosition: 0,
      experimentalSetup: null,
      currentStep: 0,
      scratchpad: '',
      signs: [],
      latinSquare: [],
      segments: [], // JSON data
      isRecording: false,
      mediaRecorder: null,
      recordedChunks: [],
      webcamStream: null,
      recordedBlob: null,
    };
  },
  methods: {
    async uploadVideo() {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'video/*';

      input.onchange = async (event) => {
        const file = event.target.files[0];
        if (file) {
          const url = URL.createObjectURL(file);
          this.player.src({src: url, type: 'video/mp4'});

          this.$saveAction('video_upload', {fileName: file.name});
          this.player.currentTime(0);
          this.playing = false;

          console.log("Extracting frames for uploaded file:", url);
          await this.extractFrames(url);

          this.uploadedFile = file; // 파일을 변수에 저장하여 나중에 사용
        }
      };

      input.click();
    },

    async extractFrames(videoUrl, fps = 29, videoWidth = 50) {

      return new Promise((resolve) => {
        const video = document.createElement('video');
        video.src = videoUrl;
        video.crossOrigin = 'anonymous';
        video.multed = true; // added to prevent auto play

        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        video.onloadedmetadata = async () => {
          // forcing to load all the video if the video duration is Infinity
          // webm file only load metadata, so they don't load all the video file. and this leads to problem that they can't extract all the frames.
          if (video.duration === Infinity) {
            console.warn("Video duration is Infinity. Attempting to fix...");

            await new Promise((resolve) => {
              video.currentTime = Number.MAX_SAFE_INTEGER;
              video.ontimeupdate = () => {
                video.ontimeupdate = null;
                console.log("Fixed duration:", video.duration);
                resolve();
              };
            });
          }


          const duration = video.duration;
          console.log("video length: ", duration);
          const totalFrames = Math.floor(duration * fps);
          console.log("total Frames: ", totalFrames);

          // Calculate the number of frames to show on the timeline
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          console.log("canvas.width: ", canvas.width);
          const totalFramesToShow = Math.floor(canvas.width / videoWidth); // 총 표시할 프레임 수
          console.log("total frames to show: ", totalFramesToShow);

          const frames = [];
          let currentFrame = 3; // to avoid black frame of recorded video

          const captureFrame = () => {
            if (frames.length >= totalFramesToShow || currentFrame >= totalFrames) {
              this.$refs.timeline.updateFrames(frames); // 타임라인 업데이트
              resolve();
              return;
            }

            // Calculate the frame interval to achieve the desired number of frames
            const interval = Math.floor(totalFrames / totalFramesToShow);
            console.log("interval: ", interval)
            // Set video time to the current frame time
            video.currentTime = (currentFrame + 1) / fps;
            console.log("Trying to seek to:", video.currentTime, "Frame:", currentFrame);

            video.onseeked = () => {
              setTimeout(() => {  // 탐색 후 프레임을 안정적으로 가져오기 위해 약간의 지연 추가
                  console.log("Seeking to: ", video.currentTime);
                  // Draw the current frame only if it meets the interval condition
                  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                  frames.push(canvas.toDataURL('image/jpeg')); // Add frame to the list
                  currentFrame += interval; // Move to the next interval frame
                  captureFrame();

                }, 150); // wait for 50ms and then execute
              };
            };

          captureFrame();
        };
      });
    },

    async Recording() {
      if (!this.isRecording) {
        await this.startRecording();
      } else {
        this.stopRecording();
      }
    },
    async startRecording() {
      try {
        // allow webcam
        const stream = await navigator.mediaDevices.getUserMedia(
            { video: {width: 640, height: 480 , frameRate: { exact: 30}  // fix w, h, fps
              }, audio: true });
        this.webcamStream = stream; // save stream


        // make sure users can see while performing
        if (this.$refs.videoPlayer) {
          this.$refs.videoPlayer.srcObject = stream;
          this.$refs.videoPlayer.play();
        }

        // MediaRecorder
        this.mediaRecorder = new MediaRecorder(stream);
        this.recordedChunks = [];

        this.mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.recordedChunks.push(event.data);
          }
        };

        this.mediaRecorder.onstop = () => {
          this.recordedBlob = new Blob(this.recordedChunks, { type: 'video/webm' }); //webm
          console.log("Recording completed. Blob size:", this.recordedBlob.size);

          if (this.recordedBlob.size === 0) {
            console.error("Recorded file is empty!");
            return;
          }
          /////////// added
          // 📌 녹화된 비디오의 FPS 체크하기!
          const video = document.createElement('video');
          video.src = URL.createObjectURL(this.recordedBlob);
          video.onloadedmetadata = async () => {
            console.log("Before fixing: Video duration:", video.duration); // Infinity 출력됨

            if (video.duration === Infinity) {
              console.warn("Video duration is Infinity. Attempting to fix...");

              await new Promise((resolve) => {
                video.currentTime = Number.MAX_SAFE_INTEGER;
                video.ontimeupdate = () => {
                  video.ontimeupdate = null;
                  console.log("Fixed duration:", video.duration);  // 정상적인 길이 출력!
                  resolve();
                };
              });
            }

            console.log("Final video duration:", video.duration);
          };
          ///////// added


          this.uploadRecordedVideo();
        };

        this.mediaRecorder.start();
        this.isRecording = true;
      } catch (error) {
        console.error('Error starting recording:', error);
      }
    },
    stopRecording() {
      if (this.mediaRecorder) {
        this.mediaRecorder.stop();
      }

      // stop webcam stream
      if (this.webcamStream) {
        this.webcamStream.getTracks().forEach((track) => track.stop());
        this.webcamStream = null;
      }

      if (this.$refs.videoPlayer) {
        this.$refs.videoPlayer.srcObject = null;
      }
      if (this.player) {
      this.player.src({ src: "", type: "video/webm" }); //webm
    } else {
      console.warn("Video player not initialized. Skipping src update.");
    }


      this.isRecording = false;
    },
    async uploadRecordedVideo() {
      if (!this.recordedBlob) {
        alert("No recording available to upload.");
        return;
      }

      const webmFile = new File([this.recordedBlob], "recorded-video.webm", {
        type: "video/webm",
      });

      // Step 1: Upload webm to backend to convert
      const formData = new FormData();
      formData.append("video", webmFile);
      formData.append("scriptName", "convert-webm");

      const response = await axios.post("http://localhost:3000/convert-video", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        responseType: "blob", // <-- 바로 blob으로 받아와!
      });

      //const convertedMp4Path = response.data.output_path;
      //console.log("MP4 path returned:", convertedMp4Path);
      // example MP4 path returned: http://localhost:3000/video-1743623211701-794951968.mp4
      // Step 2: Use converted mp4 to extract frames
      const mp4Blob = response.data //await fetch(convertedMp4Path).then(res => res.blob());
      const mp4File = new File([mp4Blob], "converted-video.mp4", { type: "video/mp4" });
      const re_url = URL.createObjectURL(mp4File);

      console.log("file blob re url:", re_url);
      //this.player.src({ src: re_url, type: "video/mp4" });
      //this.player.play();

      this.player.pause();
      this.player.src({ src: re_url, type: "video/mp4" });
      this.player.ready(() => {
        this.player.play();
      });
      this.uploadedFile = mp4File;
      await this.extractFrames(re_url);
    },

    async executePythonScript() {
      try {
        const formData = new FormData();
        formData.append("video", this.uploadedFile);
        formData.append("scriptName", "submit"); // 스크립트 이름

        //console.log("FormData after append:", formData.get("video"));

        const response = await axios.post("http://localhost:3000/process-video", formData, {
          headers: {"Content-Type": "multipart/form-data"},
        });

        this.segments = response.data; // JSON 결과를 UI에 표시
        console.log("Updated segments:", this.segments);

        // Debug: Search.vue가 데이터를 받고 있는지 확인
        //  const searchComponent = this.$refs.search;
        // console.log("Search component received signs:", searchComponent.signs);

        this.$refs.search.signs = this.segments; // Search 컴포넌트로 데이터 전달
        console.log("deliver data to Search.vue", this.$refs.search.signs);

      } catch (error) {
        console.error("Error executing Python script:", error);
      }
    },
    updateSelection: function (newBoundaries) {
      if (
        this.timelineSelection.start != newBoundaries.start ||
        this.timelineSelection.end != newBoundaries.end
      ) {
        this.timelineSelection = newBoundaries;
        this.$saveAction('update_selection', {
          current_step: this.currentStep,
          start: this.timelineSelection.start * this.duration,
          end: this.timelineSelection.end * this.duration,
        });
      }
    },
    changeTick: function (newPosition) {
      this.player.currentTime(newPosition * this.duration);
      this.videoPosition = newPosition;
      this.$saveAction('new_position', {
        current_step: this.currentStep,
        position: this.videoPosition * this.duration,
      });
    },
    generalPlay: function () {
      if (this.player) {
        if (this.playing) {
          this.player.pause();
          this.$saveAction('pause_click', {
            current_step: this.currentStep,
            position: this.videoPosition,
          });
        } else {
          this.player.play();
          this.stopAtSelection = false;
          this.$saveAction('play_click', {
            current_step: this.currentStep,
            position: this.videoPosition,
          });
        }
      }
    },
    async executeRecPythonScript() {
      try {
        const formData = new FormData();
        formData.append("video", this.uploadedFile); // 업로드된 비디오 파일
        formData.append("start", this.timelineSelection.start * this.duration); // 선택된 시작 시간
        formData.append("end", this.timelineSelection.end * this.duration); // 선택된 종료 시간
        formData.append("scriptName", "find-a-sign"); // 스크립트 이름

        console.log("Sending request to backend...");
        console.log("Uploaded File:", this.uploadedFile);
        console.log("Start:", this.timelineSelection.start * this.duration);
        console.log("End:", this.timelineSelection.end * this.duration);
        const response = await axios.post("http://localhost:3000/process-video", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        this.segments = response.data; // JSON 결과를 UI에 표시
        console.log("Updated segments:", this.segments);

        this.$refs.search.signs = this.segments; // Search 컴포넌트로 데이터 전달
        console.log("Deliver data to Search.vue", this.$refs.search.signs);

      } catch (error) {
        console.error("Error executing recognition Python script:", error);
      } finally {
        console.log("Recognition script execution complete."); // 선택적으로 추가
      }
    },

    selectionPlay: function () {
      if (this.player) {
        this.$saveAction('play_selection_click', {
          current_step: this.currentStep,
          position: this.videoPosition,
        });
        this.player.currentTime(this.selectionStart);
        this.stopAtSelection = true;
        if (!this.playing) {
          this.player.play();
        }
      }
    },
    loadCurrentStep: function () {
      if (this.currentStep == this.experimentalSetup.length) {
        console.log('Finished the sequence');
        this.$saveAction('finished_experiment');
        this.$router.push('/thank-you');
      } else {
        this.scratchpad = '';
        this.$saveAction('started_video', {
          current_step: this.currentStep,
          video:
            this.experimentalSetup[this.latinSquare[this.currentStep]].title,
        });
        // loads current video...
        this.player.src({
          src: this.experimentalSetup[this.latinSquare[this.currentStep]]
            .video_url,
          type: 'video/mp4',
        });
        let searchPanel = this.$refs.search,
          timeline = this.$refs.timeline;
        searchPanel.resetResults();
        timeline.resetSelection();
        // ...and current pre-computed search results
        fetch(
          this.experimentalSetup[this.latinSquare[this.currentStep]].signs_data,
          {
            method: 'GET',
            headers: {
              'Content-Type': 'application/text',
            },
          }
        )
          .then((response) => response.text())
          .then((data) => {
            this.signs = JSON.parse(data).signs;
          })
          .catch((error) => {
            console.error('Error:', error);
          });
      }
    },
    advanceStep: function () {
      if (this.currentStep >= this.experimentalSetup.length - 1) {
      console.warn('No more steps available.');
      return;
    }
      this.currentStep += 1;
      document.querySelectorAll('video').forEach(vid => vid.pause());
      this.$saveAction('next_video', { scratchpad: this.scratchpad });
      this.loadCurrentStep();
    },
  },
  computed: {
    frameBaseName: function () {
      if (!this.experimentalSetup ||
          !this.latinSquare ||
          !this.latinSquare[this.currentStep] ||
          !this.experimentalSetup[this.latinSquare[this.currentStep]])
      {
        return 'frame';
      }
      return this.experimentalSetup[this.latinSquare[this.currentStep]]
        .frame_base_name;
    },
    frameNumber: function () {
      if (!this.experimentalSetup ||
          !this.latinSquare ||
          !this.latinSquare[this.currentStep] ||
          !this.experimentalSetup[this.latinSquare[this.currentStep]])
      {
        return 1;
      }
      return parseInt(
        this.experimentalSetup[this.latinSquare[this.currentStep]].frame_number
      );
    },
    nextStepText: function () {
      if (!this.experimentalSetup || !this.latinSquare) {
        return '';
      }
      if (this.currentStep < this.experimentalSetup.length - 1) {
        return 'Next video';
      }
      return 'Finish experiment';
    },
    playingSelection: function () {
      if (!this.playing || this.currentPercentage == -1) {
        return false;
      }
      return (
        this.currentPercentage >= this.timelineSelection.start &&
        this.currentPercentage <= this.timelineSelection.end
      );
    },
    currentTime: function () {
      if (this.player) {
        return this.player.currentTime();
      }
      return 1;
    },
    currentPercentage: function () {
      if (!this.player) {
        return -1;
      }
      return this.player.currentTime() / this.player.duration();
    },
    duration: function () {
      if (this.player) {
        return this.player.duration();
      }
      return -1;
    },
    selectionStart: function () {
      return this.timelineSelection.start * this.duration;
    },
    selectionEnd: function () {
      return this.timelineSelection.end * this.duration;
    },
    tickInsideSelection: function () {
      return (
        this.currentTime >= this.selectionStart &&
        this.currentTime <= this.selectionEnd
      );
    },
  },
  mounted() {
    fetch('/data/experiment_setup.json', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/text',
      },
    })
      .then((response) => response.text())
      .then((data) => {
        this.experimentalSetup = JSON.parse(data).steps;
        this.$saveAction('entered_experiment');

        // creates a latin square that is always the same for this user
        // first, finds the first number in the uid.
        let found = false,
          offset,
          i = 0;
        console.log(this.$uid);
        while (!found) {
          if (isNaN(parseInt(this.$uid[i])) && i < this.$uid.length) {
            i++;
          } else {
            found = true;
          }
        }
        // there were no numbers inside the uid (very unlikely!), so
        // will default to 0
        if (i == this.$uid.length) {
          offset = 0;
        } else {
          offset = parseInt(this.$uid[i]);
        }

        this.latinSquare.push(0);
        let s = '0 ';

        // skips 0, which is the demo. This'll always be the first video.
        for (let i = 1; i < this.experimentalSetup.length; i++) {
          this.latinSquare.push(
            ((i + offset) % (this.experimentalSetup.length - 1)) + 1
          );
          s += this.latinSquare[i] + ' ';
        }

        console.log(`indexes: ${s}`);
        this.$saveAction('created_latin_square', {
          latin_square: this.latinSquare,
          offset_used: offset,
        });

        this.loadCurrentStep();
      })
      .catch((error) => {
        console.error('Error:', error);
      });
    this.player = videojs(this.$refs.videoPlayer, this.options, () => {
      this.$refs.videoPlayer.addEventListener('play', () => {
        this.playing = true;
        this.interval = setInterval(() => {
          if (
            this.stopAtSelection &&
            this.currentTime > this.selectionEnd &&
            this.player
          ) {
            this.player.pause();
            this.playing = false;
          }
          if (this.player.paused() && this.interval) {
            clearInterval(this.interval);
          }
          this.videoPosition = this.currentTime / this.duration;
        }, 60);
      });
      this.$refs.videoPlayer.addEventListener('pause', () => {
        if (this.interval) {
          this.$saveAction('end_of_video', {
            current_step: this.currentStep,
            position: this.videoPosition,
          });
          clearInterval(this.interval);
          this.playing = false;
        }
      });
    });
  },
  beforeDestroy() {
    if (this.player) {
      this.player.dispose();
    }
  },
};
</script>

<style src="video.js/dist/video-js.css"></style>
<style lang="scss">
//@import '@/assets/styles/_mixins.scss';
//@import '@/assets/styles/_variables.scss';
@use "../assets/styles/mixins" as mixins;
@use "../assets/styles/variables" as *;
$header_height: 48px;
$timeline_height: 96px;
$videocontrol_height: 60px;
$scratchpad_height: 84px;
$general_padding: 6px;

header {
  grid-column: 1/ -1;
  display: grid;
  align-items: center;
  grid-template-columns: max-content max-content auto max-content;
  gap: 0.5rem;
  padding-left: 12px;
  padding-right: 12px;
  padding-bottom: $general_padding;

  h1,
  h2 {
    color: white;
    @include mixins.fs(1);
  }
  h1 {
    font-weight: 700;
  }
  h2 {
    font-weight: 400;
  }
  #next-video {
    grid-column: 4;
  }
}

#span-selection {
  display: grid;
  grid-template-rows:
    $header_height
    calc(
      100vh - #{$header_height + $timeline_height + $videocontrol_height +
        $scratchpad_height + 2 * $general_padding}
    )
    $scratchpad_height
    $timeline_height $videocontrol_height;
  grid-template-columns: auto 576px;

  background-color: black;
  padding: $general_padding;
}

#video-container {
  grid-column: 1;
  border: 1px solid #333;
  margin: 0 12px 12px 12px;
}

#video-controls-container {
  grid-column: 1 / -1;
  background-color: #333;
  position: relative;
}

#timeline-container {
  display: grid;
  background-color: #000;
  padding: 12px;

  grid-column: 1 / -1;
}

#scratchpad {
  margin: 0 12px 24px 12px;
  display: grid;
  textarea {
    border-radius: 0.5rem;
    padding: 12px;
    @include mixins.fs(0);
    resize: none;
  }
}

#search-panel {
  background-color: $very-light-accent;
  border-radius: 4px;
  grid-row: 2 / span 2;
  grid-column: 2;

  overflow-y: scroll;

  margin-bottom: 24px;
  margin-right: 12px;
  padding: 12px;

  display: grid;
  grid-gap: 1rem;
  grid-template-rows: min-content auto;
}

#results {
  font-weight: 550;

  .result {
    background-color: rgba(255, 255, 255, 0.25);
    padding: 0.5rem 1rem;
    display: grid;
    grid-template-columns: 70% 30%;
    align-items: center;
    font-size: 14px;
    color: white;

    &.header {
      background-color: transparent;
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.1ch;
      color: rgba(255, 255, 255, 0.8);
    }
    &:not(.header) {
      margin-top: 2px;
      border-radius: 0.125rem;
    }
    .signs {
    }
    .certainty {
      span {
        background-color: white;
        height: 0.5rem;
        display: block;
      }
    }
  }
}
</style>
