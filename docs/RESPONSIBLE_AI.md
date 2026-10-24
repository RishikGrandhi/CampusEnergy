# Responsible AI and limitations

## Data and privacy

CampusEnergy AI uses **synthetic / simulated prototype campus energy data**. A real deployment should use aggregate building-level occupancy only. It must not use student identity, facial recognition, phone tracking, or individual movement tracking.

## Bias and coverage

The simulated history may underrepresent holidays, examinations, festivals, vacations, special events, equipment faults, and unusual weather. Performance for those conditions can be worse than the aggregate metrics suggest.

## Security

A real deployment would require authentication, authorization, encrypted communications, restricted meter and BMS-data access, secrets management, and audit logging. This prototype has no live integration.

## Accessibility

Interfaces should use readable text, explicit units and labels, keyboard-friendly controls, warning text, and redundant visual cues rather than colour alone.

## Human oversight

The required flow is: **AI forecast → recommendation → facility-manager verification → human decision**. The prototype does not switch equipment, change HVAC setpoints, control lighting, operate meters, or control a building-management system.

## Technical limitations

- Synthetic single-building dataset rather than real operational data.
- Simplified binary occupancy schedule.
- Assumed future temperature and occupancy inputs.
- Unexpected events are intentionally not supplied as model features.
- Dependence on historical patterns and limited robustness to distribution shift.
- No equipment-level causal understanding.
- No live smart-meter, weather-service, or BMS integration.
- Fixed 24-hour forecast horizon.
- What-if results are model scenarios, not guaranteed or causal outcomes.

