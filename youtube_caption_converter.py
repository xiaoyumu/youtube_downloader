import json
import math
import time
from typing import Optional, List


def _to_sentence(sentence_start: int, sentence_duration: int, offset: int, sentence: str) -> str:
    start_time = sentence_start + offset
    start_time = 0 if start_time < 0 else start_time
    end_time = sentence_start + sentence_duration
    start = float_to_srt_time_format(start_time / 1000)
    end = float_to_srt_time_format(end_time / 1000)
    return f"{start} --> {end}\n{sentence}"


def float_to_srt_time_format(d: float) -> str:
    """Convert decimal durations into proper srt format.

    :rtype: str
    :returns:
        SubRip Subtitle (srt) formatted time duration.

    float_to_srt_time_format(3.89) -> '00:00:03,890'
    """
    fraction, whole = math.modf(d)
    time_fmt = time.strftime("%H:%M:%S,", time.gmtime(whole))
    ms = f"{fraction:.3f}".replace("0.", "")
    return time_fmt + ms


def convert_json_caption_to_srt(json_captions: dict or str, offset: Optional[int] = 0) -> Optional[str]:
    """
XML Caption Sample:
{'wireMagic': 'pb3',
'pens': [{}],
'wsWinStyles': [{}, {'mhModeHint': 2, 'juJustifCode': 0, 'sdScrollDir': 3}],
'wpWinPositions': [{}, {'apPoint': 6, 'ahHorPos': 20, 'avVerPos': 100, 'rcRows': 2, 'ccCols': 40}],
'events': [
{'tStartMs': 0, 'dDurationMs': 1170720, 'id': 1, 'wpWinPosId': 1, 'wsWinStyleId': 1},
{'tStartMs': 40, 'dDurationMs': 5080, 'wWinId': 1, 'segs': [
    {'utf8': 'today', 'acAsrConf': 0},
    {'utf8': " we're", 'tOffsetMs': 240, 'acAsrConf': 0},
    {'utf8': ' going', 'tOffsetMs': 400, 'acAsrConf': 0},
    {'utf8': ' to', 'tOffsetMs': 520, 'acAsrConf': 0},
    {'utf8': ' be', 'tOffsetMs': 640, 'acAsrConf': 0},
    {'utf8': ' talking', 'tOffsetMs': 800, 'acAsrConf': 0},
    {'utf8': ' about', 'tOffsetMs': 1240, 'acAsrConf': 0}]
},
{'tStartMs': 1670, 'dDurationMs': 3450, 'wWinId': 1, 'aAppend': 1, 'segs': [{'utf8': '\n'}]},
{'tStartMs': 1680, 'dDurationMs': 5599, 'wWinId': 1, 'segs': [
    {'utf8': 'metric', 'acAsrConf': 0},
    {'utf8': ' driven', 'tOffsetMs': 560, 'acAsrConf': 0},
    {'utf8': ' agent', 'tOffsetMs': 1199, 'acAsrConf': 0},
    {'utf8': ' development', 'tOffsetMs': 1800, 'acAsrConf': 0},
    {'utf8': ' and', 'tOffsetMs': 2679, 'acAsrConf': 0}]},
{'tStartMs': 5110, 'dDurationMs': 2169, 'wWinId': 1, 'aAppend': 1, 'segs': [{'utf8': '\n'}]},
{'tStartMs': 5120, 'dDurationMs': 6240, 'wWinId': 1, 'segs': [
    {'utf8': 'specifically', 'acAsrConf': 0},
    {'utf8': " we're", 'tOffsetMs': 920, 'acAsrConf': 0},
    {'utf8': ' going', 'tOffsetMs': 1080, 'acAsrConf': 0},
    {'utf8': ' to', 'tOffsetMs': 1199, 'acAsrConf': 0},
    {'utf8': ' be', 'tOffsetMs': 1320, 'acAsrConf': 0},
    {'utf8': ' focusing', 'tOffsetMs': 1480, 'acAsrConf': 0}]},
{'tStartMs': 7269, 'dDurationMs': 4091, 'wWinId': 1, 'aAppend': 1, 'segs': [{'utf8': '\n'}]},
{'tStartMs': 7279, 'dDurationMs': 5881, 'wWinId': 1, 'segs': [
    {'utf8': 'on', 'acAsrConf': 0},
    {'utf8': ' ragas', 'tOffsetMs': 321, 'acAsrConf': 0},
    {'utf8': ' for', 'tOffsetMs': 1081, 'acAsrConf': 0},
    {'utf8': ' evaluating', 'tOffsetMs': 1561, 'acAsrConf': 0},
    {'utf8': ' our', 'tOffsetMs': 2561, 'acAsrConf': 0},
    {'utf8': ' agents', 'tOffsetMs': 2961, 'acAsrConf': 0},
    {'utf8': ' in', 'tOffsetMs': 3561, 'acAsrConf': 0}]},
{'tStartMs': 11350, 'dDurationMs': 1810, 'wWinId': 1, 'aAppend': 1, 'segs': [{'utf8': '\n'}]},

SRT sample
1
00:00:05,000 --> 00:00:10,000
字幕转制｜天外生物
感谢原字幕制作者

2
00:02:26,640 --> 00:02:28,510
卡西利亚斯法师
Master kaecilius.

3
00:02:29,770 --> 00:02:33,570
那个仪式 依我看 只会害了你
That ritual will bring you only sorrow.

4
00:03:08,640 --> 00:03:09,640
伪君子
Hypocrite!


    :param json_captions:
    :param offset:
    :return:
    """
    if not json_captions:
        return None
    if isinstance(json_captions, dict):
        caption = json_captions
    elif isinstance(json_captions, str):
        caption = json.loads(json_captions)
    else:
        raise ValueError("Invalid json captions specified.")

    events = caption.get("events")
    if not events:
        return None

    srt_transcripts = []
    sentence = []
    sentence_start = 0
    sentence_duration = 0
    for event in events:
        # First event is the total duration
        sentence_start = event.get("tStartMs")
        sentence_duration = event.get("dDurationMs", 0)
        if sentence_start == 0:
            print(f"Total Duration (ms): {sentence_duration}")
            continue
        if event.get("aAppend") and sentence:
            srt_transcripts.append(_to_sentence(sentence_start, sentence_duration, offset, "".join(sentence)))
        segments = event.get("segs")
        sentence = [s.get("utf8") for s in segments]

    return "\n\n".join((f"{index}\n{s}" for index, s in enumerate(srt_transcripts, start=1)))
