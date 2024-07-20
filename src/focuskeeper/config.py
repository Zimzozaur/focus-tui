from typing import Literal

import yaml

from focuskeeper.app_paths import AppPaths


class AppConfig(AppPaths):
    """Class used to manage config.yaml"""

    def forbiden_sound_names(self) -> set:
        """Return set of names that are used by app
        and user is not allowed to use
        """
        return {
            'Unfa_Woohoo', 'Unfa_Landing',
            'Unfa_Braam', 'Unfa_Acid_Bassline',
            'Woodpecker_Forest', 'Mexican_Forest',
        }

    def get_used_sound(
            self,
            sound_type: Literal['alarm', 'signal', 'ambient']
    ) -> dict:
        """Get from config.yaml name and path of chosen sound_type"""
        with open(self.config_file_path, 'r') as file:
            return yaml.safe_load(file)['used_sounds'][sound_type]

    def update_used_sound(
            self,
            sound_type: Literal['alarm', 'signal', 'ambient'],
            name: str,
            path: str
    ) -> None:
        """Update config.yaml with sound name and path"""
        with open(self.config_file_path) as file:
            yaml_file = yaml.safe_load(file)

        yaml_file['used_sounds'][sound_type]['name'] = name
        yaml_file['used_sounds'][sound_type]['path'] = path

        with open(self.config_file_path, 'w') as file:
            yaml.dump(yaml_file, file, sort_keys=False)

    def is_sound_in_config(self, sound_type: Literal['alarm', 'ambient'], sound_name: str) -> None:
        with open(self.config_file_path) as file:
            yaml_file = yaml.safe_load(file)

        if sound_type == 'alarm':
            alarm = yaml_file['used_sounds']['alarm']['name'] == sound_name
            signal = yaml_file['used_sounds']['signal']['name'] == sound_name
            return alarm or signal
        else:
            return yaml_file['used_sounds']['ambient']['name'] == sound_name

    def change_sound_name_if_in_config(self, sound_type: Literal['alarm', 'ambient'], old_name: str,  new_name: str) -> None:
        with open(self.config_file_path) as file:
            yaml_file = yaml.safe_load(file)

        if sound_type == 'alarm':
            alarm = yaml_file['used_sounds']['alarm']['name']
            signal = yaml_file['used_sounds']['signal']['name']
            if alarm == old_name:
                yaml_file['used_sounds']['alarm']['name'] = new_name
            if signal == old_name:
                yaml_file['used_sounds']['signal']['name'] = new_name
        else:
            ambient = yaml_file['used_sounds']['ambient']['name']
            if ambient != new_name:
                yaml_file['used_sounds']['ambient']['name'] = new_name

        with open(self.config_file_path, 'w') as file:
            yaml.dump(yaml_file, file, sort_keys=False)

    def change_sound_to_default(self, sound_type: Literal['alarm', 'ambient'], old_name_with_extension) -> None:
        with open(self.config_file_path) as file:
            yaml_file = yaml.safe_load(file)

        if sound_type == 'alarm':
            alarm = yaml_file['used_sounds']['alarm']['name']
            signal = yaml_file['used_sounds']['signal']['name']
            if alarm == old_name_with_extension:
                yaml_file['used_sounds']['alarm']['name'] = self.default_alarm_name
                yaml_file['used_sounds']['alarm']['path'] = str(self.sounds_path)
            if signal == old_name_with_extension:
                yaml_file['used_sounds']['signal']['name'] = self.default_signal_name
                yaml_file['used_sounds']['signal']['path'] = str(self.sounds_path)
        else:
            ambient = yaml_file['used_sounds']['ambient']['name']
            if ambient == old_name_with_extension:
                yaml_file['used_sounds']['ambient']['name'] = self.default_ambient_name
                yaml_file['used_sounds']['ambient']['path'] = str(self.ambiences_path)

        with open(self.config_file_path, 'w') as file:
            yaml.dump(yaml_file, file, sort_keys=False)

