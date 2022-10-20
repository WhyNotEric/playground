use halo2::{arithmetic::FieldExt, circuit::*, plonk::*, poly::Rotation};

#[derive(Clone, Debug)]
pub struct IsZeroConfig<F> {
    pub value_inverse: Column<Advice>,
    pub is_zero_expr: Expression<F>,
}

impl<F: FieldExt> IsZeroConfig<F> {
    pub fn expr(&self) -> Expression<F> {
        self.is_zero_expr.clone()
    }
}

pub struct IsZeroChip<F: FieldExt> {
    config: IsZeroConfig<F>,
}

impl<F: FieldExt> IsZeroChip<F> {
    pub fn construct(config: IsZeroConfig<F>) -> Self {
        IsZeroChip { config }
    }

    pub fn configure(
        meta: &mut ConstraintSystem<F>,
        q_enable: impl FnOnce(&mut VirtualCells<'_, F>) -> Expression<F>,
        value: impl FnOnce(&mut VirtualCells<'_, F>) -> Expression<F>,
        value_inverse: Column<Advice>,
    ) -> IsZeroConfig<F> {
        let mut is_zero_expr = Expression::Constant(F::zero());
        meta.create_gate("is_zero", |meta| {
            let value = value(meta);
            let q_enable = q_enable(meta);
            let value_inverse = meta.query_advice(value_inverse, Rotation::cur());

            is_zero_expr = Expression::Constant(F::one()) - value.clone() * value_inverse;
            vec![q_enable * value * is_zero_expr.clone()]
        });

        IsZeroConfig {
            value_inverse,
            is_zero_expr,
        }
    }

    pub fn assign(
        &self,
        region: &mut Region<'_, F>,
        offset: usize,
        value: Value<F>,
    ) -> Result<(), Error> {
        let value_inverse = value.map(|value| value.invert().unwrap_or(F::zero()));
        region.assign_advice(
            || "value inverse",
            self.config.value_inverse,
            offset,
            || value_inverse,
        )?;
        Ok(())
    }
}
