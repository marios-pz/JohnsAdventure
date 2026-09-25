extends SceneTree
## Headless smoke test: level wiring, data integrity and the full quest line.
## Run: godot --headless --path . -s tests/smoke_test.gd   (exit code = number of failures)

var failures := 0


func check(ok: bool, what: String) -> void:
	if not ok:
		failures += 1
		printerr("FAIL: ", what)


func _initialize() -> void:
	await process_frame  # autoloads ready
	var quests: Node = root.get_node("Quests")
	var cutscene: Node = root.get_node("Cutscene")
	var levels := {}
	for file in DirAccess.get_files_at("res://levels"):
		if file.ends_with(".tscn"):
			levels[file.get_basename()] = load("res://levels/" + file).instantiate()

	var npcs_by_level := {}
	var enemies_by_level := {}
	for id in levels:
		var level: Node = levels[id]
		check(level.level_id == id, "%s: level_id is '%s'" % [id, level.level_id])
		npcs_by_level[id] = level.find_children("*", "NPC", true, false).map(func(n: Node) -> String: return n.id)
		enemies_by_level[id] = level.find_children("*", "Enemy", true, false).map(func(n: Node) -> String: return n.kind)
		for exit in level.find_children("*", "Exit", true, false):
			if exit.target == "credits":
				continue
			check(levels.has(exit.target), "%s: exit to unknown level '%s'" % [id, exit.target])
			if levels.has(exit.target):
				check(levels[exit.target].has_node("Spawns/" + id),
						"%s -> %s: no spawn named '%s' there" % [id, exit.target, id])
			# walking out of a spawn must not immediately walk into a walk-in exit
			if exit.prompt == "":
				var box: Rect2 = exit.get_node("Shape").shape.get_rect()
				box.position += exit.position + exit.get_node("Shape").position
				for spawn in level.get_node("Spawns").get_children():
					check(not box.grow(40).has_point(spawn.position),
							"%s: spawn '%s' is inside the exit to %s" % [id, spawn.name, exit.target])

	for id in cutscene._cutscenes:
		var data: Dictionary = cutscene._cutscenes[id]
		check(levels.has(data.level), "cutscene %s: unknown level %s" % [id, data.level])
		check(data.after_step == "" or quests._step_index.has(data.after_step), "cutscene %s: unknown step" % id)

	var tips: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/tutorial.json")).tips
	for tip in tips:
		check(tip.level == "" or levels.has(tip.level), "tutorial %s: unknown level %s" % [tip.id, tip.level])
		check(tip.after_step == "" or quests._step_index.has(tip.after_step), "tutorial %s: unknown step" % tip.id)
		check(tip.done_on in ["move", "interact", "weapon", "attack", "combo", "dash", "heal", "inventory"],
				"tutorial %s: unknown action %s" % [tip.id, tip.done_on])

	var dialogue: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/dialogue.json"))
	for npc in dialogue:
		if npc != "_doc":
			for entry in dialogue[npc]:
				check(entry.after == "" or quests._step_index.has(entry.after), "dialogue %s: unknown step %s" % [npc, entry.after])

	# Play the story: every step must be completable in its level with what that level contains.
	quests.from_dict({})
	for quest in quests.quest_names():
		for step: Dictionary in quests.steps_of(quest):
			check(levels.has(step.level), "step '%s': unknown level" % step.name)
			match step.type:
				"interact":
					check(step.target in npcs_by_level.get(step.level, []), "step '%s': no NPC %s in %s" % [step.name, step.target, step.level])
					quests.enter_level(step.level)
					await process_frame
					check(quests.notify_interact(step.target), "step '%s': interaction did not complete it" % step.name)
				"kill":
					check(step.target in enemies_by_level.get(step.level, []), "step '%s': no %s in %s" % [step.name, step.target, step.level])
					quests.enter_level(step.level)  # no enemies are alive in this headless tree
				"reach":
					quests.enter_level(step.level)
			await process_frame
			check(quests.is_done(step.name), "step '%s' did not complete" % step.name)
		check(quests.current_step(quest).is_empty(), "quest %s not finished" % quest)

	for level in levels.values():
		level.free()
	print("smoke test: %d failure(s)" % failures)
	quit(failures)
