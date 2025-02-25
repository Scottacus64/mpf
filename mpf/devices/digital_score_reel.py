"""Contains the base class for digital (image-based) score reels."""

from mpf.core.system_wide_device import SystemWideDevice


class DigitalScoreReel(SystemWideDevice):

    """A digital score reel."""

    config_section = 'digital_score_reels'
    collection = 'digital_score_reels'
    class_label = 'digital_score_reel'

    def __init__(self, machine, name):
        """Initialize digital score reel."""
        super().__init__(machine, name)
        self._frames = {}
        self._reel_count = 0
        self._include_player_number = False

    async def _initialize(self):
        await super()._initialize()

        self._reel_count = self.config["reel_count"]
        self._include_player_number = self.config["include_player_number"]
        for frame in self.config["frames"]:
            self._frames[str(frame["character"])] = str(frame["frame"])

        self.machine.events.add_handler(self.name, self._post_reel_values)

    def _post_reel_values(self, **kwargs):
        # pull only the right-most digits from a score to display on the digital score reels
        # without this a score with more digits than the score reel will show the right-most digits
        # ie without this code q five digital score reel will display 123,000 as 12,300 not 23,000
        kwargs["value"] = kwargs["value"] % (10**self._reel_count)
        # Pad the string up to the necessary number of characters in the reel
        score = str(kwargs["value"]).rjust(self._reel_count, self.config["start_value"])
        # Create a dict of reel name keys to target frame values
        result = {str(i + 1): self._frames[score[i]] for i in range(self._reel_count)}
        # Post the event
        event_name = "score_reel_{}_player{}".format(self.name, self.machine.game.player.number) if \
            self._include_player_number else "score_reel_{}".format(self.name)
        self.machine.events.post(event_name, **result)
