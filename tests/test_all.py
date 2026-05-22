import os
from fontquant import quantify
import pytest


def get_font_path(filename):
    return os.path.dirname(os.path.realpath(__file__)) + "/fonts/" + filename


def get_result(filename, includes=None, excludes=None, variable=None):
    font_path = get_font_path(filename)

    return quantify(
        font_path,
        includes=includes,
        excludes=excludes,
        locations=variable,
    )


def test_quantify():
    bigshouldersstencil = get_result("BigShouldersStencilText[wght].ttf")
    # Check approximate float values separately since pytest.approx doesn't work in nested dict comparisons
    assert bigshouldersstencil["appearance"]["weight"]["value"] == pytest.approx(
        0.1877, 0.1
    )
    assert bigshouldersstencil["appearance"]["weight_perceptual"][
        "value"
    ] == pytest.approx(0.0654, 0.1)
    assert bigshouldersstencil["appearance"]["width"]["value"] == pytest.approx(
        0.3183, 0.1
    )
    assert bigshouldersstencil["appearance"]["most_common_width"]["value"] == 350.0
    assert bigshouldersstencil["stroke_contrast"]["antiqua"]["value"] == pytest.approx(
        1.175459861755371, 0.01
    )
    assert bigshouldersstencil["stroke_contrast"]["raycaster"][
        "value"
    ] == pytest.approx(1.1481037310191564, 0.01)
    assert bigshouldersstencil["casing"]["caps-to-smallcaps"]["value"] == pytest.approx(
        95.8, 1
    )
    assert bigshouldersstencil["casing"]["case_sensitive_punctuation"][
        "value"
    ] == pytest.approx(38, 1)
    assert bigshouldersstencil["casing"]["smallcaps"]["value"] == pytest.approx(93, 1)

    # Check exact values in the rest of the structure (omitting approximate floating point values)
    # Make a copy and remove the approximate values for dict comparison
    result_for_comparison = bigshouldersstencil.copy()
    result_for_comparison["appearance"] = result_for_comparison["appearance"].copy()
    # Remove approximate values that are checked separately above
    del result_for_comparison["appearance"]["weight"]
    del result_for_comparison["appearance"]["weight_perceptual"]
    del result_for_comparison["appearance"]["width"]
    del result_for_comparison["appearance"]["most_common_width"]
    del result_for_comparison["stroke_contrast"]
    del result_for_comparison["casing"]["caps-to-smallcaps"]
    del result_for_comparison["casing"]["case_sensitive_punctuation"]
    del result_for_comparison["casing"]["smallcaps"]

    assert result_for_comparison == {
        "parametric": {
            "XCLR": {"value": 50.0},
            "XCLS": {"value": 62.0},
            "XOFI": {"value": 41.0},
            "XOLC": {"value": 41.0},
            "XOPQ": {"value": 40.0},
            "XTFI": {"value": 158.0},
            "XTLC": {"value": 152.0},
            "XTRA": {"value": 160.0},
            "YOFI": {"value": 0.0},
            "YOLC": {"value": 34.0},
            "YOPQ": {"value": 38.0},
            "YTAS": {"value": 800.0},
            "YTDE": {"value": -200.0},
        },
        "appearance": {
            "ascender": {"value": 800.0},
            "cap_height": {"value": 800.0},
            "descender": {"value": -201.0},
            "monospaced": {"value": False},
            "slant": {"value": -0.44578950410294454},
            "stencil": {"value": True},
            "i_width": {"value": 164.0},
            "n_width": {"value": 354.0},
            "space_width": {"value": 200.0},
            "x_height": {"value": 600.0},
        },
        "casing": {
            "lowercase_shapes": {"value": "lowercase"},
            "unicase": {"value": False},
        },
        "features": {
            "feature_list": {
                "value": [
                    "aalt",
                    "c2sc",
                    "case",
                    "ccmp",
                    "dlig",
                    "dnom",
                    "frac",
                    "kern",
                    "liga",
                    "locl",
                    "mark",
                    "mkmk",
                    "numr",
                    "ordn",
                    "salt",
                    "sinf",
                    "smcp",
                    "ss01",
                    "subs",
                    "sups",
                ]
            },
            "stylistic_sets": {"value": {}},
        },
        "numerals": {
            "arbitrary_fractions": {"value": True},
            "default_numerals": {"value": "proportional_lining"},
            "encoded_fractions": {"value": 100.0},
            "inferior_numerals": {"value": 100.0},
            "proportional_lining": {"value": True},
            "proportional_oldstyle": {"value": False},
            "slashed_zero": {
                # "checked_additional_features": ["sups", "sinf", "frac"],
                "value": 0.0,
            },
            "superior_numerals": {"value": 100.0},
            "tabular_lining": {"value": False},
            "tabular_oldstyle": {"value": False},
        },
    }


def test_casing():
    farro = get_result("Farro-Regular.ttf", includes=["casing"])
    assert farro["casing"]["unicase"]["value"] is False
    assert farro["casing"]["lowercase_shapes"]["value"] == "lowercase"
    youngserif = get_result("YoungSerif-Regular.ttf", includes=["casing"])
    assert youngserif["casing"]["unicase"]["value"] is False
    unica = get_result("UnicaOne-Regular.ttf", includes=["casing"])
    assert unica["casing"]["unicase"]["value"] is True
    delius = get_result("DeliusUnicase-Regular.ttf", includes=["casing"])
    assert delius["casing"]["unicase"]["value"] is True
    ysabeau = get_result("Ysabeau[wght].ttf", includes=["casing"])
    assert ysabeau["casing"]["lowercase_shapes"]["value"] == "lowercase"
    ysabeau_sc = get_result("YsabeauSC[wght].ttf", includes=["casing"])
    assert ysabeau_sc["casing"]["lowercase_shapes"]["value"] == "smallcaps"
    castorotitling = get_result("CastoroTitling-Regular.ttf", includes=["casing"])
    assert castorotitling["casing"]["lowercase_shapes"]["value"] == "uppercase"


def test_numerals():
    farro = get_result("Farro-Regular.ttf", includes=["numerals"])
    assert farro["numerals"]["proportional_oldstyle"]["value"] is False
    assert farro["numerals"]["tabular_oldstyle"]["value"] is False
    assert farro["numerals"]["proportional_lining"]["value"] is True
    assert farro["numerals"]["tabular_lining"]["value"] is True
    assert farro["numerals"]["default_numerals"]["value"] == "proportional_lining"

    foldit = get_result("Foldit-VariableFont_wght.ttf", includes=["numerals"])
    assert foldit["numerals"]["proportional_oldstyle"]["value"] is False
    assert foldit["numerals"]["tabular_oldstyle"]["value"] is False
    # Foldit has tabular_lining numerals by default and an additional .lf set
    # but they look identical to the tabular_lining set, so False is reported here:
    assert foldit["numerals"]["proportional_lining"]["value"] is False
    assert foldit["numerals"]["tabular_lining"]["value"] is True
    assert foldit["numerals"]["default_numerals"]["value"] == "tabular_lining"


def test_appearance():
    # TODO:
    # Test for Foldit, which errors out
    farro = get_result("Farro-Regular.ttf", includes=["appearance"])
    assert farro["appearance"]["weight"]["value"] == pytest.approx(0.296, 0.1)
    assert farro["appearance"]["width"]["value"] == pytest.approx(0.561, 0.1)
    assert farro["appearance"]["slant"]["value"] == pytest.approx(-0.099, 0.1)
    assert farro["appearance"]["lowercase_a_style"]["value"] == "double_story"
    assert farro["appearance"]["lowercase_g_style"]["value"] == "single_story"
    assert farro["appearance"]["stencil"]["value"] is False
    assert farro["appearance"]["x_height"]["value"] == 600.0
    assert farro["appearance"]["cap_height"]["value"] == 751.0
    assert farro["appearance"]["ascender"]["value"] == 800.0
    assert farro["appearance"]["descender"]["value"] == -216.0

    youngserif = get_result("YoungSerif-Regular.ttf", includes=["appearance"])
    assert youngserif["appearance"]["stencil"]["value"] is False

    bodonimoda = get_result("BodoniModa_18pt-Italic.ttf", includes=["appearance"])
    assert bodonimoda["appearance"]["lowercase_a_style"]["value"] == "single_story"
    assert bodonimoda["appearance"]["lowercase_g_style"]["value"] == "double_story"
    assert bodonimoda["appearance"]["stencil"]["value"] is False
    assert bodonimoda["appearance"]["slant"]["value"] == pytest.approx(-11.821, 0.1)

    allertastencil = get_result(
        "AllertaStencil-Regular.ttf", includes=["appearance/stencil"]
    )
    assert allertastencil["appearance"]["stencil"]["value"] is True

    bigshouldersstencil = get_result(
        "BigShouldersStencilText[wght].ttf", includes=["appearance/stencil"]
    )
    assert bigshouldersstencil["appearance"]["stencil"]["value"] is True

    robotoflex = get_result("RobotoFlex-Var.ttf", includes=["appearance"])
    assert robotoflex["parametric"]["XOPQ"]["value"] == 94
    assert robotoflex["parametric"]["XOLC"]["value"] == 91
    assert robotoflex["parametric"]["XOFI"]["value"] == 94
    assert robotoflex["parametric"]["XTRA"]["value"] == 358
    assert robotoflex["parametric"]["XTLC"]["value"] == 234
    assert robotoflex["parametric"]["XTFI"]["value"] == 268
    assert robotoflex["parametric"]["YOPQ"]["value"] == 77
    assert robotoflex["parametric"]["YOLC"]["value"] == 69
    assert robotoflex["parametric"]["YOFI"]["value"] == 77


def test_features():
    ysabeau = get_result("Ysabeau[wght].ttf", includes=["features"])
    ysabeau = {"features": ysabeau["features"]}  # Easier to throw away than filter out
    assert ysabeau == {
        "features": {
            "feature_list": {
                "value": [
                    "aalt",
                    "c2sc",
                    "calt",
                    "case",
                    "ccmp",
                    "dlig",
                    "dnom",
                    "frac",
                    "hlig",
                    "kern",
                    "liga",
                    "lnum",
                    "locl",
                    "mark",
                    "mkmk",
                    "numr",
                    "onum",
                    "ordn",
                    "pnum",
                    "rvrn",
                    "sinf",
                    "smcp",
                    "ss01",
                    "ss02",
                    "ss03",
                    "ss09",
                    "ss10",
                    "ss11",
                    "subs",
                    "sups",
                    "tnum",
                    "zero",
                ]
            },
            "stylistic_sets": {
                "value": {
                    "ss01": "Infant cut",
                    "ss02": "Office cut",
                    "ss03": "Alternative a and u",
                    "ss09": "Serbian Cyrillic",
                    "ss10": "Bulgarian Cyrillic",
                    "ss11": "Frankfurt-style Eszett",
                }
            },
        }
    }


def test_variable():
    font = "Foldit-VariableFont_wght.ttf"
    assert (
        get_result(
            font,
            includes=["appearance/weight"],
            variable="fvar",
        )
        == get_result(
            font,
            includes=["appearance/weight"],
            variable="stat",
        )
        == get_result(
            font,
            includes=["appearance/weight"],
            variable="all",
        )
        == {
            "appearance": {
                "weight": {
                    "value": {
                        "wght=100.0": 0.137,
                        "wght=200.0": 0.177,
                        "wght=300.0": 0.237,
                        "wght=400.0": 0.305,
                        "wght=500.0": 0.357,
                        "wght=600.0": 0.377,
                        "wght=700.0": 0.419,
                        "wght=800.0": 0.474,
                        "wght=900.0": 0.515,
                    }
                }
            }
        }
    )
