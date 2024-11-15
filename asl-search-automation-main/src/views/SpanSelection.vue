<!-- 이 코드는 각 버튼들이 실행해야 할 동작들을 정리해둔 곳! -->
<template>
  <div id="span-selection">
    <header>
      <h1>Video {{ currentStep }}</h1>
      <div id="next-video">
        <custom-button size="small" :has-border="true" @clicked="advanceStep()"
          >{{ nextStepText }}
        </custom-button>
      </div>
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

          await this.extractFrames(url);

          this.uploadedFile = file; // 파일을 변수에 저장하여 나중에 사용
        }
      };

      input.click();
    },

    async extractFrames(videoUrl, fps = 30, videoWidth = 50) {
      return new Promise((resolve) => {
        const video = document.createElement('video');
        video.src = videoUrl;
        video.crossOrigin = 'anonymous';

        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        video.onloadedmetadata = () => {
          const duration = video.duration;
          const totalFrames = Math.floor(duration * fps);

          // Calculate the number of frames to show on the timeline
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          const totalFramesToShow = Math.floor(canvas.width / videoWidth); // 총 표시할 프레임 수

          const frames = [];
          let currentFrame = 0;

          const captureFrame = () => {
            if (frames.length >= totalFramesToShow || currentFrame >= totalFrames) {
              this.$refs.timeline.updateFrames(frames); // 타임라인 업데이트
              resolve();
              return;
            }

            // Calculate the frame interval to achieve the desired number of frames
            const interval = Math.floor(totalFrames / totalFramesToShow);

            // Set video time to the current frame time
            video.currentTime = currentFrame / fps;

            video.onseeked = () => {
              // Draw the current frame only if it meets the interval condition
              ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
              frames.push(canvas.toDataURL('image/jpeg')); // Add frame to the list
              currentFrame += interval; // Move to the next interval frame
              captureFrame();
            };
          };

          captureFrame();
        };
      });
    },


    async executePythonScript() {
      try {
        const formData = new FormData();
        formData.append("video", this.uploadedFile);
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
      this.currentStep += 1;
      document.querySelectorAll('video').forEach(vid => vid.pause());
      this.$saveAction('next_video', { scratchpad: this.scratchpad });
      this.loadCurrentStep();
    },
  },
  computed: {
    frameBaseName: function () {
      if (!this.experimentalSetup || !this.latinSquare) {
        return 'frame';
      }
      return this.experimentalSetup[this.latinSquare[this.currentStep]]
        .frame_base_name;
    },
    frameNumber: function () {
      if (!this.experimentalSetup || !this.latinSquare) {
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
