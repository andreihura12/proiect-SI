class PerformanceModel:
    def __init__(
        self,
        id=None,
        operation_id=None,
        memory=0,
        execution_time=0
    ):
        self.id = id
        self.operation_id = operation_id
        self.memory = memory
        self.execution_time = execution_time