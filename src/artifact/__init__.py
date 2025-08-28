from dataclasses import dataclass
from constants import MODEL

@dataclass
class ModerationCheckArtifact:
    moderation_flagged: bool = False