<template>
  <div>
    <b-row class="row border my-2 mx-1 p-1 bg-light">
      <b-col cols="1" class="py-2" align-v="center">{{index}}</b-col>
      <b-col cols="2" class="p-0">
        <b-button
          block
          class="p-3"
          size="lg"
          :variant="variantButton"
          v-on:click="clickMe"
        >{{title}}</b-button>
      </b-col>
      <b-col class="py-2" align-v="center">
        <div>{{msg}}</div>
                <div v-if="isSelected && (holdProgress>0)">
          <b-spinner small></b-spinner>
          {{parseInt(holdTime - holdProgress)+1}}
        </div>
      </b-col>

      <b-col cols="3" class="py-2">
        <b-badge class="p-2" variant="success" v-if="countdown>0">Decompte 
        <b-spinner small v-if="isSelected && (countdownProgress>0)" ></b-spinner>
        {{(isSelected && (countdownProgress>0))?(parseInt(countdown- countdownProgress )+1):countdown}}</b-badge>
        <b-badge class="p-2" variant="warning" v-if="light.length>0">Lumiere:{{light}}</b-badge>
      </b-col>
    </b-row>
    <b-row></b-row>
  </div>
</template>

<script>
export default {
  name: "RadiologicEvent",
  cachedIntervals: {},
  props: {
    title: String,
    index: Number,
    msg: String,
    countdown: Number,
    holdTime: Number,
    light: String,
    isSelected: Boolean
  },

  methods: {
    clickMe: function() {
      this.$emit("button-clicked", this.index);
      this.$emit("radiologic-event", [
        "/message/message",
        [this.msg, this.countdown,this.holdTime]
      ]);
      if (this.light) {
        this.$emit("radiologic-event", ["/light/preset", [this.light]]);
      }
      this.startCountdown();
    },
    startCountdown() {
      const deltaT = 200;
      this.holdProgress = 0;
      let interval = setInterval(() => {
        if (
          this.isSelected &&
          this.holdProgress + deltaT / 1000 < this.holdTime
        ) {
          this.holdProgress += deltaT / 1000;
        } else {
          this.holdProgress = 0;
          clearInterval(interval);
          if (this.isSelected) {
            let interval2 = setInterval(() => {
              if (
                this.isSelected &&
                this.countdownProgress + deltaT / 1000 < this.countdown
              ) {
                this.countdownProgress += deltaT / 1000;
              } else {
                this.countdownProgress = 0;
                clearInterval(interval2);
              }
            }, deltaT);
          }
        }
      }, deltaT);
    }
  },
  data: function() {
    return {
      variantButton: "primary",
      holdProgress: 0,
      countdownProgress: 0
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