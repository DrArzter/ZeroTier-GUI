import json
import os
from pathlib import Path

class UserState:
    def __init__(self):
        self.config_dir = Path.home() / '.config' / 'zerotier-gui'
        self.config_file = self.config_dir / 'state.json'
        self.state = self._load_state()

    def _load_state(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_state(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    @property
    def my_id(self):
        return self.state.get('my_id')

    @my_id.setter
    def my_id(self, value):
        self.state['my_id'] = value
        self._save_state()

    @property
    def is_me(self, member_id):
        return self.my_id == member_id

user_state = UserState()