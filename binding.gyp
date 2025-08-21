{
  "variables": {
    "vips_version": "<!(node -p \"require('./lib/libvips').minimumLibvipsVersion\")",
    "platform_and_arch": "<!(node -p \"require('./lib/platform')()\")",
    "platform": "<!(node -p \"require('./lib/platform')().split('-')[0]\")",
    "sharp_vendor_dir": "./vendor/<(vips_version)/<(platform)"
  },
  "targets": [{
    "target_name": "libvips-cpp",
    "conditions": [
      ["OS == \"win\"", {
        "type": "shared_library",
        "defines": [
          "VIPS_CPLUSPLUS_EXPORTS",
          "_ALLOW_KEYWORD_MACROS"
        ],
        "sources": [
          "src/libvips/cplusplus/VConnection.cpp",
          "src/libvips/cplusplus/VError.cpp",
          "src/libvips/cplusplus/VImage.cpp",
          "src/libvips/cplusplus/VInterpolate.cpp",
          "src/libvips/cplusplus/VRegion.cpp"
        ],
        "include_dirs": [
          "<(sharp_vendor_dir)/include",
          "<(sharp_vendor_dir)/include/glib-2.0",
          "<(sharp_vendor_dir)/lib/glib-2.0/include"
        ],
        "link_settings": {
          "library_dirs": ["<(sharp_vendor_dir)/lib"],
          "libraries": [
            "libvips.lib",
            "libglib-2.0.lib",
            "libgobject-2.0.lib"
          ]
        }
      }, {
        "type": "none"
      }]
    ]
  }, {
    "target_name": "sharp-<(platform)",
    "defines": [
      # ensure Node-API compatibility with Node 20
      "NAPI_VERSION=9",
      "NODE_ADDON_API_DISABLE_DEPRECATED=1"
    ],
    "dependencies": [
      "<!(node -p \"require('node-addon-api').gyp\")",
      "libvips-cpp"
    ],
    "variables": {
      "runtime_link%": "shared",
      "conditions": [
        ["OS != \"win\"", {
          "pkg_config_path": "<!(node -p \"require('./lib/libvips').pkgConfigPath()\")",
          "use_global_libvips": "false"
        }, {
          "pkg_config_path": "",
          "use_global_libvips": ""
        }]
      ]
    },
    "sources": [
      "src/common.cc",
      "src/metadata.cc",
      "src/stats.cc",
      "src/operations.cc",
      "src/pipeline.cc",
      "src/utilities.cc",
      "src/sharp.cc"
    ],
    "include_dirs": [
      "<!(node -p \"require('node-addon-api').include_dir\")"
    ],
    "conditions": [
      ["use_global_libvips == \"true\"", {
        "include_dirs": ["<!@(PKG_CONFIG_PATH=\"<(pkg_config_path)\" pkg-config --cflags-only-I vips-cpp vips glib-2.0 | sed s/-I//g)"],
        "conditions": [
          ["runtime_link == \"static\"", {
            "libraries": ["<!@(PKG_CONFIG_PATH=\"<(pkg_config_path)\" pkg-config --libs --static vips-cpp)"]
          }, {
            "libraries": ["<!@(PKG_CONFIG_PATH=\"<(pkg_config_path)\" pkg-config --libs vips-cpp)"]
          }],
          ["OS == \"linux\"", {
            "defines": [
              "_GLIBCXX_USE_CXX11_ABI=1"
            ]
          }]
        ]
      }, {
        "include_dirs": [
          "<(sharp_vendor_dir)/include",
          "<(sharp_vendor_dir)/include/glib-2.0",
          "<(sharp_vendor_dir)/lib/glib-2.0/include"
        ],
        "conditions": [
          ["OS == \"win\"", {
            "defines": [
              "_ALLOW_KEYWORD_MACROS",
              "_FILE_OFFSET_BITS=64"
            ],
            "link_settings": {
              "library_dirs": ["<(sharp_vendor_dir)/lib"],
              "libraries": [
                "libvips.lib",
                "libglib-2.0.lib",
                "libgobject-2.0.lib"
              ]
            }
          }],
          ["OS == \"mac\"", {
            "link_settings": {
              "library_dirs": ["../<(sharp_vendor_dir)/lib"],
              "libraries": ["-lvips-cpp"]
            },
            "xcode_settings": {
              "OTHER_CFLAGS": [
                "-arch x86_64",
                "-arch arm64"
              ],
              "OTHER_LDFLAGS": [
                "-Wl,-rpath,'@loader_path/../../<(sharp_vendor_dir)/lib'",
                "-arch x86_64",
                "-arch arm64"
              ]
            }
          }],
          ["OS == \"linux\"", {
            "defines": [
              "_GLIBCXX_USE_CXX11_ABI=1"
            ],
            "link_settings": {
              "library_dirs": ["../<(sharp_vendor_dir)/lib"],
              "libraries": ["-lvips-cpp"],
              "ldflags": [
                "-Wl,-s -Wl,--disable-new-dtags -Wl,-rpath='$$ORIGIN/../../<(sharp_vendor_dir)/lib'"
              ]
            }
          }]
        ]
      }]
    ],
    "cflags_cc": [
      "-std=c++17",
      "-fexceptions",
      "-Wall",
      "-O3"
    ],
    "xcode_settings": {
      "CLANG_CXX_LANGUAGE_STANDARD": "c++17",
      "MACOSX_DEPLOYMENT_TARGET": "10.15",
      "GCC_ENABLE_CPP_EXCEPTIONS": "YES",
      "GCC_ENABLE_CPP_RTTI": "YES",
      "OTHER_CPLUSPLUSFLAGS": [
        "-fexceptions",
        "-Wall",
        "-O3",
        "-arch x86_64",
        "-arch arm64"
      ]
    },
    "configurations": {
      "Release": {
        "conditions": [
          ["OS == \"linux\"", {
            "cflags_cc": ["-Wno-cast-function-type"]
          }],
          ["target_arch == \"arm\"", {
            "cflags_cc": ["-Wno-psabi"]
          }]
        ]
      }
    }
  }]
}
