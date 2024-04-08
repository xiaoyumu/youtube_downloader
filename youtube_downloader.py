import os
import socket

import arrow
import socks
from typing import Optional, Callable, Any, Dict

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from pytube import YouTube, Stream, StreamQuery, exceptions, Caption
from pytube.exceptions import MembersOnly
from pytube.innertube import InnerTube

from youtube_caption_converter import convert_json_caption_to_srt


def setup_proxy_socks5(proxy_ip: str, proxy_port: int):
    socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, proxy_ip, proxy_port)
    socket.socket = socks.socksocket


class YouTubeFixed(YouTube):
    def __init__(
            self,
            url: str,
            on_progress_callback: Optional[Callable[[Any, bytes, int], None]] = None,
            on_complete_callback: Optional[Callable[[Any, Optional[str]], None]] = None,
            proxies: Dict[str, str] = None,
            use_oauth: bool = False,
            allow_oauth_cache: bool = True):
        super().__init__(url, on_progress_callback, on_complete_callback, proxies, use_oauth, allow_oauth_cache)

    def bypass_age_gate(self):
        """Attempt to update the vid_info by bypassing the age gate."""
        innertube = InnerTube(
            client='ANDROID',
            use_oauth=self.use_oauth,
            allow_cache=self.allow_oauth_cache
        )
        innertube_response = innertube.player(self.video_id)

        playability_status = innertube_response['playabilityStatus'].get('status', None)

        # If we still can't access the video, raise an exception
        # (tier 3 age restriction)
        if playability_status == 'UNPLAYABLE':
            raise exceptions.AgeRestrictedError(self.video_id)

        self._vid_info = innertube_response


class Task(object):
    def __init__(self, seq: int, video_url: str, audio_offset: float = 0, **kwargs):
        self.seq = seq
        self.video_url = video_url
        self.audio_offset = audio_offset
        self.prefix = kwargs.get("prefix")
        self.download_subtitle = kwargs.get("subtitle")
        self.subtitle_language = kwargs.get("subtitle_language")
        self.subtitle_offset_ms = kwargs.get("subtitle_offset_ms")
        self.skip_video_download = kwargs.get("skip_video_download")
        self.verbose = kwargs.get("verbose")


def pickup_audio_stream(streams: StreamQuery) -> Optional[Stream]:
    stream = streams.filter(mime_type="audio/mp4").order_by("abr").last()
    return stream


def pickup_video_stream(streams: StreamQuery) -> Optional[Stream]:
    stream = streams.filter(mime_type="video/mp4").order_by("resolution").last()
    return stream


def pickup_stream_with_both_video_and_audio(streams: StreamQuery) -> Optional[Stream]:
    for f in streams.order_by("resolution"):  # type: Stream
        if len(f.codecs) == 2 and f.resolution in ["720p", "1080p"]:
            return f
    return None


def list_streams(streams: StreamQuery):
    print("Listing streams for this video...")
    for f in streams:  # type: Stream
        if f.mime_type.startswith("audio"):
            print(f"\tStream: {f.mime_type} Audio: {f.audio_codec}/{f.abr}")
        else:
            print(
                f"\tStream: {f.mime_type} {f.resolution} Video Codec: {f.video_codec}/{f.fps} Audio: {f.audio_codec}/{f.abr}")


def dump_video_description(yt: YouTube, downloaded_video_file: str):
    file_name = os.path.basename(downloaded_video_file).split(".")[0]
    file_path = os.path.dirname(downloaded_video_file)
    with open(f"{file_path}/{file_name}.txt", "w", encoding="utf-8") as desc_file:
        # Write original url and description to text file.
        desc_file.writelines([f"{yt.title}\n",
                              "=" * 80,
                              f"\n\n源视频链接: {yt.watch_url}\n\n",
                              yt.description])


def download_stream(stream: Stream, output_path, **kwargs) -> str:
    if stream.includes_video_track and stream.includes_audio_track:
        print(f"Start downloading stream {stream.mime_type} {stream.resolution} "
              f"Codec: {stream.video_codec}/{stream.audio_codec}...")
        track_type = "mixed"
    else:
        if "video" in stream.mime_type:
            print(f"Start downloading video stream {stream.mime_type} {stream.resolution} "
                  f"Codec: {stream.video_codec}...")
            track_type = "video"
        else:
            print(f"Start downloading audio stream {stream.mime_type} {stream.abr} "
                  f"Codec: {stream.audio_codec} ...")
            track_type = "audio"
    sequence = kwargs.get("sequence", 0)
    original_filename = stream.default_filename
    print("default_filename:", original_filename)
    prefix = kwargs.get("prefix")
    if prefix:
        output_file_name = f"{sequence:02}_{track_type}_{prefix}_{original_filename}"
    else:
        output_file_name = f"{sequence:02}_{track_type}_{original_filename}"

    downloaded_file = stream.download(filename=output_file_name, output_path=output_path)
    print(f"{downloaded_file} downloaded successfully.")
    return downloaded_file


def generate_download_file_name(output_path: str, output_filename: str, **kwargs):
    sequence = kwargs.get("sequence")
    prefix = kwargs.get("prefix")
    if prefix:
        final_output_file = f"{sequence:02}_{prefix}_{output_filename}"
    else:
        final_output_file = f"{sequence:02}_{output_filename}"
    return os.path.join(output_path, final_output_file)


def combine_video_audio_files(local_video_file: str, local_audio_file: str,
                              final_output_file: str,
                              **kwargs) -> str:
    video_clip = VideoFileClip(local_video_file)
    audio_clip = AudioFileClip(local_audio_file)
    audio_offset = kwargs.get("audio_offset")
    if audio_offset and isinstance(audio_offset, float):
        # Set audio start offset, to manually align with video.
        print(f"Set Audio Start Offset: {audio_offset}")
        audio_clip.set_start(audio_offset)
    video_clip = video_clip.set_audio(audio_clip)
    video_clip.write_videofile(final_output_file)

    return final_output_file


def save_srt_file(srt_content: str, lang: str, video_file_path: str):
    file_name = os.path.basename(video_file_path).split(".")[0]
    file_path = os.path.dirname(video_file_path)

    srt_file_name = f"{file_name}.{lang}.srt"
    srt_file_path = os.path.join(file_path, srt_file_name)
    print(f"Saving {srt_file_path} ...")
    with open(srt_file_path, "w", encoding="utf-8") as f:
        f.write(srt_content)


def try_download_subtitle(task: Task, yt: YouTube, final_output_file: str):
    """
    Subtitles can only be downloaded after streams loaded for the YouTube instance.
    :param task:
    :param yt:
    :param final_output_file:
    :return:
    """
    caption_tracks = yt.caption_tracks
    if caption_tracks:
        for track in caption_tracks:  # type: Caption
            # xml_captions = track.xml_captions
            json_captions: dict = track.json_captions
            print(f"Converting json caption {track} to srt ...")
            save_srt_file(convert_json_caption_to_srt(json_captions, offset=task.subtitle_offset_ms),
                          map_caption_lang(track.code),
                          final_output_file)
    else:
        print("No caption tracks found.")


def map_caption_lang(code: str):
    if code in ["a.en", "en"]:
        return "eng"
    return code


def remove_temp_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)


def ensure_temp_folder_exists(download_output_path: str) -> str:
    temp_folder = os.path.join(download_output_path, "temp")
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder, exist_ok=True)

    return temp_folder


def on_download_progress(stream: Stream, chunk_data, remaining_bytes: int):
    print(f"Remaining Bytes: {remaining_bytes}              ")


def on_download_completed(stream: Stream, downloaded_path: str):
    print("\nDownload Completed.")


def download_video(task: Task, download_output_path: str):
    now = arrow.now()
    print(f"\nStart task at {now.isoformat()} ...")
    print(f"Analyzing video link {task.video_url} ...")
    yt = YouTube(task.video_url)
    # yt.bypass_age_gate()

    try:
        yt.check_availability()
        yt.register_on_progress_callback(on_download_progress)
        yt.register_on_complete_callback(on_download_completed)
        streams = yt.streams
        if task.verbose:
            list_streams(streams)

        # Try pickup HD video and audio streams (separately)
        hd_video_stream = pickup_video_stream(streams)
        audio_stream = pickup_audio_stream(streams)
        final_output_file = None
        if hd_video_stream and audio_stream:
            final_output_file = generate_download_file_name(download_output_path,
                                                            hd_video_stream.default_filename,
                                                            sequence=task.seq,
                                                            prefix=task.prefix)
            if not task.skip_video_download:
                temp_folder = ensure_temp_folder_exists(download_output_path)

                local_video_file = download_stream(hd_video_stream, temp_folder, sequence=task.seq)
                local_audio_file = download_stream(audio_stream, temp_folder, sequence=task.seq)
                combine_video_audio_files(local_video_file, local_audio_file,
                                          final_output_file,
                                          audio_offset=task.audio_offset)

                # 如果混合成功就删除临时文件（视频和音频流）
                if os.path.exists(final_output_file) and os.path.isfile(final_output_file):
                    remove_temp_file(local_video_file)
                    remove_temp_file(local_audio_file)

        else:
            single_stream = pickup_stream_with_both_video_and_audio(streams)
            if single_stream:
                final_output_file = download_stream(single_stream, download_output_path,
                                                    sequence=task.seq,
                                                    prefix=task.prefix)

        if final_output_file:
            dump_video_description(yt, final_output_file)

        if task.download_subtitle:
            try_download_subtitle(task, yt, final_output_file)

    except MembersOnly as me:
        print(f"Unable to download video {task.seq:02} due to {str(me)}")

