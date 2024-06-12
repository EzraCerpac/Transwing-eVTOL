from pathlib import Path

from departments.flight_performance.mission_profile import MissionProfile

ROOT = Path(__file__).parent.parent.parent
MISSION_PROFILE_JSON = ROOT / 'departments/flight_performance/mission_profile_V2.json'


def mission_profile() -> MissionProfile:
    return MissionProfile.from_json(MISSION_PROFILE_JSON)
