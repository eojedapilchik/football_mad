import os


class FeatureFlags:
    def __init__(self, env=os.environ):
        self.env = env

    def is_enabled(self, key: str, default=False) -> bool:
        return self.env.get(key, str(default)).lower() in ("1", "true", "yes")

    @property
    def enable_goal_images(self) -> bool:
        return self.is_enabled("ENABLE_GOAL_IMAGES")

    @property
    def save_to_gsheet(self) -> bool:
        return self.is_enabled("SAVE_TO_GSHEET")

    @property
    def save_livescore_events(self) -> bool:
        return self.is_enabled("SAVE_LIVESCORE_EVENTS")

    @property
    def save_html_to_disk(self) -> bool:
        return self.is_enabled("SAVE_HTML_TO_DISK")

    @property
    def use_playwright(self) -> bool:
        return self.is_enabled("USE_PLAYWRIGHT")

    @property
    def use_wkhtmltopdf(self) -> bool:
        return self.is_enabled("USE_WKHTMLTOPDF")

    @property
    def log_full_event_data(self) -> bool:
        return self.is_enabled("LOG_FULL_EVENT_DATA")

    @property
    def debug_mode(self) -> bool:
        return self.is_enabled("DEBUG_MODE")

    @property
    def use_mongo_db(self) -> bool:
        return self.is_enabled("USE_MONGO_DB")


# Singleton instance
flags = FeatureFlags()
