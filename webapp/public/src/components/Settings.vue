<template>
  <b-container fluid class="bg-light py-2 px-3">
    <b-container fluid class=" py-5 px-3 app-buttons">
      <b-form-input
        type="range"
        :value="numGetter('volume')"
        @input="numSetter('volume',$event)"
        @change="saveSettings"
        min="0"
        max="1"
        step="0.001"
      ></b-form-input>
      <div>Volume</div>
    </b-container>
    <b-container fluid class=" py-5 px-3 app-buttons">
      <b-form-input
        type="range"
        :value="numGetter('masterLight')"
        @input="numSetter('masterLight',$event)"
        @change="saveSettings"
        min="0"
        max="1"
        step="0.001"
      ></b-form-input>
      <div>Lumière</div>
    </b-container>
    <div class="app-buttons py-5">
      <b-button
        block
        size="lg"
        variant="danger"
        @click="promptBeforeSend('éteindre','/app/shutdown')"
      >Eteindre</b-button>

      <b-button
        block
        size="lg"
        variant="warning"
        @click="promptBeforeSend('redémarrer','/app/reboot')"
      >Redémarrer</b-button>

      <b-button
        block
        size="lg"
        :variant="hasVeille?'outline-':''+'secondary'"
        @click="toggleVeille"
      >{{hasVeille?"Allumer":"Veille"}}</b-button>
    </div>
  </b-container>
</template>

<script>
export default {
  name: "BottomMenu",
  props: {
    // settingsData: () => {
    //   return {};
    // }
    settingsData: {}
  },
  data: function() {
    return {
      hasVeille:false
    };
  },

  methods: {
    toggleVeille(){
      this.setVeille(!this.hasVeille)

    },
    setVeille(v){
      if(v){
      this.sendEv("/app/veille",1)
      }
      else{
        this.sendEv("/app/veille",0)
      }
      this.hasVeille = v
    },
    promptBeforeSend(action, addr, arg) {
      // if (alert(`êtes vous sûr de vouloir ${action} le système?`)) {
        this.sendEv(addr, arg);
      // }
    },
    sendEv(addr, arg) {
      this.$emit("radiologic-event", [addr, arg]);
    },

    numGetter(name) {
      return this.settingsData[name] !== undefined
        ? this.settingsData[name]
        : 0;
    },
    numSetter(name, v) {
      if (this.settingsData[name] !== undefined) {
        this.settingsData[name] = v;
      } else {
        console.warn("adding non existent setting value", name);
        //  Vue.set(this.settingsData,name, v)
        this.settingsData[name] = v;
      }
      this.$emit("change-settings", name,v);
    },
    saveSettings() {
      this.$emit("save-settings", this.settingsData);
    }
  }
};
</script>

<style scoped>
.app-buttons {
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  flex: 1 1 0px;
}
.app-buttons * {
  margin: 5px;
  padding: 15px;
}
</style>
