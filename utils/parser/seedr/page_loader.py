import urllib
import urllib.request
import http.client
import zlib

_cookie = '__cfduid=d08c3c177679525925f19e8b2a03c26cb1458558786; optimizelyEndUserId=oeu1458558787724r0.19605043825684776; _gat=1; seen_cookie_message=accepted; __insp_wid=1563648670; __insp_nv=true; __insp_ref=d; __insp_targlpu=https%3A%2F%2Fwww.seedrs.com%2F; __insp_targlpt=Seedrs%20%7C%20Invest%20Online%20In%20Startups%20Via%20Equity%20Crowdfunding; __qca=P0-1421383562-1458558793568; __insp_norec_sess=true; signed_in_status=true; external_user_id=j7xhspp0ikgym1k2opt4f402yvxwrv0; _seedrs_session=4fc9356d00e7f45f5167174b7658eff0; optimizelySegments=%7B%221652103010%22%3A%22gc%22%2C%221655692999%22%3A%22referral%22%2C%221659313022%22%3A%22false%22%7D; optimizelyBuckets=%7B%7D; _ga=GA1.2.1296503646.1458558788; __insp_slim=1458558807187; analytical=%5B%5B%22identify%22%2C%22j7xhspp0ikgym1k2opt4f402yvxwrv0%22%2C%7B%22email%22%3A%22james%40jamesseymour.co.uk%22%2C%22name%22%3A%22James+Seymour%22%7D%5D%2C%5B%22set%22%2C%7B%22user_id%22%3A130330%2C%22session_id%22%3A%224fc9356d00e7f45f5167174b7658eff0%22%7D%5D%5D; mp_3bccab71799430a352d36dd035d35501_mixpanel=%7B%22distinct_id%22%3A%20%22j7xhspp0ikgym1k2opt4f402yvxwrv0%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22user_id%22%3A%20130330%2C%22session_id%22%3A%20%224fc9356d00e7f45f5167174b7658eff0%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpap%22%3A%20%5B%5D%2C%22mp_name_tag%22%3A%20%22James%20Seymour%22%7D; gs_u_GSN-749478-N=96cc34ac2a544000627ca6bfc0944954:3115:5758:1458558807770; ki_t=1458558795041%3B1458558795041%3B1458558809167%3B1%3B3; ki_r=https%3A%2F%2Fwww.facebook.com%2F; __ssid=88c25c67-4fdb-4dcd-8d82-ff29960f6f99; __zlcmid=ZlfPsDmEP8QIrY; optimizelyPendingLogEvents=%5B%22n%3Dengagement%26u%3Doeu1458558787724r0.19605043825684776%26wxhr%3Dtrue%26time%3D1458558810.872%26f%3D3386591039%26g%3D1655360595%22%5D; mp_mixpanel__c=6; PRUM_EPISODES=s=1458558810884&r=https%3A//www.seedrs.com/invest%23_%3D_; gs_p_GSN-749478-N=2'


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
