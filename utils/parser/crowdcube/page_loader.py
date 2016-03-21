import urllib
import urllib.request
import http.client
import zlib

_cookie = 'CROWDCUBE=phrb98el7qdkntoqip6ca8mr60; optimizelyEndUserId=oeu1458556637544r0.7179416295593368; cc_cookie_accept=true; ajs_anonymous_id=%229227e3df-cc1d-47e2-9754-59d52586a7b4%22; _gat=1; linkedin_oauth_lxajtg4g1m5e_crc=null; linkedin_oauth_lxajtg4g1m5e=%7B%22member_id%22%3A%229EK4L3QcEk%22%2C%22access_token%22%3A%22_BTKOYmDkE1qSwMpDYRFr5SWN5tESGZD8h8x%22%2C%22signature_order%22%3A%5B%22access_token%22%2C%22member_id%22%5D%2C%22signature%22%3A%222RLZ1kt9Z1CvzsF3D8akZ8HhJkw%3D%22%2C%22signature_version%22%3A%221%22%2C%22signature_method%22%3A%22HMAC-SHA1%22%7D; optimizelySegments=%7B%22301478757%22%3A%22false%22%2C%22301609519%22%3A%22gc%22%2C%22301718402%22%3A%22campaign%22%2C%224534217240%22%3A%22simplycook%22%7D; optimizelyBuckets=%7B%7D; ajs_group_id=null; _ga=GA1.2.815153033.1458556639; ajs_user_id=%226R89Y%22; _bizo_bzid=7057d2e9-1ed3-4d16-80ba-69e82db9e850; _bizo_cksm=26479046367CE856; _bizo_np_stats=14%3D150%2C; __storejs__=%22__storejs__%22; optimizelyPendingLogEvents=%5B%5D; PRUM_EPISODES=s=1458556876026&r=https%3A//www.crowdcube.com/investments%3Fsort_by%3D0%26q%3D%26joined%3D3%26hof%3D1%26i1%3D0%26i2%3D0%26i3%3D0%26i4%3D0%26sort_by%3D7'


def get_page(url_to_request: str) -> str:
    req = urllib.request.Request(
            url=url_to_request,
            headers={
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language':'en-US,en;q=0.8',
                'accept-encoding':'gzip, deflate, sdch',
                'Cache-Control':'no-cache',
                'Connection':'keep-alive',
                'Cookie': _cookie,
                'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'
            })

    with urllib.request.urlopen(req) as response:
        assert(isinstance(response, http.client.HTTPResponse))
        data = response.read()
        return zlib.decompress(data, 16+zlib.MAX_WBITS).decode()
