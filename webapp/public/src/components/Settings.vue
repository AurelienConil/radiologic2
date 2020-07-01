<template>
  <b-container fluid class="py-2 px-3">
    <b-row>
      <b-col cols="8" class="py-3 px-0">
        <form>
          <input
            type="range"
            v-on:input="volumeChange"
            v-model="volume"
            min="0"
            max="2"
            step="0.01"
          />
        </form>
      </b-col>
      <b-col class="py-3 px-1">
        Volume vidéo
        <br />
        {{volume}}
      </b-col>
    </b-row>
    <b-row>
      <b-col cols="8" class="py-3 px-0">
        <form>
          <input type="range" v-on:input="masterChange" v-model="master" />
        </form>
      </b-col>
      <b-col class="py-3 px-1">
        Master lumière
        <br />
        {{master}}
      </b-col>
    </b-row>
    <b-row>
      <b-col class="p-3 m-3">
        <b-button variant="success" v-on:click="reboot">Redémarrer</b-button>
      </b-col>
      <b-col class="p-3 m-3">
        <b-button variant="danger" v-on:click="shutdown">Eteindre</b-button>
      </b-col>
      <b-col class="p-3 m-3">
        <b-button variant="warning" v-on:click="sleep">Veille</b-button>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
export default {
  name: "Settings",
  methods: {
    volumeChange: function() {
      this.$emit("settings-event", ["/player/volume", [this.volume]]);
    },
    masterChange: function() {
      this.$emit("settings-event", ["/vermuth/master", [this.master]]);
    },
    shutdown: function() {
      var r = confirm("Etes-vous sur de vouloir éteindre");
      if (r == true) {
        console.log("shutdown");
        this.$emit("settings-event", ["/rpi/shutdown", [1]]);
      }
    },
    reboot: function() {
      console.log("reboot");
      this.$emit("settings-event", ["/rpi/reboot", [1]]);
    },
    sleep: function() {
      console.log("sleep");
      this.$emit("settings-event", ["/rpi/sleep", [1]]);
    }
  },
  data: function() {
    return {
      volume: 1,
      master: 100
    };
  }
};
</script>

<style scoped>
input[type="range"] {
  width: 300px;
}
</style>