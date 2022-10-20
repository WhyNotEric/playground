use halo2::circuit::Layouter;
use halo2::{arithmetic::FieldExt, circuit::*, plonk::*, poly::Rotation};
use serde::{Deserialize, Serialize};
use std::error::Error as StdError;
use std::fs::File;
use std::io::BufReader;
use std::marker::PhantomData;
use std::path::Path;

use crate::data::dict::get_dict;

#[derive(Deserialize, Serialize)]
struct Dict {
    words: Vec<String>,
}

#[derive(Debug, Clone)]
pub struct DictTableConfig<F: FieldExt> {
    pub value: TableColumn,
    _marker: PhantomData<F>,
}

impl<F: FieldExt> DictTableConfig<F> {
    pub fn configure(meta: &mut ConstraintSystem<F>) -> Self {
        let value = meta.lookup_table_column();
        Self {
            value,
            _marker: PhantomData,
        }
    }

    pub fn load(&self, layouter: &mut impl Layouter<F>) -> Result<(), Error> {
        let mut words = get_dict();
        words.push(0);
        layouter.assign_table(
            || "load dictionary check table",
            |mut table| {
                let mut offset = 0;
                for word in words.iter() {
                    table.assign_cell(
                        || "num_bits",
                        self.value,
                        offset,
                        || Value::known(F::from(word.clone() as u64)),
                    )?;
                    offset += 1;
                }
                Ok(())
            },
        )
    }
}
