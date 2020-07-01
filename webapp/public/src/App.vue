<template>
  <div id="app" class="mt-0">
    <div class="container-fluid bg-dark m-0">
      <b-row align-v="stretch" class="p-2 justify-content-center">
        <b-col cols="1" class="py-2" align-v="center">
          <img src="./assets/left-white.png" v-on:click="backToMenu" />
        </b-col>
        <b-col cols="10" align-v="end" class>
          <h5 class="text-light my-3">RADIOLOGIC</h5>
        </b-col>
        <b-col cols="1" class="py-2" align-v="center">
          <img src="./assets/gear-white.png" v-on:click="setDisplayMenuSettings(true)" />
        </b-col>
      </b-row>
    </div>
    <MenuScenario
      :listOfScenario="listOfScenario"
      v-on:scenario-event="switchScenario"
      v-if="actualScenarioIndex<0"
    ></MenuScenario>

    <Scenario
      :title="this.actualScenario"
      :listOfEvent="list"
      v-on:radio-event="sendMessageFromEvent"
      v-if="actualScenarioIndex>=0"
    ></Scenario>
    <bottom-menu
      id="bottommenu"
      title="menu"
      v-bind:listOfLight="['truc', 'machin']"
      v-on:menu-event="sendMessageFromEvent"
    ></bottom-menu>
    <b-modal title="Settings" id="modal-settings" :hide-footer="true">
      <Settings v-on:settings-event="sendMessageFromEvent"></Settings>
    </b-modal>
  </div>
</template>

<script>
import Scenario from "./components/Scenario.vue";
import MenuScenario from "./components/MenuScenario.vue";
import BottomMenu from "./components/BottomMenu.vue";
import Settings from "./components/Settings.vue";
import datafilejson from "./datajson.json";
import osc from "osc";

export default {
  name: "App",
  data: function() {
    return {
      displayMenuSettings: true,
      datafile: datafilejson,
      actualScenario: "none",
      actualScenarioIndex: -1,
      listOfScenario: [],
      list: [],
      listOfButton: ["edit", "new", "undo", "reset"],
      port: new osc.WebSocketPort({
        url: "ws://" + self.location.host.split(":")[0] + ":8081" // get the host ip xx.xx.xx.xx:3000 then remove ":3000"
      })
    };
  },
  methods: {
    addButton: function() {
      let buttonindex = this.list.length.toString();
      this.list.push({ name: "button" + buttonindex });
      console.log("send message");
    },
    switchScenario: function(i) {
      console.log("switch scenario : key = " + i);
      if (i >= 0 && i < this.listOfScenario.length) {
        this.actualScenario = this.listOfScenario[i];
        this.actualScenarioIndex = 1;
        this.list = this.datafile[this.actualScenario];
      } else {
        this.actualScenario = "none";
        this.actualScenarioIndex = -1;
        this.list = [];
      }
    },
    backToMenu: function() {
      this.switchScenario(-1);
    },
    sendMessage: function() {
      this.sendOscMessage("/bonjour/machin", 1);
    },
    sendMessageFromEvent: function(msg) {
      console.log("send message from event");
      //Msg must be [ "/oscAdress", [arg1, arg2, arg3]]
      if (msg.length > 1) {
        this.sendOscMessage(msg[0], msg[1]);
      } else {
        console.log("sendMessageFromEvent : msg format not valid");
        console.log(msg.length);
      }
    },
    sendOscMessage: function(oscAddress, arg) {
      this.port.send({
        address: oscAddress,
        args: arg
      });
      console.log("send message : " + oscAddress + " arg=" + arg);
    },
    setDisplayMenuSettings(isOpen) {
      console.log("setDisplayMenuSettings");
      this.displayMenuSettings = isOpen;
      if (this.displayMenuSettings) {
        this.$bvModal.show("modal-settings");
      } else {
        this.$bvModal.hide("modal-settings");
      }
    }
  },
  beforeMount() {
    console.log("before mount is called");
    this.port.open();
    if (this.datafile == null) {
      console.log("data file is null");
    } else {
      this.listOfScenario = Object.keys(this.datafile);
    }
  },
  components: {
    Scenario,
    MenuScenario,
    BottomMenu,
    Settings
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 0px;
  min-height: 100vh;
}
#bottommenu {
  position: fixed;
  bottom: 0;
}
</style>
