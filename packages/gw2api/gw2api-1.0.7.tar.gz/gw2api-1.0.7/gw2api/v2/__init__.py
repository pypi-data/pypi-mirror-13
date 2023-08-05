VERSION = "v2"
BASE_URL = "https://api.guildwars2.com/%s/" % VERSION
LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "de": "German",
    "fr": "French",
    "ko": "Korean",
    "zh": "Chinese"
}


from .endpoint import Endpoint, LocaleAwareEndpoint
from .recipes import RecipeSearchEndpoint
from .account import (AuthenticatedEndpoint, AccountEndpoint,
                      TokenInfoEndpoint, CharacterEndpoint,
                      PvpGamesEndpoint, PvpStatsEndpoint, GuildEndpoint)
from .transactions import TransactionEndpoint
from .wvw import WvwMatchesEndpoint


build = Endpoint("build")
colors = LocaleAwareEndpoint("colors")
exchange = Endpoint("commerce/exchange")
listings = Endpoint("commerce/listings")
prices = Endpoint("commerce/prices")
continents = LocaleAwareEndpoint("continents")
events = LocaleAwareEndpoint("events")
events_state = Endpoint("events-state")
files = Endpoint("files")
floors = LocaleAwareEndpoint("floors")
items = LocaleAwareEndpoint("items")
leaderboards = Endpoint("leaderboards")
maps = LocaleAwareEndpoint("maps")
quaggans = Endpoint("quaggans")
recipes = Endpoint("recipes")
recipe_search = RecipeSearchEndpoint(recipes)
skins = LocaleAwareEndpoint("skins")
specializations = LocaleAwareEndpoint("specializations")
traits = LocaleAwareEndpoint("traits")
worlds = LocaleAwareEndpoint("worlds")
wvw_matches = WvwMatchesEndpoint("wvw/matches")
wvw_objectives = LocaleAwareEndpoint("wvw/objectives")
materials = LocaleAwareEndpoint("materials")
currencies = LocaleAwareEndpoint("currencies")
achievements = LocaleAwareEndpoint("achievements")
achievement_categories = LocaleAwareEndpoint("achievements/categories")
achievement_groups = LocaleAwareEndpoint("achievements/groups")
minis = LocaleAwareEndpoint("minis")
emblem_foregrounds = Endpoint("emblem/foregrounds")
emblem_backgrounds = Endpoint("emblem/backgrounds")
guild_upgrades = LocaleAwareEndpoint("guild/upgrades")
guild_permissions = LocaleAwareEndpoint("guild/permissions")
skills = LocaleAwareEndpoint("skills")

account = AccountEndpoint("account")
token_info = TokenInfoEndpoint("tokeninfo")
characters = CharacterEndpoint("characters")
transactions = TransactionEndpoint("commerce/transactions")
pvp_games = PvpGamesEndpoint("pvp/games")
pvp_stats = PvpStatsEndpoint("pvp/stats")
guild = GuildEndpoint("guild")
