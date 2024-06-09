"use strict";

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


app.data = {    
    data: function() {
        return {
            // Complete as you see fit.
            my_value: 1, // This is an example.
        };
    },
    methods: {
        // Complete as you see fit.
        my_function: function() {
            // This is an example.
            this.my_value += 1;
        },
        initMap: function() {
            let map = new google.maps.Map(document.getElementById('map'), {
                center: {lat: -34.397, lng: 150.644},
                zoom: 8
            });

            let marker = new google.maps.Marker({
                position: {lat: -34.397, lng: 150.644},
                map: map,
                title: 'Bird Sighting!'
            });
        },

    },
    mounted() {
        this.initMap();
    }
};

app.vue = Vue.createApp(app.data).mount("#app");

app.load_data = function () {
    axios.get(my_callback_url).then(function (r) {
        app.vue.my_value = r.data.my_value;
    });
}

app.load_data();

