#!/bin/sh

echo "Creating map-data..."
mkdir -p map-data
echo "Changing to map-data directory..."
cd map-data

echo "Downloading Ukraine OSM data..."
wget https://download.geofabrik.de/europe/ukraine-latest.osm.pbf


# extract
echo "Extracting OSM data..."
docker run -t -v $(pwd):/data osrm/osrm-backend osrm-extract -p /opt/car.lua /data/ukraine-latest.osm.pbf

# contract
echo "Contracting OSM data..."
docker run -t -v $(pwd):/data osrm/osrm-backend osrm-contract /data/ukraine-latest.osrm

echo "OSRM data is ready."

echo "Going back to the previous directory..."
cd ..