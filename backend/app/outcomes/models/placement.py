from __future__ import annotations

import numpy as np
import pandas as pd


class PlacementModel:
    def build_lookup(self, placement_frame: pd.DataFrame) -> pd.DataFrame:
        if placement_frame.empty:
            return pd.DataFrame(
                columns=[
                    "program_family",
                    "country",
                    "institution_tier",
                    "base_rate",
                    "p3",
                    "p6",
                    "p12",
                    "source_count",
                    "sources_used",
                ]
            )

        working = placement_frame.copy()
        working["weight"] = working["sample_size"].fillna(1.0).clip(lower=1.0)
        rows: list[dict[str, object]] = []
        for keys, chunk in working.groupby(["program_family", "country", "institution_tier"], dropna=False):
            base_rate = np.average(chunk["employment_rate"], weights=chunk["weight"])
            p12 = float(np.clip(base_rate, 0.05, 0.98))
            p6 = float(np.clip(p12 * 0.76, 0.03, p12))
            p3 = float(np.clip(p12 * 0.48, 0.02, p6))
            rows.append(
                {
                    "program_family": keys[0],
                    "country": keys[1],
                    "institution_tier": int(keys[2]),
                    "base_rate": round(base_rate, 4),
                    "p3": round(p3, 4),
                    "p6": round(p6, 4),
                    "p12": round(p12, 4),
                    "source_count": int(chunk["source"].nunique()),
                    "sources_used": ",".join(sorted(chunk["source"].unique())),
                }
            )
        return pd.DataFrame(rows)

