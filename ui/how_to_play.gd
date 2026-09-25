extends PanelContainer
## "How to Play" card: controls for keyboard/mouse and controller plus the core
## combat tips. Shared by the title screen and the pause menu.

signal closed

const ROWS := [
	["Move", "W A S D", "Left stick"],
	["Aim", "Mouse", "Right stick"],
	["Attack", "Left click", "X / RT"],
	["Dash", "Shift", "B / RB"],
	["Talk, open, use", "Space", "A"],
	["Drink potion", "Q", "Y"],
	["Inventory, stats, quests", "E", "View"],
	["Pause", "Esc / P", "Menu"],
	["Fullscreen", "F11", "-"],
]
const TIPS := [
	"Press attack three times in rhythm: the third hit is a finisher.",
	"Enemies flash red just before they strike. Dash away or hit them first to stagger them.",
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
