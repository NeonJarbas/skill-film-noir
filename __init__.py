from os.path import join, dirname

from json_database import JsonStorage

from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill


class FilmNoirSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        self.supported_media = [MediaType.SILENT_MOVIE, MediaType.BLACK_WHITE_MOVIE]
        self.skill_icon = join(dirname(__file__), "ui", "filmnoir_icon.gif")
        self.archive = {v["streams"][0]: v for v in JsonStorage(f"{dirname(__file__)}/Film_Noir.json").values()
                        if v["streams"]}
        super().__init__(*args, **kwargs)
        self.load_ocp_keywords()

    def load_ocp_keywords(self):
        bw_movies = []
        directors = []

        for url, data in self.archive.items():
            t = data["title"].split("|")[0].split("(")[0].strip()
            if " - " in t:
                pieces = t.split(" - ")
                t = pieces[0].strip()
                if t.isdigit():
                    y = pieces[0]  # year
                    pieces = pieces[1:]
                    t = pieces[0]  # english title
                    if len(pieces) == 2:
                        director = pieces[1]
                        directors.append(director)
                    elif len(pieces) == 3:
                        t2 = pieces[1]  # original lang title
                        bw_movies.append(t2.strip())
                        director = pieces[-1]
                        directors.append(director)
                elif pieces[-1].isdigit():
                    y = pieces[-1]  # year
            elif '"' in t:
                t = t.split('"')[1]
            elif t.startswith("19"):
                t = " ".join(t.split()[1:])
            elif " aka " in t:
                t, t2 = t.split(" aka ")
                bw_movies.append(t2.strip())
            else:
                t = t.split(",")[0].split(" 19")[0].split("/")[0].split(" aka ")[0].split("-")[0].split("[")[0].replace(".", " ")

            bw_movies.append(t.strip())

        self.register_ocp_keyword(MediaType.BLACK_WHITE_MOVIE,
                                  "bw_movie_name", bw_movies)
        self.register_ocp_keyword(MediaType.MOVIE,
                                  "movie_director", directors)
        self.register_ocp_keyword(MediaType.MOVIE,
                                  "movie_streaming_provider",
                                  ["FilmNoir",
                                   "Film Noir"])

    def get_playlist(self, score=50, num_entries=25):
        pl = self.featured_media()[:num_entries]
        return {
            "match_confidence": score,
            "media_type": MediaType.MOVIE,
            "playlist": pl,
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "image": self.skill_icon,
            "title": "FilmNoir (Movie Playlist)",
            "author": "Internet Archive"
        }

    @ocp_search()
    def search_db(self, phrase, media_type):
        base_score = 15 if media_type in [MediaType.MOVIE, MediaType.BLACK_WHITE_MOVIE] else 0
        entities = self.ocp_voc_match(phrase)

        bw_title = entities.get("bw_movie_name")
        director = entities.get("movie_director")
        skill = "movie_streaming_provider" in entities  # skill matched

        base_score += 30 * len(entities)

        if bw_title or director:
            candidates = self.archive.values()

            if bw_title:
                base_score += 20
                candidates = [video for video in self.archive.values()
                              if bw_title.lower() in video["title"].lower()]
            elif director:
                base_score += 25
                candidates = [video for video in self.archive.values()
                              if director.lower() in video["title"].lower()]

            for video in candidates:
                yield {
                    "title": video["title"],
                    "match_confidence": min(100, base_score),
                    "media_type": MediaType.BLACK_WHITE_MOVIE,
                    "uri": video["streams"][0],
                    "playback": PlaybackType.VIDEO,
                    "skill_icon": self.skill_icon,
                    "skill_id": self.skill_id,
                    "image": video["images"][0] if video["images"] else self.skill_icon
                }

        if skill:
            yield self.get_playlist()

    @ocp_featured_media()
    def featured_media(self):
        return [{
            "title": video["title"],
            "match_confidence": 70,
            "media_type": MediaType.MOVIE,
            "uri": video["streams"][0],
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "skill_id": self.skill_id
        } for video in self.archive.values()]


if __name__ == "__main__":
    from ovos_utils.messagebus import FakeBus

    s = FilmNoirSkill(bus=FakeBus(), skill_id="t.fake")
    for r in s.search_db("play A Colt Is My Passport", MediaType.BLACK_WHITE_MOVIE):
        print(r)
        # {'title': 'A Colt Is My Passport', 'match_confidence': 65, 'media_type': <MediaType.BLACK_WHITE_MOVIE: 20>, 'uri': 'https://archive.org/download/a-colt-is-my-passport/A Colt is my Passport.mp4', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
