"use strict";

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


app.data = {    
    data: function() {
        return {
            // Complete as you see fit.
            search_query: "",
            species_list: [],
            all_sightings_list: [],
        };
    },

    computed: {
        search: function() {
            let self = this;
            console.log(self.search_query)
        }
    },

    methods: {
        // Complete as you see fit.
        order_first_seen: function() {  
            let self = this
            axios.post(order_first_seen_url, {}).then(function(r){
                self.species_list =r.data.species_list;
            });       
        },
        order_recently_seen: function() {  
            let self = this
            axios.post(order_recently_seen_url, {}).then(function(r){
                self.species_list =r.data.species_list;
            });  
        },
        
        search: function() {
            console.log(self.query)
        }
        /*
        search: function() {
            let self = this;
            if(self.query.length > 1) {
                self.results = []
                for(s in self.species_list) {
                    if(s.name.includes(self.query)) {
                        self.results.append(s.name)
                    }   
                }
            } else {
                self.results = []
            }
        } 
        */    
    }
};

/*
app.search = function() {
    if(app.vue.query.length > 1) {
        console.log(app.vue.query.length)
    }
}
*/
app.vue = Vue.createApp(app.data).mount("#app");


app.load_data = function () {
    axios.get(load_species_url).then(function (r) {
        app.vue.query = r.data.query;
        app.vue.species_list = r.data.species_list;
        app.vue.all_sightings_list = r.data.all_sightings_list;
    });
}

app.load_data();
