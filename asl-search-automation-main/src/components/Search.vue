<!--filtering and dropdown menu here-->

<template>
  <div id="search">
    <h3>Search Results</h3>
    <p v-if="segmentOptions.length > 0" id="summary">
      Showing {{ segmentOptions.length }} results between
      {{ segmentOptions[0].start.toFixed(1) }} and {{ segmentOptions[segmentOptions.length - 1].end.toFixed(1) }} seconds.
    </p>
    <div id="results">
      <div id="dropdown">
      <label for="segment-select">Select a Segment:  </label>
      <select id="segment-select" v-model="selectedSegment">
        <option v-for="(segment, index) in segmentOptions" :key="`segment-${index}`" :value="segment">
          {{ `Segment ${index + 1} (${segment.start.toFixed(1)} - ${segment.end.toFixed(1)})` }}
        </option>
      </select>
      </div>
      <template v-if="filteredResults.length > 0">
        <div v-for="(chunk, chunkIndex) in chunkResults(filteredResults, 2)" :key="`chunk-${chunkIndex}`" class="result-row">

        <search-result
          v-for="(result, index) in chunk"
          :key="`result-${index}`"
          :sign="result.sign"
          :start-time="result.startTime.toFixed(1)"
          :end-time="result.endTime.toFixed(1)"
          :confidence="result.confidence"
          :img-src="result.imgSrc"
          :hands="result.hands"
          :handshape="result.handshape"
          :location="result.location"
          :movement="result.movement"
        />
        </div>
      </template>
      <p v-else>No results found for this segment.</p>
    </div>
  </div>
</template>

<script>
import SearchResult from './SearchResult.vue';
import signsData from '@/assets/data/signs_2731_gloss_added.json'; // Load signs.json

export default {
  name: 'Search',
  components: {SearchResult},
  props: {
    currentStep: {type: Number, default: -1},
    signs: { // get JSON
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      selectedSegment: null, // currently selected segment
    };
  },
  computed: {
      preparedResults() {
      return this.signs.flatMap((segment) =>
        segment[2].map((prediction) => {
          const match = signsData.signs.find(
            (item) => item.sign.toLowerCase() === prediction[0].toLowerCase()
          );

              return {
                startTime: segment[0],
                endTime: segment[1],
                sign: prediction[0],
                confidence: prediction[1],
                imgSrc: match ? match.img_src : '',
                hands: match ? match.hands : 'Unknown',
                handshape: match ? match.handshape : 'Unknown',
                location: match ? match.location : 'Unknown',
                movement: match ? match.movement : 'Unknown',
              };
            })
        );
      },
    segmentOptions() {
      // Segment 구간 목록 생성
      return this.signs.map((segment) => ({
        start: segment[0],
        end: segment[1],
      }));
    },
    filteredResults() {
      // 선택된 segment에 해당하는 결과 필터링
      if (!this.selectedSegment) return [];
      return this.preparedResults.filter(
        (result) =>
          result.startTime === this.selectedSegment.start &&
          result.endTime === this.selectedSegment.end
      );
    },
  },
  watch: {
    signs: {
      handler(newSigns) {
        // 이전 데이터와 동일하면 리프레시 방지
        if (JSON.stringify(newSigns) === JSON.stringify(this.previousSigns)) return;

        // 데이터 변경 시에만 갱신
        this.previousSigns = [...newSigns];
        this.selectedSegment = this.segmentOptions[0] || null;
      },
      immediate: true,
    },
    selectedSegment(newSegment, oldSegment) {
      if (!newSegment || JSON.stringify(newSegment) === JSON.stringify(oldSegment)) {
        console.log('No change in segment selection');
        return;
      }
      console.log('New segment selected:', newSegment);
      // Additional logic here
    },
  },
  methods: {
    chunkResults(results, size) {
      const chunks = [];
      for (let i = 0; i < results.length; i += size) {
        chunks.push(results.slice(i, i + size));
      }
      return chunks;
    },
  },
    mounted() {
    if (this.segmentOptions.length > 0 && !this.selectedSegment) {
      this.selectedSegment = this.segmentOptions[0];
    }
  },


};

</script>

<style lang="scss" scoped>
#search {
  padding: 1rem;
}

#results {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}


.result-row {
  display: flex;
  gap: 1rem;
}

.result-row > * {
  flex: 1; /* 두 결과가 같은 크기를 갖도록 설정 */
}

</style>