<template>
  <b-row class="row border my-5 mx-1 p-1 bg-light">
    <b-col cols="1" class="py-2" align-v="center">{{index}}</b-col>
    <b-col cols="2" class="p-0">
      <b-button block size="lg" :variant="variantButton" v-on:click="clickMe">{{title}}</b-button>
    </b-col>
    <b-col cols="6" class="py-2" align-v="center">{{msg}}</b-col>
    <b-col cols="3" class="py-2">
      <b-badge variant="success" v-if="countdown>0">Decompte {{countdown}}</b-badge>
      <b-badge variant="warning" v-if="light.length>0">Lumiere</b-badge>
    </b-col>
  </b-row>
</template>

<script>
export default {
  name: "RadiologicEvent",
  props: {
    title: String,
    index: Number,
    msg: String,
    countdown: Number,
    light: String,
    isSelected: Boolean
  },
  methods: {
    clickMe: function() {
      this.$emit("radiologic-event", [
        "/message/message",
        [this.msg, this.countdown],
        this.index
      ]);
    }
  },
  data: function() {
    return {
      variantButton: "primary"
    };
  },
  watch: {
    isSelected: function() {
      if (this.isSelected) {
        this.variantButton = "secondary";
      } else {
        this.variantButton = "primary";
      }
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>