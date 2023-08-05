import json
import requests

tradingpost = "tradingpost-fra-live.ncplatform.net"
user_agent = ("Mozilla/5.0 (Windows NT 6.1; WOW64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/28.0.1500.68 Safari/537.36")

profession = {
    "guardian": 1,
    "warrior": 2,
    "engineer": 3,
    "ranger": 4,
    "thief": 5,
    "elemental": 6,
    "mesmer": 7,
    "necro": 8,
    "necromancer": 8,
}
rarity = {
    "basic": 1,
    "fine": 2,
    "masterwork": 3,
    "rare": 4,
    "exotic": 5,
    "ascended": 6,
    "legendary": 7,
}
categories = {
    "armor": 0,
    "back": 1,
    "bag": 2,
    "consumable": 3,
    "container": 4,
    "craftingmaterial": 5,
    "gathering": 6,
    "gizmo": 7,
    "minipet": 11,
    "tool": 13,
    "trinket": 15,
    "trophy": 16,
    "upgradecomponent": 17,
    "weapon": 18,
}
subcategory = {
    "armor-coat": 0,
    "armor-leggings": 1,
    "armor-gloves": 2,
    "armor-helm": 3,
    "armor-helmaquatic": 4,
    "armor-boots": 5,
    "armor-shoulders": 6,
    "consumable-booze": 3001,
    "consumable-food": 3003,
    "consumable-generic": 3004,
    "consumable-transmutation": 3008,
    "consumable-unlock": 3009,
    "consumable-utility": 3012,
    "container-default": 4000,
    "container-giftbox": 4001,
    "gathering-foraging": 6000,
    "gathering-logging": 6001,
    "gathering-mining": 6002,
    "gizmo-default": 7000,
    "gizmo-salvage": 7002,
    "tool-crafting": 13000,
    "tool-salvage": 13002,
    "trinket-accessory": 15000,
    "trinket-amulet": 15001,
    "trinket-ring": 15002,
    "upgradecomponent-weapon": 17003,
    "upgradecomponent-armor": 17002,
    "upgradecomponent-trinket": 17001,
    "upgradecomponent-infusion": 17000,
    "weapon-sword": 18000,
    "weapon-hammer": 18001,
    "weapon-bowlong": 18002,
    "weapon-bowshort": 18003,
    "weapon-axe": 18004,
    "weapon-dagger": 18005,
    "weapon-greatsword": 18006,
    "weapon-mace": 18007,
    "weapon-pistol": 18008,
    "weapon-rifle": 18010,
    "weapon-scepter": 18011,
    "weapon-staff": 18012,
    "weapon-focus": 18013,
    "weapon-torch": 18014,
    "weapon-warhorn": 18015,
    "weapon-shield": 18016,
    "weapon-harpoon": 18019,
    "weapon-speargun": 18020,
    "weapon-trident": 18021,
    "weapon-toy": 18022
}


def sts_request(host, protocol, command, headers, body, type="One"):
    request = {
        "protocol": protocol,
        "command": command,
        "headers": headers,
        "body": body,
        "type": type
    }

    url = "https://%s/stsRequest?%s/%s" % (host, protocol, command)

    # print url
    # print json.dumps(request, indent=2)

    headers = {
        "Origin": "https://" + host,
        "Referer": "https://" + host + "/",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": user_agent,
        "Content-Type": "application/json",
    }

    r = requests.post(url, json.dumps(request), headers=headers)
    r.raise_for_status()
    response = r.json()

    return response["body"]


def search(m, query):
    response = sts_request(tradingpost,
                           "Game.gw2.ItemSearch", "TradeSearch",
                           {"m": m}, query)
    return response


def get_listings(m, item_id):
    response = sts_request(tradingpost,
                           "Game.gw2.Trade", "GetListings",
                           {"t": "$" + str(item_id), "m": m},
                           {"buys": "", "sells": ""})
    return response


def buy(m, item_id, unit_price, quantity=1):
    offer = {"UnitPrice": unit_price, "Quantity": quantity}
    response = sts_request(tradingpost,
                           "Game.gw2.Trade", "Buy",
                           {"t": "$" + str(item_id), "m": m},
                           {"offers": [offer]})
    return response

