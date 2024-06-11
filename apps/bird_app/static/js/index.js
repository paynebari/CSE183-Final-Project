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
            selectedLatLng: null,
            checklistDate: '',
            checklistTime: '',
            checklistDuration: '',
            get_sightings_url: get_sightings_url, // Use the URL passed from the template
            get_species_url: get_species_url,     // Use the URL passed from the template
            create_checklist_url: create_checklist_url // random comment
        };
    },
    methods: {
        initMap: function() {
            this.map = new google.maps.Map(document.getElementById('map'), {
                center: {lat: -34.397, lng: 150.644},
                zoom: 8
            });
            
            google.maps.event.addListener(this.map, 'click', (event) => {
                this.selectedLatLng = event.latLng;
                console.log("Selected LatLng:", this.selectedLatLng);
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
                const url = `/bird_app/location?ne_lat=${ne.lat()}&ne_lng=${ne.lng()}&sw_lat=${sw.lat()}&sw_lng=${sw.lng()}`;
                //const url = `/bird_app/location`;
                console.log(url)
                window.location.href = url;
            } else {
                alert("Please draw a rectangle to select a region first.");
            }
        },
        openChecklistPage() {
            const date = this.checklistDate;
            const time = this.checklistTime;
            const duration = this.checklistDuration;
            const uniqueId = uuid.v4();
            const latLng = this.selectedLatLng

            if (latLng && date && time && duration) {
                const lat = latLng.lat();
                const lng = latLng.lng();

            axios.post(this.create_checklist_url, {
                sampling_id: uniqueId,
                latitude: lat,
                longitude: lng,
                date: date,
                time: time,
                duration: duration
            }).then(response => {
                const url = `/bird_app/checklist?sampling_id=${uniqueId}`;
                window.location.href = url;
            }).catch(error => {
                console.error("Error creating checklist:", error);
            });

            } else {
                alert("Please draw a rectangle, enter date, time, and duration.");
            }
        }
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

