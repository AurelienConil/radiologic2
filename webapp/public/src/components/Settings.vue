<template>
  <b-container fluid class="py-2 px-3">
    <b-row>
      <b-col class="p-3 m-3">BIJOUR</b-col>
      <b-col class="p-3 m-3">LE VIE</b-col>
    </b-row>
    <b-row>
      <b-col class="p-3 m-3">Volume</b-col>
      <b-col class="p-3 m-3">
        <form>
          <input type="range" />
        </form>
      </b-col>
    </b-row>
    <b-row>
      <b-col class="p-3 m-3">
        <b-button variant="success">redémarrer</b-button>
      </b-col>
      <b-col class="p-3 m-3">
        <b-button variant="danger">ETEINDRE</b-button>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
export default {
  name: "Settings",
  methods: {
    changeVolume: function() {
      this.$emit("settings-event", ["/player/play", [1]]);
    }
  }
};
</script>