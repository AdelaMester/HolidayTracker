TRACK YOUR TRIPS

MY VIDEO: https://www.youtube.com/watch?v=E-XCzs7yW0k

Description:

I have created a web application that allows users to track their past trips by adding a marker on the map.
Every marker has a unique id which is saved in the database and also can be deleted from the database in case the user
clicked on a place by mistake. Markers can only be removed if they were added in the same log in session. Once the user wil sign back in,
the markers will be displayed on the map.

Database:

The first table created "users" stores user_id, username and the hashed password, notice that user_id is a primary key here.
The second table called "Past_trips" is where I have saved all the markers added on the map, where id is a primary key.

Setting markers on map and save them into the database:

1.Using event listener, I have added markers on the maps

    var location;
    //On click, set marker
    google.maps.event.addListener(map, 'click', function (e) {
        location = e.latLng;
        console.log("location=" + location);
        var marker = new google.maps.Marker({
            position: location,
            map: map
        });

2. I have made the request to the controller to be able to save them in my db

    //Make request to controller and save into db
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/past_trips");
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(location));


3. To delete the markers, I have created another event listener that gave me the possibility to remove the markers

    google.maps.event.addListener(marker, "click", function (e) {
            var content = 'Latitude: ' + location.lat() + '<br />Longitude: ' + location.lng();
            content += "<br /><input type = 'button' value = 'Delete' onclick = 'DeleteMarker(" + marker.id + ","+location.lat()+","+location.lng()+");' value = 'Delete' />";
            var infoWindow = new google.maps.InfoWindow({
                content: content
            });
            infoWindow.open(map, marker);
        });
        markers.push(marker);
    });
};

4. Then I have done the request to the controller to remove them from my db

    function DeleteMarker(id, lat, lng) {
        for (var i = 0; i < markers.length; i++) {
            if (markers[i].id == id) {
                markers[i].setMap(null);

                //Remove marker from array
                markers.splice(i, 1);

                var xhr = new XMLHttpRequest();
                var new_location = {};
                new_location.lat = lat;
                new_location.lng = lng;
                xhr.open("DELETE", "/past_trips");
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.send(JSON.stringify(new_location));
                //print in javascript
                console.log("message: " +new_location.lat +" "+ new_location.lng);


I have also added validation for log in, log out, change password and rendered the appropiate templates.

