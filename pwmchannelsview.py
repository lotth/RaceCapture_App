import kivy
kivy.require('1.8.0')

from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.scrollview import ScrollView
from kivy.app import Builder
from fieldlabel import FieldLabel
from mappedspinner import MappedSpinner
from utils import *

Builder.load_file('pwmchannelsview.kv')
    
class PwmOutputModeSpinner(MappedSpinner):
    def __init__(self, **kwargs):
        super(PwmOutputModeSpinner, self).__init__(**kwargs)
        self.setValueMap({0:'Analog', 1:'Frequency'}, 'Frequency')

class PwmLoggingModeSpinner(MappedSpinner):
    def __init__(self, **kwargs):
        super(PwmLoggingModeSpinner, self).__init__(**kwargs)
        self.setValueMap({0:'Period', 1:'Duty Cycle', 2:'Volts'}, 'Duty Cycle')
    
class AnalogPulseOutputChannel(BoxLayout):
    channelConfig = None
    channels = None    
    def __init__(self, **kwargs):
        super(AnalogPulseOutputChannel, self).__init__(**kwargs)
        kvFind(self, 'rcid', 'sr').bind(on_sample_rate = self.on_sample_rate)
        kvFind(self, 'rcid', 'chanId').bind(on_channel = self.on_channel)

    def on_channel(self, instance, value):
        if self.channelConfig:
            self.channelConfig.channelId = self.channels.getIdForName(value)

    def on_sample_rate(self, instance, value):
        if self.channelConfig:
            self.channelConfig.sampleRate = value

    def on_output_mode(self, instance, value):
        if self.channelConfig:
            self.channelConfig.outputMode = instance.getValueFromKey(value)

    def on_logging_mode(self, instance, value):
        if self.channelConfig:
            self.channelConfig.loggingMode = instance.getValueFromKey(value)
    
    def on_startup_duty_cycle(self, instance, value):
        if self.channelConfig:
            self.channelConfig.loggingMode = int(value)
    
    def on_startup_period(self, instance, value):
        if self.channelConfig:
            self.channelConfig.startupPeriod = int(value)
    
    def on_voltage_scaling(self, instance, value):
        if self.channelConfig:
            self.channelConfig.voltageScaling = float(value)
    
    def on_config_updated(self, channelConfig, channels ):
        channelSpinner = kvFind(self, 'rcid', 'chanId')
        channelSpinner.setValue(channels.getNameForId(channelConfig.channelId))

        sampleRateSpinner = kvFind(self, 'rcid', 'sr')
        sampleRateSpinner.setValue(channelConfig.sampleRate)
        
        voltageScalingField = kvFind(self, 'rcid', 'vScal')
        voltageScalingField.text =  '{:.3g}'.format(channelConfig.voltageScaling)
        
        startupDutyCycle = kvFind(self, 'rcid', 'dutyCycle')
        startupDutyCycle.text = str(channelConfig.startupDutyCycle)
        
        startupPeriod = kvFind(self, 'rcid', 'period')
        startupPeriod.text = str(channelConfig.startupPeriod)
        
        outputModeSpinner = kvFind(self, 'rcid', 'outputMode')
        outputModeSpinner.setFromValue(channelConfig.outputMode)
        
        loggingModeSpinner = kvFind(self, 'rcid', 'loggingMode')
        loggingModeSpinner.setFromValue(channelConfig.loggingMode)
        
        self.channelConfig = channelConfig
        self.channels = channels
        
class AnalogPulseOutputChannelsView(BoxLayout):
    editors = []
    def __init__(self, **kwargs):
        self.register_event_type('on_config_updated')
        self.channelCount = kwargs['channelCount']
        self.channels = kwargs['channels']
        
        super(AnalogPulseOutputChannelsView, self).__init__(**kwargs)
        accordion = Accordion(orientation='vertical', size_hint=(1.0, None), height=100 * self.channelCount)
    
        # add button into that grid
        for i in range(self.channelCount):
            channel = AccordionItem(title='Pulse / Analog Output ' + str(i + 1))
            editor = AnalogPulseOutputChannel(id='pwm' + str(i))
            channel.add_widget(editor)
            accordion.add_widget(channel)
            self.editors.append(editor)
    
        #create a scroll view, with a size < size of the grid
        sv = ScrollView(size_hint=(1.0,1.0), do_scroll_x=False)
        sv.add_widget(accordion)
        self.add_widget(sv)

    def on_config_updated(self, rcpCfg):
        pwmCfg = rcpCfg.pwmConfig
        channelCount = pwmCfg.channelCount

        for i in range(channelCount):
            editor = self.editors[i]
            pwmChannel = pwmCfg.channels[i]
            editor.on_config_updated(pwmChannel, self.channels)
