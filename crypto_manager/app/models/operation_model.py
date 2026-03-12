class OperationModel:
    def __init__(
        self,
        id=None,
        file_id=None,
        algorithm_id=None,
        framework_id=None,
        key_id=None,
        operation_type="",
        input_path="",
        output_path="",
        status="",
        created_at=None
    ):
        self.id = id
        self.file_id = file_id
        self.algorithm_id = algorithm_id
        self.framework_id = framework_id
        self.key_id = key_id
        self.operation_type = operation_type
        self.input_path = input_path
        self.output_path = output_path
        self.status = status
        self.created_at = created_at