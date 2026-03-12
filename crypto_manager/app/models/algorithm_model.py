class AlgorithmModel:
    def __init__(
        self,
        id=None,
        name="",
        type="",
        key_size=0,
        mode="",
        created_at=None
    ):
        self.id = id
        self.name = name
        self.type = type
        self.key_size = key_size
        self.mode = mode
        self.created_at = created_at