from dataclasses import dataclass, field, asdict
from typing import Any

BURDEN_DIMS = ('actions','handling_minutes','rework','waiting_minutes','financial_cost','cognitive_load','uncertainty_minutes','temporal_span_days')

@dataclass(frozen=True)
class Event:
    event_id:str; unit_id:str; timestamp:float; actor:str; activity:str
    state_before:str=''; state_after:str=''; source_id:str=''; confidence:float=1.0
    completion:int=1; rework:int=0; attributes:dict[str,Any]=field(default_factory=dict)
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class Capacity:
    actor:str; minutes_per_day:float; utilisation_target:float=.85

@dataclass(frozen=True)
class Requirement:
    requirement_id:str; name:str; trigger_activity:str; actions_per_unit:float; minutes_per_unit:float
    rework_per_unit:float=0.0; waiting_minutes_per_unit:float=0.0; financial_cost_per_unit:float=0.0
    cognitive_load_per_unit:float=0.0; uncertainty_minutes_per_unit:float=0.0; temporal_span_days_per_unit:float=0.0

@dataclass(frozen=True)
class Actor:
    actor_id:str; role:str; eligible:bool=True

@dataclass(frozen=True)
class Stage:
    name:str; actor:str; share:float

@dataclass(frozen=True)
class Topology:
    topology_id:str; name:str; description:str; stages:tuple[Stage,...]

@dataclass(frozen=True)
class Estimate:
    actor:str; dimension:str; estimate:float; lower:float; upper:float; source_type:str
    source_refs:tuple[str,...]; assumption:str; base_estimate:float=0.0; increment_over_base:float=0.0
    evidence_role:str='requirement_allocation'
    def to_dict(self): return asdict(self)|{'source_refs':list(self.source_refs)}
