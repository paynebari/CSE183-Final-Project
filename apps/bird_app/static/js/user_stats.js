"use strict";

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

app.data = {    
    data: function() {
        return {
            search_query: "",
            species_list: [],
            backup_species_list: [],
            plot_data: [],
        };
    },

    methods: {
        order_first_seen: function() {  
            let self = this;
            axios.post(order_first_seen_url, {}).then(function(r) {
                self.species_list =r.data.species_list;
                self.backup_species_list =r.data.species_list;
            });       
        },
        order_recently_seen: function() {  
            let self = this;
            axios.post(order_recently_seen_url, {}).then(function(r) {
                self.species_list =r.data.species_list;
                self.backup_species_list =r.data.species_list;
            }); 
        },

        search: function() {
            let self = this;
            if (self.search_query) { 
                console.log("query: " + self.search_query);
                console.log("backup list " + self.backup_species_list);
                self.species_list = self.backup_species_list.slice().filter(
                    s => s.name.toLowerCase().includes(self.search_query.toLowerCase()));
                console.log("list after load" + self.species_list);
            }
            // If length is 0, call function that resets the list. 
            else {
                self.reset();
                console.log("list coming back from reset: " + self.species_list);
                /*
                axios.get(load_species_url).then(function (r) {
                    app.vue.query = r.data.query;
                    app.vue.species_list = r.data.species_list;
                    app.vue.plot_data = r.data.plot_data;
                }); 
                console.log(self.search_query);
                */
            }
        },

        reset: function() {
            let self = this;
            axios.post(reset_url, {}).then(function (r) {
                self.species_list = r.data.species_list;
                self.backup_species_list = r.data.species_list;
                self.search_query = "";
            });
            console.log("list after reset: " + self.species_list)
            console.log("query after reset: " + self.search_query)
        },

        initialize_chart: function(data) {
            console.log("list: " + data)
            let dataset = [];
            let dates = [];
            let max_count = 0;
            let length = data.length;
            console.log(data[1].checklist.date)
            for (let row = 0; row < length; row++) {
                let date = data[row].checklist.date;
                let count = data[row].sightings.observation_count;
                //console.log(date + " count before being pushed: " + count)
                // If date is not in dates, add it to dates and add it to the dataset, plus its count
                if( !(dates.includes(date)) )  {
                    dates.push(date);
                    dataset.push({date: date, count: count})
                    console.log(date + " count being added: " + count)
                }
                // If date is already in dates, then search for it in dataset and add to its count.
                else {
                    for(let pair of dataset) {
                        console.log(pair.date, date)
                        if(pair.date == date) {
                            pair.count = pair.count + count;
                            console.log(date + " count after being added to: " + pair.count)
                        }
                    }
                }
            }

            console.log("this is my dataset: " + dataset)
            console.log("the count: " + dataset[1].count)

            // Aggregate data by date
            var aggregatedData = dataset.reduce((acc, entry) => {
                if (acc[entry.date]) {
                    acc[entry.date] += entry.count;
                    console.log(entry.count);

                } else {
                    acc[entry.date] = entry.count;
                    console.log(entry.count);
                }
                return acc;
            }, {});
        
            // Sort the dates
            var sortedDates = Object.keys(aggregatedData).sort((a, b) => new Date(a) - new Date(b));
        
            // Prepare labels and data for the chart
            var labels = sortedDates;
            var data = sortedDates.map(date => aggregatedData[date]);

            console.log(data)

            const CHART = document.getElementById("myChart");
            console.log(CHART);
            let myChart = new Chart(CHART, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                      label: 'Number of Birds Spotted',
                      data: data,
                      backgroundColor: 'rgba(75, 192, 192, 0.2)',
                      borderColor: 'rgba(75, 192, 192, 1)',
                      borderWidth: 1
                    }]
                  },
                  options: {
                    scales: {
                      y: {
                        beginAtZero: true
                      }
                    }
                  }
                });
                /*
                data: {
                    labels: labels, //['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
                    datasets: [{
                      label: 'All Species Seen',
                      data: data,
                      borderWidth: 1
                    }]
                  },
                  options: {
                    scales: {
                      y: {
                        beginAtZero: true
                      }
                    }
                  }
            })
                  */
        } 
    },

    /*
    mounted: function() {
        this.initialize_chart();
        console.log("mounted: " + this.plot_data)
    }
    */
};

app.vue = Vue.createApp(app.data).mount("#app");


app.load_data = function () {
    axios.get(load_species_url).then(function (r) {
        app.vue.query = r.data.query;
        app.vue.species_list = r.data.species_list;
        app.vue.backup_species_list = r.data.species_list;
        app.vue.plot_data = r.data.plot_data;
        app.vue.initialize_chart(app.vue.plot_data);
    });
}

app.load_data();
