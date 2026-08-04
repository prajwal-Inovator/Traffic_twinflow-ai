# simulation/generate_network.py
import os
import subprocess
import logging
import osmnx as ox
from ..digital_twin.osm_importer import OSMImporter
import yaml

logger = logging.getLogger(__name__)

def generate_sumo_network(config_path: str = "../digital_twin/config.yaml", output_dir: str = "."):
    """Fetch OSM data and convert to SUMO network."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    bbox = config["city"]["bbox"]
    # Use OSMnx to get the graph
    importer = OSMImporter(config_path)
    G = importer.fetch_graph()

    # Save as .osm.xml
    osm_file = os.path.join(output_dir, "road_network.osm.xml")
    ox.save_graph_xml(G, filepath=osm_file)

    # Convert to SUMO network using netconvert
    net_file = os.path.join(output_dir, "road_network.net.xml")
    cmd = [
        "netconvert",
        "--osm-files", osm_file,
        "--output-file", net_file,
        "--geometry.remove",
        "--roundabouts.guess",
        "--ramps.guess",
        "--junctions.join",
        "--tls.guess",
        "--tls.join",
        "--tls.default-type", "actuated",
    ]
    subprocess.run(cmd, check=True)

    logger.info(f"SUMO network generated: {net_file}")
    return net_file

if __name__ == "__main__":
    generate_sumo_network()