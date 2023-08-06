import messaging as m
import ownership as o
import pixelwriter as p

content_url = "https://s3-us-west-1.amazonaws.com/bitiverse/content3.json"##'https://goo.gl/Q71zMW' 'http://tinyurl.com/grcqm68'
private_key = '5J2ua97TSZPPKSWvBo8jDdQ4wrB3hYvt2zs1LKCXVCTr8RpMuVS'
from_address = '1KHeNhmb2AWbbpS4WCgk9cbAChRK4v3fvU'
coords_set = [[400, 400], [600, 600]]
owners, ownerlist = o.process_all()

tx = p.content_tx(from_address, coords_set, content_url, private_key, ownerlist, \
push=True, fee=20000, sign=True)

print tx
