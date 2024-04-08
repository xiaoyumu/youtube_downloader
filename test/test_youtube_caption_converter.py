import unittest

from youtube_caption_converter import convert_json_caption_to_srt


class YoutubeCaptionConverterTest(unittest.TestCase):
    def build_caption_data(self):
        data = {"wireMagic": "pb3",
"pens": [{}],
"wsWinStyles": [{}, {"mhModeHint": 2, "juJustifCode": 0, "sdScrollDir": 3}],
"wpWinPositions": [{}, {"apPoint": 6, "ahHorPos": 20, "avVerPos": 100, "rcRows": 2, "ccCols": 40}],
"events": [
{"tStartMs": 0, "dDurationMs": 1170720, "id": 1, "wpWinPosId": 1, "wsWinStyleId": 1},
{"tStartMs": 40, "dDurationMs": 5080, "wWinId": 1, "segs": [
    {"utf8": "today", "acAsrConf": 0},
    {"utf8": " we're", "tOffsetMs": 240, "acAsrConf": 0},
    {"utf8": " going", "tOffsetMs": 400, "acAsrConf": 0},
    {"utf8": " to", "tOffsetMs": 520, "acAsrConf": 0},
    {"utf8": " be", "tOffsetMs": 640, "acAsrConf": 0},
    {"utf8": " talking", "tOffsetMs": 800, "acAsrConf": 0},
    {"utf8": " about", "tOffsetMs": 1240, "acAsrConf": 0}]
},
{"tStartMs": 1670, "dDurationMs": 3450, "wWinId": 1, "aAppend": 1, "segs": [{"utf8": "\n"}]},
{"tStartMs": 1680, "dDurationMs": 5599, "wWinId": 1, "segs": [
    {"utf8": "metric", "acAsrConf": 0},
    {"utf8": " driven", "tOffsetMs": 560, "acAsrConf": 0},
    {"utf8": " agent", "tOffsetMs": 1199, "acAsrConf": 0},
    {"utf8": " development", "tOffsetMs": 1800, "acAsrConf": 0},
    {"utf8": " and", "tOffsetMs": 2679, "acAsrConf": 0}]},
{"tStartMs": 5110, "dDurationMs": 2169, "wWinId": 1, "aAppend": 1, "segs": [{"utf8": "\n"}]},
{"tStartMs": 5120, "dDurationMs": 6240, "wWinId": 1, "segs": [
    {"utf8": "specifically", "acAsrConf": 0},
    {"utf8": " we're", "tOffsetMs": 920, "acAsrConf": 0},
    {"utf8": " going", "tOffsetMs": 1080, "acAsrConf": 0},
    {"utf8": " to", "tOffsetMs": 1199, "acAsrConf": 0},
    {"utf8": " be", "tOffsetMs": 1320, "acAsrConf": 0},
    {"utf8": " focusing", "tOffsetMs": 1480, "acAsrConf": 0}]},
{"tStartMs": 7269, "dDurationMs": 4091, "wWinId": 1, "aAppend": 1, "segs": [{"utf8": "\n"}]},
{"tStartMs": 7279, "dDurationMs": 5881, "wWinId": 1, "segs": [
    {"utf8": "on", "acAsrConf": 0},
    {"utf8": " ragas", "tOffsetMs": 321, "acAsrConf": 0},
    {"utf8": " for", "tOffsetMs": 1081, "acAsrConf": 0},
    {"utf8": " evaluating", "tOffsetMs": 1561, "acAsrConf": 0},
    {"utf8": " our", "tOffsetMs": 2561, "acAsrConf": 0},
    {"utf8": " agents", "tOffsetMs": 2961, "acAsrConf": 0},
    {"utf8": " in", "tOffsetMs": 3561, "acAsrConf": 0}]},
{"tStartMs": 11350, "dDurationMs": 1810, "wWinId": 1, "aAppend": 1, "segs": [{"utf8": "\n"}]}
]
}
        return data

    def test_convert_json_caption_to_srt(self):
        actual = convert_json_caption_to_srt(self.build_caption_data())

        print(actual)
