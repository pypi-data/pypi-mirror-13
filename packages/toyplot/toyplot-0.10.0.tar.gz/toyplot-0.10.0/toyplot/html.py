# Copyright 2014, Sandia Corporation. Under the terms of Contract
# DE-AC04-94AL85000 with Sandia Corporation, the U.S. Government retains certain
# rights in this software.

from __future__ import division

from multipledispatch import dispatch
import collections
import copy
import itertools
import json
import numbers
import numpy
import string
import toyplot.axes
import toyplot.canvas
import toyplot.color
import toyplot.compatibility
import toyplot.mark
import uuid
import xml.etree.ElementTree as xml

try:
    import HTMLParser
except:
    import html.parser as HTMLParser

class _NumpyJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, numpy.generic):
            return numpy.asscalar(obj)
        return json.JSONEncoder.default(self, obj)


_export_data_tables = string.Template("""
(function()
{
  var data_tables = $data_tables;

  function save_csv(data_table)
  {
    var uri = "data:text/csv;charset=utf-8,";
    uri += data_table.names.join(",") + "\\n";
    for(var i = 0; i != data_table.data[0].length; ++i)
    {
      for(var j = 0; j != data_table.data.length; ++j)
      {
        if(j)
          uri += ",";
        uri += data_table.data[j][i];
      }
      uri += "\\n";
    }
    uri = encodeURI(uri);

    var link = document.createElement("a");
    if(typeof link.download != "undefined")
    {
      link.href = uri;
      link.style = "visibility:hidden";
      link.download = data_table.filename + ".csv";

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
    else
    {
      window.open(uri);
    }
  }

  function open_popup(data_table)
  {
    return function(e)
    {
      var popup = document.querySelector("#$root_id .toyplot-mark-popup");
      popup.querySelector(".toyplot-mark-popup-title").innerHTML = data_table.title;
      popup.querySelector(".toyplot-mark-popup-save-csv").onclick = function() { popup.style.visibility = "hidden"; save_csv(data_table); }
      popup.style.left = (e.clientX - 50) + "px";
      popup.style.top = (e.clientY - 20) + "px";
      popup.style.visibility = "visible";
      e.stopPropagation();
      e.preventDefault();
    }

  }

  for(var i = 0; i != data_tables.length; ++i)
  {
    var data_table = data_tables[i];
    var event_target = document.querySelector("#" + data_table.id);
    event_target.oncontextmenu = open_popup(data_table);
  }
})();
""")

_show_mouse_coordinates = string.Template("""
(function()
{
  var axes = $cartesian_axes;

  function sign(x)
  {
    return x < 0 ? -1 : x > 0 ? 1 : 0;
  }

  function _mix(a, b, amount)
  {
    return ((1.0 - amount) * a) + (amount * b);
  }

  function _log(x, base)
  {
    return Math.log(Math.abs(x)) / Math.log(base);
  }

  function _in_range(a, x, b)
  {
    var left = Math.min(a, b);
    var right = Math.max(a, b);
    return left <= x && x <= right;
  }

  function to_domain(projection, range)
  {
    for(var i = 0; i != projection.length; ++i)
    {
      var segment = projection[i];
      if(_in_range(segment.range.bounds.min, range, segment.range.bounds.max))
      {
        if(segment.scale == "linear")
        {
          var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
          return _mix(segment.domain.min, segment.domain.max, amount)
        }
        else if(segment.scale[0] == "log")
        {
          var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
          var base = segment.scale[1];
          return sign(segment.domain.min) * Math.pow(base, _mix(_log(segment.domain.min, base), _log(segment.domain.max, base), amount));
        }
      }
    }
  }

  // Compute mouse coordinates relative to a DOM object, with thanks to d3js.org, where this code originated.
  function d3_mousePoint(container, e)
  {
    if (e.changedTouches) e = e.changedTouches[0];
    var svg = container.ownerSVGElement || container;
    if (svg.createSVGPoint) {
      var point = svg.createSVGPoint();
      point.x = e.clientX, point.y = e.clientY;
      point = point.matrixTransform(container.getScreenCTM().inverse());
      return [point.x, point.y];
    }
    var rect = container.getBoundingClientRect();
    return [e.clientX - rect.left - container.clientLeft, e.clientY - rect.top - container.clientTop];
  };

  function display_coordinates(e)
  {
    var dom_axes = e.currentTarget.parentElement;
    var data = axes[dom_axes.id];

    point = d3_mousePoint(e.target, e);
    var x = Number(to_domain(data["x"], point[0])).toFixed(2);
    var y = Number(to_domain(data["y"], point[1])).toFixed(2);

    var coordinates = dom_axes.querySelectorAll(".toyplot-coordinates");
    for(var i = 0; i != coordinates.length; ++i)
    {
      coordinates[i].style.visibility = "visible";
      coordinates[i].querySelector("text").textContent = "x=" + x + " y=" + y;
    }
  }

  function clear_coordinates(e)
  {
    var dom_axes = e.currentTarget.parentElement;
    var coordinates = dom_axes.querySelectorAll(".toyplot-coordinates");
    for(var i = 0; i != coordinates.length; ++i)
      coordinates[i].style.visibility = "hidden";
  }

  for(var axes_id in axes)
  {
    var event_target = document.querySelector("#" + axes_id + " .toyplot-coordinate-events");
    event_target.onmousemove = display_coordinates;
    event_target.onmouseout = clear_coordinates;
  }
})();
""")

_animation_controls = string.Template("""
(function()
{
  var root_id = "$root_id";
  var frame_durations = $frame_durations;
  var state_changes = $state_changes;

  var current_frame = null;
  var timeout = null;

  function on_set_frame()
  {
    if(timeout !== null)
      window.clearTimeout(timeout);
    timeout = null;
    set_current_frame(document.getElementById(root_id + "-current-frame").valueAsNumber);
    for(var frame = 0; frame <= current_frame; ++frame)
      render_changes(frame);
  }

  function on_frame_rewind()
  {
    if(timeout !== null)
      window.clearTimeout(timeout);
    set_current_frame((current_frame - 1 + frame_durations.length) % frame_durations.length);
    for(var frame = 0; frame <= current_frame; ++frame)
      render_changes(frame);
  }

  function on_rewind()
  {
    render_changes(0);
    set_current_frame(0);
  }

  function on_play_reverse()
  {
    if(timeout !== null)
      window.clearTimeout(timeout);
    timeout = window.setTimeout(play_reverse, frame_durations[(current_frame - 1 + frame_durations.length) % frame_durations.length] * 1000);
  }

  function on_stop()
  {
    if(timeout !== null)
      window.clearTimeout(timeout);
    timeout = null;
  }

  function on_play_forward()
  {
    if(timeout !== null)
      window.clearTimeout(timeout);
    timeout = window.setTimeout(play_forward, frame_durations[current_frame] * 1000);
  }

  function on_fast_forward()
  {
    for(var frame = 0; frame != frame_durations.length; ++frame)
      render_changes(frame);
    set_current_frame(frame_durations.length - 1);
  }

  function on_frame_advance()
  {
    if(timeout !== null)
      window.clearTimeout(timeout);
    set_current_frame((current_frame + 1) % frame_durations.length);
    render_changes(current_frame);
  }

  function set_current_frame(frame)
  {
    current_frame = frame;
    document.getElementById(root_id + "-current-frame").value = frame;
  }

  function play_reverse()
  {
    set_current_frame((current_frame - 1 + frame_durations.length) % frame_durations.length);
    for(var frame = 0; frame <= current_frame; ++frame)
      render_changes(frame);
    timeout = window.setTimeout(play_reverse, frame_durations[(current_frame - 1 + frame_durations.length) % frame_durations.length] * 1000);
  }

  function play_forward()
  {
    set_current_frame((current_frame + 1) % frame_durations.length);
    render_changes(current_frame);
    timeout = window.setTimeout(play_forward, frame_durations[current_frame] * 1000);
  }

  var item_cache = {};
  function get_item(id)
  {
    if(!(id in item_cache))
      item_cache[id] = document.getElementById(id);
    return item_cache[id];
  }

  function render_changes(frame)
  {
    var changes = state_changes[frame];
    for(var type in changes)
    {
      var type_changes = changes[type]
      if(type == "set-mark-style")
      {
        for(var i = 0; i != type_changes.length; ++i)
        {
          var mark_style = type_changes[i];
          var mark = get_item(mark_style[0]);
          for(var key in mark_style[1])
            mark.style.setProperty(key, mark_style[1][key]);
        }
      }
      else if(type == "set-datum-style")
      {
        for(var i = 0; i != type_changes.length; ++i)
        {
          var datum_style = type_changes[i];
          var datum = get_item(datum_style[0]).querySelectorAll(".toyplot-Series")[datum_style[1]].querySelectorAll(".toyplot-Datum")[datum_style[2]];
          for(var key in datum_style[3])
            datum.style.setProperty(key, datum_style[3][key]);
        }
      }
      else if(type == "set-datum-text")
      {
        for(var i = 0; i != type_changes.length; ++i)
        {
          var datum_text = type_changes[i];
          var datum = get_item(datum_text[0]).querySelectorAll(".toyplot-Series")[datum_text[1]].querySelectorAll(".toyplot-Datum")[datum_text[2]];
          datum.textContent = datum_text[3];
        }
      }
    }
  }

  set_current_frame(0);
  render_changes(current_frame);

  document.getElementById(root_id + "-current-frame").oninput = on_set_frame;
  document.getElementById(root_id + "-rewind").onclick = on_rewind;
  document.getElementById(root_id + "-reverse-play").onclick = on_play_reverse;
  document.getElementById(root_id + "-frame-rewind").onclick = on_frame_rewind;
  document.getElementById(root_id + "-stop").onclick = on_stop;
  document.getElementById(root_id + "-frame-advance").onclick = on_frame_advance;
  document.getElementById(root_id + "-forward-play").onclick = on_play_forward;
  document.getElementById(root_id + "-fast-forward").onclick = on_fast_forward;

})();
""")


class _RenderContext(object):
    def __init__(self, **kwargs):
        self.root = None
        self._id_cache = dict()
        self._data_tables = list()
        self._cartesian_axes = dict()
        self.rendered = set()

        for name in kwargs:
            setattr(self, name, kwargs[name])

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self):
        type_name = type(self).__name__
        arg_strings = []
        for name, value in sorted(self.__dict__.items()):
            arg_strings.append('%s=%r' % (name, value))
        return '%s(%s)' % (type_name, ', '.join(arg_strings))

    def add_cartesian_axes(self, axes):
        self._cartesian_axes[self.get_id(axes)] = axes

    def add_data_table(self, mark, table, title, filename):
        self._data_tables.append({
            "mark": mark,
            "title": title,
            "table": table,
            "filename": filename,
            })

    def get_id(self, obj):
        python_id = id(obj)
        if python_id not in self._id_cache:
            self._id_cache[python_id] = "t" + uuid.uuid4().hex
        return self._id_cache[python_id]

    def copy(self, **kwargs):
        result = copy.copy(self)
        for name in kwargs:
            setattr(result, name, kwargs[name])
        return result


def apply_changes(html, changes):
    for change_type, instructions in changes.items():
        if change_type == "set-mark-style":
            for mark_id, style in instructions:
                mark = html.find(".//*[@id='%s']" % mark_id)
                style = toyplot.style.combine(dict([declaration.split(
                    ":") for declaration in mark.get("style").split(";") if declaration != ""]), style)
                mark.set("style", _css_style(style))
        elif change_type == "set-datum-style":
            for mark_id, series, datum, style in instructions:
                mark_xml = html.find(".//*[@id='%s']" % mark_id)
                series_xml = mark_xml.findall(
                    "*[@class='toyplot-Series']")[series]
                datum_xml = series_xml.findall(
                    "*[@class='toyplot-Datum']")[datum]
                style = toyplot.style.combine(dict([declaration.split(
                    ":") for declaration in datum_xml.get("style").split(";") if declaration != ""]), style)
                datum_xml.set("style", _css_style(style))
        elif change_type == "set-datum-text":
            for mark_id, series, datum, text in instructions:
                mark_xml = html.find(".//*[@id='%s']" % mark_id)
                series_xml = mark_xml.findall(
                    "*[@class='toyplot-Series']")[series]
                datum_xml = series_xml.findall(
                    "*[@class='toyplot-Datum']")[datum]
                datum_xml.text = text


def render(canvas, fobj=None, animation=False):
    """Render the HTML representation of a canvas.

    Generates HTML markup with an embedded SVG representation of the canvas, plus
    JavaScript code for interactivity.  If the canvas contains animation, the
    markup will include an HTML user interface to control playback.

    Parameters
    ----------
    canvas: :class:`toyplot.canvas.Canvas`
      The canvas to be rendered.

    fobj: file-like object or string, optional
      The file to write.  Use a string filepath to write data directly to disk.
      If `None` (the default), the HTML tree will be returned to the caller
      instead.

    animation: boolean, optional
      If `True`, return a representation of the changes to be made to the HTML
      tree for animation.

    Returns
    -------
    html: xml.etree.ElementTree.Element or `None`
      HTML representation of `canvas`, as a DOM tree, or `None` if the caller
      specifies the `fobj` parameter.

    changes: JSON-compatible data structure, or `None`
      JSON-compatible representation of the animated changes to `canvas`.

    Notes
    -----
    The output HTML is the "canonical" representation of a Toyplot canvas - the
    other toyplot backends operate by converting the output from
    toyplot.html.render() to the desired end target.

    Note that the output HTML is a fragment wrapped in a <div>, suitable for
    embedding in a larger document.  It is the caller's responsibility to
    supply the <html>, <body> etc. if the result is intended as a standalone
    HTML document.
    """
    canvas.autorender(False)

    # Create the SVG representation.
    context = _RenderContext()
    svg = xml.Element(
        "svg",
        xmlns="http://www.w3.org/2000/svg",
        attrib={"xmlns:toyplot": "http://www.sandia.gov/toyplot"},
        width="%rpx" % canvas.width,
        height="%rpx" % canvas.height,
        viewBox="0 0 %r %r" % (canvas.width, canvas.height),
        preserveAspectRatio="xMidYMid meet",
        style=_css_style(canvas._style),
        id=context.get_id(canvas))
    for child in canvas._children:
        _render(canvas, child, context.copy(root=svg))

    # Collect animation data.
    svg_animation = collections.defaultdict(
        lambda: collections.defaultdict(list))
    for time, time_changes in list(canvas._animation.items())[:-1]:
        # Ensure we have an entry for every time, even if there aren't any
        # changes.
        svg_animation[time]
        for type, type_changes in time_changes.items():
            for change in type_changes:
                svg_animation[time][type].append(
                    [context.get_id(change[0])] + list(change[1:]))

    # Create the top-level HTML element.
    root = xml.Element(
        "div",
        align="center",
        attrib={
            "class": "toyplot"},
        id="t" +
        uuid.uuid4().hex)
    root.append(svg)

    # Add HTML controls.
    controls = xml.SubElement(
        root,
        "div",
        attrib={"class": "toyplot-controls"},
        )
    mark_popup = xml.SubElement(
        controls,
        "ul",
        attrib={"class": "toyplot-mark-popup"},
        onmouseleave="this.style.visibility='hidden'",
        style=_css_style({
            "background": "rgba(0%,0%,0%,0.75)",
            "border": "0",
            "border-radius": "6px",
            "color": "white",
            "cursor": "default",
            "list-style": "none",
            "margin": "0",
            "padding": "5px",
            "position": "fixed",
            "visibility": "hidden",
        }))
    xml.SubElement(
        mark_popup,
        "li",
        attrib={
            "class": "toyplot-mark-popup-title"},
        style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0;")
    xml.SubElement(
        mark_popup,
        "li",
        attrib={
            "class": "toyplot-mark-popup-save-csv"},
        style="border-radius:3px;padding:5px;list-style:none;margin:0;",
        onmouseover="this.style.color='steelblue';this.style.background='white'",
        onmouseout="this.style.color='white';this.style.background='steelblue'").text = "Save as .csv"

    # Allow users to export embedded table data.
    if context._data_tables:
        data_tables = list()
        for data_table in context._data_tables:
            mark = data_table["mark"]
            title = data_table["title"]
            table = data_table["table"]
            filename = data_table["filename"] if data_table["filename"] else "toyplot"

            names = []
            data = []
            for name, column in table.items():
                if "toyplot:exportable" in table.metadata(
                        name) and table.metadata(name)["toyplot:exportable"]:
                    if column.dtype == toyplot.color.dtype:
                        for suffix, channel in zip(
                                [":red", ":green", ":blue", ":alpha"], ["r", "g", "b", "a"]):
                            names.append(name + suffix)
                            data.append(column[channel].tolist())
                    else:
                        names.append(name)
                        data.append(column.tolist())
            if names:
                data_tables.append(
                    {"id": context.get_id(mark), "filename": filename, "title": title, "names": names, "data": data})

        xml.SubElement(controls, "script").text = _export_data_tables.substitute(root_id=root.get("id"), data_tables=json.dumps(data_tables))

    # Provide interactive mouse coordinates.
    def _flip_infinities(value):
        if numpy.isinf(value):
            return -value
        return value

    if context._cartesian_axes:
        cartesian_axes = dict()
        for key, axes in context._cartesian_axes.items():
            cartesian_axes[key] = dict()
            cartesian_axes[key]["x"] = list()
            for segment in axes._x_projection._segments:
                cartesian_axes[key]["x"].append(
                    {
                        "scale": segment.scale,
                        "domain": {
                            "min": segment.domain.min,
                            "max": segment.domain.max,
                            "bounds": {
                                "min": segment.domain.bounds.min,
                                "max": segment.domain.bounds.max}},
                        "range": {
                            "min": segment.range.min,
                            "max": segment.range.max,
                            "bounds": {
                                "min": segment.range.bounds.min,
                                "max": segment.range.bounds.max}}})
            cartesian_axes[key]["y"] = list()
            for segment in axes._y_projection._segments:
                cartesian_axes[key]["y"].append(
                    {
                        "scale": segment.scale,
                        "domain": {
                            "min": segment.domain.min,
                            "max": segment.domain.max,
                            "bounds": {
                                "min": segment.domain.bounds.min,
                                "max": segment.domain.bounds.max}},
                        "range": {
                            "min": segment.range.min,
                            "max": segment.range.max,
                            "bounds": {
                                "min": _flip_infinities(segment.range.bounds.min),
                                "max": _flip_infinities(segment.range.bounds.max)}}})

        xml.SubElement(controls, "script").text = _show_mouse_coordinates.substitute(
            root_id=root.get("id"),
            cartesian_axes=json.dumps(cartesian_axes, cls=_NumpyJSONEncoder, sort_keys=True))

    # Provide VCR controls.
    if len(svg_animation) > 1:
        times = numpy.array(sorted(svg_animation.keys()))
        durations = times[1:] - times[:-1]
        changes = [change for time, change in sorted(svg_animation.items())]

        vcr_controls = xml.SubElement(
            controls, "div", attrib={"class": "toyplot-vcr-controls"})
        xml.SubElement(
            vcr_controls,
            "input",
            title="Frame",
            type="range",
            min="0",
            max=str(
                len(times) -
                2),
            step="1",
            value="0",
            id="%s-current-frame" %
            root.get("id"))
        xml.SubElement(
            vcr_controls,
            "button",
            title="Rewind",
            style="width:40px;height:24px",
            id="%s-rewind" % root.get("id")).append(
                xml.XML(
                    """<svg width="20" height="20"><polygon points="10,5 0,10 10,15" stroke="none" fill="{near_black}"/><polygon points="20,5 10,10 20,15" stroke="none" fill="{near_black}"/></svg>""".format(
                        near_black=toyplot.color.near_black)))
        xml.SubElement(
            vcr_controls,
            "button",
            title="Reverse Play",
            style="width:40px;height:24px",
            id="%s-reverse-play" % root.get("id")).append(
                xml.XML(
                    """<svg width="20" height="20"><polygon points="15,5 5,10 15,15" stroke="none" fill="{near_black}"/></svg>""".format(
                        near_black=toyplot.color.near_black)))
        xml.SubElement(
            vcr_controls,
            "button",
            title="Frame Rewind",
            style="width:40px;height:24px",
            id="%s-frame-rewind" % root.get("id")).append(
                xml.XML(
                    """<svg width="20" height="20"><polygon points="15,5 5,10 15,15" stroke="none" fill="{near_black}"/><rect x="17" y="5" width="2" height="10" stroke="none" fill="{near_black}"/></svg>""".format(
                        near_black=toyplot.color.near_black)))
        xml.SubElement(
            vcr_controls,
            "button",
            title="Stop",
            style="width:40px;height:24px",
            id="%s-stop" % root.get("id")).append(
                xml.XML(
                    """<svg width="20" height="20"><rect x="5" y="5" width="10" height="10" stroke="none" fill="{near_black}"/></svg>""".format(
                        near_black=toyplot.color.near_black)))
        xml.SubElement(
            vcr_controls,
            "button",
            title="Frame Advance",
            style="width:40px;height:24px",
            id="%s-frame-advance" % root.get("id")).append(
                xml.XML(
                    """<svg width="20" height="20"><polygon points="5,5 15,10 5,15" stroke="none" fill="{near_black}"/><rect x="1" y="5" width="2" height="10" stroke="none" fill="{near_black}"/></svg>""".format(
                        near_black=toyplot.color.near_black)))
        xml.SubElement(
            vcr_controls,
            "button",
            title="Play",
            style="width:40px;height:24px",
            id="%s-forward-play" % root.get("id")).append(
                xml.XML(
                    """<svg width="20" height="20"><polygon points="5,5 15,10 5,15" stroke="none" fill="{near_black}"/></svg>""".format(
                        near_black=toyplot.color.near_black)))
        xml.SubElement(
            vcr_controls,
            "button",
            title="Fast Forward",
            style="width:40px;height:24px",
            id="%s-fast-forward" % root.get("id")).append(
                xml.XML(
                    """<svg width="20" height="20"><polygon points="0,5 10,10 0,15" stroke="none" fill="{near_black}"/><polygon points="10,5 20,10 10,15" stroke="none" fill="{near_black}"/></svg>""".format(
                        near_black=toyplot.color.near_black)))

        xml.SubElement(controls, "script").text = _animation_controls.substitute(
            root_id=root.get("id"),
            frame_durations=json.dumps(durations.tolist()),
            state_changes=json.dumps(changes, cls=_NumpyJSONEncoder))

    if isinstance(fobj, toyplot.compatibility.string_type):
        with open(fobj, "wb") as file:
            file.write(xml.tostring(root, method="html"))
    elif fobj is not None:
        fobj.write(xml.tostring(root, method="html"))
    else:
        if animation:
            return root, svg_animation
        return root


def _color_fixup(styles):
    """It turns-out that many applications and libraries (Inkscape, Adobe Illustrator, Qt)
    don't handle CSS rgba() colors correctly.  So convert them to CSS rgb colors and use
    fill-opacity / stroke-opacity instead."""

    if "fill" in styles:
        color = toyplot.color.css(styles["fill"])
        if color is not None:
            opacity = float(styles.get("fill-opacity", 1.0))
            styles["fill"] = "rgb(%.3g%%,%.3g%%,%.3g%%)" % (
                color["r"] * 100, color["g"] * 100, color["b"] * 100)
            styles["fill-opacity"] = str(color["a"] * opacity)
    if "stroke" in styles:
        color = toyplot.color.css(styles["stroke"])
        if color is not None:
            opacity = float(styles.get("stroke-opacity", 1.0))
            styles["stroke"] = "rgb(%.3g%%,%.3g%%,%.3g%%)" % (
                color["r"] * 100, color["g"] * 100, color["b"] * 100)
            styles["stroke-opacity"] = str(color["a"] * opacity)

    return styles

def _css_style(*styles):
    style = _color_fixup(toyplot.style.combine(*styles))
    return ";".join(["%s:%s" % (key, value)
                     for key, value in sorted(style.items())])


def _css_attrib(*styles):
    style = _color_fixup(toyplot.style.combine(*styles))
    attrib = {}
    if len(style):
        attrib["style"] = ";".join(
            ["%s:%s" % (key, value) for key, value in sorted(style.items())])
    return attrib


def _flat_contiguous(a):
    i = 0
    result = []
    for (k, g) in itertools.groupby(a.ravel()):
        n = len(list(g))
        if k:
            result.append(slice(i, i + n))
        i += n
    return result


#def indent(elem, level=0):
#    i = "\n" + level*"  "
#    if len(elem):
#        if not elem.text or not elem.text.strip():
#            elem.text = i + "  "
#        if not elem.tail or not elem.tail.strip():
#            elem.tail = i
#        for elem in elem:
#            indent(elem, level+1)
#        if not elem.tail or not elem.tail.strip():
#            elem.tail = i
#    else:
#        if level and (not elem.tail or not elem.tail.strip()):
#            elem.tail = i

class _HTMLParser(HTMLParser.HTMLParser):
    def __init__(self, element, font_size):
        HTMLParser.HTMLParser.__init__(self)
        self._element = element
        self._font_size = font_size
        self._root_node = xml.Element("root")
        self._current_node = self._root_node
        self._parent_map = {self._root_node: self._root_node}

    def push_node(self, tag, **kwargs):
        node = xml.SubElement(self._current_node, tag, **kwargs)
        self._parent_map[node] = self._current_node
        self._current_node = node

    def pop_node(self):
        while self._current_node.tag == "br":
            self._current_node = self._parent_map[self._current_node]
        while True:
            self._current_node = self._parent_map[self._current_node]
            if self._current_node.tag != "br":
                break

    def walk_tree(self, node, attributes, style, stack_state, global_state):
        if node.tag == "text":
            attributes = copy.copy(attributes)
            style = copy.copy(style)
            style["dominant-baseline"] = "inherit"
            x = global_state.pop("x", None)
            if x is not None:
                attributes["x"] = x
            new_y = global_state["line-y"] + stack_state["dy"]
            if new_y != global_state["current-y"]:
                attributes["dy"] = new_y - global_state["current-y"]
                global_state["current-y"] = new_y
            tspan = xml.SubElement(self._element, "tspan")
            for key, value in attributes.items():
                tspan.set(key, str(value))
            tspan.set("style", _css_style(style))
            tspan.text = node.text
        else:
            attributes = copy.copy(attributes)
            style = copy.copy(style)
            stack_state = copy.copy(stack_state)
            if node.tag in ["b", "strong"]:
                style["font-weight"] = "bold"
            elif node.tag == "br":
                font_size = stack_state["font-size"]
                global_state["x"] = 0
                global_state["line-y"] += font_size * 1.2
            elif node.tag == "code":
                style["font-family"] = "monospace"
            elif node.tag in ["em", "i"]:
                style["font-style"] = "italic"
            elif node.tag == "small":
                font_size = stack_state["font-size"]
                stack_state["font-size"] = font_size * 0.8
                style["font-size"] = "%spx" % (font_size * 0.8)
            elif node.tag == "sub":
                font_size = stack_state["font-size"]
                stack_state["font-size"] = font_size * 0.7
                style["font-size"] = "%spx" % (font_size * 0.7)
                stack_state["dy"] += font_size * 0.2
            elif node.tag == "sup":
                font_size = stack_state["font-size"]
                stack_state["font-size"] = font_size * 0.7
                style["font-size"] = "%spx" % (font_size * 0.7)
                stack_state["dy"] -= font_size * 0.3
            for child in node:
                self.walk_tree(child, attributes, style, stack_state, global_state)

    def handle_starttag(self, tag, attrs):
        if tag == "br":
            self.push_node("br")
        elif tag in ["b", "code", "em", "i", "small", "strong", "sub", "sup"]:
            self.push_node(tag)
        else:
            toyplot.log.warning("Ignoring unknown <%s> tag." % tag)

    def handle_endtag(self, tag):
        if tag in ["br"]:
            toyplot.log.warning("%s must not have an end tag." % tag)
        elif tag in ["b", "code", "em", "i", "small", "strong", "sub", "sup"]:
            self.pop_node()
        else:
            toyplot.log.warning("Ignoring unknown </%s> tag." % tag)

    def handle_data(self, text):
        xml.SubElement(self._current_node, "text").text = text

    def close(self):
        HTMLParser.HTMLParser.close(self)
        self.walk_tree(self._root_node, attributes={}, style={}, stack_state={"dy":0,"font-size":self._font_size}, global_state={"line-y":0, "current-y":0})
#        indent(self._root_node)
#        print xml.tostring(self._root_node)


def _draw_text(
        root,
        text,
        x=0,
        y=0,
        style=None,
        angle=None,
        title=None,
        attributes={},
        ):

    if not text:
        return

    style = copy.copy(style)

    font_size = toyplot.units.convert(style["font-size"], target="px", default="px")
    style["dominant-baseline"] = style.pop("alignment-baseline", "middle")

    baseline_shift = 0
    baseline_shift -= toyplot.units.convert(style.pop("baseline-shift", 0), target="px", default="px", reference=font_size)

    x += toyplot.units.convert(style.pop("-toyplot-anchor-shift", 0), target="px", default="px")

    transform = "translate(%r,%r)" % (x, y)
    if angle:
        transform += "rotate(%r)" % angle
    if baseline_shift:
        transform += "translate(0,%r)" % baseline_shift

    text_xml = xml.SubElement(
        root,
        "text",
        transform=transform,
        style=_css_style(style),
        attrib=attributes,
        )
    if title is not None:
        xml.SubElement(text_xml, "title").text = str(title)

    parser = _HTMLParser(text_xml, font_size)
    parser.feed(text)
    parser.close()


def _draw_marker(
        root,
        cx,
        cy,
        size,
        marker,
        marker_style=None,
        label_style=None,
        extra_class=None,
        title=None):
    if marker is None:
        return
    if isinstance(marker, toyplot.compatibility.string_type):
        marker = {"shape": marker}
    shape = marker.get("shape", None)
    shape_angle = marker.get("angle", 0)
    shape_style = marker.get("mstyle", None)
    shape_label = marker.get("label", None)
    shape_label_style = marker.get("lstyle", None)

    if shape in _draw_marker.variations:
        variation = _draw_marker.variations[shape]
        shape = variation[0]
        shape_angle += variation[1]

    attrib = _css_attrib(marker_style, shape_style)
    if extra_class is not None:
        attrib["class"] = extra_class
    marker_xml = xml.SubElement(root, "g", attrib=attrib)
    if title is not None:
        xml.SubElement(marker_xml, "title").text = str(title)
    if shape == "|":
        xml.SubElement(marker_xml,
                       "line",
                       transform="rotate(%r, %r, %r)" % (-shape_angle,
                                                         cx,
                                                         cy),
                       x1=repr(cx),
                       x2=repr(cx),
                       y1=repr(cy - (size / 2)),
                       y2=repr(cy + (size / 2)))
    elif shape == "+":
        xml.SubElement(marker_xml,
                       "line",
                       transform="rotate(%r, %r, %r)" % (-shape_angle,
                                                         cx,
                                                         cy),
                       x1=repr(cx),
                       x2=repr(cx),
                       y1=repr(cy - (size / 2)),
                       y2=repr(cy + (size / 2)))
        xml.SubElement(marker_xml,
                       "line",
                       transform="rotate(%r, %r, %r)" % (-shape_angle,
                                                         cx,
                                                         cy),
                       x1=repr(cx - (size / 2)),
                       x2=repr(cx + (size / 2)),
                       y1=repr(cy),
                       y2=repr(cy))
    elif shape == "*":
        xml.SubElement(marker_xml,
                       "line",
                       transform="rotate(%r, %r, %r)" % (-shape_angle,
                                                         cx,
                                                         cy),
                       x1=repr(cx),
                       x2=repr(cx),
                       y1=repr(cy - (size / 2)),
                       y2=repr(cy + (size / 2)))
        xml.SubElement(marker_xml,
                       "line",
                       transform="rotate(%r, %r, %r)" % (-shape_angle + 60,
                                                         cx,
                                                         cy),
                       x1=repr(cx),
                       x2=repr(cx),
                       y1=repr(cy - (size / 2)),
                       y2=repr(cy + (size / 2)))
        xml.SubElement(marker_xml,
                       "line",
                       transform="rotate(%r, %r, %r)" % (-shape_angle - 60,
                                                         cx,
                                                         cy),
                       x1=repr(cx),
                       x2=repr(cx),
                       y1=repr(cy - (size / 2)),
                       y2=repr(cy + (size / 2)))
    elif shape == "^":
        xml.SubElement(marker_xml,
                       "polygon",
                       transform="rotate(%r, %r, %r)" % (-shape_angle,
                                                         cx,
                                                         cy),
                       points=" ".join(["%r,%r" % (xp,
                                                   yp) for xp,
                                        yp in [(cx - (size / 2),
                                                cy + (size / 2)),
                                               (cx,
                                                cy - (size / 2)),
                                               (cx + (size / 2),
                                                cy + (size / 2))]]))
    elif shape == "s":
        xml.SubElement(marker_xml,
                       "rect",
                       transform="rotate(%r, %r, %r)" % (-shape_angle,
                                                         cx,
                                                         cy),
                       x=repr(cx - (size / 2)),
                       y=repr(cy - (size / 2)),
                       width=repr(size),
                       height=repr(size))
    elif shape == "o":
        xml.SubElement(
            marker_xml, "circle", cx=repr(cx), cy=repr(cy), r=repr(size / 2))
    elif shape == "oo":
        xml.SubElement(
            marker_xml, "circle", cx=repr(cx), cy=repr(cy), r=repr(size / 2))
        xml.SubElement(
            marker_xml, "circle", cx=repr(cx), cy=repr(cy), r=repr(size / 4))
    elif shape == "o|":
        xml.SubElement(
            marker_xml, "circle", cx=repr(cx), cy=repr(cy), r=repr(size / 2))
        xml.SubElement(marker_xml,
                       "line",
                       transform="rotate(%r, %r, %r)" % (-shape_angle,
                                                         cx,
                                                         cy),
                       x1=repr(cx),
                       x2=repr(cx),
                       y1=repr(cy - (size / 2)),
                       y2=repr(cy + (size / 2)))
    elif shape == "o+":
        xml.SubElement(
            marker_xml, "circle", cx=repr(cx), cy=repr(cy), r=repr(size / 2))
        xml.SubElement(marker_xml,
                       "line",
                       transform="rotate(%r, %r, %r)" % (-shape_angle,
                                                         cx,
                                                         cy),
                       x1=repr(cx),
                       x2=repr(cx),
                       y1=repr(cy - (size / 2)),
                       y2=repr(cy + (size / 2)))
        xml.SubElement(marker_xml,
                       "line",
                       transform="rotate(%r, %r, %r)" % (-shape_angle,
                                                         cx,
                                                         cy),
                       x1=repr(cx - (size / 2)),
                       x2=repr(cx + (size / 2)),
                       y1=repr(cy),
                       y2=repr(cy))
    elif shape == "o*":
        xml.SubElement(
            marker_xml, "circle", cx=repr(cx), cy=repr(cy), r=repr(size / 2))
        xml.SubElement(marker_xml,
                       "line",
                       transform="rotate(%r, %r, %r)" % (-shape_angle,
                                                         cx,
                                                         cy),
                       x1=repr(cx),
                       x2=repr(cx),
                       y1=repr(cy - (size / 2)),
                       y2=repr(cy + (size / 2)))
        xml.SubElement(marker_xml,
                       "line",
                       transform="rotate(%r, %r, %r)" % (-shape_angle + 60,
                                                         cx,
                                                         cy),
                       x1=repr(cx),
                       x2=repr(cx),
                       y1=repr(cy - (size / 2)),
                       y2=repr(cy + (size / 2)))
        xml.SubElement(marker_xml,
                       "line",
                       transform="rotate(%r, %r, %r)" % (-shape_angle - 60,
                                                         cx,
                                                         cy),
                       x1=repr(cx),
                       x2=repr(cx),
                       y1=repr(cy - (size / 2)),
                       y2=repr(cy + (size / 2)))
    elif shape == "path":
        shape_path = marker.get("path")
        xml.SubElement(
            marker_xml, "path", transform="translate(%r, %r) scale(%r) translate(%r, %r)" %
            (cx, cy, size, -cx, -cy), d="M " + repr(cx) + " " + repr(cy) + shape_path)

    if shape_label: # Not technically necessary, but we should avoid computing the style for every marker if we don't have to.
        _draw_text(
            root=marker_xml,
            text=shape_label,
            x=cx,
            y=cy,
            style = toyplot.style.combine(
                {
                    "stroke": "none",
                    "fill": toyplot.color.near_black,
                    "text-anchor": "middle",
                    "alignment-baseline": "middle",
                    "font-size": "%rpx" % (size * 0.75),
                },
                label_style,
                shape_label_style),
            )
    return marker_xml

_draw_marker.variations = {"-": ("|", 90), "x": ("+", 45), "v": ("^", 180), "<": (
    "^", -90), ">": ("^", 90), "d": ("s", 45), "o-": ("o|", 90), "ox": ("o+", 45)}


def _rotated_frame(x1, y1, x2, y2, offset):
    p = numpy.row_stack(((x1, y1), (x2, y2)))
    basis = p[1] - p[0]
    length = numpy.linalg.norm(basis)
    theta = numpy.rad2deg(numpy.arctan2(basis[1], basis[0]))
    transform="translate(%s,%s) rotate(%s) translate(0,%s)" % (p[0][0], p[0][1], theta, offset)
    return transform, length


@dispatch(toyplot.canvas.Canvas, toyplot.axes.Axis, _RenderContext)
def _render(canvas, axis, context):
    if axis in context.rendered:
        return
    context.rendered.add(axis)

    if axis.show:
        p = numpy.row_stack(((context.x1, context.y1), (context.x2, context.y2)))
        basis = p[1] - p[0]
        length = numpy.linalg.norm(basis)
        theta = numpy.rad2deg(numpy.arctan2(basis[1], basis[0]))

        project = axis.projection(range_min=0.0, range_max=length)

        axis_xml = xml.SubElement(
            context.root,
            "g",
            id=context.get_id(axis),
            transform="translate(%s,%s) rotate(%s) translate(%s,%s)" % (p[0][0], p[0][1], theta, 0, context.offset),
            attrib={"class": "toyplot-axes-Axis"},
            )

        if axis.spine.show:
            x1 = 0
            x2 = length
            if axis._data_min is not None and axis._data_max is not None:
                x1 = max(
                    x1, project(axis._data_min))
                x2 = min(
                    x2, project(axis._data_max))
            xml.SubElement(
                axis_xml,
                "line",
                x1=repr(x1),
                y1=repr(0),
                x2=repr(x2),
                y2=repr(0),
                style=_css_style(
                    axis.spine._style))

            if axis.ticks._show:
                y1 = -context.ticks_above if axis.ticks.above is None else -axis.ticks.above
                y2 = context.ticks_below if axis.ticks.below is None else axis.ticks.below

                ticks_group = xml.SubElement(axis_xml, "g")
                for location, tick_style in zip(
                        axis._tick_locations,
                        axis.ticks.tick.styles(axis._tick_locations),
                    ):
                    x = project(location)
                    xml.SubElement(
                        ticks_group,
                        "line",
                        x1=repr(x),
                        y1=repr(y1),
                        x2=repr(x),
                        y2=repr(y2),
                        style=_css_style(
                            axis.ticks._style,
                            tick_style))

        if axis.ticks.labels.show:
            y = axis.ticks.labels.offset

            ticks_group = xml.SubElement(axis_xml, "g")
            for location, label, title, label_style in zip(
                    axis._tick_locations,
                    axis._tick_labels,
                    axis._tick_titles,
                    axis.ticks.labels.label.styles(axis._tick_locations),
                ):
                x = project(location)

                _draw_text(
                    root=ticks_group,
                    text=label,
                    x=x,
                    y=y,
                    style=toyplot.style.combine(
                        {
                            "text-anchor": "middle",
                            "alignment-baseline": "middle",
                            "baseline-shift": context.tick_labels_baseline_shift,
                        },
                        axis.ticks.labels.style,
                        label_style,
                        ),
                    angle=-axis.ticks.labels.angle,
                    title=title,
                    )

        _draw_text(
            root=axis_xml,
            text=axis.label.text,
            x=length * 0.5,
            y=0,
            style=toyplot.style.combine({"baseline-shift": context.label_baseline_shift}, axis.label.style),
            )


@dispatch(toyplot.canvas.Canvas, toyplot.axes.NumberLine, _RenderContext)
def _render(canvas, axes, context):
    axes._finalize()

    axes_xml = xml.SubElement(context.root, "g", id=context.get_id(
        axes), attrib={"class": "toyplot-axes-NumberLine"})

    children_xml = xml.SubElement(
        axes_xml,
        "g",
        attrib={"class": "toyplot-coordinate-events"},
        )

    for child in axes._children:
        _render(axes, child, context.copy(root=children_xml))

    _render(canvas, axes.axis, context.copy(
        root=axes_xml,
        x1=axes._x1,
        y1=axes._y1,
        x2=axes._x2,
        y2=axes._y2,
        offset=axes.padding,
        ticks_above=3,
        ticks_below=3,
        tick_labels_baseline_shift="-100%",
        label_baseline_shift="-200%",
        ))


@dispatch(toyplot.axes.NumberLine, toyplot.color.CategoricalMap, _RenderContext)
def _render(numberline, colormap, context):
    offset = numberline._offset[colormap]
    width = numberline._width[colormap]
    style = numberline._style[colormap]

    transform, length = _rotated_frame(numberline._x1, numberline._y1, numberline._x2, numberline._y2, -offset)

    mark_xml = xml.SubElement(
        context.root,
        "g", id=context.get_id(colormap),
        attrib={"class": "toyplot-color-CategoricalMap"},
        transform=transform,
        )

    projection = numberline.axis.projection(range_min=0, range_max=length)
    samples = numpy.linspace(colormap.domain.min, colormap.domain.max, len(colormap._palette), endpoint=True)
    projected = projection(samples)
    colormap_range_min, colormap_range_max = projection([colormap.domain.min, colormap.domain.max])

    for index, (x1, x2), in enumerate(zip(projected[:-1], projected[1:])):
        color = colormap._palette[index]
        xml.SubElement(
            mark_xml,
            "rect",
            x=repr(x1),
            y=repr(-width * 0.5),
            width=repr(x2 - x1),
            height=repr(width),
            style=_css_style({"stroke": "none", "fill": toyplot.color.to_css(color)}),
            )

    style = toyplot.style.combine(
        {"stroke": "none", "stroke-width":1.0, "fill": "none"},
        style,
        )

    xml.SubElement(
        mark_xml,
        "rect",
        x=repr(colormap_range_min),
        y=repr(-width * 0.5),
        width=repr(colormap_range_max - colormap_range_min),
        height=repr(width),
        style=_css_style(style),
        )

@dispatch(toyplot.axes.NumberLine, toyplot.color.Map, _RenderContext)
def _render(numberline, colormap, context):
    offset = numberline._offset[colormap]
    width = numberline._width[colormap]
    style = numberline._style[colormap]

    transform, length = _rotated_frame(numberline._x1, numberline._y1, numberline._x2, numberline._y2, -offset)
    projection = numberline.axis.projection(range_min=0, range_max=length)
    colormap_range_min, colormap_range_max = projection([colormap.domain.min, colormap.domain.max])

    mark_xml = xml.SubElement(
        context.root,
        "g", id=context.get_id(colormap),
        attrib={"class": "toyplot-color-Map"},
        transform=transform,
        )

    defs_xml = xml.SubElement(
        mark_xml,
        "defs",
        )

    gradient_xml = xml.SubElement(
        defs_xml,
        "linearGradient",
        id="t" + uuid.uuid4().hex,
        x1=repr(colormap_range_min),
        x2=repr(colormap_range_max),
        y1=repr(0),
        y2=repr(0),
        gradientUnits="userSpaceOnUse",
        )

    samples = numpy.linspace(colormap.domain.min, colormap.domain.max, 64, endpoint=True)
    for sample in samples:
        color = colormap.colors(sample)
        psample = projection(sample)
        offset = (psample - colormap_range_min) / (colormap_range_max - colormap_range_min)
        xml.SubElement(
            gradient_xml,
            "stop",
            offset="%s" % offset,
            attrib={
                "stop-color": "rgb(%.3g%%,%.3g%%,%.3g%%)" % (color["r"] * 100, color["g"] * 100, color["b"] * 100),
                "stop-opacity": str(color["a"]),
                },
            )

    style = toyplot.style.combine(
        {"stroke": "none", "stroke-width":1.0, "fill": "url(#%s)" % gradient_xml.get("id")},
        style,
        )

    xml.SubElement(
        mark_xml,
        "rect",
        x=repr(colormap_range_min),
        y=repr(-width * 0.5),
        width=repr(colormap_range_max - colormap_range_min),
        height=repr(width),
        style=_css_style(style),
        )


@dispatch(toyplot.axes.NumberLine, toyplot.mark.Scatterplot, _RenderContext)
def _render(numberline, mark, context):
    transform, length = _rotated_frame(numberline._x1, numberline._y1, numberline._x2, numberline._y2, -numberline._offset[mark])
    mark_xml = xml.SubElement(
        context.root,
        "g",
        style=_css_style(mark._style),
        id=context.get_id(mark),
        attrib={"class": "toyplot-mark-Scatterplot"},
        transform=transform,
        )
    context.add_data_table(mark, mark._table, title="Scatterplot Data", filename=mark._filename)

    dimension1 = numpy.ma.column_stack([mark._table[key] for key in mark._coordinates])
    projection = numberline.axis.projection(range_min=0, range_max=length)
    X = projection(dimension1)
    for x, marker, msize, mfill, mstroke, mopacity, mtitle in zip(
            X.T,
            [mark._table[key] for key in mark._marker],
            [mark._table[key] for key in mark._msize],
            [mark._table[key] for key in mark._mfill],
            [mark._table[key] for key in mark._mstroke],
            [mark._table[key] for key in mark._mopacity],
            [mark._table[key] for key in mark._mtitle],
        ):
        not_null = numpy.invert(numpy.ma.getmaskarray(x))

        series_xml = xml.SubElement(
            mark_xml, "g", attrib={"class": "toyplot-Series"})
        for dx, dmarker, dsize, dfill, dstroke, dopacity, dtitle in zip(
                x[not_null],
                marker[not_null],
                msize[not_null],
                mfill[not_null],
                mstroke[not_null],
                mopacity[not_null],
                mtitle[not_null],
            ):
            dstyle = toyplot.style.combine(
                {
                    "fill": toyplot.color.to_css(dfill),
                    "stroke": toyplot.color.to_css(dstroke),
                    "opacity": dopacity,
                },
                mark._mstyle)
            datum_xml = _draw_marker(
                series_xml,
                dx,
                0,
                dsize,
                dmarker,
                dstyle,
                mark._mlstyle,
                extra_class="toyplot-Datum",
                title=dtitle,
                )


@dispatch(toyplot.canvas.Canvas, toyplot.axes.Cartesian, _RenderContext)
def _render(canvas, axes, context):
    axes._finalize()

    axes_xml = xml.SubElement(context.root, "g", id=context.get_id(
        axes), attrib={"class": "toyplot-axes-Cartesian"})

    clip_xml = xml.SubElement(axes_xml, "clipPath", id="t" + uuid.uuid4().hex)
    xml.SubElement(
        clip_xml,
        "rect",
        x=repr(axes._xmin_range - axes.padding),
        y=repr(axes._ymin_range - axes.padding),
        width=repr(axes._xmax_range - axes._xmin_range + axes.padding * 2),
        height=repr(axes._ymax_range - axes._ymin_range + axes.padding * 2),
        )

    children_xml = xml.SubElement(
        axes_xml,
        "g",
        attrib={
            "class" : "toyplot-coordinate-events",
            "clip-path" : "url(#%s)" % clip_xml.get("id"),
        },
        style=_css_style({"cursor": "crosshair"}),
        )

    xml.SubElement(
        children_xml,
        "rect",
        x=repr(axes._xmin_range - axes.padding),
        y=repr(axes._ymin_range - axes.padding),
        width=repr(axes._xmax_range - axes._xmin_range + axes.padding * 2),
        height=repr(axes._ymax_range - axes._ymin_range + axes.padding * 2),
        style=_css_style({"visibility": "hidden", "pointer-events": "all"}),
        )

    for child in axes._children:
        _render(axes, child, context.copy(root=children_xml))

    if axes.coordinates._show:
        context.add_cartesian_axes(axes)
        coordinates_xml = xml.SubElement(axes_xml, "g", style=_css_style(
            {"visibility": "hidden"}), attrib={"class": "toyplot-coordinates"})
        xml.SubElement(
            coordinates_xml,
            "rect",
            x=repr(
                axes.coordinates._xmin_range),
            y=repr(
                axes.coordinates._ymin_range),
            width=repr(
                axes.coordinates._xmax_range -
                axes.coordinates._xmin_range),
            height=repr(
                axes.coordinates._ymax_range -
                axes.coordinates._ymin_range),
            style=_css_style(
                axes.coordinates._style))
        xml.SubElement(
            coordinates_xml,
            "text",
            x=repr(
                (axes.coordinates._xmin_range + axes.coordinates._xmax_range) * 0.5),
            y=repr(
                (axes.coordinates._ymin_range + axes.coordinates._ymax_range) * 0.5),
            style=_css_style(
                axes.coordinates.label._style))

    if axes._show:
        if axes.x.spine.position == "low":
            x_offset = axes.padding
            x_spine_y = axes._ymax_range
            x_ticks_above = 5
            x_ticks_below = 0
            x_tick_labels_baseline_shift = "-80%"
            x_label_baseline_shift = "-200%"
        elif axes.x.spine.position == "high":
            x_offset = -axes.padding
            x_spine_y = axes._ymin_range
            x_ticks_above = 0
            x_ticks_below = 5
            x_tick_labels_baseline_shift = "80%"
            x_label_baseline_shift = "200%"
        else:
            x_offset = 0
            x_spine_y = axes._project_y(axes.x.spine.position)
            x_ticks_above = 3
            x_ticks_below = 3
            x_tick_labels_baseline_shift = "-100%"
            x_label_baseline_shift = "-200%"

        if axes.y.spine._position == "low":
            y_offset = -axes.padding
            y_spine_x = axes._xmin_range
            y_ticks_above = 0
            y_ticks_below = 5
            y_tick_labels_baseline_shift = "80%"
            y_label_baseline_shift = "200%"
        elif axes.y.spine._position == "high":
            y_offset = axes.padding
            y_spine_x = axes._xmax_range
            y_ticks_above = 5
            y_ticks_below = 0
            y_tick_labels_baseline_shift = "-80%"
            y_label_baseline_shift = "-200%"
        else:
            y_offset = 0
            y_spine_x = axes._project_x(axes.y.spine._position)
            y_ticks_above = 3
            y_ticks_below = 3
            y_tick_labels_baseline_shift = "80%"
            y_label_baseline_shift = "200%"

        _render(canvas, axes.x, context.copy(
            root=axes_xml,
            x1=axes._xmin_range,
            y1=x_spine_y,
            x2=axes._xmax_range,
            y2=x_spine_y,
            offset=x_offset,
            ticks_above=x_ticks_above,
            ticks_below=x_ticks_below,
            tick_labels_baseline_shift=x_tick_labels_baseline_shift,
            label_baseline_shift=x_label_baseline_shift,
            ))

        _render(canvas, axes.y, context.copy(
            root=axes_xml,
            x1=y_spine_x,
            y1=axes._ymax_range,
            x2=y_spine_x,
            y2=axes._ymin_range,
            offset=y_offset,
            ticks_above=y_ticks_above,
            ticks_below=y_ticks_below,
            tick_labels_baseline_shift=y_tick_labels_baseline_shift,
            label_baseline_shift=y_label_baseline_shift,
            ))

        _draw_text(
            root=axes_xml,
            text=axes.label._text,
            x=(axes._xmin_range + axes._xmax_range) * 0.5,
            y=axes._ymin_range,
            style=axes.label._style,
            )


@dispatch(toyplot.canvas.Canvas, toyplot.axes.Table, _RenderContext)
def _render(canvas, axes, context):
    axes._finalize()

    axes_xml = xml.SubElement(context.root, "g", id=context.get_id(
        axes), attrib={"class": "toyplot-axes-Table"})

    # Render title
    _draw_text(
        root=axes_xml,
        text=axes._label._text,
        x=(axes._xmin_range + axes._xmax_range) * 0.5,
        y=axes._ymin_range,
        style=axes._label._style,
        )

    # Render children.
    for child in axes._children:
        _render(axes._parent, child, context.copy(root=axes_xml))

    # Render visible cells.
    for cell in axes._visible_cells:
        if cell._bstyle is not None:
            cell_xml = xml.SubElement(
                axes_xml,
                "rect",
                x=repr(
                    cell.left),
                y=repr(
                    cell.top),
                width=repr(
                    cell.right -
                    cell.left),
                height=repr(
                    cell.bottom -
                    cell.top),
                style=_css_style(
                    cell._bstyle))
            if cell._title is not None:
                xml.SubElement(cell_xml, "title").text = str(cell._title)

        if cell._data is None:
            continue

        prefix, separator, suffix = cell._format.format(cell._data)

        padding = 5

        column_left = cell.left + padding
        column_right = cell.right - padding
        column_center = (cell.left + cell.right) / 2

        row_top = cell.top
        row_bottom = cell.bottom
        row_center = (cell.top + cell.bottom) / 2

        y = row_center + cell._row_offset

        if cell._align == "left":
            x = column_left + cell._column_offset
            _draw_text(
                root=axes_xml,
                x=x,
                y=y,
                style=toyplot.style.combine(cell._style, {"text-anchor": "begin"}),
                text=prefix + separator + suffix,
                )
        elif cell._align == "center":
            x = column_center + cell._column_offset
            _draw_text(
                root=axes_xml,
                x=x,
                y=y,
                angle=-cell._angle,
                style=toyplot.style.combine(cell._style, {"text-anchor": "middle"}),
                text=prefix + separator + suffix,
                )
        elif cell._align == "right":
            x = column_right + cell._column_offset
            _draw_text(
                root=axes_xml,
                x=x,
                y=y,
                style=toyplot.style.combine(cell._style, {"text-anchor": "end"}),
                text=prefix + separator + suffix,
                )
        elif cell._align is "separator":
            x = column_center + cell._column_offset
            _draw_text(
                root=axes_xml,
                x=x - 2,
                y=y,
                style=toyplot.style.combine(cell._style, {"text-anchor": "end"}),
                text=prefix,
                )
            _draw_text(
                root=axes_xml,
                x=x,
                y=y,
                style=toyplot.style.combine(cell._style, {"text-anchor": "middle"}),
                text=separator,
                )
            _draw_text(
                root=axes_xml,
                x=x + 2,
                y=y,
                style=toyplot.style.combine(cell._style, {"text-anchor": "begin"}),
                text=suffix,
                )

    # Render grid lines.
    column_boundaries = axes._column_boundaries
    row_boundaries = axes._row_boundaries
    separation = axes._separation / 2

    def contiguous(a):
        i = 0
        result = []
        for (k, g) in itertools.groupby(a.ravel()):
            n = len(list(g))
            if k:
                result.append((i, i + n, k))
            i += n
        return result

    hlines = numpy.copy(axes._hlines)
    hlines[axes._hmask] = False
    for row_index, row in enumerate(hlines):
        y = row_boundaries[row_index]
        for start, end, line_type in contiguous(row):
            if line_type == "single":
                xml.SubElement(
                    axes_xml,
                    "line",
                    x1=repr(column_boundaries[start]),
                    y1=repr(y),
                    x2=repr(column_boundaries[end]),
                    y2=repr(y),
                    style=_css_style(axes._gstyle),
                    )
            elif line_type == "double":
                xml.SubElement(
                    axes_xml,
                    "line",
                    x1=repr(
                        column_boundaries[start]),
                    y1=repr(
                        y - separation),
                    x2=repr(
                        column_boundaries[end]),
                    y2=repr(
                        y - separation),
                    style=_css_style(
                        axes._gstyle))
                xml.SubElement(
                    axes_xml,
                    "line",
                    x1=repr(
                        column_boundaries[start]),
                    y1=repr(
                        y + separation),
                    x2=repr(
                        column_boundaries[end]),
                    y2=repr(
                        y + separation),
                    style=_css_style(
                        axes._gstyle))

    vlines = numpy.copy(axes._vlines)
    vlines[axes._vmask] = False
    for column_index, column in enumerate(vlines.T):
        x = column_boundaries[column_index]
        for start, end, line_type in contiguous(column):
            if line_type == "single":
                xml.SubElement(
                    axes_xml,
                    "line",
                    x1=repr(x),
                    y1=repr(row_boundaries[start]),
                    x2=repr(x),
                    y2=repr(row_boundaries[end]),
                    style=_css_style(axes._gstyle),
                    )
            elif line_type == "double":
                xml.SubElement(
                    axes_xml,
                    "line",
                    x1=repr(x - separation),
                    y1=repr(row_boundaries[start]),
                    x2=repr(x - separation),
                    y2=repr(row_boundaries[end]),
                    style=_css_style(axes._gstyle),
                    )
                xml.SubElement(
                    axes_xml,
                    "line",
                    x1=repr(x + separation),
                    y1=repr(row_boundaries[start]),
                    x2=repr(x + separation),
                    y2=repr(row_boundaries[end]),
                    style=_css_style(axes._gstyle),
                    )


@dispatch(toyplot.axes.Cartesian, toyplot.mark.BarBoundaries, _RenderContext)
def _render(axes, mark, context):
    left = mark._table[mark._left[0]]
    right = mark._table[mark._right[0]]
    boundaries = numpy.ma.column_stack(
        [mark._table[key] for key in mark._boundaries])

    if mark._coordinate_axes.tolist() == ["x", "y"]:
        axis1 = "x"
        axis2 = "y"
        distance1 = "width"
        distance2 = "height"
        left = axes._project_x(left)
        right = axes._project_x(right)
        boundaries = axes._project_y(boundaries)
    elif mark._coordinate_axes.tolist() == ["y", "x"]:
        axis1 = "y"
        axis2 = "x"
        distance1 = "height"
        distance2 = "width"
        left = axes._project_y(left)
        right = axes._project_y(right)
        boundaries = axes._project_x(boundaries)

    mark_xml = xml.SubElement(
        context.root,
        "g",
        style=_css_style(
            mark._style),
        id=context.get_id(mark),
        attrib={
            "class": "toyplot-mark-BarBoundaries"})
    context.add_data_table(mark, mark._table, title="Bar Data", filename=mark._filename)

    for boundary1, boundary2, fill, opacity, title in zip(
            boundaries.T[:-1],
            boundaries.T[1:],
            [mark._table[key] for key in mark._fill],
            [mark._table[key] for key in mark._opacity],
            [mark._table[key] for key in mark._title],
        ):
        not_null = numpy.invert(
            numpy.logical_or(
                numpy.ma.getmaskarray(boundary1),
                numpy.ma.getmaskarray(boundary2)))

        series_xml = xml.SubElement(
            mark_xml, "g", attrib={"class": "toyplot-Series"})
        for dleft, dright, dboundary1, dboundary2, dfill, dopacity, dtitle in zip(
                left[not_null],
                right[not_null],
                boundary1[not_null],
                boundary2[not_null],
                fill[not_null],
                opacity[not_null],
                title[not_null],
            ):
            dstyle = toyplot.style.combine({
                "fill": toyplot.color.to_css(dfill),
                "opacity": dopacity,
                }, mark._style)
            datum_xml = xml.SubElement(
                series_xml,
                "rect",
                attrib={
                    "class": "toyplot-Datum",
                    axis1: repr(min(dleft, dright)),
                    axis2: repr(min(dboundary1, dboundary2)),
                    distance1: repr(numpy.abs(dleft - dright)),
                    distance2: repr(numpy.abs(dboundary1 - dboundary2)),
                    },
                style=_css_style(dstyle),
                )
            if dtitle is not None:
                xml.SubElement(datum_xml, "title").text = str(dtitle)


@dispatch(toyplot.axes.Cartesian, toyplot.mark.BarMagnitudes, _RenderContext)
def _render(axes, mark, context):
    left = mark._table[mark._left[0]]
    right = mark._table[mark._right[0]]
    boundaries = numpy.ma.cumsum(numpy.ma.column_stack(
        [mark._table[mark._baseline[0]]] + [mark._table[key] for key in mark._magnitudes]), axis=1)
    not_null = numpy.invert(
        numpy.ma.any(numpy.ma.getmaskarray(boundaries), axis=1))

    if mark._coordinate_axes.tolist() == ["x", "y"]:
        axis1 = "x"
        axis2 = "y"
        distance1 = "width"
        distance2 = "height"
        left = axes._project_x(left)
        right = axes._project_x(right)
        boundaries = axes._project_y(boundaries)
    elif mark._coordinate_axes.tolist() == ["y", "x"]:
        axis1 = "y"
        axis2 = "x"
        distance1 = "height"
        distance2 = "width"
        left = axes._project_y(left)
        right = axes._project_y(right)
        boundaries = axes._project_x(boundaries)

    mark_xml = xml.SubElement(
        context.root,
        "g",
        style=_css_style(
            mark._style),
        id=context.get_id(mark),
        attrib={
            "class": "toyplot-mark-BarMagnitudes"})
    context.add_data_table(mark, mark._table, title="Bar Data", filename=mark._filename)

    for boundary1, boundary2, fill, opacity, title in zip(
            boundaries.T[:-1],
            boundaries.T[1:],
            [mark._table[key] for key in mark._fill],
            [mark._table[key] for key in mark._opacity],
            [mark._table[key] for key in mark._title],
        ):
        series_xml = xml.SubElement(
            mark_xml, "g", attrib={"class": "toyplot-Series"})
        for dleft, dright, dboundary1, dboundary2, dfill, dopacity, dtitle in zip(
                left[not_null],
                right[not_null],
                boundary1[not_null],
                boundary2[not_null],
                fill[not_null],
                opacity[not_null],
                title[not_null],
            ):
            dstyle = toyplot.style.combine(
                {"fill": toyplot.color.to_css(dfill), "opacity": dopacity}, mark._style)
            datum_xml = xml.SubElement(
                series_xml,
                "rect",
                attrib={
                    "class": "toyplot-Datum",
                    axis1: repr(min(dleft, dright)),
                    axis2: repr(min(dboundary1, dboundary2)),
                    distance1: repr(numpy.abs(dleft - dright)),
                    distance2: repr(numpy.abs(dboundary1 - dboundary2)),
                    },
                style=_css_style(dstyle),
                )
            if dtitle is not None:
                xml.SubElement(datum_xml, "title").text = str(dtitle)


@dispatch(toyplot.axes.Cartesian, toyplot.mark.FillBoundaries, _RenderContext)
def _render(axes, mark, context):
    boundaries = numpy.ma.column_stack(
        [mark._table[key] for key in mark._boundaries])

    if mark._coordinate_axes.tolist() == ["x", "y"]:
        position = axes._project_x(mark._table[mark._position[0]])
        boundaries = axes._project_y(boundaries)
    elif mark._coordinate_axes.tolist() == ["y", "x"]:
        position = axes._project_y(mark._table[mark._position[0]])
        boundaries = axes._project_x(boundaries)

    mark_xml = xml.SubElement(
        context.root,
        "g",
        style=_css_style(
            mark._style),
        id=context.get_id(mark),
        attrib={
            "class": "toyplot-mark-FillBoundaries"})
    context.add_data_table(mark, mark._table, title="Fill Data", filename=mark._filename)

    for boundary1, boundary2, fill, opacity, title in zip(
            boundaries.T[:-1], boundaries.T[1:], mark._fill, mark._opacity, mark._title):
        not_null = numpy.invert(
            numpy.logical_or(
                numpy.ma.getmaskarray(boundary1),
                numpy.ma.getmaskarray(boundary2)))
        segments = _flat_contiguous(not_null)

        series_style = toyplot.style.combine(
            {"fill": toyplot.color.to_css(fill), "opacity": opacity}, mark._style)

        for segment in segments:
            if mark._coordinate_axes[0] == "x":
                coordinates = zip(
                    numpy.concatenate((position[segment], position[segment][::-1])),
                    numpy.concatenate((boundary1[segment], boundary2[segment][::-1])))
            elif mark._coordinate_axes[0] == "y":
                coordinates = zip(
                    numpy.concatenate((boundary1[segment], boundary2[segment][::-1])),
                    numpy.concatenate((position[segment], position[segment][::-1])))
            series_xml = xml.SubElement(mark_xml, "polygon", points=" ".join(
                ["%r,%r" % (xi, yi) for xi, yi in coordinates]), style=_css_style(series_style))
            if title is not None:
                xml.SubElement(series_xml, "title").text = str(title)


@dispatch(toyplot.axes.Cartesian, toyplot.mark.FillMagnitudes, _RenderContext)
def _render(axes, mark, context):
    magnitudes = numpy.ma.column_stack(
        [mark._table[mark._baseline[0]]] + [mark._table[key] for key in mark._magnitudes])
    boundaries = numpy.ma.cumsum(magnitudes, axis=1)
    not_null = numpy.invert(
        numpy.ma.any(numpy.ma.getmaskarray(boundaries), axis=1))
    segments = _flat_contiguous(not_null)

    if mark._coordinate_axes.tolist() == ["x", "y"]:
        position = axes._project_x(mark._table[mark._position[0]])
        boundaries = axes._project_y(boundaries)
    elif mark._coordinate_axes.tolist() == ["y", "x"]:
        position = axes._project_y(mark._table[mark._position[0]])
        boundaries = axes._project_x(boundaries)

    mark_xml = xml.SubElement(
        context.root,
        "g",
        style=_css_style(
            mark._style),
        id=context.get_id(mark),
        attrib={
            "class": "toyplot-mark-FillMagnitudes"})
    context.add_data_table(mark, mark._table, title="Fill Data", filename=mark._filename)

    for boundary1, boundary2, fill, opacity, title in zip(
            boundaries.T[:-1], boundaries.T[1:], mark._fill, mark._opacity, mark._title):
        series_style = toyplot.style.combine(
            {"fill": toyplot.color.to_css(fill), "opacity": opacity}, mark._style)
        for segment in segments:
            if mark._coordinate_axes[0] == "x":
                coordinates = zip(
                    numpy.concatenate((position[segment], position[segment][::-1])),
                    numpy.concatenate((boundary1[segment], boundary2[segment][::-1])))
            elif mark._coordinate_axes[0] == "y":
                coordinates = zip(
                    numpy.concatenate((boundary1[segment], boundary2[segment][::-1])),
                    numpy.concatenate((position[segment], position[segment][::-1])))
            series_xml = xml.SubElement(mark_xml, "polygon", points=" ".join(
                ["%r,%r" % (xi, yi) for xi, yi in coordinates]), style=_css_style(series_style))
            if title is not None:
                xml.SubElement(series_xml, "title").text = str(title)


@dispatch(toyplot.axes.Cartesian, toyplot.mark.AxisLines, _RenderContext)
def _render(axes, mark, context):
    if mark._coordinate_axes[0] == "x":
        p1 = "x1"
        p2 = "x2"
        b1 = "y1"
        b2 = "y2"
        position = axes._project_x(mark._table[mark._coordinates[0]])
        boundary1 = axes._ymin_range
        boundary2 = axes._ymax_range
    elif mark._coordinate_axes[0] == "y":
        p1 = "y1"
        p2 = "y2"
        b1 = "x1"
        b2 = "x2"
        position = axes._project_y(mark._table[mark._coordinates[0]])
        boundary1 = axes._xmin_range
        boundary2 = axes._xmax_range
    mark_xml = xml.SubElement(
        context.root,
        "g",
        style=_css_style(
            mark._style),
        id=context.get_id(mark),
        attrib={
            "class": "toyplot-mark-AxisLines"})
    series_xml = xml.SubElement(
        mark_xml, "g", attrib={"class": "toyplot-Series"})
    for dposition, dstroke, dopacity, dtitle in zip(
            position,
            mark._table[mark._stroke[0]],
            mark._table[mark._opacity[0]],
            mark._table[mark._title[0]],
        ):
        dstyle = toyplot.style.combine(
            {"stroke": toyplot.color.to_css(dstroke), "opacity": dopacity}, mark._style)
        datum_xml = xml.SubElement(
            series_xml,
            "line",
            attrib={
                "class": "toyplot-Datum",
                p1: repr(dposition),
                p2: repr(dposition),
                b1: repr(boundary1),
                b2: repr(boundary2),
            },
            style=_css_style(dstyle),
        )
        if dtitle is not None:
            xml.SubElement(datum_xml, "title").text = str(dtitle)


@dispatch((toyplot.canvas.Canvas, toyplot.axes.Cartesian), toyplot.mark.Legend, _RenderContext)
def _render(canvas, legend, context):
    x = legend._xmin
    y = legend._ymin
    width = legend._xmax - legend._xmin
    height = legend._ymax - legend._ymin
    xml.SubElement(
        context.root,
        "rect",
        x=repr(x),
        y=repr(y),
        width=repr(width),
        height=repr(height),
        style=_css_style(legend._style),
        id=context.get_id(legend),
        attrib={"class": "toyplot-mark-Legend"},
        )

    mark_count = len(legend._marks)
    if mark_count:
        mark_gutter = legend._gutter
        mark_height = (
            height - (legend._gutter * (mark_count + 1))) / mark_count

        for i, item in enumerate(legend._marks):
            mark_x = x + mark_gutter
            mark_y = y + ((i + 1) * mark_gutter) + (i * mark_height)
            mark_width = mark_height

            mark_style = {}
            if isinstance(item, tuple) and len(item) == 2:
                mark_label, mark = item
            elif isinstance(item, tuple) and len(item) == 3:
                mark_label, mark, mark_style = item

            if mark == "line":
                xml.SubElement(
                    context.root,
                    "line",
                    x1=repr(mark_x),
                    y1=repr(mark_y + mark_height),
                    x2=repr(mark_x + mark_width),
                    y2=repr(mark_y),
                    style=_css_style(mark_style),
                    )
            elif mark == "rect":
                xml.SubElement(
                    context.root,
                    "rect",
                    x=repr(mark_x),
                    y=repr(mark_y),
                    width=repr(mark_width),
                    height=repr(mark_height),
                    style=_css_style({"stroke": "none"}, mark_style),
                    )
            elif isinstance(mark, toyplot.mark.Plot):
                dstyle = toyplot.style.combine(
                    {"stroke": toyplot.color.to_css(mark._stroke[0])}, mark._style)
                xml.SubElement(
                    context.root,
                    "line",
                    x1=repr(mark_x),
                    y1=repr(mark_y + mark_height),
                    x2=repr(mark_x + mark_width),
                    y2=repr(mark_y),
                    style=_css_style(dstyle, mark_style))
            elif isinstance(mark, toyplot.mark.Scatterplot):
                dstyle = toyplot.style.combine(
                    {
                        "fill": toyplot.color.to_css(mark._table[mark._mfill[0]][0]),
                        "stroke": toyplot.color.to_css(mark._table[mark._mstroke[0]][0]),
                        "opacity": mark._table[mark._mopacity[0]][0],
                    },
                    mark_style)
                _draw_marker(
                    context.root,
                    mark_x + (mark_width / 2),
                    mark_y + (mark_height / 2),
                    min(mark_width, mark_height),
                    mark._table[mark._marker[0]][0],
                    dstyle,
                    {},
                    )
                pass
            elif isinstance(mark, (toyplot.mark.BarBoundaries, toyplot.mark.BarMagnitudes, toyplot.mark.FillBoundaries, toyplot.mark.FillMagnitudes)):
                dstyle = toyplot.style.combine({"fill": toyplot.color.to_css(
                    mark._fill[0]), "opacity": mark._opacity[0]}, mark._style)
                xml.SubElement(
                    context.root,
                    "rect",
                    x=repr(mark_x),
                    y=repr(mark_y),
                    width=repr(mark_width),
                    height=repr(mark_height),
                    style=_css_style(dstyle, mark_style),
                    )
            else:
                computed_style = toyplot.style.combine(
                    {"stroke": toyplot.color.near_black, "fill": "none"}, mark_style)
                _draw_marker(
                    context.root,
                    mark_x + (mark_width / 2),
                    mark_y + (mark_height / 2),
                    min(mark_width, mark_height),
                    mark,
                    computed_style,
                    {},
                    )

            _draw_text(
                root=context.root,
                text=mark_label,
                x=x + mark_width + (2 * mark_gutter),
                y=y + ((i + 1) * mark_gutter) +  (i * mark_height) + (mark_height / 2),
                style=legend._lstyle,
                )


@dispatch(toyplot.axes.Cartesian, toyplot.mark.Graph, _RenderContext)
def _render(axes, mark, context): # pragma: no cover
    # Project edge coordinates
    for i in range(2):
        if mark._coordinate_axes[i] == "x":
            x = axes._project_x(mark._ecoordinates.T[i])
        elif mark._coordinate_axes[i] == "y":
            y = axes._project_y(mark._ecoordinates.T[i])

    mark_xml = xml.SubElement(context.root, "g", id=context.get_id(mark), attrib={"class": "toyplot-mark-Graph"})
    #context.add_data_table(mark, mark._vtable, title="Graph Vertex Data", filename=mark._vertex_filename)
    #context.add_data_table(mark, mark._etable, title="Graph Edge Data", filename=mark._edge_filename)

    coordinate_index = 0
    edge_xml = xml.SubElement(mark_xml, "g", attrib={"class": "toyplot-Edges"})
    for esource, etarget, eshape, ecolor, ewidth, eopacity in zip(
            mark._etable[mark._esource[0]],
            mark._etable[mark._etarget[0]],
            mark._etable[mark._eshape[0]],
            mark._etable[mark._ecolor[0]],
            mark._etable[mark._ewidth[0]],
            mark._etable[mark._eopacity[0]],
        ):
        estyle = toyplot.style.combine(
            {
                "fill": "none",
                "stroke": toyplot.color.to_css(ecolor),
                "stroke-width": ewidth,
                "stroke-opacity": eopacity,
            },
            mark._estyle)

        path = []
        for segment in eshape:
            if segment == "M":
                count = 1
            elif segment == "L":
                count = 1
            elif segment == "Q":
                count = 2
            elif segment == "C":
                count = 3
            path.append(segment)
            for i in range(count):
                path.append(str(x[coordinate_index]))
                path.append(str(y[coordinate_index]))
                coordinate_index += 1

        xml.SubElement(
            edge_xml,
            "path",
            d=" ".join(path),
            style=_css_style(estyle),
            )

    # Project vertex coordinates
    for i in range(2):
        if mark._coordinate_axes[i] == "x":
            x = axes._project_x(mark._vtable[mark._vcoordinates[i]])
        elif mark._coordinate_axes[i] == "y":
            y = axes._project_y(mark._vtable[mark._vcoordinates[i]])

    vertex_xml = xml.SubElement(mark_xml, "g", attrib={"class": "toyplot-Vertices"})
    for vx, vy, vmarker, vsize, vcolor, vopacity, vtitle in zip(
            x,
            y,
            mark._vtable[mark._vmarker[0]],
            mark._vtable[mark._vsize[0]],
            mark._vtable[mark._vcolor[0]],
            mark._vtable[mark._vopacity[0]],
            mark._vtable[mark._vtitle[0]],
        ):
        vstyle = toyplot.style.combine(
            {
                "fill": toyplot.color.to_css(vcolor),
                "stroke": toyplot.color.to_css(vcolor),
                "opacity": vopacity,
            },
            mark._vstyle)
        _draw_marker(
            vertex_xml,
            vx,
            vy,
            vsize,
            vmarker,
            vstyle,
            mark._vlstyle,
            extra_class="toyplot-Datum",
            title=vtitle,
            )

    # Render vertex labels
    if mark._vlshow:
        vlabel_xml = xml.SubElement(mark_xml, "g", attrib={"class": "toyplot-Labels"})
        for dx, dy, dtext in zip(x, y, mark._vtable[mark._vlabel[0]]):
            _draw_text(
                root=vlabel_xml,
                text=toyplot.compatibility.unicode_type(dtext),
                x=dx,
                y=dy,
                style=mark._vlstyle,
                attributes={"class": "toyplot-Datum"},
                )


@dispatch(toyplot.axes.Cartesian, toyplot.mark.Plot, _RenderContext)
def _render(axes, mark, context):
    position = mark._table[mark._coordinates[0]]
    series = numpy.ma.column_stack([mark._table[key] for key in mark._series])

    if mark._coordinate_axes[0] == "x":
        position = axes._project_x(position)
        series = axes._project_y(series)
    elif mark._coordinate_axes[0] == "y":
        position = axes._project_y(position)
        series = axes._project_x(series)

    mark_xml = xml.SubElement(
        context.root,
        "g",
        style=_css_style(toyplot.style.combine({"fill":"none"}, mark._style)),
        id=context.get_id(mark),
        attrib={
            "class": "toyplot-mark-Plot"})
    context.add_data_table(mark, mark._table, title="Plot Data", filename=mark._filename)

    for series, stroke, stroke_width, stroke_opacity, stroke_title, marker, msize, mfill, mstroke, mopacity, mtitle in zip(
            series.T,
            mark._stroke.T,
            mark._stroke_width.T,
            mark._stroke_opacity.T,
            mark._stroke_title.T,
            [mark._table[key] for key in mark._marker],
            [mark._table[key] for key in mark._msize],
            [mark._table[key] for key in mark._mfill],
            [mark._table[key] for key in mark._mstroke],
            [mark._table[key] for key in mark._mopacity],
            [mark._table[key] for key in mark._mtitle],
        ):
        not_null = numpy.invert(numpy.logical_or(
            numpy.ma.getmaskarray(position), numpy.ma.getmaskarray(series)))
        segments = _flat_contiguous(not_null)

        stroke_style = toyplot.style.combine(
            {
                "stroke": toyplot.color.to_css(stroke),
                "stroke-width": stroke_width,
                "stroke-opacity": stroke_opacity},
            mark._style)
        if mark._coordinate_axes[0] == "x":
            x = position
            y = series
        elif mark._coordinate_axes[0] == "y":
            x = series
            y = position
        series_xml = xml.SubElement(
            mark_xml, "g", attrib={"class": "toyplot-Series"})
        if stroke_title is not None:
            xml.SubElement(series_xml, "title").text = str(stroke_title)

        d = []
        for segment in segments:
            start, stop, step = segment.indices(len(not_null))
            for i in range(start, start + 1):
                d.append("M %r %r" % (x[i], y[i]))
            for i in range(start + 1, stop):
                d.append("L %r %r" % (x[i], y[i]))
        xml.SubElement(
            series_xml,
            "path",
            d=" ".join(d),
            style=_css_style(stroke_style))
        for dx, dy, dmarker, dsize, dfill, dstroke, dopacity, dtitle in zip(
                x[not_null],
                y[not_null],
                marker[not_null],
                msize[not_null],
                mfill[not_null],
                mstroke[not_null],
                mopacity[not_null],
                mtitle[not_null],
            ):
            dstyle = toyplot.style.combine(
                {
                    "fill": toyplot.color.to_css(dfill),
                    "stroke": toyplot.color.to_css(dstroke),
                    "opacity": dopacity},
                mark._mstyle)
            datum_xml = _draw_marker(
                series_xml,
                dx,
                dy,
                dsize,
                dmarker,
                dstyle,
                mark._mlstyle,
                extra_class="toyplot-Datum",
                title=dtitle,
                )


@dispatch(toyplot.axes.Cartesian, toyplot.mark.Rect, _RenderContext)
def _render(axes, mark, context):
    if mark._coordinate_axes.tolist() == ["x", "y"]:
        x1 = axes._project_x(mark._table[mark._left[0]])
        x2 = axes._project_x(mark._table[mark._right[0]])
        y1 = axes._project_y(mark._table[mark._top[0]])
        y2 = axes._project_y(mark._table[mark._bottom[0]])
    elif mark._coordinate_axes.tolist() == ["y", "x"]:
        x1 = axes._project_x(mark._table[mark._top[0]])
        x2 = axes._project_x(mark._table[mark._bottom[0]])
        y1 = axes._project_y(mark._table[mark._left[0]])
        y2 = axes._project_y(mark._table[mark._right[0]])
    mark_xml = xml.SubElement(
        context.root,
        "g",
        style=_css_style(
            mark._style),
        id=context.get_id(mark),
        attrib={
            "class": "toyplot-mark-Rect"})
    context.add_data_table(mark, mark._table, title="Rect Data", filename=mark._filename)

    series_xml = xml.SubElement(
        mark_xml, "g", attrib={"class": "toyplot-Series"})
    for dx1, dx2, dy1, dy2, dfill, dopacity, dtitle in zip(
            x1,
            x2,
            y1,
            y2,
            mark._table[mark._fill[0]],
            mark._table[mark._opacity[0]],
            mark._table[mark._title[0]],
        ):
        dstyle = toyplot.style.combine(
            {"fill": toyplot.color.to_css(dfill), "opacity": dopacity}, mark._style)
        datum_xml = xml.SubElement(
            series_xml,
            "rect",
            attrib={"class": "toyplot-Datum"},
            x=repr(min(dx1, dx2)),
            y=repr(min(dy1, dy2)),
            width=repr(numpy.abs(dx1 - dx2)),
            height=repr(numpy.abs(dy1 - dy2)),
            style=_css_style(dstyle),
            )
        if dtitle is not None:
            xml.SubElement(datum_xml, "title").text = str(dtitle)


@dispatch(toyplot.axes.Cartesian, toyplot.mark.Scatterplot, _RenderContext)
def _render(axes, mark, context):
    dimension1 = numpy.ma.column_stack([mark._table[key] for key in mark._coordinates[0::2]])
    dimension2 = numpy.ma.column_stack([mark._table[key] for key in mark._coordinates[1::2]])

    if mark._coordinate_axes[0] == "x":
        X = axes._project_x(dimension1)
        Y = axes._project_y(dimension2)
    elif mark._coordinate_axes[0] == "y":
        X = axes._project_x(dimension2)
        Y = axes._project_y(dimension1)

    mark_xml = xml.SubElement(
        context.root,
        "g",
        style=_css_style(mark._style),
        id=context.get_id(mark),
        attrib={"class": "toyplot-mark-Scatterplot"},
        )
    context.add_data_table(mark, mark._table, title="Scatterplot Data", filename=mark._filename)

    for x, y, marker, msize, mfill, mstroke, mopacity, mtitle in zip(
            X.T,
            Y.T,
            [mark._table[key] for key in mark._marker],
            [mark._table[key] for key in mark._msize],
            [mark._table[key] for key in mark._mfill],
            [mark._table[key] for key in mark._mstroke],
            [mark._table[key] for key in mark._mopacity],
            [mark._table[key] for key in mark._mtitle],
        ):
        not_null = numpy.invert(numpy.logical_or(
            numpy.ma.getmaskarray(x), numpy.ma.getmaskarray(y)))

        series_xml = xml.SubElement(
            mark_xml, "g", attrib={"class": "toyplot-Series"})
        for dx, dy, dmarker, dsize, dfill, dstroke, dopacity, dtitle in zip(
                x[not_null],
                y[not_null],
                marker[not_null],
                msize[not_null],
                mfill[not_null],
                mstroke[not_null],
                mopacity[not_null],
                mtitle[not_null],
            ):
            dstyle = toyplot.style.combine(
                {
                    "fill": toyplot.color.to_css(dfill),
                    "stroke": toyplot.color.to_css(dstroke),
                    "opacity": dopacity,
                },
                mark._mstyle)
            datum_xml = _draw_marker(
                series_xml,
                dx,
                dy,
                dsize,
                dmarker,
                dstyle,
                mark._mlstyle,
                extra_class="toyplot-Datum",
                title=dtitle,
                )


@dispatch((toyplot.canvas.Canvas, toyplot.axes.Cartesian), toyplot.mark.Text, _RenderContext)
def _render(parent, mark, context):
    x = mark._table[mark._coordinates[numpy.where(mark._coordinate_axes == "x")[0][0]]]
    y = mark._table[mark._coordinates[numpy.where(mark._coordinate_axes == "y")[0][0]]]

    if isinstance(parent, toyplot.axes.Cartesian):
        x = parent._project_x(x)
        y = parent._project_y(y)

    mark_xml = xml.SubElement(
        context.root,
        "g",
        style=_css_style(
            mark._style),
        id=context.get_id(mark),
        attrib={
            "class": "toyplot-mark-Text"})
    context.add_data_table(mark, mark._table, title="Text Data", filename=mark._filename)
    series_xml = xml.SubElement(
        mark_xml, "g", attrib={"class": "toyplot-Series"})
    for dx, dy, dtext, dangle, dfill, dopacity, dtitle in zip(
            x,
            y,
            mark._table[mark._text[0]],
            mark._table[mark._angle[0]],
            mark._table[mark._fill[0]],
            mark._table[mark._opacity[0]],
            mark._table[mark._title[0]],
        ):

        _draw_text(
            root=series_xml,
            text=toyplot.compatibility.unicode_type(dtext),
            x=dx,
            y=dy,
            angle=-dangle,
            attributes={"class": "toyplot-Datum"},
            style=toyplot.style.combine({"fill": toyplot.color.to_css(dfill), "opacity": dopacity}, mark._style),
            title=dtitle,
            )

