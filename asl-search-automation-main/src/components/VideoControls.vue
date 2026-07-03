



<template>
  <div id="video-controls">
    <button
      id="general-play"
      @click="$emit('general-play')"
      class="icon-bg"
      :class="generalPlayClass"
    >
      &nbsp;
    </button>

    <button
      id="selection-play"
      @click="
        $emit('selection-play', { start: startSelection, end: endSelection })
      "
      :class="{ pause: playingSelection, play: !playingSelection }"
    >
      Play selection
    </button>

    <button id="execute-model" @click="$emit('execute-model')">
      Segment and Search
    </button> 

    <button id="execute-recognition" @click="$emit('execute-recognition')">
      Search
    </button>

    
    <button id="upload-video" @click="$emit('upload-video')">
      Upload Video
    </button>
    <button id="record-video" @click="$emit('record-video')">Recording</button>
  

    <p id="elapsed-time">
      <span class="hours" :class="{ 'less-than-an-hour': duration < 3600 }">{{
        formattedTime.hours
      }}</span
      ><span class="colon">:</span
      ><span class="minutes" :class="{ 'less-than-a-minute': duration < 60 }">{{
        formattedTime.minutes
      }}</span
      ><span class="colon">:</span
      ><span class="seconds">{{ formattedTime.seconds }}</span
      ><span class="period">.</span
      ><span class="deciseconds">{{ formattedTime.deciseconds }}</span>
    </p>
  </div>
</template>

<script>
export default {
  name: "VideoControls",
  props: {
    playing: {
      type: Boolean,
      default: false,
    },
    playingSelection: {
      type: Boolean,
      default: false,
    },
    currentTime: {
      type: Number,
      default: 0,
    },
    duration: {
      type: Number,
      default: 0,
    },
    startSelection: {
      type: Number,
      default: 0,
    },
    endSelection: {
      type: Number,
      default: 1,
    },
  },
  computed: {
    generalPlayClass: function () {
      if (!this.playing) {
        if (this.currentTime == this.duration) {
          return "reset";
        }
        return "play";
      }
      return "pause";
    },
    formattedTime: function () {
      let t = new Date(0);
      t.setSeconds(this.currentTime);
      let s = t.toISOString();
      return {
        hours: s.substr(11, 2),
        minutes: s.substr(14, 2),
        seconds: s.substr(17, 2),
        deciseconds: (this.currentTime % 1).toFixed(2).substring(2, 3),
      };
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/styles/_variables.scss";
@import "@/assets/styles/_mixins.scss";

#video-controls {
  display: flex;
  grid-template-columns: max-content max-content auto;
  align-items: center;
  grid-gap: 1rem;
  background-color: black;
  padding: 0 12px;
  position: absolute;
  inset: 0;
}

#elapsed-time {
  @include fs(1);
  margin-left: auto; /* arrange on right side */
  text-align: right;
  color: white;
  display: flex;
  justify-content: flex-end;
  span {
    width: 2.5ch;
    display: inline-block;
    text-align: center;
    &.colon,
    &.period {
      width: 0.4ch;
    }
    &.deciseconds {
      width: 1.25ch;
    }
    &.colon,
    &.less-than-an-hour,
    &.less-than-a-minute {
      color: #666;
    }
  }
}

// added upload
#upload-video {
  background-color: rgba(0, 123, 255, 0.8);
  border-color: rgba(255, 255, 255, 0.8);
  color: rgba(255, 255, 255, 0.8);
  padding: 0.25rem 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
  margin-left: 30%; /* move to right */
  &:hover {
    background-color: rgba(0, 123, 255, 0.8);
    color: #fff;
  }
}
#record-video {
  background-color: rgba(0, 123, 255, 0.8);
  border-color: rgba(255, 255, 255, 0.8);
  color: rgba(255, 255, 255, 0.8);
  padding: 0.25rem 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
  &:hover {
    background-color: rgba(0, 123, 255, 0.8);
    color: #fff;
  }
}

// added upload
#execute-model {
  background-color: rgba(0, 123, 255, 0.8);
  border-color: rgba(255, 255, 255, 0.8);
  color: rgba(255, 255, 255, 0.8);
  padding: 0.25rem 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
  &:hover {
    background-color: rgba(0, 123, 255, 0.8);
    color: #fff;
  }
}
#execute-recognition {
  background-color: rgba(0, 123, 255, 0.8);
  border-color: rgba(255, 255, 255, 0.8);
  color: rgba(255, 255, 255, 0.8);
  padding: 0.25rem 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
  &:hover {
    background-color: rgba(0, 123, 255, 0.8);
    color: #fff;
  }
}

button {
  border: none;
  padding: 0.25rem 1rem;
  border-radius: 0.25rem;
  border: 3px solid transparent;
  color: white;
  cursor: pointer;
  user-select: none;
  &#general-play {
    background-color: #666;
    padding-left: 2.25rem;
    padding-right: 2.25rem;
    &.play {
      background-image: url(play-icon());
      &:hover {
        background-image: url(play-icon(#666));
      }
    }
    &.pause {
      background-image: url(pause-icon());
      &:hover {
        background-image: url(pause-icon(#666));
      }
    }
    &.reset {
      background-image: url(reset-icon());
      &:hover {
        background-image: url(reset-icon(#666));
      }
    }
    &:hover {
      background-color: #fff;
      color: #333;
    }
  }
  &#selection-play {
    background-color: rgba(0, 123, 255, 0.8);
    border-color: mix(#ffffff, rgba(255, 255, 255, 0.8));
    color: rgba(255, 255, 255, 0.8);
    &:hover {
      background-color: rgba(0, 123, 255, 0.8);
      color: #fff;
    }
  }
}
.icon-bg {
  background-repeat: no-repeat;
  background-size: 1rem;
  background-position-y: center;
  background-position-x: center;
}
</style>

