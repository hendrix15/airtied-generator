from search.config import TrussEnvironmentConfig


class TrussEnvironment:
    def __init__(self, config: TrussEnvironmentConfig) -> None:
        self.config = config
