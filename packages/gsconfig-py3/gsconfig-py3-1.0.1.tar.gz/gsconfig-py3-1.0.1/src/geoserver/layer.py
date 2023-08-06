# coding: utf-8

from urllib.parse import urljoin

from geoserver.support import ResourceInfo, xml_property, write_bool
from geoserver.style import Style
from geoserver import settings


class _Attribution:
    def __init__(self, title, width, height):
        self.title = title
        self.width = width
        self.height = height


def _read_attribution(node):
    title = node.find("title")
    width = node.find("logoWidth")
    height = node.find("logoHeight")
    if title is not None:
        title = title.text
    if width is not None:
        width = width.text
    if height is not None:
        height = height.text
    return _Attribution(title, width, height)


def _write_attribution(builder, attribution):
    builder.start("attribution", dict())
    if attribution.title is not None:
        builder.start("title", dict())
        builder.data(attribution.title)
        builder.end("title")
    if attribution.width is not None:
        builder.start("logoWidth", dict())
        builder.data(attribution.width)
        builder.end("logoWidth")
    if attribution.height is not None:
        builder.start("logoHeight", dict())
        builder.data(attribution.height)
        builder.end("logoHeight")
    builder.end("attribution")


def _write_style_element(builder, name):
    ws, name = name.split(':') if ':' in name else (None, name)
    builder.start("name", dict())
    builder.data(name)
    builder.end("name")
    if ws:
        builder.start("workspace", dict())
        builder.data(ws)
        builder.end("workspace")


def _write_default_style(builder, name):
    builder.start("defaultStyle", dict())
    if name is not None:
        _write_style_element(builder, name)
    builder.end("defaultStyle")


def _write_alternate_styles(builder, styles):
    builder.start("styles", dict())
    for s in styles:
        builder.start("style", dict())
        _write_style_element(builder, getattr(s, 'fqn', s))
        builder.end("style")
    builder.end("styles")


class Layer(ResourceInfo):
    def __init__(self, catalog, name):
        super(Layer, self).__init__()
        self.catalog = catalog
        self.name = name

    resource_type = "layer"
    save_method = settings.PUT

    @property
    def href(self):
        return urljoin(
            self.catalog.service_url,
            "layer/{}.xml".format(self.name)
        )

    @property
    def resource(self):
        if self.dom is None:
            self.fetch()
        name = self.dom.find("resource/name").text
        return self.catalog.get_resource(name)

    @property
    def default_style(self):
        if 'default_style' in self.dirty:
            return self.dirty['default_style']
        if self.dom is None:
            self.fetch()
        element = self.dom.find("defaultStyle")
        # aborted data uploads can result in no default style
        return self._resolve_style(element) if element is not None else None

    @default_style.setter
    def default_style(self, style):
        if isinstance(style, Style):
            style = style.fqn
        self.dirty["default_style"] = style

    @property
    def styles(self):
        if "alternate_styles" in self.dirty:
            return self.dirty["alternate_styles"]
        if self.dom is None:
            self.fetch()
        styles_list = self.dom.findall("styles/style")
        return filter(None, [self._resolve_style(s) for s in styles_list])

    @styles.setter
    def styles(self, styles):
        self.dirty["alternate_styles"] = styles

    def _resolve_style(self, element):
        # instead of using name or the workspace element (which only appears
        # in >=2.4), just use the atom link href attribute
        atom_link = [n for n in element.getchildren() if 'href' in n.attrib]
        if atom_link:
            style_workspace_url = atom_link[0].attrib.get("href")
            return self.catalog.get_style_by_url(style_workspace_url)

    @property
    def attribution(self):
        return self.attribution_object.title

    @attribution.setter
    def attribution(self, text):
        self.dirty["attribution"] = _Attribution(
            text,
            self.attribution_object.width,
            self.attribution_object.height
        )
        assert self.attribution_object.title == text

    attribution_object = xml_property("attribution", _read_attribution)
    enabled = xml_property("enabled", lambda x: x.text == "true")
    advertised = xml_property("advertised", lambda x: x.text == "true",
                              default=True)

    writers = {
        'attribution': _write_attribution,
        'enabled': write_bool("enabled"),
        'advertised': write_bool("advertised"),
        'default_style': _write_default_style,
        'alternate_styles': _write_alternate_styles
    }
