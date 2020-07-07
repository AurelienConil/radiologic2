<template>
  <div class="container-fluid my-3">
    <h2>Choisir une séquence</h2>
    <b-list-group>
      <b-list-group-item
        href="#"
        class="flex-column align-items-start mx-2"
        v-for="(item, index) in listOfScenario"
        :key="index"
        v-on:click="switchScenario(index)"
      >
        <div class="container-fluid mt-0">
          <b-row>
            <b-col cols="10 p-3 text-left">
              <!-- <h3>scenario {{index}} : {{item}}</h3> -->
              <h3>{{item}}</h3>
            </b-col>
            <img src="@/assets/right-black.png" height="50px"/>
            <b-col cols="2"></b-col>
          </b-row>
        </div>
      </b-list-group-item>
    </b-list-group>
  </div>
</template>

<script>
export default {
  name: "Scenario",
  props: {
    listOfScenario: Array
  },
  methods: {
    switchScenario: function(index) {
      console.log("Menu scenario - swithScenario :" + index);
      this.$emit("scenario-event", index);
    }
  }
};
</script>