use std::collections::{BTreeSet, HashMap};

use itertools::Either;
use read_fonts::{
    ReadError, TableProvider,
    tables::layout::{Feature, FeatureRecord},
};
use skrifa::{FontRef, MetadataProvider};

use crate::{MetricValue, quantifier};

/// Returns the font's FeatureRecord and associated Feature tables
fn feature_records<'a>(
    font: &'a FontRef,
    gsub_only: bool,
) -> impl Iterator<Item = (&'a FeatureRecord, Result<Feature<'a>, ReadError>)> {
    let gsub_featurelist = font.gsub().ok().and_then(|gsub| gsub.feature_list().ok());
    let gpos_feature_list = font.gpos().ok().and_then(|gpos| gpos.feature_list().ok());
    let gsub_feature_and_data = gsub_featurelist.map(|list| {
        list.feature_records()
            .iter()
            .map(move |feature| (feature, feature.feature(list.offset_data())))
    });
    let gpos_feature_and_data = gpos_feature_list.map(|list| {
        list.feature_records()
            .iter()
            .map(move |feature| (feature, feature.feature(list.offset_data())))
    });
    let iter = gsub_feature_and_data.into_iter().flatten();
    if gsub_only {
        Either::Left(iter)
    } else {
        Either::Right(iter.chain(gpos_feature_and_data.into_iter().flatten()))
    }
}

pub fn gather_features(
    font: &skrifa::FontRef,
    _location: &[skrifa::setting::VariationSetting],
    results: &mut crate::Results,
) -> Result<(), crate::FontquantError> {
    let mut all_features = BTreeSet::new();
    let mut stylistic_sets = HashMap::new();
    for (record, featuretable) in feature_records(font, false) {
        let name = record.feature_tag().to_string();
        if name.starts_with("ss")
            && let Some(Ok(read_fonts::tables::layout::FeatureParams::StylisticSet(params))) =
                featuretable?.feature_params()
            && let Some(set_name) = font
                .localized_strings(params.ui_name_id())
                .english_or_first()
        {
            stylistic_sets.insert(name.to_string(), set_name.to_string());
        }
        all_features.insert(name);
    }
    results.add_metric(
        &FEATURE_LIST,
        MetricValue::List(all_features.into_iter().collect()),
    );
    results.add_metric(
        &FEATURE_STYLISTIC_SETS,
        MetricValue::Dictionary(stylistic_sets.into_iter().collect()),
    );
    Ok(())
}

quantifier!(
    FEATURE_LIST,
    "features/feature_list",
    "Returns a list of all registed OpenType features in the font from both GSUB and GPOS tables.",
    MetricValue::List(vec!["aalt".to_string(), "liga".to_string()])
);

quantifier!(
    FEATURE_STYLISTIC_SETS,
    "features/stylistic_sets",
    "Returns a dictionary of all registered OpenType stylistic sets in the font.",
    MetricValue::Dictionary(HashMap::from([(
        "ss01".to_string(),
        "Stylistic Set 1".to_string()
    )]))
);
