"""Request/response contracts. Pydantic validates the *shape*; services validate the *meaning*.

Keep this file in step with docs/API.md. Field defaults here intentionally mirror the service defaults.
"""

from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

Source = Literal["real", "demo"]
ModelName = Literal["Logistic regression", "Random forest"]  # == fairlens.models.MODEL_NAMES (tested)
ToggleableInput = Literal["Attribute13", "Attribute9"]  # age, personal status and sex


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ErrorDetail(BaseModel):
    code: str = Field(description="Stable machine-readable error code, e.g. dataset_missing.")
    message: str = Field(description="Plain-language explanation that is safe to show to a person.")
    details: dict = Field(default_factory=dict, description="Optional structured extras.")


class ErrorResponse(BaseModel):
    error: ErrorDetail


class DecisionRule(Strict):
    threshold: float = Field(0.5, ge=0, le=1, description="Classify Good when P(Good) >= threshold.")
    per_group: Optional[dict[str, float]] = Field(
        None, description="Optional separate thresholds keyed by the two age-group labels (a cautionary what-if)."
    )


class SourceRequest(Strict):
    source: Source = "real"


class SettingsRequest(SourceRequest):
    model: ModelName = "Logistic regression"
    excluded: list[ToggleableInput] = Field(default_factory=list, description="Sensitive inputs hidden from the model.")


class RuleRequest(SettingsRequest):
    decision_rule: DecisionRule = Field(default_factory=DecisionRule)


class StabilityRequest(SettingsRequest):
    n_splits: int = Field(30, ge=2, le=50)


class ModelRuleRequest(SourceRequest):
    model: ModelName = "Logistic regression"
    decision_rule: DecisionRule = Field(default_factory=DecisionRule)


class MitigationRequest(SourceRequest):
    model: ModelName = "Logistic regression"


class ProxyRequest(SourceRequest):
    drop_status: bool = False


class MapRequest(RuleRequest):
    include_train: bool = False
    bins: int = Field(5, ge=2, le=12)
    min_per_group: int = Field(5, ge=1, le=100)


class MapApplicantRequest(RuleRequest):
    include_train: bool = False
    index: int = Field(0, ge=0)


class SimulatorEvaluateRequest(RuleRequest):
    profile: dict[str, Union[int, float, str]] = Field(description="One value for each of the 20 inputs.")


class ByomAuditRequest(Strict):
    upload_id: str
    decision_column: str
    group_column: str
    truth_column: Optional[str] = None
    favorable_value: Optional[str] = None
    threshold: Optional[float] = None
    truth_positive_value: Optional[str] = None
    reference_group: Optional[str] = None