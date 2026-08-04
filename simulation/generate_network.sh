#!/bin/bash
# Convert OSM file to SUMO network
netconvert --osm-files city.osm --output-file road_network.net.xml --geometry.remove --lefthand False