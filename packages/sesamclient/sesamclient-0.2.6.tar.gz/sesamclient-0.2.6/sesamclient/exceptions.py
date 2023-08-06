# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.


class PumpIsAlreadyRunning(Exception):
    def __init__(self, running_task):
        self.running_task = running_task


class TimeoutWhileWaitingForRunningPumpToFinishException(Exception):
    pass
