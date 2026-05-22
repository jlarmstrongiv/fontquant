use kurbo::Shape;
use read_fonts::TableProvider;
use skrifa::{MetadataProvider, instance::Size};

use crate::quantifiers::appearance::stats::CurveStatistics;
use crate::{MetricValue, monkeypatching::MakeBezGlyphs, quantifier};

quantifier!(
    LOWERCASE_A_STYLE,
    "appearance/lowercase_a_style",
    r#" Attempts to determine the style of the lowercase "a" to be single or double story.

    Only the most sturdy routines are used here. If the results are not conclusive,
    the metric will return None and you need to determine it manually.

    The error margin for recognizing the single story "a" is 0-2%, and for the double story "a" 4-7%."#,
    MetricValue::String("single_story".to_string())
);

quantifier!(
    LOWERCASE_G_STYLE,
    "appearance/lowercase_g_style",
    r#" Attempts to determine the style of the lowercase "g" to be single or double story.

    This metric is based on contour counting, which is not very reliable.
    A "g" which generally looks like a double story "g" but has an open lower bowl
    will be counted as single story, and a "g" in cursive writing that looks like
    a single story "g" but has a closed loop as part of an upstroke will be counted as double story."#,
    MetricValue::String("single_story".to_string())
);

pub(crate) fn check_lowercase_a_style(
    font: &skrifa::FontRef,
    location: &[skrifa::setting::VariationSetting],
    results: &mut crate::Results,
) -> Result<(), crate::FontquantError> {
    let Some(stencil) = results
        .get("appearance/stencil")
        .and_then(|(_k, v)| v.as_boolean())
    else {
        return Ok(());
    };
    let Some(unicase) = results
        .get("casing/unicase")
        .and_then(|(_k, v)| v.as_boolean())
    else {
        return Ok(());
    };
    if stencil || unicase {
        // We can't tell, too complex
        return Ok(());
    }
    let upem = font.head()?.units_per_em() as f64;
    let Some(glyph) = font.bezglyph_for_char(location, Some(1.0), 'a')? else {
        return Ok(());
    };
    let Some(glyph_id) = font.charmap().map('a') else {
        return Ok(());
    };
    let Some(h_glyph) = font.bezglyph_for_char(location, None, 'H')? else {
        return Ok(());
    };

    let glyph = glyph.remove_overlaps()?;
    // Ensure we have two paths
    let normalized = font.axes().location(location);
    let glyph_width = font
        .glyph_metrics(Size::unscaled(), &normalized)
        .advance_width(glyph_id)
        .unwrap_or(0.0) as f64
        * upem;
    let area = glyph.iter().map(|p| p.area()).fold(0.0, |acc, s| acc + s);
    let weight = area.abs() / glyph_width;
    let paths = glyph.0;
    if paths.len() != 2 {
        return Ok(());
    }
    let mut threshold = if weight < 0.1 {
        1.7
    } else if weight > 0.3 {
        3.0
    } else {
        (weight - 0.1) / (0.3 - 0.1) * (3.0 - 1.7) + 1.7
    };
    let path_0_len = paths[0].perimeter(0.01);
    let path_1_len = paths[1].perimeter(0.01);
    let ratio = if path_0_len < path_1_len {
        path_1_len / path_0_len
    } else {
        path_0_len / path_1_len
    };
    let slant = h_glyph
        .iter()
        .map(|p| p.slant())
        .fold(0.0, |acc, s| acc + s);
    if slant > 0.1 {
        threshold *= 1.2;
    } else if slant > 0.2 {
        threshold *= 1.4;
    }
    results.add_metric(
        &LOWERCASE_A_STYLE,
        if ratio > threshold {
            MetricValue::String("double_story".to_string())
        } else {
            MetricValue::String("single_story".to_string())
        },
    );

    Ok(())
}

pub(crate) fn check_lowercase_g_style(
    font: &skrifa::FontRef,
    location: &[skrifa::setting::VariationSetting],
    results: &mut crate::Results,
) -> Result<(), crate::FontquantError> {
    let Some(stencil) = results
        .get("appearance/stencil")
        .and_then(|(_k, v)| v.as_boolean())
    else {
        return Ok(());
    };
    let Some(unicase) = results
        .get("casing/unicase")
        .and_then(|(_k, v)| v.as_boolean())
    else {
        return Ok(());
    };
    if stencil || unicase {
        // We can't tell, too complex
        return Ok(());
    }

    let Some(glyph) = font.bezglyph_for_char(location, None, 'g')? else {
        return Ok(());
    };

    let glyph = glyph.remove_overlaps()?;
    let paths = glyph.0;
    if paths.len() == 2 {
        results.add_metric(
            &LOWERCASE_G_STYLE,
            MetricValue::String("single_story".to_string()),
        );
    } else if paths.len() == 3 {
        results.add_metric(
            &LOWERCASE_G_STYLE,
            MetricValue::String("double_story".to_string()),
        );
    }

    Ok(())
}
