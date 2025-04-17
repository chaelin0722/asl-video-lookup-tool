<template>
  <div id="recognition-main">
    <!-- Use the VideoPlayer component to upload the video -->
    <VideoPlayer @video-uploaded="handleVideoUpload" />

    <!-- Video Controls and Timeline -->
    <VideoControls @play-video="playVideo" @pause-video="pauseVideo" />
    <Timeline :duration="videoDuration" @update-selection="updateSelection" />

    <!-- Show predictions after processing -->
    <Results v-if="predictions.length > 0" :predictions="predictions" />
  </div>
</template>

<script>
// Import the components you’ve already created
import VideoPlayer from '@/components/VideoPlayer.vue';
import VideoControls from '@/components/VideoControls.vue';
import Timeline from '@/components/Timeline.vue';
import Results from '@/components/Results.vue';

// Import necessary libraries
import { obtain_pose_data } from '@/spoter_mod/skeleton_extractor';
import * as tf from '@tensorflow/tfjs'; // Assuming you use TensorFlow.js

export default {
  name: 'RecognitionMain',
  data() {
    return {
      videoData: null,
      predictions: [],
      videoDuration: 0,
    };
  },
  components: {
    VideoPlayer,
    VideoControls,
    Timeline,
    Results,
  },
  methods: {
    // Handle video upload from VideoPlayer component
    handleVideoUpload(video) {
      this.videoData = video;
      this.videoDuration = this.getVideoDuration(video);
      this.runRecognitionModel(video); // Process the video when uploaded
    },

    // Method to get video duration for Timeline
    getVideoDuration(video) {
      const videoElement = document.createElement('video');
      videoElement.src = URL.createObjectURL(video);
      videoElement.onloadedmetadata = () => {
        return videoElement.duration;
      };
    },

    // This is the main function that processes the video with the model
    async runRecognitionModel(video) {
      try {
        // Step 1: Extract pose data (your logic using obtain_pose_data)
        const poseData = obtain_pose_data(video);

        // Step 2: Prepare the pose data for model input
        const processedPoseData = this.preparePoseData(poseData);

        // Step 3: Run the model on the extracted pose data
        const model = await tf.loadGraphModel('path/to/your/model.json'); // Load the TensorFlow.js model
        const predictions = model.predict(processedPoseData);

        // Step 4: Process the model predictions
        this.predictions = this.processModelOutput(predictions);

      } catch (error) {
        console.error('Error processing the recognition model:', error);
      }
    },

    // Prepare pose data for the model (you can adapt this as needed)
    preparePoseData(poseData) {
      // Normalization and tensor creation logic
      const tensorData = tf.tensor(poseData);
      return tensorData;
    },

    // Process the model's output and convert to readable predictions
    processModelOutput(predictions) {
      const results = predictions.dataSync();
      return results.map((prediction, index) => ({
        label: `Sign ${index + 1}`, // Adjust label logic based on your output
        confidence: prediction,
      }));
    },

    // Video controls handling
    playVideo() {
      // Add logic to control video playback
    },
    pauseVideo() {
      // Add logic to pause video
    },

    // Handle timeline selection updates
    updateSelection(selection) {
      // You can pass the selected segment of the video here
    },
  },
};
</script>

<style scoped>
#recognition-main {
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>