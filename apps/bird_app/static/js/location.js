"use strict";

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

app.data = {    
    data: function() {
        return {
            my_value: 1, // This is an example.
            species: [],
            new_species: "",
            checklists: [],
            chartInitialized: false,
            top_users: [],
            total_sightings: "",
            selectedSpecies: null, // Track the selected species
        };
    },
    methods: {
        my_function: function() {
            // This is an example.
            this.my_value += 1;
        },
       fetch_names: function(s){
            console.log(s.type);
            let self = this;
            axios.post(load_names_url, {
                bird_name: s.type,
            }).then(response => {
                let labels = response.data.labels;
                let values = response.data.values;
                console.log("labels:", labels);
                console.log("values:", values);
                if(labels.length > 0){
                    self.updateChart(labels, values);
                }
            }).catch(error => {
                console.error("Error fetching names:", error);
            });
       },
        initializeChart: function(){
            const ctx = document.getElementById('myChart');
            this.myChart = new Chart(ctx, {
              type: 'bar',
              data: {
                labels: [],
                datasets: [{
                    label: 'Number of Birds Seen Over Time',
                    data: [],
                    backgroundColor: 'rgba(54, 162, 235, 1)', // Blue with some transparency
                    borderColor: 'rgba(54, 162, 235, 1)', // Solid blue border
                    borderWidth: 1,
                }]
              },
              options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Birds'
                        }
                    },
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day',
                            tooltipFormat: 'll', // Format for tooltip
                            displayFormats: {
                                day: 'MMM D'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                label += context.parsed.y;
                                label += ' birds';
                                return label;
                            },
                            title: function(context) {
                                let title = context[0].label;
                                return moment(title).format('LL'); // Format the date
                            }
                        }
                    }
                }
              }
            });
            this.chartInitialized = true;
        },
        updateChart(labels, values) {
            this.myChart.data.labels = labels;
            this.myChart.data.datasets[0].data = values;
            if (!this.chartInitialized) {
                this.initializeChart();
            }
            this.myChart.update();
        },
        selectSpecies: function(species) {
            this.selectedSpecies = species.id;
            this.fetch_names(species); // Fetch names when a species is selected
        },
        test(s){
            console.log(s.type);
        }
    },
    mounted: function() {
        this.initializeChart();
    }
};

app.vue = Vue.createApp(app.data).mount("#app");

app.load_data = function () {
    console.log("test");
    axios.get(load_info_url).then(function(r){
        console.log(r.status);
        let c = r.data.checklists;
        let s = r.data.species;
        console.log(s);
        app.vue.checklists = c;
        app.vue.species = s;
        app.vue.top_users = r.data.top_users;
        console.log("top_users:", r.data.top_users);
        app.vue.total_sightings = r.data.total_sightings;
    });
}

app.load_data();