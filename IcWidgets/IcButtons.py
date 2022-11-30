import logging
from threading import Timer
import ipywidgets as widgets
from IPython.display import display
from utils.loggers import Logger, OutputWidgetHandler

logging_handler = OutputWidgetHandler()
_logger = Logger(logger_name="IcButton", log_handler=logging_handler, logging_level=logging.DEBUG)
default_switch_values = ["inactive", "active"]


class DigtalSwitch:
    def __init__(self, 
                 button_name="DigtalSwitch", 
                 status_name="DisplayedSatus",
                 switch_values=default_switch_values, 
                 value_index=0, 
                 stauts_setback_delay=2,
                 logger=_logger):
        self.__button_name = button_name
        self.__status_name = status_name
        self.__switch_values = switch_values
        self.logger = logger
        self.__displayed_status = DisplayedStatus(options=self.__switch_values, 
                                                  value=self.__switch_values[0])
        self.__ui_button = UIButton(name=button_name, 
                                    values=switch_values, 
                                    default_value_index=value_index, 
                                    internal_timer_callback=self.__on_clink_timer_callback,
                                    logger=self.logger)
        self.__status_btn_jsdlink = widgets.dlink((self.__displayed_status, "value"), (self.__ui_button, "value"))
        self.__stauts_setback_delay = stauts_setback_delay
        self.__on_click_timer = Timer(self.__stauts_setback_delay, self.__setback_status)
        self.__displayed_switch = self.__display_switch()
        
    @property
    def displayed_switch(self):
        return self.__displayed_switch
        
    def __display_switch(self):
        status_label = widgets.Label(self.__status_name)
        displayed_status = widgets.VBox([status_label, self.__displayed_status])
        return widgets.HBox([self.__ui_button, displayed_status])
    
    def unlink_status_btn(self):
        self.__status_btn_jsdlink.unlink()
        
    def link_status_btn(self):
        self.__status_btn_jsdlink.link()
    
    @property
    def displayed_status(self):
        return self.__displayed_status
    
    @property
    def ui_button(self):
        return self.__ui_button
    
    def __setback_status(self):
        self.__ui_button.value = self.__displayed_status.value
        self.__on_click_timer.cancel()        
        self.__on_click_timer = Timer(self.__stauts_setback_delay, self.__setback_status)
        
    def __on_clink_timer_callback(self, button_value):
        self.logger.debug(f"Triggered {self.__button_name} button on_clink_timer_callback with button value: {button_value}.")
        self.__on_click_timer.start()
        

                

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


class UIButton(widgets.Button, widgets.ValueWidget):
    def __init__(self,
                 name="UIButton", 
                 values = default_switch_values,
                 default_value_index = 0,
                 internal_timer_callback=None,
                 logger=_logger, **kwargs):
        super().__init__(**kwargs)
        self.logger = logger
        self.description = name
        self.__name = name
        self.__values = values
        self.__value_index = default_value_index
        self.__values_len = len(values)
        self.value = values[default_value_index]
        self.__internal_timer_callback = internal_timer_callback
        self.__external_on_click_callback = None
        self.__external_on_change_callback = None
        self.on_click(self.__on_click_callback)
        self.observe(self.__on_change_callback)
        
    def set_on_click_callback(self, callback):
        self.__external_on_click_callback = callback
        self.on_click(self.__on_click_callback)
        
    def set_on_change_callback(self, callback):
        self.__external_on_change_callback = callback
        self.observe(self.__on_change_callback)
        
    def __internal_on_click_callback(self):
        # self.logger.debug(f"{self.__name} on_click_callback executing.")
        
        if self.__value_index < (self.__values_len - 1):
            self.__value_index += 1
        else:
            self.__value_index = 0
            
        self.value = self.__values[self.__value_index]
        self.logger.debug(f"{self.__name} on_click_callback executed with new value {self.value}.")   
        
        if self.__internal_timer_callback:
            self.__internal_timer_callback(self.value)    
        
    def __on_click_callback(self, btn):
        self.__internal_on_click_callback()
        if self.__external_on_click_callback:
            self.__external_on_click_callback(btn)
            
    def __internal_on_change_callback(self):
        self.logger.debug(f"{self.__name} on_change_callback executed with new value {self.value}.")
        
    def __on_change_callback(self, change):
        self.__internal_on_change_callback()
        if self.__external_on_change_callback:
            self.__external_on_change_callback(change)
            
            