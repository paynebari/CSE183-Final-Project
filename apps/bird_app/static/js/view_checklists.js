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
    methods: {
        find_checklist_idx: function(id) {
            // Finds the index of an item in the list.
            for (let i = 0; i < this.checklists.length; i++) {
                if (this.checklists[i].id === id) {
                    return i;
                }
            }
            return null;
        },
        delete_checklist: function(id){
            let self = this;
            let i = self.find_checklist_idx(id);
            axios.post(del_checklists_url, { id: id }).then(function (r) {
                self.checklists.splice(i, 1);
            })
        },
    }
};

app.vue = Vue.createApp(app.data).mount("#app");

app.load_checklists = function() {
    axios.get(load_checklists_url).then(function(response) {
        console.log("Loaded checklists:", response.data.checklists);
        app.vue.checklists = response.data.checklists;
      
    }).catch(function(error) {
      console.error("Error loading checklists:", error);
    });
}

app.load_checklists();