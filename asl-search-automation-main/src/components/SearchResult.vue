<!--handling json data for each sign results here!-->

<template>
  <div id="search-result">
    <div class="img-container">
      <img :src="imgSrc" alt="Sign Image" />
    </div>
    <div class="details">
      <!--<p><strong>Segment:</strong> {{ startTime }} <strong>-</strong> {{ endTime }}</p>-->
      <p><strong>Sign:</strong> {{ sign }}</p>
      <p>Confidence: {{ confidence }}</p>
      <!-- <p><strong>Hands:</strong> {{ hands }}</p>
      <p><strong>Handshape:</strong> {{ handshape }}</p>
      <p><strong>Location:</strong> {{ location }}</p>
      <p><strong>Movement:</strong> {{ movement }}</p>-->
    </div>
  </div>
</template>

<script>
export default {
  name: "SearchResult",
  props: {
    sign: String,
    imgSrc: String,
    confidence: String,
    //hands: String,
    // handshape: String,
    //location: String,
    //movement: String,
    //startTime: Number,
    //endTime: Number,
  },
};
</script>

<style scoped>
#search-result {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border: 1px solid #e1e8ed;
  padding: 1.0rem;
  border-radius: 12px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

#search-result::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  /*background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);*/
  border-radius: 12px 12px 0 0;
}

#search-result:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border-color: #3b82f6;
}

.img-container {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  background: #f1f5f9;
  box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
}

.img-container img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
  transition: transform 0.3s ease;
}

.img-container:hover img {
  transform: scale(1.02);
}

.details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.details p {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.details p strong {
  color: #1f2937;
  font-weight: 600;
  min-width: 43px;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Confidence text style */
.details p:has(strong:contains("Confidence")) {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  border-left: 3px solid #f59e0b;
  margin: 0.5rem 0;
}

/* Sign name style */
.details p:first-child {
  font-size: 14px;
  font-weight: 700;
  color: #1f2937;
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  padding: 0.75rem;
  border-radius: 8px; 
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.details p:first-child strong {
  color: #1e40af;
  font-size: 14px;
  font-weight: 600;
}

.details p:not(:first-child):not(:has(strong:contains("Confidence"))) {
  padding: 0.5rem 0.75rem;
  background: #f9fafb;
  border-radius: 6px;
  border-left: 2px solid #e5e7eb;
  transition: all 0.2s ease;
}

.details p:not(:first-child):not(:has(strong:contains("Confidence"))):hover {
  background: #f3f4f6;
  border-left-color: #3b82f6;
}

</style>
