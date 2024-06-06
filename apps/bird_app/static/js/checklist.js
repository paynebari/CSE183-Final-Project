"use strict";

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


app.data = {    
    data: function() {
        return {
            sightings: [],
            name: "",
            count:""
        };
    },
    methods: {
        // Complete as you see fit.
        find_sighting_idx: function(id) {
            // Finds the index of an item in the list.
            for (let i = 0; i < this.sightings.length; i++) {
                if (this.sightings[i].id === id) {
                    return i;
                }
            }
            return null;
        },
        add_count: function(s_id) {
            let self = this;
            let i = self.find_sighting_idx(s_id);
            axios.post(inc_sightings_url, { id: s_id }).then(function (r) {
                self.sightings[i].observation_count = r.data.bird_count;
            })
        },
        add_sighting: function() {
            // This is time 1, the time of the button click.
            let self = this; 
            let name = self.name;
            let count = self.count;
            axios.post(add_sightings_url, {
                name: name,
                observation_count: count,
            }).then(function (r) {
                // This is time 2, much later, when the server answer comes back. 
                console.log("Got the id");
                self.sightings.push({
                    id: r.data.id,
                    name: name,
                    observation_count: count,
                });
                self.name = "";
                self.count = "";
            });
        },
        del_sighting:function(id){
            let self = this;
            let i = self.find_sighting_idx(id);
            axios.post(del_sightings_url, { id: id }).then(function (r) {
                self.sightings.splice(i, 1);
            })
        },
        
    }
};

app.vue = Vue.createApp(app.data).mount("#app");

app.load_data = function () {
    axios.get(load_sightings_url).then(function (r) {
        console.log(r.status);
        let s = r.data.sightings;
        app.vue.sightings = s;
    });
}

app.load_data();