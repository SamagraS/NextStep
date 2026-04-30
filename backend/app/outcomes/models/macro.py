from __future__ import annotations

import numpy as np
import pandas as pd


class MacroRiskModel:
    def build_lookup(self, macro_frame: pd.DataFrame) -> pd.DataFrame:
        if macro_frame.empty:
            return pd.DataFrame(columns=["country", "unemployment_rate", "unemployment_trend", "macro_factor"])
        rows: list[dict[str, object]] = []
        for country, chunk in macro_frame.groupby("country"):
            latest = chunk.sort_values("year").tail(3)
            current = float(latest.iloc[-1]["unemployment_rate"])
            previous = float(latest.iloc[-2]["unemployment_rate"]) if len(latest) > 1 else current
            trend = current - previous
            macro_factor = float(np.clip(1.0 - (trend * 0.035), 0.85, 1.05))
            rows.append(
                {
                    "country": country,
                    "unemployment_rate": round(current, 3),
                    "unemployment_trend": round(trend, 3),
                    "macro_factor": round(macro_factor, 4),
                }
            )
        return pd.DataFrame(rows)

