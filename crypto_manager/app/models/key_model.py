class KeyModel:
    def __init__(
        self,
        id=None,
        algorithm_id=None,
        key_name="",
        key_type="",
        key_path="",
        created_at=None,
        is_active=1
    ):
        self.id = id
        self.algorithm_id = algorithm_id
        self.key_name = key_name
        self.key_type = key_type
        self.key_path = key_path
        self.created_at = created_at
        self.is_active = is_active