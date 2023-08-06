# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import logging

from .entitybase import EntityBase

logger = logging.getLogger(__name__)


class System(EntityBase):
    """
    This class represents a system.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
