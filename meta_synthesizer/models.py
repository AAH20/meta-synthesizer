from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
import time
import uuid


class PatchStatus(str, Enum):
    PROPOSED = "proposed"
    SHADOW_VALIDATING = "shadow_validating"
    HOT_SWAPPED = "hot_swapped"
    ROLLED_BACK = "rolled_back"
    COMMITTED = "committed"


@dataclass
class HotPatchDescriptor:
    patch_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    target_module: str = ""
    target_symbol: str = ""
    synthesized_source_code: str = ""
    patch_reason: str = ""
    author_model: str = "Claude Opus 5.5"  # or GPT-6 Sol
    created_at: float = field(default_factory=time.time)
    status: PatchStatus = PatchStatus.PROPOSED


@dataclass
class PatchVerificationAudit:
    patch_id: str
    syntax_valid: bool
    ast_invariants_passed: bool
    shadow_execution_succeeded: bool
    performance_gain_pct: float = 0.0
    error_message: Optional[str] = None


@dataclass
class RollbackCheckpoint:
    patch_id: str
    target_module: str
    target_symbol: str
    original_symbol_ref: Any
    created_at: float = field(default_factory=time.time)
