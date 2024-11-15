<template>
  <div id="search">
    <h3>Search Results</h3>
    <div id="results">
      <template v-if="preparedResults.length > 0">
        <search-result
          v-for="(result, index) in preparedResults"
          :key="`result-${index}`"
          :sign="result.sign"
          :start-time="result.startTime"
          :end-time="result.endTime"
          :confidence="result.confidence"
          :img-src="result.imgSrc"
          :hands="result.hands"
          :handshape="result.handshape"
          :location="result.location"
          :movement="result.movement"
        />
      </template>
      <p v-else>No results to display.</p>
    </div>
  </div>
</template>

<script>
import SearchResult from './SearchResult.vue';
import signsData from '@/assets/data/signs.json'; // Load signs.json

export default {
  name: 'Search',
  components: {SearchResult},
  props: {
    currentStep: {type: Number, default: -1},
    signs: { // JSON 데이터를 받는 props
      type: Array,
      default: () => [],
    },
  },

  computed: {
      preparedResults() {
        //check
        console.log("Processing signs:", this.signs);
        // Process predictions from `signs` and match them with `signs.json`
        return this.signs.flatMap((segment) =>
            segment[2].map((prediction) => {
              const match = signsData.signs.find(
                  (item) => item.sign.toLowerCase() === prediction[0].toLowerCase()
              );

              return {

                startTime: segment[0],
                endTime: segment[1],
                sign: prediction[0],
                confidence: prediction[1],  // confidence 값 확인
                imgSrc: match ? match.img_src : '', // Default to empty string if no match
                hands: match ? match.hands : 'Unknown',
                handshape: match ? match.handshape : 'Unknown',
                location: match ? match.location : 'Unknown',
                movement: match ? match.movement : 'Unknown',
              };
            })
        );

      },
    },
    mounted() {
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
</style>