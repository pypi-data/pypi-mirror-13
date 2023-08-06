import io

import ndex.client as nc
import json

anon_ndex = nc.Ndex("http://dev2.ndexbio.org")

ns = anon_ndex.get_network_summary('7e6835e3-d1e6-11e5-bff3-0251251672f9')

print ns.get('name')
print ns.get('edgeCount')
print ns.get('nodeCount')

metabolic_networks = anon_ndex.search_networks('metabo*')
print len(metabolic_networks)

for ns in metabolic_networks: print ns.get('name')

metabolic_networks = anon_ndex.search_networks('metabo*', 'drh', block_size=2)
print len(metabolic_networks)
for ns in metabolic_networks: print ns.get('name')

# First change:
cx_stream_as_json = anon_ndex.get_network_as_cx_stream('7e6835e3-d1e6-11e5-bff3-0251251672f9').json()
print len( cx_stream_as_json )

q = anon_ndex.get_neighborhood_as_cx_stream('7e6835e3-d1e6-11e5-bff3-0251251672f9', 'P62308').json()
print q

ndex = nc.Ndex("http://dev2.ndexbio.org", "test", "test")

ndex.set_debug_mode(True)


cx_stream = io.BytesIO(ndex.get_network_as_cx_stream('7e6835e3-d1e6-11e5-bff3-0251251672f9').content)
new_network_id = ndex.save_cx_stream_as_new_network(cx_stream)

cx_stream2 = io.BytesIO(ndex.get_network_as_cx_stream('7e6835e3-d1e6-11e5-bff3-0251251672f9').content)
read_only_new_network_id = ndex.save_cx_stream_as_new_network(cx_stream2)

cx_stream3 = io.BytesIO(ndex.get_network_as_cx_stream('7e6835e3-d1e6-11e5-bff3-0251251672f9').content)
to_be_updated_network_id = ndex.save_cx_stream_as_new_network(cx_stream3)

response = ndex.get_network_as_cx_stream('b6bdf38f-d639-11e5-863c-0251251672f9')
update_cx_stream = io.BytesIO(response.content)
ndex.update_cx_network(update_cx_stream, to_be_updated_network_id)
print r
print '!!!Done updating!'


network_profile = {"name":"Renamed Network","description":"New Description","version":"2.0","visibility":"PUBLIC"}
ndex.update_network_profile(new_network_id,network_profile)

network_profile = {"name":"Renamed Read-Only Network","description":"New Description","version":"2.0","visibility":"PUBLIC"}
ndex.update_network_profile(read_only_new_network_id, network_profile)

ndex.set_read_only(read_only_new_network_id, True)

ndex.delete_network(new_network_id)

