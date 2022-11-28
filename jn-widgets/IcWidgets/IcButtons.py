import ipywidgets as widgets
from ipywidgets import interact
import logging
_logger = logging.getLogger("ipywidgetsButton")
_logger.setLevel(logging.DEBUG)

_ch = logging.StreamHandler()
_ch.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_ch.setFormatter(formatter)
_logger.addHandler(_ch)


default_switch_values = ["inactive", "active"]


class DisplayedStatus(widgets.Select):
    def __init__(self, 
                 options=default_switch_values, 
                 value=default_switch_values[0],
                 *args, 
                 **kwargs):
        super().__init__(options=options,
                         value=value,
                         *args, 
                         **kwargs)

widgets.ToggleButton

class UIButton(widgets.Button, widgets.ValueWidget):
    def __init__(self,
                 name="UIButton", 
                 values = default_switch_values,
                 default_value_index = 0,
                 logger=_logger, **kwargs):
        super().__init__(**kwargs)
        self.logger = logger
        self.description = name
        self.__name = name
        self.__values = values
        self.__value_index = default_value_index
        self.__values_len = len(values)
        self.value = values[default_value_index]
        self.__external_on_click_callback = None
        self.on_click(self.__on_click_callback)
        
    def set_callback(self, callback):
        self.__external_on_click_callback = callback
        self.on_click(self.__on_click_callback)
        
    def __internal_on_click_callback(self):
        # self.logger.debug(f"{self.__name} on_click_callback executing.")
        
        if self.__value_index < (self.__values_len - 1):
            self.__value_index += 1
        else:
            self.__value_index = 0
            
        self.value = self.__values[self.__value_index]
        self.logger.debug(f"{self.__name} on_click_callback executed with new value {self.value}.")       
        
    def __on_click_callback(self, btn):
        self.__internal_on_click_callback()
        if self.__external_on_click_callback:
            self.__external_on_click_callback(btn)
            
            