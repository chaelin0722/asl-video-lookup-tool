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
    <!--Add upload button-->
    <button
      id="upload-video"
      @click="$emit('upload-video')"
    >
      Upload Video
    </button>
    <!--Add upload button-->

    <button
      id="selection-play"
      @click="$emit('selection-play')"
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
  name: 'VideoControls',
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
  },
  computed: {
    generalPlayClass: function () {
      if (!this.playing) {
        if (this.currentTime == this.duration) {
          return 'reset';
        }
        return 'play';
      }
      return 'pause';
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
@import '@/assets/styles/_variables.scss';
@import '@/assets/styles/_mixins.scss';


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
  margin-left: auto; /* 오른쪽에 배치 */
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
#upload-video{
  background-color: #444;
  border-color: $accent;
  color: $accent;
  padding: 0.25rem 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
  &:hover {
    background-color: $accent;
    color: #fff;
  }
}

// added upload
#execute-model{
  background-color: #444;
  border-color: $accent;
  color: $accent;
  padding: 0.25rem 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
  &:hover {
    background-color: $accent;
    color: #fff;
  }
}
#execute-recognition{
  background-color: #444;
  border-color: $accent;
  color: $accent;
  padding: 0.25rem 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
  &:hover {
    background-color: $accent;
    color: #fff;
  }
}

button {
  border: none;
  padding: 0.25rem 1rem;
  border-radius: 0.25rem;
  border: 1px solid transparent;
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
    background-color: #333;
    border-color: mix(#333, $accent);
    color: $accent;
    &:hover {
      background-color: $accent;
      border-color: $accent;
      color: #333;
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
