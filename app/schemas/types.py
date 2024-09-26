from typing import TypeVar, TypeAlias, TypedDict, Optional
from datetime import datetime


class ServiceStatus(TypedDict):
    status: Optional[bool]
    last_update_time: datetime


class UnifiedServiceStatus(TypedDict):
    trader_websocket_status: ServiceStatus
    trader_polling_status: ServiceStatus
    balance_notifyer_status: ServiceStatus
    balance_updater_status: ServiceStatus
    balance_warden_status: ServiceStatus


# TypeVar's
M = TypeVar("M")

Position: TypeAlias = dict
# for binane.com
# [
#   {
#         "symbol": "ADAUSDT",
#         "positionSide": "LONG",               // position side
#         "positionAmt": "30",
#         "entryPrice": "0.385",
#         "breakEvenPrice": "0.385077",
#         "markPrice": "0.41047590",
#         "unRealizedProfit": "0.76427700",     // unrealized profit
#         "liquidationPrice": "0",
#         "isolatedMargin": "0",
#         "notional": "12.31427700",
#         "marginAsset": "USDT",
#         "isolatedWallet": "0",
#         "initialMargin": "0.61571385",        // initial margin required with current mark price
#         "maintMargin": "0.08004280",          // maintenance margin required
#         "positionInitialMargin": "0.61571385",// initial margin required for positions with current mark price
#         "openOrderInitialMargin": "0",        // initial margin required for open orders with current mark price
#         "adl": 2,
#         "bidNotional": "0",                   // bids notional, ignore
#         "askNotional": "0",                   // ask notional, ignore
#         "updateTime": 1720736417660
#   },
#   {
#         "symbol": "COMPUSDT",
#         "positionSide": "SHORT",
#         "positionAmt": "-1.000",
#         "entryPrice": "70.92841",
#         "breakEvenPrice": "70.900038636",
#         "markPrice": "49.72023376",
#         "unRealizedProfit": "21.20817624",
#         "liquidationPrice": "2260.56757210",
#         "isolatedMargin": "0",
#         "notional": "-49.72023376",
#         "marginAsset": "USDT",
#         "isolatedWallet": "0",
#         "initialMargin": "2.48601168",
#         "maintMargin": "0.49720233",
#         "positionInitialMargin": "2.48601168",
#         "openOrderInitialMargin": "0",
#         "adl": 2,
#         "bidNotional": "0",
#         "askNotional": "0",
#         "updateTime": 1708943511656
#   }
# ]

Order: TypeAlias = dict
# for binance.com:
# {
#   	"avgPrice": "0.00000",
#   	"clientOrderId": "abc",
#   	"cumQuote": "0",
#   	"executedQty": "0",
#   	"orderId": 1917641,
#   	"origQty": "0.40",
#   	"origType": "TRAILING_STOP_MARKET",
#   	"price": "0",
#   	"reduceOnly": false,
#   	"side": "BUY",
#   	"positionSide": "SHORT",
#   	"status": "NEW",
#   	"stopPrice": "9300",				// please ignore when order type is TRAILING_STOP_MARKET
#   	"closePosition": false,   // if Close-All
#   	"symbol": "BTCUSDT",
#   	"time": 1579276756075,				// order time
#   	"timeInForce": "GTC",
#   	"type": "TRAILING_STOP_MARKET",
#   	"activatePrice": "9020",			// activation price, only return with TRAILING_STOP_MARKET order
#   	"priceRate": "0.3",					// callback rate, only return with TRAILING_STOP_MARKET order
#   	"updateTime": 1579276756075,		// update time
#   	"workingType": "CONTRACT_PRICE",
#   	"priceProtect": false,              // if conditional order trigger is protected
#       "priceMatch": "NONE",              //price match mode
#       "selfTradePreventionMode": "NONE", //self trading preventation mode
#       "goodTillDate": 0                  //order pre-set auot cancel time for TIF GTD order
# }

