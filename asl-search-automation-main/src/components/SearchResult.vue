<template>
  <div id="search-result">
    <div class="img-container">
      <img :src="imgSrc" alt="Sign Image" />
    </div>
    <div class="details">
      <p><strong>Sign:</strong> {{ sign }}</p>
      <p><strong>Confidence:</strong> {{ confidence.toFixed(2) }}</p>
      <p><strong>Hands:</strong> {{ hands }}</p>
      <p><strong>Handshape:</strong> {{ handshape }}</p>
      <p><strong>Location:</strong> {{ location }}</p>
      <p><strong>Movement:</strong> {{ movement }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchResult',
  props: {
    sign: String,
    imgSrc: String,
    confidence: Number,
    hands: String,
    handshape: String,
    location: String,
    movement: String,
  },
};
</script>

<style scoped>
#search-result {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  border: 1px solid #ddd;
  padding: 1rem;
  border-radius: 0.5rem;
}

.img-container img {
  width: 100%;
  border-radius: 0.5rem;
}

.details p {
  margin: 0.5rem 0;
}
</style>