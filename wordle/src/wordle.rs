use std::vec;

use halo2::{
    circuit::AssignedCell,
    halo2curves::FieldExt,
    plonk::{Advice, Assigned, Column, ConstraintSystem, Expression, Instance, Selector},
    poly::Rotation,
};

use crate::{
    is_zero::{IsZeroChip, IsZeroConfig},
    table::DictTableConfig,
    utils::{BASE, WORD_LEN},
};

struct RangeConstrained<F: FieldExt>(AssignedCell<Assigned<F>, F>);

#[derive(Debug, Clone)]
pub struct WorkdCheckConfig<F: FieldExt> {
    q_input: Selector,
    q_diff_g: Selector,
    q_diff_y: Selector,
    q_diff_green_is_zero: Selector,
    q_diff_yellow_is_zero: Selector,
    q_color_is_zero: Selector,
    q_color: Selector,
    ploy_word: Column<Advice>,
    chars: [Column<Advice>; WORD_LEN],
    color_is_zero_advice_column: [Column<Advice>; WORD_LEN],
    final_word_chars_instance: Column<Instance>,
    char_green_instance: Column<Instance>,
    char_yellow_instance: Column<Instance>,
    table: DictTableConfig<F>,
    diffs_green_is_zero: [IsZeroConfig<F>; WORD_LEN],
    diffs_yellow_is_zero: [IsZeroConfig<F>; WORD_LEN],
}

impl<F: FieldExt> WorkdCheckConfig<F> {
    pub fn configure(
        meta: &mut ConstraintSystem<F>,
        q_input: Selector,
        q_diff_g: Selector,
        q_diff_y: Selector,
        q_diff_green_is_zero: Selector,
        q_diff_yellow_is_zero: Selector,
        q_color_is_zero: Selector,
        q_color: Selector,
        ploy_word: Column<Advice>,
        chars: [Column<Advice>; WORD_LEN],
        color_is_zero_advice_column: [Column<Advice>; WORD_LEN],
        final_word_chars_instance: Column<Instance>,
        char_green_instance: Column<Instance>,
        char_yellow_instance: Column<Instance>,
    ) -> Self {
        let table = DictTableConfig::configure(meta);
        let mut diffs_green_is_zero = vec![];
        let mut diffs_yellow_is_zero = vec![];

        for i in 0..WORD_LEN {
            diffs_green_is_zero.push(IsZeroChip::configure(
                meta,
                |meta| meta.query_selector(q_diff_green_is_zero),
                |meta| meta.query_advice(chars[i], Rotation(-2)),
                color_is_zero_advice_column[i],
            ));

            diffs_yellow_is_zero.push(IsZeroChip::configure(
                meta,
                |meta| meta.query_selector(q_diff_yellow_is_zero),
                |meta| meta.query_advice(chars[i], Rotation(-2)),
                color_is_zero_advice_column[i],
            ))
        }

        for i in 0..WORD_LEN {
            meta.enable_equality(chars[i]);
        }

        meta.enable_equality(final_word_chars_instance);
        meta.enable_equality(char_green_instance);
        meta.enable_equality(char_yellow_instance);
        meta.lookup("lookup", |meta| {
            let q_lookup = meta.query_selector(q_input);
            let ploy_word = meta.query_advice(ploy_word, Rotation::cur());

            vec![(q_lookup * ploy_word, table.value)]
        });

        meta.create_gate("character range check", |meta| {
            let q = meta.query_selector(q_input);
            let mut constraints = vec![];
            for idx in 0..WORD_LEN {
                let value = meta.query_advice(chars[idx], Rotation::cur());
                let range_check = |range: usize, value: Expression<F>| {
                    assert!(range > 0);
                    (1..range).fold(value.clone(), |expr, i| {
                        expr * (Expression::Constant(F::from(i as u64)) - value.clone())
                    })
                };
                constraints.push(q.clone() * range_check(28, value.clone()));
            }
            constraints
        });

        meta.create_gate("poly hashing check", |meta| {
            let q = meta.query_selector(q_input);
            let ploy_word = meta.query_advice(ploy_word, Rotation::cur());
            let hash_check = {
                (0..WORD_LEN).fold(Expression::Constant(F::from(0)), |expr, i| {
                    let char = meta.query_advice(chars[i], Rotation::cur());
                    expr * Expression::Constant(F::from(BASE)) + char
                })
            };

            [q * (hash_check - ploy_word)]
        });

        meta.create_gate("diff_g checker", |meta| {
            let q = meta.query_selector(q_diff_g);
            let mut constraints = vec![];
            for i in 0..WORD_LEN {
                let char = meta.query_advice(chars[i], Rotation(-2));
                let final_char = meta.query_advice(chars[i], Rotation(-1));
                let diff_g = meta.query_advice(chars[i], Rotation::cur());
                constraints.push(q.clone() * ((char - final_char) - diff_g));
            }
            constraints
        });

        meta.create_gate("diff_y checker", |meta| {
            let q = meta.query_selector(q_diff_y);
            let mut constraints = vec![];
            for i in 0..WORD_LEN {
                let char = meta.query_advice(chars[i], Rotation(-3));
                let diff_y = meta.query_advice(chars[i], Rotation::cur());
                let yellow_check = {
                    (0..WORD_LEN).fold(Expression::Constant(F::one()), |expr, i| {
                        let final_char = meta.query_advice(chars[i], Rotation(-2));
                        expr * (char.clone() - final_char)
                    })
                };
                constraints.push(q.clone() * (yellow_check - diff_y));
            }
            constraints
        });

        meta.create_gate("diff_color_is_zero checker", |meta| {
            let q_green = meta.query_selector(q_diff_green_is_zero);
            let q_yellow = meta.query_selector(q_diff_yellow_is_zero);
            let q_color_is_zero = meta.query_selector(q_color_is_zero);
            let mut constraints = vec![];
            
            for i in 0..WORD_LEN {
                let diff_color_is_zero = meta.query_advice(chars[i], Rotation::cur());
                constraints.push(q_color_is_zero.clone() * (diff_color_is_zero - (q_green.clone() * diffs_green_is_zero[i].expr() + q_yellow.clone() * diffs_yellow_is_zero[i].expr())));
            }
            constraints
        });

        meta.create_gate("color check", |meta| {
            let q = meta.query_selector(q_color);
            let mut constraints = vec![];

            for i in 0..WORD_LEN {
                let diff_color = meta.query_advice(chars[i], Rotation(-4));
                let diff_color_is_zero = meta.query_advice(chars[i], Rotation(-2));
                let color = meta.query_advice(chars[i], Rotation::cur());
                constraints.push(q.clone() * diff_color * color.clone());
                constraints.push(q.clone() * diff_color_is_zero * (Expression::Constant(F::one()) - color.clone()));
            }
            constraints
        });

        Self {
            q_input,
            q_diff_g,
            q_diff_y,
            q_diff_green_is_zero,
            q_diff_yellow_is_zero,
            q_color_is_zero,
            q_color,
            ploy_word,
            chars,
            color_is_zero_advice_column,
            final_word_chars_instance,
            char_green_instance,
            char_yellow_instance,
            table,
            diffs_green_is_zero: diffs_green_is_zero.try_into().unwrap(),
            diffs_yellow_is_zero: diffs_yellow_is_zero.try_into().unwrap(),
        }
    }
}
