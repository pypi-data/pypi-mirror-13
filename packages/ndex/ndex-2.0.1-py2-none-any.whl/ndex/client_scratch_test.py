import ndex.client as nc
import json

devNdex = nc.Ndex("http://dev.ndexbio.org", "test", "ndex")

devNdex.set_debug_mode(True)

network = devNdex.get_complete_network('feb33e25-1f5c-11e5-8169-0aa4c1de39d1')

query = {u"properties":[{u"name":u"foo",u"value":u"bar"},],u"admin": u"test", u"limit" : 500}

results = devNdex.search_for_networks_by_network_properties(query)

print results

