<template>
  <div>
    <b-container fluid class="px-0 border-bottom py-5">
      <h1 class="display-2 text-muted">{{ title }}</h1>
    </b-container>
    <b-container fluid>
      <b-row class="row my-5 mx-1 p-1">
        <b-col cols="1" class="p-0">
          <b>#</b>
        </b-col>
        <b-col cols="2" class>
          <b>Nom</b>
        </b-col>
        <b-col cols="6" class>
          <b>Message</b>
        </b-col>
        <b-col cols="3" class>
          <b>Options</b>
        </b-col>
      </b-row>
      <radiologicEvent
        v-for="(item, index) in listOfEvent"
        :key="item.nom"
        :index="index"
        :title="item.nom"
        :msg="item.message"
        :countdown="item.countdown"
        :holdTime="item.holdTime!==undefined?item.holdTime: defaultMessageHoldTime"
        :fadeMsgTime="fadeMsgTime"
        :light="item.light"
        :isSelected="index==currentSelection"
        v-on:radiologic-event="sendRadiologicEvent"
        v-on:button-clicked="startAtIndex(index)"
      ></radiologicEvent>
      <b-row class="row py-5">&ensp;</b-row>
    </b-container>
  </div>
</template>

<script>
import RadiologicEvent from "./RadiologicEvent.vue";

export default {
  name: "Scenario",
  props: {
    title: String,
    listOfEvent: Array,
    defaultMessageHoldTime: Number,
    fadeMsgTime: Number
  },
  methods: {
    sendRadiologicEvent: function(data) {
      if (data.length >= 2) {
        this.$emit("radio-event", data);
      } else {
        console.error("bad event formatting", data);
      }
    },
    startAtIndex(i) {
      this.currentSelection = i;
    }
  },
  computed: {},
  data: function() {
    return {
      currentSelection: 2
    };
  },
  mounted: function() {
    console.log("mount Scenario");
    this.currentSelection = -1;
  },

  watch: {
    listOfEvent: function() {
      //Once the scenario is changed, reset de current selection
      console.log("Scenario : reset selection");
      this.currentSelection = -1;
    }
  },
  components: {
    RadiologicEvent
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>