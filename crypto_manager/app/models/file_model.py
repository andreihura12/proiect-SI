class FileModel:
    def __init__(
        self,
        id=None,
        filename="",
        path="",
        status="necriptat",
        file_type="",
        size_bytes=0,
        hash="",
        created_at=None
    ):
        self.id = id
        self.filename = filename
        self.path = path
        self.status=status
        self.file_type = file_type
        self.size_bytes = size_bytes
        self.hash = hash
        self.created_at = created_at