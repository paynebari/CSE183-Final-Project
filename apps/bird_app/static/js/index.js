"use strict";

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


app.data = {    
    data: function() {
        return {
            map: null,
            drawingManager: null,
            heatmap: null,
            selectedSpecies: '',
            birdSightings: [],
            speciesList: [],
            selectedBounds: null,
            get_sightings_url: get_sightings_url, // Use the URL passed from the template
            get_species_url: get_species_url     // Use the URL passed from the template
        };
    },
    methods: {
        initMap: function() {
            this.map = new google.maps.Map(document.getElementById('map'), {
                center: {lat: -34.397, lng: 150.644},
                zoom: 8
            });
            
            this.drawingManager = new google.maps.drawing.DrawingManager({
                drawingMode: null,
                drawingControl: true,
                drawingControlOptions: {
                    position: google.maps.ControlPosition.TOP_CENTER,
                    drawingModes: ['rectangle']
                }
            });
            this.drawingManager.setMap(this.map);
            
            google.maps.event.addListener(this.drawingManager, 'overlaycomplete', (event) => {
                if (event.type === 'rectangle') {
                    this.selectedBounds = event.overlay.getBounds();
                }
            });

            this.heatmap = new google.maps.visualization.HeatmapLayer({
                data: [],
                map: this.map
            });
        },
        getHeatmapData() {
            const heatmapData = this.birdSightings.map(sighting => {
                if (sighting.checklist && sighting.checklist.latitude && sighting.checklist.longitude) {
                    return new google.maps.LatLng(sighting.checklist.latitude, sighting.checklist.longitude);
                } else {
                    console.warn("Invalid sighting data:", sighting);
                    return null;
                }
            }).filter(data => data !== null);

            console.log("Heatmap Data:", heatmapData);
            return heatmapData;
        },
        loadBirdSightings() {
            axios.get(this.get_sightings_url).then(response => {
                this.birdSightings = response.data.sightings;
                this.heatmap.setData(this.getHeatmapData());
                console.log("Bird sightings", this.birdSightings);

                this.birdSightings.forEach(sighting => {
                    if (!sighting.checklist || !sighting.checklist.latitude || !sighting.checklist.longitude) {
                        console.warn("Invalid sighting coordinates:", sighting);
                    }
                });
            }).catch(error => {
                console.error("Error loading sightings:", error);
            });
        },
        loadSpecies() {
            axios.get(this.get_species_url).then(response => {
                this.speciesList = response.data.species;
                console.log(this.speciesList);
            }).catch(error => {
                console.error("Error loading species:", error);
            });
        },
        filterBySpecies() {
            let filteredData = this.birdSightings;
            
            if(this.selectedSpecies) {
                filteredData = this.birdSightings.filter(sighting => sighting.sightings.name === this.selectedSpecies);
            }

            const heatmapData = filteredData.map(sighting => new google.maps.LatLng(sighting.checklist.latitude, sighting.checklist.longitude));
            this.heatmap.setData(heatmapData);
        },
        showRegionStatistics() {
            if (this.selectedBounds) {
                const ne = this.selectedBounds.getNorthEast();
                const sw = this.selectedBounds.getSouthWest();
                const bounds = {
                    ne: { lat: ne.lat(), lng: ne.lng() },
                    sw: { lat: sw.lat(), lng: sw.lng() }
                };
                const boundsStr = encodeURIComponent(JSON.stringify(bounds));
                const checklistStr = encodeURIComponent(JSON.stringify(this.birdSightings));
                const url = `checklist?bounds=${boundsStr}&checklist=${checklistStr}`;
                window.location.href = url;
                //console.log("Selected region bounds:", this.selectedBounds.toString());
            } else {
                alert("draw a rectangle to select a region first");
            }
        },
    },
    mounted() {
        this.initMap();
        this.loadBirdSightings();
        this.loadSpecies();
    }
};

app.vue = Vue.createApp(app.data).mount("#app");

app.load_data = function () {
    //axios.get(my_callback_url).then(function (r) {
        //app.vue.my_value = r.data.my_value;
    //});
}

app.load_data();

