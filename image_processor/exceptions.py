class PlayerPhotoFilenameNotFoundError(Exception):
    """Exception raised when a player is not found in the database."""

    def __init__(self, player_name):
        self.player_id = player_name
        super().__init__(
            f"player: {player_name} photo attribute not found in the Direcuts."
        )
