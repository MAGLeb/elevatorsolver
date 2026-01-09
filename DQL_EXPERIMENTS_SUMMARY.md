# DQL Experiments Summary

## Goal
Make DQL agent outperform BASE (SCAN algorithm) on elevator control task.

**Target**: BASE achieves +4607 validation reward.

---

## Experiment Timeline

### Phase 1: Initial DQL Analysis
- DQL delivers MORE passengers (5602 vs 4953) but loses overall
- Root cause: MISSED_STOP penalty (-1746) and MOVE_TO_EDGE (-1080)
- DQL doesn't understand floor boundaries or when to stop

### Phase 2: Action Masking v1
**Idea**: Mask invalid actions before choosing:
- Mask UP at top floor, DOWN at bottom floor
- Mask UP/DOWN when `should_stop` is true (passenger at current floor)

**Result**: MOVE_TO_EDGE=0, MISSED_STOP=0, but training didn't converge.

**Problem found**: Action masking only applied in `choose_action()`, not in `learn()`. Q-target was computed for ALL actions including masked ones, causing Q-values for valid actions to decrease.

### Phase 3: Action Masking v2 (with masked learning)
**Fix**: Store action masks in replay buffer, apply mask to Q-target calculation.

**Changes**:
1. Added `next_action_mask` to Transition namedtuple
2. Added `_compute_action_mask()` method
3. Modified `learn()` to compute and store masks
4. Added `_process_q_values_masked()` for masked Q-target

**Training results**:
- 100 episodes completed
- Best validation: -1998 (episode 58)
- Still far from BASE (+4607)

### Phase 4: Final Evaluation
**Result**: Complete failure.

```
BASE: +4606
DQL:  -2240
```

**DQL behavior**:
- 93% STOP actions
- 0 deliveries (BASE: 4953)
- Only 10 passengers picked up
- Agent stuck at one floor

---

## Root Cause Analysis

The action masking approach has a fundamental flaw:

```python
should_stop = (
    elevator_state.going_to_level[current_level] > 0 or
    manager_state.outside_calls[current_level] > 0
)
if should_stop:
    action_mask[0] = False  # disable UP
    action_mask[1] = False  # disable DOWN
```

**Problem**: When passengers continuously appear at the same floor, the elevator can NEVER leave. It's stuck choosing between STOP and WAIT forever.

The mask prevents MISSED_STOP but also prevents the elevator from moving at all.

---

## What Was Learned

1. **Action masking needs careful design** - masking based on `outside_calls` is too aggressive
2. **Q-learning with masks requires masked Q-targets** - otherwise training is unstable
3. **MISSED_STOP penalty is the core problem** - DQL can't learn when stopping is worth the opportunity cost

---

## Possible Future Approaches

### A. Soft masking (only internal passengers)
```python
should_stop = elevator_state.going_to_level[current_level] > 0  # only exiting passengers
```
Allow movement when there are outside calls, only force stop for passengers wanting to exit.

### B. Remove MISSED_STOP penalty entirely
Let agent learn without this harsh penalty. It might develop its own stopping strategy.

### C. Prioritized stopping
Only force stop if:
- Passengers inside want to exit (must stop)
- OR elevator is not full AND has been moving in same direction for N steps

### D. Different architecture
- Use attention mechanism to focus on relevant floors
- Use explicit direction state in network
- Use hierarchical RL (high-level: where to go, low-level: how to get there)

---

## Files Modified

- `core/agent/dql_agent/dql_agent.py` - action masking implementation
- `core/agent/utils.py` - reward shaping, masked learning support
- `core/types/reward_type.py` - reward values documentation
- `README.md` - reward system documentation
- `debug_compare.py` - comparison script with detailed breakdown

---

## Conclusion

Action masking solves MOVE_TO_EDGE and MISSED_STOP penalties but introduces a new problem: the elevator gets stuck. The fundamental challenge is that DQL needs to learn a complex stopping policy that the current reward structure doesn't support well.

Next steps should focus on either:
1. Smarter masking that allows movement
2. Different reward structure
3. Different RL approach (e.g., policy gradient, actor-critic)

*Last updated: 2026-01-09*
