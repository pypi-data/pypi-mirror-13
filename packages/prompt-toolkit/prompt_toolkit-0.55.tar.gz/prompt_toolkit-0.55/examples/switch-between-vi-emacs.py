from prompt_toolkit import prompt
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.keys import Keys
from pygments.token import Token

def run():
    vi_mode_enabled = False

    # Create a set of key bindings that have Vi mode enabled if the
    # ``vi_mode_enabled`` is True..
    manager = KeyBindingManager.for_prompt(
        enable_vi_mode=Condition(lambda cli: vi_mode_enabled))

    # Add an additional key binding for toggling this flag.
    @manager.registry.add_binding(Keys.F4)
    def _(event):
        " Toggle between Emacs and Vi mode. "
        nonlocal vi_mode_enabled
        vi_mode_enabled = not vi_mode_enabled

    def get_bottom_toolbar_tokens(cli):
        " Display the current input mode. "
        text = 'Vi' if vi_mode_enabled else 'Emacs'
        return [
            (Token.Toolbar, ' [F4] %s ' % text)
        ]

    prompt('> ', key_bindings_registry=manager.registry,
           get_bottom_toolbar_tokens=get_bottom_toolbar_tokens)

run()
