extends Node
## Quest progression (autoload "Quests").
##
## Quests are defined in data/quests.json as ordered steps. Only the current
## step of each quest can complete, which keeps the story strictly linear.
## Step types:
##   reach    - John enters `level`
##   interact - John talks to the NPC whose id is `target` in `level`
##   kill     - no living enemy of kind `target` is left in `level`

signal step_completed(quest: String, step: String)
signal step_started(quest: String, step: String)
signal quest_finished(quest: String)

const DATA_PATH := "res://data/quests.json"

var _quests: Dictionary = {}     ## name -> {xp, steps}
var _progress: Dictionary = {}   ## name -> index of the current step
var _step_index: Dictionary = {} ## step name -> [quest, index], for is_done()
var _level := ""


func _ready() -> void:
	_quests = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	for quest in _quests:
		var steps: Array = _quests[quest].steps
		for i in steps.size():
			_step_index[steps[i].name] = [quest, i]
	from_dict({})


## True when `step` has been completed. The empty step "" always counts as done,
## so `after: ""` in data files means "from the start".
func is_done(step: String) -> bool:
	if step == "":
		return true
	if not _step_index.has(step):
		push_warning("Unknown quest step: %s" % step)
		return false
	var at: Array = _step_index[step]
	return _progress[at[0]] > at[1]


## Current step of `quest`, or {} once the quest is finished.
func current_step(quest: String) -> Dictionary:
	var steps: Array = _quests[quest].steps
	var i: int = _progress[quest]
	return steps[i] if i < steps.size() else {}


func quest_names() -> Array:
	return _quests.keys()


func steps_of(quest: String) -> Array:
	return _quests[quest].steps


func enter_level(level_id: String) -> void:
	_level = level_id
	refresh()


## Returns true when the interaction completed a step (the caller then stays quiet:
## a cutscene usually takes over).
func notify_interact(target: String) -> bool:
	for quest in _quests:
		var step := current_step(quest)
		if step.get("type") == "interact" and step.target == target and step.level == _level:
			_complete(quest)
			return true
	return false


## Re-checks reach/kill steps. Deferred, so nodes revealed by the step that
## just completed (e.g. the boss) are in the tree before we count enemies.
func refresh() -> void:
	_refresh.call_deferred()


func _refresh() -> void:
	if Cutscene.holding:
		return  # the enemies to kill have not appeared yet; the level refreshes on release
	for quest in _quests:
		var step := current_step(quest)
		if step.is_empty() or step.level != _level:
			continue
		if step.type == "reach" or (step.type == "kill" and _alive(step.target) == 0):
			_complete(quest)


func _alive(kind: String) -> int:
	var count := 0
	for enemy in get_tree().get_nodes_in_group("enemies"):
		if enemy.kind == kind:
			count += 1
	return count


func _complete(quest: String) -> void:
	var step := current_step(quest)
	_progress[quest] += 1
	step_completed.emit(quest, step.name)
	var next := current_step(quest)
	if next.is_empty():
		Game.add_experience(_quests[quest].xp)
		quest_finished.emit(quest)
	else:
		step_started.emit(quest, next.name)
	refresh()


func to_dict() -> Dictionary:
	return _progress.duplicate()


func from_dict(d: Dictionary) -> void:
	for quest in _quests:
		_progress[quest] = int(d.get(quest, 0))
