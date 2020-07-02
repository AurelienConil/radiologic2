<template>
  <div id="app" class="mt-0">
    <div class="container-fluid bg-dark m-0">
      <b-row align-v="stretch" class="p-2 justify-content-center">
        <b-col cols="1" class="py-2" align-v="center">
          <img
            src="./assets/left-white.png"
            v-on:click="backToMenu"
            :style="{display:isRootPage?'none':'block'}"
          />
        </b-col>
        <b-col align-v="end" class>
          <h5 class="text-light my-3">RADIOLOGIC</h5>
          <b-badge v-if="portOpenState!=='open'" variant="warning">Server déconnecté</b-badge>
        </b-col>

        <b-col cols="1" class="py-2" align-v="center">
          <img src="./assets/gear-white.png" v-on:click="setDisplayMenuSettings(true)" />
        </b-col>
      </b-row>
    </div>
    <MenuScenario
      :listOfScenario="listOfScenario"
      v-on:scenario-event="switchScenario"
      v-if="isRootPage"
    ></MenuScenario>

    <Scenario
      v-else
      :title="this.actualScenario"
      :listOfEvent="list"
      :defaultMessageHoldTime="defaultMessageHoldTime"
      v-on:radio-event="sendMessageFromEvent"
    ></Scenario>
    <bottom-menu
      id="bottommenu"
      title="menu"
      :listOfLight="listOfLight"
      v-on:menu-event="sendMessageFromEvent"
    ></bottom-menu>
    <b-modal size="xl" title="Réglages" id="modal-settings" ok-only>
      <Settings id="settings" :settingsData="settingsData" v-on:radiologic-event="sendMessageFromEvent" v-on:save-settings="saveSettings" v-on:change-settings="changeSettings"  />
    </b-modal>
  </div>
</template>

<script>
import Scenario from "./components/Scenario.vue";
import MenuScenario from "./components/MenuScenario.vue";
import BottomMenu from "./components/BottomMenu.vue";
import Settings from "./components/Settings.vue";
// import datafilejson from "./datajson.json";
import osc from "osc";

export default {
  name: "App",
  data: function() {
    return {
      displayMenuSettings: true,
      datafile: {},
      actualScenario: "none",
      actualScenarioIndex: -1,
      list: [],
      listOfButton: ["edit", "new", "undo", "reset"],
      portOpenState: "closed",
      port: new osc.WebSocketPort({
        url: "ws://" + self.location.host.split(":")[0] + ":8081" // get the host ip xx.xx.xx.xx:3000 then remove ":3000"
      }),
      settingsData :{volume:1,masterLight:1}
    };
  },
  computed: {
    listOfScenario() {
      return Object.keys(this.datafile).filter(n => n !== "metadata");
    },
    listOfLight() {
      return this.datafile?.metadata?.light?.fastAccessPresets || [];
    },
    defaultMessageHoldTime(){
      return this.datafile?.metadata?.video?.defaultMessageHoldTime || 0;
    },
    isRootPage() {
      return this.actualScenarioIndex < 0;
    },


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
    },
    portClose() {
      if (this.portOpenState != "trying") {
        this.portOpenState = "trying";
        setTimeout(() => {
          this.tryOpenPort();
        }, 100);
      }
    },
    tryOpenPort(force) {
      const openPort = () => {
        console.warn("trying openning port");
        const res = this.port.open();
        console.warn("res openning port", res);
      };

      if (!!force || this.portOpenState !== "open") {
        openPort();
        setTimeout(() => {
          this.tryOpenPort();
        }, 3000);
      }
    }
    ,saveSettings(){
      this.sendOscMessage("/settings/save")
      console.log("save settings")
    }
    ,changeSettings(name,v){
      if(name=="volume"){
        this.sendOscMessage("/settings/volume",v)
      }
      else if(name==="masterLight"){
        this.sendOscMessage("/settings/masterLight",v)
      }
      else{
        console.error("setting not supported",name)
      }
    }
  },

  created() {
    const serverURL = "http://" + self.location.host.split(":")[0] + ":3000" // forces to connect to server (useful while debugging npm run serve) 
    fetch(serverURL + "/datajson.json")
      .then(stream => stream.json())
      .then(json => {
        console.log("fetched session json", json);
        this.datafile = json;
      })
      .catch(err => console.error("failed to fetch json", err));

    fetch(serverURL + "/UserSettings.json")
      .then(stream => stream.json())
      .then(json => {
        console.log("fetched UserSettings json", json);
        this.settingsData = json;
      })
      .catch(err => console.error("failed to fetch json", err));

          

    this.port.on("close", this.portClose);
    this.port.on("error", this.portClose);
    this.port.on("open", () => {
      console.warn("port send open message");
      this.portOpenState = "open";
    });
    this.portOpenState = "open"; // avoid non connected button flashing on page load
    this.tryOpenPort(true);
  },
  beforeMount() {
    // if (this.datafile == null) {
    //   console.log("data file is null");
    // } else {
    //   this.listOfScenario = Object.keys(this.datafile);
    // }
  },
  mounted() {},

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
.modal-dialog{
  min-width: 80vw;
}
</style>
