extends PanelContainer
## "How to Play" card: controls for keyboard/mouse and controller plus the core
## combat tips. Opened from the pause menu.

signal closed

const ROWS := [
	["Move", "W A S D", "Left stick"],
	["Aim", "Mouse", "Right stick"],
	["Attack", "Left click", "X / RT"],
	["Dash", "C", "RB"],
	["Parry", "Shift", "LB"],
	["Talk, open, use", "Space", "A"],
	["Back / close", "Esc", "B"],
	["Drink potion", "Q", "D-pad up"],
	["Inventory, stats, quests", "E", "Y"],
	["Pause", "Esc / P", "Menu"],
	["Fullscreen", "F11", "-"],
]
const TIPS := [
	"Press attack three times in rhythm: the third hit knocks enemies back.",
	"Enemies flash red just before they strike. Dash away, hit them first to stagger them, or parry the strike to stun them.",
	"Dashing makes you invulnerable, passes through enemies and cancels your attack.",
	"Level up to earn upgrade points and spend them in the inventory.",
]


func _ready() -> void:
	var text := "[table=3][cell][b]Action[/b][/cell][cell][b]Keyboard & mouse[/b][/cell][cell][b]Controller[/b][/cell]"
	for row in ROWS:
		text += "[cell]%s   [/cell][cell]%s   [/cell][cell]%s[/cell]" % row
	text += "[/table]\n\n"
	for tip in TIPS:
		text += "- %s\n" % tip
	%HowToPlayText.text = text
	%HowToPlayClose.pressed.connect(close)


func open() -> void:
	show()
	%HowToPlayClose.grab_focus()


func close() -> void:
	hide()
	closed.emit()
