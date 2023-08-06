import ndex.client as nc
import json

public_ndex = nc.Ndex("http://public.ndexbio.org", "drh", "drh")

public_ndex.set_debug_mode(False)

query1 = {"properties":[{"name":"ORGANISM","value":"http://identifiers.org/taxonomy/9606"}]}

query2 = {"properties":[{"name":"URI","value":"http://purl.org/pc2/4/Pathway_098d5b97ab0d39bfcf905771f06d18a5"}]}


networks = public_ndex.search_networks_by_property_filter(query1, account_name='ndextutorials')

for network in networks:
    print "Network: " + network.get("name")
    print "Properties: "
    for prop in network.get("properties"):
        print "  " + prop.get("predicateString") + " : " + prop.get("value")

networks2 = public_ndex.find_networks("large")