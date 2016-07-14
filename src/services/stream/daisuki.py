# Shows in a region: https://motto.daisuki.net/api2/search/mode:1
# Specific show: https://motto.daisuki.net/api2/seriesdetail/SHOW_ID

from logging import debug, info, warning, error
from datetime import datetime

from .. import AbstractServiceHandler
from data.models import Episode

import re

class ServiceHandler(AbstractServiceHandler):
	_api_show_url = "https://motto.daisuki.net/api2/seriesdetail/{id}"
	_episode_url = "http://www.daisuki.net/anime/watch.{show}.{ep}.html"
	_show_url = "http://www.daisuki.net/anime/detail.{show}.html"
	_show_re = re.compile("daisuki.net/anime/detail.([\w-]+)", re.I)

	def __init__(self):
		super().__init__("daisuki", "Daisuki", False)

	# Episode finding

	def get_all_episodes(self, stream, **kwargs):
		info("Getting episodes for Daisuki/{}".format(stream.show_id))

		episodes = []
		response = self.request(url, xml=True, **kwargs)

		for movieset in response.findall("movieset"):
			for items in movieset.findall("items"):
				for item in items.findall("item"):
                	episodes.append(Episode(item.get("chapter"), None, _episode_url.format(show=stream.show_key, ep=item.get("productid")), datetime.utcnow()))

		return episodes

	# Remote info getting

	def get_stream_info(self, stream, **kwargs):
		info("Getting stream info for Daisuki/{}".format(stream.show_id))

		url = _api_show_url.format(id=stream.show_id)
		response = self.request(url, xml=True, **kwargs)
		if response is None:
			error("Cannot get feed")
			return None

		stream.name = response.get("result").get("abstruct").get("title")
		return stream

	def get_seasonal_streams(self, year=None, season=None, **kwargs):
		# Seasonal streams are not supported by Daisuki
		return list()

	# Local info formatting

	def get_stream_link(self, stream):
		# Just going to assume it's the correct service
		return self._show_url.format(show=stream.show_key)

	def extract_show_key(self, url):
		match = self._show_re.search(url)
		if match:
			return match.group(1)
		return None
