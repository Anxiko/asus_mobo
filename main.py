import asyncio
import datetime
import os
import sys
import traceback
from pprint import pprint, pformat
from typing import Self

import httpx
from telegram.ext import ApplicationBuilder, Application

_REQUEST_URL = (
	"https://www.asus.com/support/api/product.asmx/"
	"GetPDQVLMemory?website=global&model=PRIME-X670-P&pdhashedid=5pv1a1nmz9ylflce&PageSize=20&PageIndex=1"
	"&keyword=KF560C36BBEK2-32&CPUSeries=Ryzen%E2%84%A2+7000-Series+CPU&pdid=21006&siteID=www&sitelang="
)

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


class Notifier:
	_telegram: Application
	_chat_id: int | str

	def __init__(self, telegram: Application, chat_id: int | str):
		self._telegram = telegram
		self._chat_id = chat_id

	@classmethod
	def from_token(cls, token: str, chat_id: int | str) -> Self:
		return cls(telegram=ApplicationBuilder().token(token).build(), chat_id=chat_id)

	@classmethod
	def from_env(cls) -> Self:
		token: str = os.getenv("NOTIFIER_TOKEN")
		chat_id: str = os.getenv("NOTIFIER_CHAT_ID")
		return cls.from_token(token, chat_id)

	def notify(self, item: dict) -> None:
		has_changed: bool = item != _EXPECTED
		timestamp: str = datetime.datetime.now(datetime.UTC).isoformat()
		changes: str = "ITEM HAS CHANGED" if has_changed else "NO CHANGES DETECTED"
		item_str: str = pformat(item)

		msg: str = f"{timestamp}: {changes}\n{item_str}"
		self._send_message(msg)

	def _send_message(self, message: str) -> None:
		asyncio.run(self._telegram.bot.send_message(self._chat_id, message))


def main() -> None:
	response: httpx.Response = httpx.get(url=_REQUEST_URL)
	response.raise_for_status()

	item = _extract_item_from_response(response)
	pprint(item)

	notifier: Notifier = Notifier.from_env()
	notifier.notify(item)


def _extract_item_from_response(response: httpx.Response) -> dict:
	items: list[dict] = response.json()["Result"]["Obj"]

	if (items_count := len(items)) != 1:
		raise ValueError(f"Expected exactly 1 item, found {items_count}: {items}")

	return items[0]


def _notify_unchanged(_item: dict) -> None:
	pass


def _notify_changed(_item: dict) -> None:
	pass


if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		print(f"ERROR: {e!r}", file=sys.stderr)
		traceback.print_exc()
