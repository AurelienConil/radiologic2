<template>
  <div class="container-fluid my-3">
    <h3>Choisir une séquence</h3>
    <b-list-group>
      <b-list-group-item
        href="#"
        class="flex-column align-items-start mx-2"
        v-for="(item, index) in listOfScenario"
        :key="index"
        v-on:click="switchScenario(index)"
      >
        <div class="container-fluid my-0">
          <b-row>
            <b-col cols="11 px-3 text-left">
              <!-- <h3>scenario {{index}} : {{item}}</h3> -->
              <h4>{{item}}</h4>
              
            </b-col>
            <img src="@/assets/right-black.png" height="30px" class="my-0"/>
            <b-col cols="1"></b-col>
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