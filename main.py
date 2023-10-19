from pprint import pprint

import httpx

_REQUEST_URL = "https://www.asus.com/support/api/product.asmx/GetPDQVLMemory?website=global&model=PRIME-X670-P&pdhashedid=5pv1a1nmz9ylflce&PageSize=20&PageIndex=1&keyword=KF560C36BBEK2-32&CPUSeries=Ryzen%E2%84%A2+7000-Series+CPU&pdid=21006&siteID=www&sitelang="

_EXPECTED = {
	"ChipBrand": "SK Hynix",
	"DIMM": "1,2",
	"PartNo": "KF560C36BBEK2-32",
	"RAMSpeed": "6000",
	"Remark": "",
	"RunSpeed": "6000",
	"SSDS": "SS",
	"Size": "2x 16GB",
	"Timing": "36-38-38-80",
	"Vendors": "KINGSTON",
	"Voltage": "1.35",
	"XMPEXPO": "XMP/EXPO"
}

response: httpx.Response = httpx.get(url=_REQUEST_URL)
response.raise_for_status()

pprint(response.json())


def main() -> None:
	response: httpx.Response = httpx.get(url=_REQUEST_URL)
	response.raise_for_status()

	item = _extract_item_from_response(response)

	if item != _EXPECTED:
		_notify_changes(item)


def _extract_item_from_response(response: httpx.Response) -> dict:
	items: list[dict] = response.json()["Result"]["Obj"]

	if (items_count := len(items)) != 1:
		raise ValueError(f"Expected exactly 1 item, found {items_count}: {items}")

	return items[0]


def _notify_changes(item: dict) -> None:
	pass
