import xml.etree.ElementTree as XML
from jenkins_jobs.errors import MissingAttributeError


def hidden_param(parser, xml_parent, data):

    """yaml: hidden
    A hidden parameter.

    :arg str name: the name of the parameter
    :arg str default: the default value of the parameter (optional)
    :arg str description: a description of the parameter (optional)

    Example::

      parameters:
        - hidden:
            name: FOO
            default: bar
            description: "A parameter named FOO, defaults to 'bar'."
    """

    h_p = XML.SubElement(xml_parent,
                         'com.wangyin.parameter.WHideParameterDefinition')
    h_p.set('plugin', 'hidden-parameter@0.0.4')


    try:
        name = data['name']
    except KeyError:
        raise MissingAttributeError('name')

    XML.SubElement(h_p, 'name').text = name
    XML.SubElement(h_p, 'default').text = data.get('default', '')
    XML.SubElement(h_p, 'description').text = data.get('description', '')
