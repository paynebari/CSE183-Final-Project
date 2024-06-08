"use strict";

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


app.data = {    
    data: function() {
        return {
            checklists: [],
        };
    },
    methods: {}
};

app.vue = Vue.createApp(app.data).mount("#app");

app.load_checklists = function() {
    axios.get(load_checklists_url).then(function(response) {
      app.vue.checklists = response.data.checklists;
      console.log("Loaded checklists:", response.data.checklists);
    }).catch(function(error) {
      console.error("Error loading checklists:", error);
    });
}

app.load_checklists();



