# coding=utf-8

from lxml import etree

from . import exceptions


class Node(object):

    """Node object."""

    def __new__(cls, name, value=None, parent=None, **kwargs):
        """Create object.

        :param name: name of node.
        :param value (optional): text of node.
        :param parent (optional): `etree.Element` instance parent of node.
        """
        element = etree.Element(name, **kwargs)

        if value is not None:
            element.text = value

        if parent is not None:
            parent.append(element)

        return element


class XMLObject(object):

    """XML object."""

    @classmethod
    def from_node(cls, node):
        """Load values from node.

        :param node: `etree.Element` instance.
        """
        if not etree.iselement(node):
            raise ValueError('Is not an `etree.Element` instance.')

        if node.tag != cls.__name__:
            raise exceptions.MalformedEntityError(
                '{} not a "{}" tag.'.format(node.tag, cls.__name__)
            )

    def to_node(self):
        """Serialize to `etree.Element` instance.

        :returns: `etree.Element` instance.
        """
        raise NotImplementedError('Object should contains method `to_node`.')

    def to_dict(self):
        """Serialize to `dict` instance.

        :returns: `dict` instance.
        """
        raise NotImplementedError('Object should contains method `to_dict`.')

    def to_xml(self, pretty_print=False):
        """Serialize to XML string.

        :returns: `str` XML.
        """
        return etree.tostring(self.to_node(), pretty_print=pretty_print)


class Label(XMLObject):

    """Label object."""

    def __init__(self, name, value, content_type='text/html'):
        """Initialization object.

        :param name (optional): label name.
        :param value (optional): label value.
        :param content_type (optional): label content type.
        """
        self.name = name
        self.value = value
        self.content_type = content_type

    @classmethod
    def from_node(cls, node):
        """Load values from node.

        :param node: `etree.Element` instance.
        :returns: `entities.Label` instance.
        """
        super(Label, cls).from_node(node)

        return cls(
            node.attrib['Name'], node.text.strip(), node.attrib.get('Type', '')
        )

    def to_node(self):
        """Serialize to `etree.Element` instance.

        :returns: `etree.Element` instance.
        """
        node = Node(self.__class__.__name__)

        node.attrib['Name'] = self.name
        node.attrib['Type'] = self.content_type
        node.text = etree.CDATA(self.value)

        return node

    def to_dict(self):
        """Serialize to `dict` instance.

        :returns: `dict` instance.
        """
        return {
            'name': self.name, 'value': self.value,
            'content_type': self.content_type
        }


class Field(XMLObject):

    """Field object."""

    def __init__(self, name, value, display_name=None, matching_rule=None):
        """Initialization object.

        :param name (optional): field name.
        :param value (optional): field value.
        :param display_name (optional): field display name.
        :param matching_rule (optional): field matching rule.
        """
        self.name = name
        self.value = value
        self.display_name = display_name or (
            self.name[0].upper() + self.name[1:]
        )
        self.matching_rule = matching_rule

    @classmethod
    def from_node(cls, node):
        """Load values from node.

        :param node: `etree.Element` instance.
        :returns: `entities.Field` instance.
        """
        super(Field, cls).from_node(node)

        return cls(
            node.attrib['Name'], node.text.strip(),
            node.attrib.get('DisplayName'), node.attrib.get('MatchingRule')
        )

    def to_node(self):
        """Serialize to `etree.Element` instance.

        :returns: `etree.Element` instance.
        """
        node = Node(self.__class__.__name__, self.value)

        node.attrib['Name'] = self.name
        node.attrib['DisplayName'] = self.display_name

        if self.matching_rule is not None:
            node.attrib['MatchingRule'] = self.matching_rule

        return node

    def to_dict(self):
        """Serialize to `dict` instance.

        :returns: `dict` instance.
        """
        return {
            'name': self.name, 'value': self.value,
            'display_name': self.display_name,
            'matching_rule': self.matching_rule
        }


class Entity(XMLObject):

    """Entity base object."""

    def __init__(self, name, value, weight=None, icon_url=None,
                 labels=None, fields=None):
        """Initialization object.

        :param name (optional): entity name.
        :param value (optional): entity value.
        :param weight (optional): entity weight.
        :param icon_url (optional): entity icon url.
        :param labels (optional): entity display information.
        :param fields (optional): `dict` of `Field` instance.
        """
        self.name = name
        self.value = value
        self.weight = weight
        self.icon_url = icon_url
        self.fields = fields or []
        self.labels = labels or []

    @classmethod
    def from_node(cls, node):
        """Load values from node.

        :param node: `etree.Element` instance.
        :returns: `entities.Entity` instance.
        """
        super(Entity, cls).from_node(node)

        try:
            name = node.attrib['Type']
        except KeyError:
            raise exceptions.MalformedEntityError('No "Type" attribute.')

        value = node.find('Value')
        if value is None:
            raise exceptions.MalformedEntityError('Missing "Value" tag.')

        value = value.text and value.text.strip()

        instance = cls(name, value)

        weight = node.find('Weight')
        if weight is not None:
            instance.weight = weight.text and weight.text.strip()

        additional_fields = node.find('AdditionalFields')
        if additional_fields is not None:
            for field_node in additional_fields.getchildren():
                field = Field.from_node(field_node)
                instance.fields.append(field)

        labels = node.find('DisplayInformation')
        if labels is not None:
            for label_node in labels.getchildren():
                label = Label.from_node(label_node)
                instance.labels.append(label)

        icon_url = node.find('IconURL')
        if icon_url is not None:
            instance.icon_url = icon_url.text and icon_url.text.strip()

        return instance

    def to_node(self):
        """Serialize to `etree.Element` instance.

        :returns: `etree.Element` instance.
        """
        node = Node(self.__class__.__name__)
        node.attrib['Type'] = self.name

        Node('Value', self.value, parent=node)

        if self.weight is not None:
            Node('Weight', self.weight, parent=node)

        if self.fields:
            additional_fields = Node('AdditionalFields', parent=node)
            for field in self.fields:
                if field.value:
                    additional_fields.append(field.to_node())

        if self.labels:
            labels = Node('DisplayInformation', parent=node)
            for label in self.labels:
                labels.append(label.to_node())

        if self.icon_url:
            Node('IconURL', value=self.icon_url, parent=node)

        return node

    def to_dict(self):
        """Serialize to `dict` instance.

        :returns: `dict` instance.
        """
        result = {}
        result[self.name] = {}
        result[self.name]['value'] = self.value
        result[self.name]['weight'] = self.weight

        result[self.name]['fields'] = {
            field.name.lower(): field.value for field in self.fields
        }

        return result
