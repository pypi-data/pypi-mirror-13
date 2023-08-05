var all_defaults, all_view_model_names, get_defaults;

all_defaults = {
  "AutocompleteInput": {
    "callback": null,
    "completions": [],
    "disabled": false,
    "name": null,
    "tags": [],
    "title": "",
    "value": ""
  },
  "Button": {
    "callback": null,
    "clicks": 0,
    "disabled": false,
    "icon": null,
    "label": "Button",
    "name": null,
    "tags": [],
    "type": "default"
  },
  "CheckboxButtonGroup": {
    "active": [],
    "disabled": false,
    "labels": [],
    "name": null,
    "tags": [],
    "type": "default"
  },
  "CheckboxGroup": {
    "active": [],
    "disabled": false,
    "inline": false,
    "labels": [],
    "name": null,
    "tags": []
  },
  "DataTable": {
    "columns": [],
    "disabled": false,
    "editable": false,
    "fit_columns": true,
    "height": 400,
    "name": null,
    "row_headers": true,
    "scroll_to_selection": true,
    "selectable": true,
    "sortable": true,
    "source": null,
    "tags": [],
    "width": null
  },
  "DatePicker": {
    "callback": null,
    "disabled": false,
    "max_date": null,
    "min_date": null,
    "name": null,
    "tags": [],
    "title": "",
    "value": 1452038400000.0
  },
  "DateRangeSlider": {
    "arrows": true,
    "bounds": null,
    "callback": null,
    "disabled": false,
    "enabled": true,
    "name": null,
    "range": null,
    "step": {},
    "tags": [],
    "title": "",
    "value": null,
    "value_labels": "show",
    "wheel_mode": null
  },
  "Dialog": {
    "buttons": [],
    "buttons_box": null,
    "closable": true,
    "content": "",
    "disabled": false,
    "name": null,
    "tags": [],
    "title": "",
    "visible": false
  },
  "Dropdown": {
    "callback": null,
    "default_value": null,
    "disabled": false,
    "icon": null,
    "label": "Dropdown",
    "menu": [],
    "name": null,
    "tags": [],
    "type": "default",
    "value": null
  },
  "HBox": {
    "children": [],
    "disabled": false,
    "height": null,
    "name": null,
    "tags": [],
    "width": null
  },
  "Icon": {
    "disabled": false,
    "flip": null,
    "icon_name": "check",
    "name": null,
    "size": null,
    "spin": false,
    "tags": []
  },
  "MultiSelect": {
    "callback": null,
    "disabled": false,
    "name": null,
    "options": [],
    "tags": [],
    "title": "",
    "value": []
  },
  "Panel": {
    "child": null,
    "closable": false,
    "disabled": false,
    "name": null,
    "tags": [],
    "title": ""
  },
  "PreText": {
    "disabled": false,
    "height": 400,
    "name": null,
    "tags": [],
    "text": "",
    "width": 500
  },
  "RadioButtonGroup": {
    "active": null,
    "disabled": false,
    "labels": [],
    "name": null,
    "tags": [],
    "type": "default"
  },
  "RadioGroup": {
    "active": null,
    "disabled": false,
    "inline": false,
    "labels": [],
    "name": null,
    "tags": []
  },
  "Select": {
    "callback": null,
    "disabled": false,
    "name": null,
    "options": [],
    "tags": [],
    "title": "",
    "value": ""
  },
  "Slider": {
    "callback": null,
    "disabled": false,
    "end": 1,
    "name": null,
    "orientation": "horizontal",
    "start": 0,
    "step": 0.1,
    "tags": [],
    "title": "",
    "value": 0.5
  },
  "Tabs": {
    "active": 0,
    "callback": null,
    "disabled": false,
    "name": null,
    "tabs": [],
    "tags": []
  },
  "Toggle": {
    "active": false,
    "callback": null,
    "disabled": false,
    "icon": null,
    "label": "Toggle",
    "name": null,
    "tags": [],
    "type": "default"
  },
  "VBoxForm": {
    "children": [],
    "disabled": false,
    "height": null,
    "name": null,
    "tags": [],
    "width": null
  }
};

get_defaults = function(name) {
  if (name in all_defaults) {
    return all_defaults[name];
  } else {
    return null;
  }
};

all_view_model_names = function() {
  return Object.keys(all_defaults);
};

module.exports = {
  get_defaults: get_defaults,
  all_view_model_names: all_view_model_names
};
