from enum import Enum
from typing import Optional
from pynput.mouse import Button, Controller
from robot.api.deco import keyword
from RPA.core.helpers import delay
from RPA.core.geometry import Point
from RPA.Desktop.keywords import LibraryContext


class Action(Enum):
    """Possible mouse click actions."""

    click = 0
    left_click = 0
    double_click = 1
    triple_click = 2
    right_click = 3


def to_action(value):
    """Convert value to Action enum."""
    if isinstance(value, Action):
        return value

    sanitized = str(value).lower().strip().replace(" ", "_")
    try:
        return Action[sanitized]
    except KeyError:
        raise ValueError(f"Unknown mouse action: {value}")


def to_button(value):
    """Convert value to Button enum."""
    if isinstance(value, Button):
        return value

    sanitized = str(value).lower().strip().replace(" ", "_")
    try:
        return Button[sanitized]
    except KeyError:
        raise ValueError(f"Unknown mouse button: {value}")


class MouseKeywords(LibraryContext):
    """Keywords for sending inputs through an (emulated) mouse."""

    def __init__(self, ctx):
        super().__init__(ctx)
        self._mouse = Controller()

    def _move(self, point: Point) -> None:
        """Move mouse to given point."""
        # TODO: Clamp to screen dimensions?
        self.logger.info("Moving mouse to (%d, %d)", *point)
        self._mouse.position = point.as_tuple()

    def _click(
        self, action: Action = Action.click, point: Optional[Point] = None
    ) -> None:
        """Perform defined mouse action, and optionally move to given point first."""
        action = to_action(action)

        if point:
            self._move(point)

        self.logger.info("Performing mouse action: %s", action)

        if action is Action.click:
            self._mouse.click(Button.left)
        elif action is Action.double_click:
            self._mouse.click(Button.left, 2)
        elif action is Action.triple_click:
            self._mouse.click(Button.left, 3)
        elif action is Action.right_click:
            self._mouse.click(Button.right)
        else:
            # TODO: mypy should handle enum exhaustivity validation
            raise ValueError(f"Unsupported action: {action}")

    @keyword
    def click(
        self,
        locator: Optional[str] = None,
        action: Action = Action.click,
    ) -> None:
        """Click at the element indicated by locator."""
        action = to_action(action)
        if locator:
            match = self.find_element(locator)
            self._click(action, match)
        else:
            self._click(action)

    @keyword
    def click_with_offset(
        self,
        locator: Optional[str] = None,
        x: int = 0,
        y: int = 0,
        action: Action = Action.click,
    ) -> None:
        """Click at a given pixel offset from the given locator."""
        action = to_action(action)
        if locator:
            match = self.find_element(locator)
            match.offset(x, y)
            self._click(action, match)
        else:
            self._mouse.move(int(x), int(y))
            self._click(action)

    @keyword
    def get_mouse_position(self) -> Point:
        """Get current mouse position in pixel coordinates."""
        x, y = self._mouse.position
        return Point(x, y)

    @keyword
    def move_mouse_to(self, locator: str) -> None:
        """Move mouse to given coordinates."""
        match = self.find_element(locator)
        self._move(match)

    @keyword
    def press_mouse_button(self, button: Button = Button.left) -> None:
        """Press down mouse button and keep it pressed."""
        button = to_button(button)
        self._mouse.press(button)

    @keyword
    def release_mouse_button(self, button: Button = Button.left) -> None:
        """Release mouse button that was previously pressed."""
        button = to_button(button)
        self._mouse.release(button)

    @keyword
    def drag_and_drop(
        self,
        source: str,
        destination: str,
        start_delay: float = 2.0,
        end_delay: float = 0.5,
    ) -> None:
        """Drag mouse from source to destination while holding a button."""
        src = self.find_element(source)
        dst = self.find_element(destination)

        self.logger.info("Dragging from (%d, %d) to (%d, %d)", *src, *dst)

        self._move(src)
        self.press_mouse_button()
        delay(start_delay)
        self._move(dst)
        delay(end_delay)
        self.release_mouse_button()