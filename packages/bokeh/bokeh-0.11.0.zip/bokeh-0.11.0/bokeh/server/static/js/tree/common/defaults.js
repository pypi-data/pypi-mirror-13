var all_defaults, all_view_model_names, get_defaults;

all_defaults = {
  "AjaxDataSource": {
    "callback": null,
    "column_names": [],
    "data": {},
    "data_url": null,
    "if_modified": false,
    "max_size": null,
    "method": "POST",
    "mode": "replace",
    "name": null,
    "polling_interval": null,
    "selected": {
      "0d": {
        "glyph": null,
        "indices": []
      },
      "1d": {
        "indices": []
      },
      "2d": {
        "indices": []
      }
    },
    "tags": []
  },
  "AnnularWedge": {
    "direction": "anticlock",
    "end_angle": null,
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "inner_radius": null,
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "outer_radius": null,
    "start_angle": null,
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "Annulus": {
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "inner_radius": null,
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "outer_radius": null,
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "Arc": {
    "direction": "anticlock",
    "end_angle": null,
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "radius": null,
    "start_angle": null,
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "Asterisk": {
    "angle": {
      "units": "rad",
      "value": 0.0
    },
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "size": {
      "units": "screen",
      "value": 4
    },
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "BBoxTileSource": {
    "attribution": "",
    "extra_url_vars": {},
    "initial_resolution": 156543.03392804097,
    "max_zoom": 30,
    "min_zoom": 0,
    "name": null,
    "tags": [],
    "tile_size": 256,
    "url": "",
    "use_latlon": false,
    "wrap_around": true,
    "x_origin_offset": 20037508.34,
    "y_origin_offset": 20037508.34
  },
  "BasicTickFormatter": {
    "name": null,
    "power_limit_high": 5,
    "power_limit_low": -3,
    "precision": "auto",
    "tags": [],
    "use_scientific": true
  },
  "BasicTicker": {
    "base": 10.0,
    "desired_num_ticks": 6,
    "mantissas": [1, 2, 5],
    "max_interval": null,
    "min_interval": 0.0,
    "name": null,
    "num_minor_ticks": 5,
    "tags": []
  },
  "Bezier": {
    "cx0": null,
    "cx1": null,
    "cy0": null,
    "cy1": null,
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "tags": [],
    "visible": true,
    "x0": null,
    "x1": null,
    "y0": null,
    "y1": null
  },
  "BlazeDataSource": {
    "callback": null,
    "column_names": [],
    "data": {},
    "data_url": null,
    "expr": {},
    "local": null,
    "name": null,
    "namespace": {},
    "polling_interval": null,
    "selected": {
      "0d": {
        "glyph": null,
        "indices": []
      },
      "1d": {
        "indices": []
      },
      "2d": {
        "indices": []
      }
    },
    "tags": []
  },
  "BooleanFormatter": {
    "icon": "check",
    "name": null,
    "tags": []
  },
  "BoxAnnotation": {
    "bottom": null,
    "bottom_units": "data",
    "fill_alpha": {
      "value": 0.4
    },
    "fill_color": {
      "value": "#fff9ba"
    },
    "left": null,
    "left_units": "data",
    "level": "annotation",
    "line_alpha": {
      "value": 0.3
    },
    "line_cap": "butt",
    "line_color": {
      "value": "#cccccc"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "plot": null,
    "render_mode": "canvas",
    "right": null,
    "right_units": "data",
    "tags": [],
    "top": null,
    "top_units": "data",
    "x_range_name": "default",
    "y_range_name": "default"
  },
  "BoxSelectTool": {
    "callback": null,
    "dimensions": ["width", "height"],
    "name": null,
    "names": [],
    "overlay": {
      "attributes": {
        "bottom": null,
        "bottom_units": "screen",
        "fill_alpha": {
          "value": 0.5
        },
        "fill_color": {
          "value": "lightgrey"
        },
        "left": null,
        "left_units": "screen",
        "level": "overlay",
        "line_alpha": {
          "value": 1.0
        },
        "line_cap": "butt",
        "line_color": {
          "value": "black"
        },
        "line_dash": [4, 4],
        "line_dash_offset": 0,
        "line_join": "miter",
        "line_width": {
          "value": 2
        },
        "name": null,
        "plot": null,
        "render_mode": "css",
        "right": null,
        "right_units": "screen",
        "tags": [],
        "top": null,
        "top_units": "screen",
        "x_range_name": "default",
        "y_range_name": "default"
      },
      "type": "BoxAnnotation"
    },
    "plot": null,
    "renderers": [],
    "select_every_mousemove": false,
    "tags": []
  },
  "BoxZoomTool": {
    "dimensions": ["width", "height"],
    "name": null,
    "overlay": {
      "attributes": {
        "bottom": null,
        "bottom_units": "screen",
        "fill_alpha": {
          "value": 0.5
        },
        "fill_color": {
          "value": "lightgrey"
        },
        "left": null,
        "left_units": "screen",
        "level": "overlay",
        "line_alpha": {
          "value": 1.0
        },
        "line_cap": "butt",
        "line_color": {
          "value": "black"
        },
        "line_dash": [4, 4],
        "line_dash_offset": 0,
        "line_join": "miter",
        "line_width": {
          "value": 2
        },
        "name": null,
        "plot": null,
        "render_mode": "css",
        "right": null,
        "right_units": "screen",
        "tags": [],
        "top": null,
        "top_units": "screen",
        "x_range_name": "default",
        "y_range_name": "default"
      },
      "type": "BoxAnnotation"
    },
    "plot": null,
    "tags": []
  },
  "CategoricalAxis": {
    "axis_label": "",
    "axis_label_standoff": 5,
    "axis_label_text_align": "center",
    "axis_label_text_alpha": {
      "value": 1.0
    },
    "axis_label_text_baseline": "alphabetic",
    "axis_label_text_color": {
      "value": "#444444"
    },
    "axis_label_text_font": "helvetica",
    "axis_label_text_font_size": {
      "value": "16pt"
    },
    "axis_label_text_font_style": "normal",
    "axis_line_alpha": {
      "value": 1.0
    },
    "axis_line_cap": "butt",
    "axis_line_color": {
      "value": "black"
    },
    "axis_line_dash": [],
    "axis_line_dash_offset": 0,
    "axis_line_join": "miter",
    "axis_line_width": {
      "value": 1
    },
    "bounds": "auto",
    "formatter": {
      "attributes": {
        "name": null,
        "tags": []
      },
      "type": "CategoricalTickFormatter"
    },
    "level": "overlay",
    "location": "auto",
    "major_label_orientation": "horizontal",
    "major_label_standoff": 5,
    "major_label_text_align": "center",
    "major_label_text_alpha": {
      "value": 1.0
    },
    "major_label_text_baseline": "alphabetic",
    "major_label_text_color": {
      "value": "#444444"
    },
    "major_label_text_font": "helvetica",
    "major_label_text_font_size": {
      "value": "10pt"
    },
    "major_label_text_font_style": "normal",
    "major_tick_in": 2,
    "major_tick_line_alpha": {
      "value": 1.0
    },
    "major_tick_line_cap": "butt",
    "major_tick_line_color": {
      "value": "black"
    },
    "major_tick_line_dash": [],
    "major_tick_line_dash_offset": 0,
    "major_tick_line_join": "miter",
    "major_tick_line_width": {
      "value": 1
    },
    "major_tick_out": 6,
    "minor_tick_in": 0,
    "minor_tick_line_alpha": {
      "value": 1.0
    },
    "minor_tick_line_cap": "butt",
    "minor_tick_line_color": {
      "value": "black"
    },
    "minor_tick_line_dash": [],
    "minor_tick_line_dash_offset": 0,
    "minor_tick_line_join": "miter",
    "minor_tick_line_width": {
      "value": 1
    },
    "minor_tick_out": 4,
    "name": null,
    "plot": null,
    "tags": [],
    "ticker": {
      "attributes": {
        "name": null,
        "tags": []
      },
      "type": "CategoricalTicker"
    },
    "visible": true,
    "x_range_name": "default",
    "y_range_name": "default"
  },
  "CategoricalTickFormatter": {
    "name": null,
    "tags": []
  },
  "CategoricalTicker": {
    "name": null,
    "tags": []
  },
  "CheckboxEditor": {
    "name": null,
    "tags": []
  },
  "Circle": {
    "angle": {
      "units": "rad",
      "value": 0.0
    },
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "radius": null,
    "radius_dimension": "x",
    "size": {
      "units": "screen",
      "value": 4
    },
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "CircleCross": {
    "angle": {
      "units": "rad",
      "value": 0.0
    },
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "size": {
      "units": "screen",
      "value": 4
    },
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "CircleX": {
    "angle": {
      "units": "rad",
      "value": 0.0
    },
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "size": {
      "units": "screen",
      "value": 4
    },
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "Cross": {
    "angle": {
      "units": "rad",
      "value": 0.0
    },
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "size": {
      "units": "screen",
      "value": 4
    },
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "CrosshairTool": {
    "dimensions": ["width", "height"],
    "line_alpha": 1.0,
    "line_color": "black",
    "line_width": 1,
    "name": null,
    "plot": null,
    "tags": []
  },
  "CustomJS": {
    "args": {},
    "code": "",
    "lang": "javascript",
    "name": null,
    "tags": []
  },
  "DataRange1d": {
    "bounds": null,
    "callback": null,
    "default_span": 2.0,
    "end": null,
    "flipped": false,
    "follow": null,
    "follow_interval": null,
    "name": null,
    "names": [],
    "range_padding": 0.1,
    "renderers": [],
    "start": null,
    "tags": []
  },
  "DateEditor": {
    "name": null,
    "tags": []
  },
  "DateFormatter": {
    "format": "yy M d",
    "name": null,
    "tags": []
  },
  "DatetimeAxis": {
    "axis_label": "",
    "axis_label_standoff": 5,
    "axis_label_text_align": "center",
    "axis_label_text_alpha": {
      "value": 1.0
    },
    "axis_label_text_baseline": "alphabetic",
    "axis_label_text_color": {
      "value": "#444444"
    },
    "axis_label_text_font": "helvetica",
    "axis_label_text_font_size": {
      "value": "16pt"
    },
    "axis_label_text_font_style": "normal",
    "axis_line_alpha": {
      "value": 1.0
    },
    "axis_line_cap": "butt",
    "axis_line_color": {
      "value": "black"
    },
    "axis_line_dash": [],
    "axis_line_dash_offset": 0,
    "axis_line_join": "miter",
    "axis_line_width": {
      "value": 1
    },
    "bounds": "auto",
    "formatter": {
      "attributes": {
        "formats": {},
        "name": null,
        "tags": []
      },
      "type": "DatetimeTickFormatter"
    },
    "level": "overlay",
    "location": "auto",
    "major_label_orientation": "horizontal",
    "major_label_standoff": 5,
    "major_label_text_align": "center",
    "major_label_text_alpha": {
      "value": 1.0
    },
    "major_label_text_baseline": "alphabetic",
    "major_label_text_color": {
      "value": "#444444"
    },
    "major_label_text_font": "helvetica",
    "major_label_text_font_size": {
      "value": "10pt"
    },
    "major_label_text_font_style": "normal",
    "major_tick_in": 2,
    "major_tick_line_alpha": {
      "value": 1.0
    },
    "major_tick_line_cap": "butt",
    "major_tick_line_color": {
      "value": "black"
    },
    "major_tick_line_dash": [],
    "major_tick_line_dash_offset": 0,
    "major_tick_line_join": "miter",
    "major_tick_line_width": {
      "value": 1
    },
    "major_tick_out": 6,
    "minor_tick_in": 0,
    "minor_tick_line_alpha": {
      "value": 1.0
    },
    "minor_tick_line_cap": "butt",
    "minor_tick_line_color": {
      "value": "black"
    },
    "minor_tick_line_dash": [],
    "minor_tick_line_dash_offset": 0,
    "minor_tick_line_join": "miter",
    "minor_tick_line_width": {
      "value": 1
    },
    "minor_tick_out": 4,
    "name": null,
    "plot": null,
    "tags": [],
    "ticker": {
      "attributes": {
        "desired_num_ticks": 6,
        "name": null,
        "num_minor_ticks": 0,
        "tags": [],
        "tickers": [
          {
            "id": "afbad0aa-ffab-44e5-b28e-3c976195cfc3",
            "type": "AdaptiveTicker"
          }, {
            "id": "36967e15-e0fd-4e83-92a5-253ab2df0d9a",
            "type": "AdaptiveTicker"
          }, {
            "id": "bd4e9060-9b8d-4126-b534-a36818d0819e",
            "type": "AdaptiveTicker"
          }, {
            "id": "8c9ffd97-f8bb-4446-a75c-f35690ed7f91",
            "type": "DaysTicker"
          }, {
            "id": "5666bc62-f707-483b-9f6a-f1e655fcbfa1",
            "type": "DaysTicker"
          }, {
            "id": "70bb9d02-445d-4216-9105-ef63fe5c7122",
            "type": "DaysTicker"
          }, {
            "id": "5ee977c5-acb2-4274-8c56-1e3c962413c0",
            "type": "DaysTicker"
          }, {
            "id": "08a2ee9d-8e2b-4108-9a54-925e7b1aa892",
            "type": "MonthsTicker"
          }, {
            "id": "d12ed532-0f67-4c8d-8e4f-a591baf9e3e7",
            "type": "MonthsTicker"
          }, {
            "id": "c3c69136-ade5-4486-a651-4fee04a81a66",
            "type": "MonthsTicker"
          }, {
            "id": "14f9e853-6c5c-44d9-a190-9866f722a03e",
            "type": "MonthsTicker"
          }, {
            "id": "4ec09c86-d1ac-4a01-898c-db009e73204d",
            "type": "YearsTicker"
          }
        ]
      },
      "type": "DatetimeTicker"
    },
    "visible": true,
    "x_range_name": "default",
    "y_range_name": "default"
  },
  "DatetimeTickFormatter": {
    "formats": {},
    "name": null,
    "tags": []
  },
  "DatetimeTicker": {
    "desired_num_ticks": 6,
    "name": null,
    "num_minor_ticks": 0,
    "tags": [],
    "tickers": [
      {
        "id": "65cbd9b0-ac7a-40b1-8492-6deaa3a78883",
        "type": "AdaptiveTicker"
      }, {
        "id": "2e891965-39e0-44ec-8c08-f9e9ff9e2068",
        "type": "AdaptiveTicker"
      }, {
        "id": "0734dcf7-a96a-48b3-b6a7-99d2d4c2eb97",
        "type": "AdaptiveTicker"
      }, {
        "id": "5e6ea5b7-81ad-4e10-b5b7-86cfa17420bb",
        "type": "DaysTicker"
      }, {
        "id": "8c87cab5-8c91-4c79-9df6-5d7dfb2cc4c5",
        "type": "DaysTicker"
      }, {
        "id": "98224787-8dc2-4ba1-ae9c-65d165a9882c",
        "type": "DaysTicker"
      }, {
        "id": "548c4898-72a1-4c7f-bab0-357e17f67b7f",
        "type": "DaysTicker"
      }, {
        "id": "23ba939b-22f9-46b6-b8e5-2fee59fa8bca",
        "type": "MonthsTicker"
      }, {
        "id": "5c5b4504-e011-4d33-8bb6-347109b7950e",
        "type": "MonthsTicker"
      }, {
        "id": "58074975-4f75-40ca-98fe-6e01e2b3bf3a",
        "type": "MonthsTicker"
      }, {
        "id": "a3731cd9-9bfa-4785-9589-023424f7047a",
        "type": "MonthsTicker"
      }, {
        "id": "6428ea87-6a25-4190-8b30-6c902582eb28",
        "type": "YearsTicker"
      }
    ]
  },
  "DaysTicker": {
    "days": [],
    "desired_num_ticks": 6,
    "interval": null,
    "name": null,
    "num_minor_ticks": 5,
    "tags": []
  },
  "Diamond": {
    "angle": {
      "units": "rad",
      "value": 0.0
    },
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "size": {
      "units": "screen",
      "value": 4
    },
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "DiamondCross": {
    "angle": {
      "units": "rad",
      "value": 0.0
    },
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "size": {
      "units": "screen",
      "value": 4
    },
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "DynamicImageRenderer": {
    "alpha": 1.0,
    "image_source": null,
    "level": "underlay",
    "name": null,
    "render_parents": true,
    "tags": []
  },
  "FactorRange": {
    "bounds": null,
    "callback": null,
    "factors": [],
    "name": null,
    "offset": 0,
    "tags": []
  },
  "FixedTicker": {
    "desired_num_ticks": 6,
    "name": null,
    "num_minor_ticks": 5,
    "tags": [],
    "ticks": []
  },
  "GMapPlot": {
    "above": [],
    "background_fill_alpha": {
      "value": 1.0
    },
    "background_fill_color": {
      "value": "#ffffff"
    },
    "below": [],
    "border_fill_alpha": {
      "value": 1.0
    },
    "border_fill_color": {
      "value": "#ffffff"
    },
    "disabled": false,
    "extra_x_ranges": {},
    "extra_y_ranges": {},
    "h_symmetry": true,
    "hidpi": true,
    "left": [],
    "lod_factor": 10,
    "lod_interval": 300,
    "lod_threshold": 2000,
    "lod_timeout": 500,
    "logo": "normal",
    "map_options": null,
    "min_border": 50,
    "min_border_bottom": 50,
    "min_border_left": 50,
    "min_border_right": 50,
    "min_border_top": 50,
    "name": null,
    "outline_line_alpha": {
      "value": 1.0
    },
    "outline_line_cap": "butt",
    "outline_line_color": {
      "value": "#aaaaaa"
    },
    "outline_line_dash": [],
    "outline_line_dash_offset": 0,
    "outline_line_join": "miter",
    "outline_line_width": {
      "value": 1
    },
    "plot_height": 600,
    "plot_width": 600,
    "renderers": [],
    "responsive": false,
    "right": [],
    "tags": [],
    "title": "",
    "title_standoff": 8,
    "title_text_align": "center",
    "title_text_alpha": {
      "value": 1.0
    },
    "title_text_baseline": "alphabetic",
    "title_text_color": {
      "value": "#444444"
    },
    "title_text_font": "helvetica",
    "title_text_font_size": {
      "value": "20pt"
    },
    "title_text_font_style": "normal",
    "tool_events": {
      "attributes": {
        "geometries": [],
        "name": null,
        "tags": []
      },
      "type": "ToolEvents"
    },
    "toolbar_location": "above",
    "tools": [],
    "v_symmetry": false,
    "webgl": false,
    "x_mapper_type": "auto",
    "x_range": null,
    "y_mapper_type": "auto",
    "y_range": null
  },
  "Gear": {
    "angle": {
      "units": "rad",
      "value": 0
    },
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "internal": {
      "value": false
    },
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "module": null,
    "name": null,
    "pressure_angle": {
      "value": 20
    },
    "shaft_size": {
      "value": 0.3
    },
    "tags": [],
    "teeth": null,
    "visible": true,
    "x": null,
    "y": null
  },
  "GeoJSONDataSource": {
    "callback": null,
    "column_names": [],
    "data": {},
    "geojson": null,
    "name": null,
    "selected": {
      "0d": {
        "glyph": null,
        "indices": []
      },
      "1d": {
        "indices": []
      },
      "2d": {
        "indices": []
      }
    },
    "tags": []
  },
  "GlyphRenderer": {
    "data_source": null,
    "glyph": null,
    "hover_glyph": null,
    "level": "glyph",
    "name": null,
    "nonselection_glyph": null,
    "selection_glyph": null,
    "tags": [],
    "x_range_name": "default",
    "y_range_name": "default"
  },
  "Grid": {
    "band_fill_alpha": {
      "value": 0
    },
    "band_fill_color": {
      "value": null
    },
    "bounds": "auto",
    "dimension": 0,
    "grid_line_alpha": {
      "value": 1.0
    },
    "grid_line_cap": "butt",
    "grid_line_color": {
      "value": "#cccccc"
    },
    "grid_line_dash": [],
    "grid_line_dash_offset": 0,
    "grid_line_join": "miter",
    "grid_line_width": {
      "value": 1
    },
    "level": "underlay",
    "minor_grid_line_alpha": {
      "value": 1.0
    },
    "minor_grid_line_cap": "butt",
    "minor_grid_line_color": {
      "value": null
    },
    "minor_grid_line_dash": [],
    "minor_grid_line_dash_offset": 0,
    "minor_grid_line_join": "miter",
    "minor_grid_line_width": {
      "value": 1
    },
    "name": null,
    "plot": null,
    "tags": [],
    "ticker": null,
    "x_range_name": "default",
    "y_range_name": "default"
  },
  "GridPlot": {
    "border_space": 0,
    "children": [[]],
    "disabled": false,
    "name": null,
    "tags": [],
    "toolbar_location": "left"
  },
  "HTMLTemplateFormatter": {
    "name": null,
    "tags": [],
    "template": "<%= value %>"
  },
  "HelpTool": {
    "help_tooltip": "Click the question mark to learn more about Bokeh plot tools.",
    "name": null,
    "plot": null,
    "redirect": "http://bokeh.pydata.org/en/latest/docs/user_guide/tools.html",
    "tags": []
  },
  "HoverTool": {
    "always_active": true,
    "callback": null,
    "line_policy": "prev",
    "mode": "mouse",
    "name": null,
    "names": [],
    "plot": null,
    "point_policy": "snap_to_data",
    "renderers": [],
    "tags": [],
    "tooltips": [["index", "$index"], ["data (x, y)", "($x, $y)"], ["canvas (x, y)", "($sx, $sy)"]]
  },
  "Image": {
    "color_mapper": {
      "attributes": {
        "high": null,
        "low": null,
        "name": null,
        "palette": ["#000000", "#252525", "#525252", "#737373", "#969696", "#bdbdbd", "#d9d9d9", "#f0f0f0", "#ffffff"],
        "reserve_color": "#ffffff",
        "reserve_val": null,
        "tags": []
      },
      "type": "LinearColorMapper"
    },
    "dh": null,
    "dilate": false,
    "dw": null,
    "image": null,
    "name": null,
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "ImageRGBA": {
    "cols": null,
    "dh": null,
    "dilate": false,
    "dw": null,
    "image": null,
    "name": null,
    "rows": null,
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "ImageSource": {
    "extra_url_vars": {},
    "name": null,
    "tags": [],
    "url": ""
  },
  "ImageURL": {
    "anchor": "top_left",
    "angle": {
      "units": "rad",
      "value": 0
    },
    "dilate": false,
    "global_alpha": 1.0,
    "h": null,
    "name": null,
    "retry_attempts": 0,
    "retry_timeout": 0,
    "tags": [],
    "url": null,
    "visible": true,
    "w": null,
    "x": null,
    "y": null
  },
  "IntEditor": {
    "name": null,
    "step": 1,
    "tags": []
  },
  "InvertedTriangle": {
    "angle": {
      "units": "rad",
      "value": 0.0
    },
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "size": {
      "units": "screen",
      "value": 4
    },
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "LassoSelectTool": {
    "name": null,
    "names": [],
    "overlay": {
      "attributes": {
        "fill_alpha": {
          "value": 0.5
        },
        "fill_color": {
          "value": "lightgrey"
        },
        "level": "overlay",
        "line_alpha": {
          "value": 1.0
        },
        "line_cap": "butt",
        "line_color": {
          "value": "black"
        },
        "line_dash": [4, 4],
        "line_dash_offset": 0,
        "line_join": "miter",
        "line_width": {
          "value": 2
        },
        "name": null,
        "plot": null,
        "tags": [],
        "x_range_name": "default",
        "xs": [],
        "xs_units": "screen",
        "y_range_name": "default",
        "ys": [],
        "ys_units": "screen"
      },
      "type": "PolyAnnotation"
    },
    "plot": null,
    "renderers": [],
    "select_every_mousemove": true,
    "tags": []
  },
  "LayoutBox": {
    "name": null,
    "tags": []
  },
  "Legend": {
    "background_fill_alpha": {
      "value": 1.0
    },
    "background_fill_color": {
      "value": "#ffffff"
    },
    "border_line_alpha": {
      "value": 1.0
    },
    "border_line_cap": "butt",
    "border_line_color": {
      "value": "black"
    },
    "border_line_dash": [],
    "border_line_dash_offset": 0,
    "border_line_join": "miter",
    "border_line_width": {
      "value": 1
    },
    "glyph_height": 20,
    "glyph_width": 20,
    "label_height": 20,
    "label_standoff": 15,
    "label_text_align": "left",
    "label_text_alpha": {
      "value": 1.0
    },
    "label_text_baseline": "middle",
    "label_text_color": {
      "value": "#444444"
    },
    "label_text_font": "helvetica",
    "label_text_font_size": {
      "value": "10pt"
    },
    "label_text_font_style": "normal",
    "label_width": 50,
    "legend_padding": 10,
    "legend_spacing": 3,
    "legends": [],
    "level": "annotation",
    "location": "top_right",
    "name": null,
    "plot": null,
    "tags": []
  },
  "Line": {
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "LinearColorMapper": {
    "high": null,
    "low": null,
    "name": null,
    "palette": null,
    "reserve_color": "#ffffff",
    "reserve_val": null,
    "tags": []
  },
  "LogAxis": {
    "axis_label": "",
    "axis_label_standoff": 5,
    "axis_label_text_align": "center",
    "axis_label_text_alpha": {
      "value": 1.0
    },
    "axis_label_text_baseline": "alphabetic",
    "axis_label_text_color": {
      "value": "#444444"
    },
    "axis_label_text_font": "helvetica",
    "axis_label_text_font_size": {
      "value": "16pt"
    },
    "axis_label_text_font_style": "normal",
    "axis_line_alpha": {
      "value": 1.0
    },
    "axis_line_cap": "butt",
    "axis_line_color": {
      "value": "black"
    },
    "axis_line_dash": [],
    "axis_line_dash_offset": 0,
    "axis_line_join": "miter",
    "axis_line_width": {
      "value": 1
    },
    "bounds": "auto",
    "formatter": {
      "attributes": {
        "name": null,
        "tags": [],
        "ticker": null
      },
      "type": "LogTickFormatter"
    },
    "level": "overlay",
    "location": "auto",
    "major_label_orientation": "horizontal",
    "major_label_standoff": 5,
    "major_label_text_align": "center",
    "major_label_text_alpha": {
      "value": 1.0
    },
    "major_label_text_baseline": "alphabetic",
    "major_label_text_color": {
      "value": "#444444"
    },
    "major_label_text_font": "helvetica",
    "major_label_text_font_size": {
      "value": "10pt"
    },
    "major_label_text_font_style": "normal",
    "major_tick_in": 2,
    "major_tick_line_alpha": {
      "value": 1.0
    },
    "major_tick_line_cap": "butt",
    "major_tick_line_color": {
      "value": "black"
    },
    "major_tick_line_dash": [],
    "major_tick_line_dash_offset": 0,
    "major_tick_line_join": "miter",
    "major_tick_line_width": {
      "value": 1
    },
    "major_tick_out": 6,
    "minor_tick_in": 0,
    "minor_tick_line_alpha": {
      "value": 1.0
    },
    "minor_tick_line_cap": "butt",
    "minor_tick_line_color": {
      "value": "black"
    },
    "minor_tick_line_dash": [],
    "minor_tick_line_dash_offset": 0,
    "minor_tick_line_join": "miter",
    "minor_tick_line_width": {
      "value": 1
    },
    "minor_tick_out": 4,
    "name": null,
    "plot": null,
    "tags": [],
    "ticker": {
      "attributes": {
        "base": 10.0,
        "desired_num_ticks": 6,
        "mantissas": [1, 5],
        "max_interval": null,
        "min_interval": 0.0,
        "name": null,
        "num_minor_ticks": 5,
        "tags": []
      },
      "type": "LogTicker"
    },
    "visible": true,
    "x_range_name": "default",
    "y_range_name": "default"
  },
  "LogTickFormatter": {
    "name": null,
    "tags": [],
    "ticker": null
  },
  "LogTicker": {
    "base": 10.0,
    "desired_num_ticks": 6,
    "mantissas": [1, 5],
    "max_interval": null,
    "min_interval": 0.0,
    "name": null,
    "num_minor_ticks": 5,
    "tags": []
  },
  "MonthsTicker": {
    "desired_num_ticks": 6,
    "interval": null,
    "months": [],
    "name": null,
    "num_minor_ticks": 5,
    "tags": []
  },
  "MultiLine": {
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "tags": [],
    "visible": true,
    "xs": null,
    "ys": null
  },
  "NumberEditor": {
    "name": null,
    "step": 0.01,
    "tags": []
  },
  "NumberFormatter": {
    "font_style": "normal",
    "format": "0,0",
    "language": "en",
    "name": null,
    "rounding": "round",
    "tags": [],
    "text_align": "left",
    "text_color": null
  },
  "NumeralTickFormatter": {
    "format": "0,0",
    "language": "en",
    "name": null,
    "rounding": "round",
    "tags": []
  },
  "OpenURL": {
    "name": null,
    "tags": [],
    "url": "http://"
  },
  "Oval": {
    "angle": {
      "units": "rad",
      "value": 0.0
    },
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "height": null,
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "tags": [],
    "visible": true,
    "width": null,
    "x": null,
    "y": null
  },
  "PanTool": {
    "dimensions": ["width", "height"],
    "name": null,
    "plot": null,
    "tags": []
  },
  "Patch": {
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "Patches": {
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "tags": [],
    "visible": true,
    "xs": null,
    "ys": null
  },
  "PercentEditor": {
    "name": null,
    "tags": []
  },
  "PolyAnnotation": {
    "fill_alpha": {
      "value": 0.4
    },
    "fill_color": {
      "value": "#fff9ba"
    },
    "level": "annotation",
    "line_alpha": {
      "value": 0.3
    },
    "line_cap": "butt",
    "line_color": {
      "value": "#cccccc"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "plot": null,
    "tags": [],
    "x_range_name": "default",
    "xs": [],
    "xs_units": "data",
    "y_range_name": "default",
    "ys": [],
    "ys_units": "data"
  },
  "PolySelectTool": {
    "name": null,
    "names": [],
    "overlay": {
      "attributes": {
        "fill_alpha": {
          "value": 0.5
        },
        "fill_color": {
          "value": "lightgrey"
        },
        "level": "overlay",
        "line_alpha": {
          "value": 1.0
        },
        "line_cap": "butt",
        "line_color": {
          "value": "black"
        },
        "line_dash": [4, 4],
        "line_dash_offset": 0,
        "line_join": "miter",
        "line_width": {
          "value": 2
        },
        "name": null,
        "plot": null,
        "tags": [],
        "x_range_name": "default",
        "xs": [],
        "xs_units": "screen",
        "y_range_name": "default",
        "ys": [],
        "ys_units": "screen"
      },
      "type": "PolyAnnotation"
    },
    "plot": null,
    "renderers": [],
    "tags": []
  },
  "PreviewSaveTool": {
    "name": null,
    "plot": null,
    "tags": []
  },
  "PrintfTickFormatter": {
    "format": "%s",
    "name": null,
    "tags": []
  },
  "QUADKEYTileSource": {
    "attribution": "",
    "extra_url_vars": {},
    "initial_resolution": 156543.03392804097,
    "max_zoom": 30,
    "min_zoom": 0,
    "name": null,
    "tags": [],
    "tile_size": 256,
    "url": "",
    "wrap_around": true,
    "x_origin_offset": 20037508.34,
    "y_origin_offset": 20037508.34
  },
  "Quad": {
    "bottom": null,
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "left": null,
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "right": null,
    "tags": [],
    "top": null,
    "visible": true
  },
  "Quadratic": {
    "cx": null,
    "cy": null,
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "tags": [],
    "visible": true,
    "x0": null,
    "x1": null,
    "y0": null,
    "y1": null
  },
  "Range1d": {
    "bounds": null,
    "callback": null,
    "end": 1,
    "name": null,
    "start": 0,
    "tags": []
  },
  "Ray": {
    "angle": null,
    "length": null,
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "Rect": {
    "angle": {
      "units": "rad",
      "value": 0.0
    },
    "dilate": false,
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "height": null,
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "tags": [],
    "visible": true,
    "width": null,
    "x": null,
    "y": null
  },
  "ResetTool": {
    "name": null,
    "plot": null,
    "tags": []
  },
  "ResizeTool": {
    "name": null,
    "plot": null,
    "tags": []
  },
  "Segment": {
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "tags": [],
    "visible": true,
    "x0": null,
    "x1": null,
    "y0": null,
    "y1": null
  },
  "SelectEditor": {
    "name": null,
    "options": [],
    "tags": []
  },
  "Span": {
    "dimension": "width",
    "level": "annotation",
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "location": null,
    "location_units": "data",
    "name": null,
    "plot": null,
    "render_mode": "canvas",
    "tags": [],
    "x_range_name": "default",
    "y_range_name": "default"
  },
  "Square": {
    "angle": {
      "units": "rad",
      "value": 0.0
    },
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "size": {
      "units": "screen",
      "value": 4
    },
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "SquareCross": {
    "angle": {
      "units": "rad",
      "value": 0.0
    },
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "size": {
      "units": "screen",
      "value": 4
    },
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "SquareX": {
    "angle": {
      "units": "rad",
      "value": 0.0
    },
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "size": {
      "units": "screen",
      "value": 4
    },
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "StringEditor": {
    "completions": [],
    "name": null,
    "tags": []
  },
  "TMSTileSource": {
    "attribution": "",
    "extra_url_vars": {},
    "initial_resolution": 156543.03392804097,
    "max_zoom": 30,
    "min_zoom": 0,
    "name": null,
    "tags": [],
    "tile_size": 256,
    "url": "",
    "wrap_around": true,
    "x_origin_offset": 20037508.34,
    "y_origin_offset": 20037508.34
  },
  "TableColumn": {
    "default_sort": "ascending",
    "editor": {
      "attributes": {
        "completions": [],
        "name": null,
        "tags": []
      },
      "type": "StringEditor"
    },
    "field": null,
    "formatter": {
      "attributes": {
        "font_style": "normal",
        "name": null,
        "tags": [],
        "text_align": "left",
        "text_color": null
      },
      "type": "StringFormatter"
    },
    "name": null,
    "sortable": true,
    "tags": [],
    "title": null,
    "width": 300
  },
  "TapTool": {
    "callback": null,
    "name": null,
    "names": [],
    "plot": null,
    "renderers": [],
    "tags": []
  },
  "Text": {
    "angle": {
      "units": "rad",
      "value": 0
    },
    "name": null,
    "tags": [],
    "text": {
      "field": "text"
    },
    "text_align": "left",
    "text_alpha": {
      "value": 1.0
    },
    "text_baseline": "bottom",
    "text_color": {
      "value": "#444444"
    },
    "text_font": "helvetica",
    "text_font_size": {
      "value": "12pt"
    },
    "text_font_style": "normal",
    "visible": true,
    "x": null,
    "x_offset": {
      "value": 0
    },
    "y": null,
    "y_offset": {
      "value": 0
    }
  },
  "TextEditor": {
    "name": null,
    "tags": []
  },
  "TileRenderer": {
    "alpha": 1.0,
    "level": "underlay",
    "name": null,
    "render_parents": true,
    "tags": [],
    "tile_source": {
      "attributes": {
        "attribution": "",
        "extra_url_vars": {},
        "initial_resolution": 156543.03392804097,
        "max_zoom": 30,
        "min_zoom": 0,
        "name": null,
        "tags": [],
        "tile_size": 256,
        "url": "",
        "wrap_around": true,
        "x_origin_offset": 20037508.34,
        "y_origin_offset": 20037508.34
      },
      "type": "WMTSTileSource"
    },
    "x_range_name": "default",
    "y_range_name": "default"
  },
  "TimeEditor": {
    "name": null,
    "tags": []
  },
  "ToolEvents": {
    "geometries": [],
    "name": null,
    "tags": []
  },
  "Tooltip": {
    "inner_only": true,
    "level": "overlay",
    "name": null,
    "plot": null,
    "side": "auto",
    "tags": []
  },
  "Triangle": {
    "angle": {
      "units": "rad",
      "value": 0.0
    },
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "size": {
      "units": "screen",
      "value": 4
    },
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "WMTSTileSource": {
    "attribution": "",
    "extra_url_vars": {},
    "initial_resolution": 156543.03392804097,
    "max_zoom": 30,
    "min_zoom": 0,
    "name": null,
    "tags": [],
    "tile_size": 256,
    "url": "",
    "wrap_around": true,
    "x_origin_offset": 20037508.34,
    "y_origin_offset": 20037508.34
  },
  "Wedge": {
    "direction": "anticlock",
    "end_angle": null,
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "radius": null,
    "start_angle": null,
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "WheelZoomTool": {
    "dimensions": ["width", "height"],
    "name": null,
    "plot": null,
    "tags": []
  },
  "X": {
    "angle": {
      "units": "rad",
      "value": 0.0
    },
    "fill_alpha": {
      "value": 1.0
    },
    "fill_color": {
      "value": "gray"
    },
    "line_alpha": {
      "value": 1.0
    },
    "line_cap": "butt",
    "line_color": {
      "value": "black"
    },
    "line_dash": [],
    "line_dash_offset": 0,
    "line_join": "miter",
    "line_width": {
      "value": 1
    },
    "name": null,
    "size": {
      "units": "screen",
      "value": 4
    },
    "tags": [],
    "visible": true,
    "x": null,
    "y": null
  },
  "YearsTicker": {
    "desired_num_ticks": 6,
    "interval": null,
    "name": null,
    "num_minor_ticks": 5,
    "tags": []
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
