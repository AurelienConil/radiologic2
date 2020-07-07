<template>
  <b-container fluid class="bg-dark py-2 px-3">
    <b-row>
      <b-col v-for="(item, index) in listOfButton" :key="item" class="px-1 mb-1">
        <b-button block variant="primary" size="sm" v-on:click="clickMe(index)">{{item}}</b-button>
      </b-col>
      <b-col v-for="(item) in listOfLight" :key="item" class="px-1 mb-1">
        <b-button block variant="secondary" size="sm" v-on:click="sendLightPreset(item)">{{item}}</b-button>
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
      lastLightMemoryCalled: ""
    };
  },
  computed: {
    listOfButton() {
      console.log("update list of button");
      const res = [];
      res.push("Lecture");
      res.push("Stop");
      //res.push("clear msg");
      // res.push("OFF");
      return res;
    }
  },
  methods: {
    startVideo: function() {
      this.$emit("menu-event", ["/player/play", [1]]);
    },
    stopVideo: function() {
      this.$emit("menu-event", ["/player/stop", [1]]);
      //SEND THE LAST LIGHT PRESET WHEN STOP VIDEO IS CALLED
      if (this.lastLightMemoryCalled.length > 0) {
        //this.sendLightPreset(this.lastLightMemoryCalled);
      }
    },
    stopLight: function() {
      this.$emit("menu-event", ["/light/blackout", [1]]);
    },
    clearMsg: function() {
      this.$emit("menu-event", ["/message/clear", [1]]);
    },
    sendLightPreset: function(name) {
      this.$emit("menu-event", ["/light/preset", [name]]);
      this.lastLightMemoryCalled = name;
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
        }
      }
    }
  }
};
</script>
