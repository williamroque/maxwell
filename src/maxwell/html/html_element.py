import datetime

from dataclasses import dataclass, replace

from maxwell.client.message import Message
from maxwell.client.client import Client
from maxwell.core.properties import Properties
from maxwell.core.coordinates.system import System


@dataclass
class HTMLElementConfig:
    client: Client = None
    system: System = None
    element_name: str = None
    type: str = 'button'
    label: str = 'Button'
    classes: list = None
    width: int = None
    height: int = None


class HTMLElement:
    "The HTML element superclass."

    DEFAULT_CLIENT = None
    DEFAULT_SYSTEM = None
    DEFAULT_HTML_ELEMENT_CONFIG = HTMLElementConfig()

    def __init__(self, point, element_type=None, label=None, html_element_config=None):
        "The HTML element superclass."

        if html_element_config is None:
            html_element_config = self.get_default('html_element_config')

        self.client = html_element_config.client
        if self.client is None:
            default_client = self.get_default('client')

            if default_client is None:
                raise ValueError("Client specification required. Consider setting DEFAULT_CLIENT.")

            self.client = default_client

        if element_type is None:
            element_type = html_element_config.type

        if label is None:
            label = html_element_config.label

        self.system = html_element_config.system
        if self.system is None:
            self.system = self.get_default('system')

        self.element_name = html_element_config.element_name
        if self.element_name is None:
            self.element_name = f'{datetime.datetime.now()}-element'

        classes = html_element_config.classes
        if classes is None:
            classes = []

        self.properties = Properties(
            type = html_element_config.type,
            name = self.element_name,
            point = point,
            label = html_element_config.label,
            width = html_element_config.width,
            height = html_element_config.height,
            classes = classes
        )
        self.properties.set_normalized('point')


    def get_default(self, attribute):
        "Get class default using short form of attribute."

        expanded_attribute = 'DEFAULT_{}'.format(attribute.upper())

        return getattr(self.__class__, expanded_attribute)


    @classmethod
    def set_default(cls, attribute, value):
        "Set class default using short form of attribute."

        expanded_attribute = 'DEFAULT_{}'.format(attribute.upper())

        return setattr(cls, expanded_attribute, value)


    def create(self):
        message = Message(
            self.client,
            'create',
            args = self.properties.get_normalized(self.system)
        )
        message.send()

        return self
