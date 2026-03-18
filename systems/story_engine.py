# systems/story_engine.py


class StoryEngine:
    def __init__(self):
        self.flags = {}
        self.story_log = []

    def reset(self):
        self.flags = {}
        self.story_log = []

    def set_flag(self, key, value=True):
        self.flags[key] = value
        self.story_log.append(f"[STORY] {key} = {value}")

    def get_flag(self, key):
        return self.flags.get(key, False)

    def log(self, msg):
        self.story_log.append(msg)
