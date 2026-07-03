<!--filtering and dropdown menu here-->

<template>
  <div id="search">
    <h3>Search Results</h3>
    
    <!-- loading message -->
    <div v-if="isLoading" class="loading-message">
      <div class="loading-spinner"></div>
      <p>{{ loadingMessage }}</p>
    </div>
    
    <p v-else-if="segmentOptions.length > 0" id="summary">
      Processing done, showing {{ segmentOptions.length }} results between
      {{ segmentOptions[0].start.toFixed(1) }} -
      {{ segmentOptions[segmentOptions.length - 1].end.toFixed(1) }}
    </p>
    <div v-if="!isLoading" id="results">
      <div id="dropdown-container">
        <div class="dropdown-wrapper">
          <label for="segment-select" class="dropdown-label">
            Select a Segment
          </label>
          <div class="select-wrapper">
            <select id="segment-select" v-model="selectedSegment" class="custom-select">
              <option
                v-for="(segment, index) in segmentOptions"
                :key="`segment-${index}`"
                :value="segment"
                class="select-option"
              >
                {{
                  `Segment ${index + 1} (${segment.start.toFixed(
                    1
                  )}s - ${segment.end.toFixed(1)}s)`
                }}
              </option>
            </select>
            <div class="select-arrow">▼</div>
          </div>
        </div>
      </div>
      <template v-if="filteredResults.length > 0">
        <div
          v-for="(chunk, chunkIndex) in chunkResults(filteredResults, 2)"
          :key="`chunk-${chunkIndex}`"
          class="result-row"
        >
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
      <!--<p v-else>No results found for this segment.</p>-->
    </div>
  </div>
</template>

<script>
import SearchResult from "./SearchResult.vue";
import signsData from "@/assets/data/signs_991.json"; // Load signs.json

export default {
  name: "Search",
  components: { SearchResult },
  props: {
    currentStep: { type: Number, default: -1 },
    signs: {
      // receive JSON data
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      selectedSegment: null, // currently selected segment
      isLoading: false, // loading state for search results
      loadingMessage: "Searching for signs...", // default loading message
    };
  },
  watch: {
    selectedSegment(newSegment) {
      // notify parent component when selected segment is changed
      if (newSegment) {
        this.$emit('segment-selected', {
          start: newSegment.start,
          end: newSegment.end
        });
      }
    },
    signs: {
      handler(newSigns) {
        // When new signs data is loaded, automatically select first segment
        if (newSigns && newSigns.length > 0 && !this.selectedSegment) {
          // Use $nextTick to ensure segmentOptions is calculated
          this.$nextTick(() => {
            if (this.segmentOptions.length > 0) {
              this.selectedSegment = this.segmentOptions[0];
              console.log("Auto-selected first segment:", this.selectedSegment);
            }
          });
        }
      },
      immediate: true
    }
  },
  computed: {
    preparedResults() {
      console.log("=== preparedResults calculated ===");
      console.log("signs length:", this.signs.length);
      console.log("selectedSegment:", this.selectedSegment);
      
      return this.signs.flatMap((segment) =>
        segment[2].map((prediction) => {
          // remove spaces and match
          const predictedSign = prediction[0].toLowerCase().replace(/\s+/g, '');
          
          const match = signsData.signs.find(
            (item) => item.sign.toLowerCase().replace(/\s+/g, '') === predictedSign
          );

          let confidence_level = "Unknown";
          if (prediction[1] <0.33)  confidence_level = "Low";
          else if (prediction[1] <0.66)  confidence_level = "Medium";
          else  confidence_level = "High";
          
          let confidence_score = prediction[1].toFixed(2);
          
          return {
            startTime: segment[0],
            endTime: segment[1],
            sign: match ? match.sign : prediction[0], 
            confidence: confidence_level + " (" + confidence_score + ")",
            imgSrc: match ? match.img_src : "",
            hands: match ? match.hands : "Unknown",
            handshape: match ? match.handshape : "Unknown",
            location: match ? match.location : "Unknown",
            movement: match ? match.movement : "Unknown",
          };
        })
      );
    },
    segmentOptions() {
      // create segment list
      console.log("=== segmentOptions calculated ===");
      console.log("signs:", this.signs);
      console.log("signs length:", this.signs.length);
      
      const options = this.signs.map((segment) => ({
        start: segment[0],
        end: segment[1],
      }));
      
      console.log("segmentOptions:", options);
      return options;
    },
    filteredResults() {
      // filter results by selected segment
      if (!this.selectedSegment) {
        // if no segment is selected, show all results
        return this.preparedResults;
      }
      return this.preparedResults.filter(
        (result) =>
          result.startTime === this.selectedSegment.start &&
          result.endTime === this.selectedSegment.end
      );
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
    startLoading(message) {
      this.isLoading = true;
      this.loadingMessage = message;
    },
    stopLoading() {
      this.isLoading = false;
    },
    resetResults() {
      // check if new JSON file is created in parent component
      if (this.$parent && this.$parent.currentJsonPath) {
        // reset results only when new video is loaded
        this.signs = [];
        this.selectedSegment = null;
        console.log("Search results reset - clearing all results for new video");
        
      } else {
        // ignore if called by timeline click or etc.
        // keep selectedSegment to keep results from disappearing
        console.log("Search results reset called but keeping results (no new JSON)");
      }
    },
  },
  mounted() {
    console.log("=== Search component mounted ===");
    console.log("segmentOptions length:", this.segmentOptions.length);
    console.log("current selectedSegment:", this.selectedSegment);
    
    // set initial selected segment
    if (this.segmentOptions.length > 0) {
      this.selectedSegment = this.segmentOptions[0];
      console.log("selectedSegment:", this.selectedSegment);
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
  flex: 1; /* set two results to the same size */
}

.loading-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-message p {
  color: #666;
  font-size: 14px;
  margin: 0;
}

  /* dropdown styling */
#dropdown-container {
  margin-bottom: 0.5rem;
}

.dropdown-wrapper {
  background:#d0ddef;
  border-radius: 12px;
  padding: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
}

.dropdown-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
  font-size: 14px;
}

.select-wrapper {
  position: relative;
  display: inline-block;
  width: 100%;
}

.custom-select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  padding-right: 2.5rem;
  background: white;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  color: #374151;
  cursor: pointer;
  appearance: none;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.custom-select:hover {
  border-color: #9ca3af;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.custom-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.select-arrow {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  font-size: 12px;
  pointer-events: none;
  transition: transform 0.2s ease;
}

.custom-select:focus + .select-arrow {
  transform: translateY(-50%) rotate(180deg);
}

.select-option {
  padding: 0.5rem;
  background: white;
  color: #374151;
}

.select-option:hover {
  background: #f3f4f6;
}

/* dropdown active arrow */
.custom-select:focus ~ .select-arrow {
  transform: translateY(-50%) rotate(180deg);
}
</style>
