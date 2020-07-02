<template>
  <b-container fluid class="bg-dark py-2 px-3">
    <b-row>
      <b-col v-for="(item, index) in listOfButton" :key="item" class="px-1">
        <b-button block variant="primary" v-on:click="clickMe(index)">{{item}}</b-button>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
export default {
  name: "BottomMenu",
  props: {
    title: String,
    listOfLight: Array
  },
  data: function() {
    return {
      // listOfButton: []
    };
  },
  computed: {
    listOfButton() {
      console.log("update list of button");
      const res = [];
      res.push("start video");
      res.push("stop video");
      res.push("clear msg");
      this.listOfLight.forEach(element => {
        res.push(element);
      });
      res.push("OFF");
      return res;
    }
  },
  methods: {
    startVideo: function() {
      this.$emit("menu-event", ["/player/play", [1]]);
    },
    stopVideo: function() {
      this.$emit("menu-event", ["/player/stop", [1]]);
    },
    stopLight: function() {
      this.$emit("menu-event", ["/light/blackout", [1]]);
    },
    clearMsg: function() {
      this.$emit("menu-event", ["/message/clear", [1]]);
    },
    sendLightPreset: function(name) {
      this.$emit("menu-event", ["/light/preset", [name]]);
    },
    clickMe: function(index) {
      if (index < this.listOfButton.length) {
        switch (index) {
          case 0:
            this.startVideo();
            break;
          case 1:
            this.stopVideo();
            break;
          case 2:
            this.clearMsg();
            break;
          case this.listOfButton.length - 1:
            this.stopLight();
            break;

          default:
            this.sendLightPreset(this.listOfButton[index]);
            break;
        }
      }
    },
  },

};
</script>
