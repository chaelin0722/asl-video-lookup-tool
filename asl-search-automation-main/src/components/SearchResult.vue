<!--handling json data for each sign results here!-->

<template>
  <div id="search-result">
    <div class="img-container" :class="{ loaded: imgHasLoaded }">
      <img :src="imgSrc" alt="Sign Image" />
      <div class="expanded-info" v-show="showInfo">
      <p><strong>Hands:</strong> {{ hands }}</p>
      <p><strong>Handshape:</strong> {{ handshape }}</p>
      <p><strong>Location:</strong> {{ location }}</p>
      <p><strong>Movement:</strong> {{ movement }}</p>
      </div>
    </div>
    <!-- hover details-->
    <div class="sign-description">
      <a
        class="info"
        @mouseover="showInfo = true"
        @mouseout="showInfo = false"
        title="Hover to see details"
      >
        <span class="icon"></span>
      </a>
      <p class="sign-name">{{ formattedSign }}</p>
      <p class="confidence">{{  confidenceLabel }}</p>

    </div>
  </div>

</template>

<script>

export default {
  name: 'SearchResult',
  data() {
    return {
      showInfo: false, // Toggle for showing hover details
      imgHasLoaded: false,
    };
  },
  props: {
    sign: { type: String, default: '' },
    confidence: { type: Number, default: 0 },
    imgSrc: { type: String, default: '' },
    hands: { type: String, default: '' },
    handshape: { type: String, default: '' },
    location: { type: String, default: '' },
    movement: { type: String, default: '' },
  },
  computed: {
    formattedSign() {
      return this.sign.charAt(0).toUpperCase() + this.sign.slice(1);
    },
    confidenceLabel() {
      if (this.confidence >= 0.667) {
        return 'High';
      } else if (this.confidence >= 0.33) {
        return 'Moderate';
      } else {
        return 'Low';
      }
    },
  },
};
</script>

<style scoped>

@use "../assets/styles/variables" as *;
@use "../assets/styles/mixins" as mixins;

#search-result {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.img-container {
  position: relative;
  background: rgba(0, 0, 0, 0.1);
  aspect-ratio: 4/3;
  img {
    width: 100%;
  }
}

.sign-description {
  display: grid;
  grid-template-columns: min-content auto;
  gap: 0.08rem;
}

.expanded-info {
  position: absolute;
  inset: 0.25rem;
  border-radius: 0.25rem;
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(8px);
  padding: 0.5rem;

  p {
    @include mixins.fs(-1);
    line-height: 1.1;

    & + p {
      margin-top: 0.5rem;
    }
    strong {
      font-weight: 700;
    }
  }
}

.info {
  span {
    display: inline-block;
    margin-top: 0.2rem;
    width: 1rem;
    height: 1rem;
    cursor: help;
    background-size: contain;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'%3E%3Cpath fill='%236363e7' d='M256 8C119.043 8 8 119.083 8 256c0 136.997 111.043 248 248 248s248-111.003 248-248C504 119.083 392.957 8 256 8zm0 110c23.196 0 42 18.804 42 42s-18.804 42-42 42-42-18.804-42-42 18.804-42 42-42zm56 254c0 6.627-5.373 12-12 12h-88c-6.627 0-12-5.373-12-12v-24c0-6.627 5.373-12 12-12h12v-64h-12c-6.627 0-12-5.373-12-12v-24c0-6.627 5.373-12 12-12h64c6.627 0 12-5.373 12 12v100h12c6.627 0 12-5.373 12 12v24z'/%3E%3C/svg%3E");
  }
}

.sign-name {
  @include mixins.fs(-1);
  flex: 1;
  font-weight: normal;
  text-align: left;
}
.confidence {
  @include mixins.fs(-1);
  font-size: 0.9rem;
  color: gray;
  text-align: right;
}

</style>