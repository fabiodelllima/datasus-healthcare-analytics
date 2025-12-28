"""
KPIs: Indicadores-chave de performance hospitalar.

Referência: docs/DATA_GUIDE.md seção "KPIs Implementados"
"""

from typing import Any, overload

import pandas as pd


class KPICalculator:
    """
    Calculador de KPIs hospitalares para dados SIH/DataSUS.

    KPIs implementados:
        1. Taxa de Ocupação (occupancy_rate)
        2. Tempo Médio de Permanência - TMP (average_length_of_stay)
        3. Volume de Atendimentos (volume)
        4. Receita Total (revenue)
        5. Distribuição Demográfica (demographics)

    Exemplo:
        >>> calculator = KPICalculator()
        >>> df = pd.read_parquet("data/processed/SIH_AC_202401.parquet")
        >>> print(calculator.summary(df, beds=100, days=31))
    """

    def occupancy_rate(self, df: pd.DataFrame, beds: int, days: int) -> float:
        """
        Calcula taxa de ocupação de leitos.

        Fórmula: (pacientes_dia / leitos_disponiveis) * 100

        Args:
            df: DataFrame com coluna 'stay_days'
            beds: Número de leitos disponíveis
            days: Número de dias no período

        Returns:
            Taxa de ocupação em percentual

        Raises:
            ValueError: Se beds ou days forem zero ou negativos
        """
        if beds <= 0:
            raise ValueError("Número de leitos deve ser maior que zero")
        if days <= 0:
            raise ValueError("Número de dias deve ser maior que zero")

        if df.empty or "stay_days" not in df.columns:
            return 0.0

        patient_days = df["stay_days"].sum()
        capacity = beds * days
        return float((patient_days / capacity) * 100)

    @overload
    def average_length_of_stay(self, df: pd.DataFrame) -> float: ...

    @overload
    def average_length_of_stay(self, df: pd.DataFrame, group_by: None) -> float: ...

    @overload
    def average_length_of_stay(self, df: pd.DataFrame, group_by: str) -> dict[str, float]: ...

    def average_length_of_stay(
        self, df: pd.DataFrame, group_by: str | None = None
    ) -> float | dict[str, float]:
        """
        Calcula Tempo Médio de Permanência (TMP).

        Args:
            df: DataFrame com coluna 'stay_days'
            group_by: Coluna para agrupamento (opcional)

        Returns:
            TMP geral (float) ou por grupo (dict)

        Raises:
            KeyError: Se group_by especificado não existir
        """
        if df.empty or "stay_days" not in df.columns:
            return 0.0

        if group_by is None:
            return float(df["stay_days"].mean())

        if group_by not in df.columns:
            raise KeyError(f"Coluna '{group_by}' não encontrada no DataFrame")

        grouped = df.groupby(group_by)["stay_days"].mean()
        return {str(k): float(v) for k, v in grouped.items()}

    @overload
    def volume(self, df: pd.DataFrame) -> int: ...

    @overload
    def volume(self, df: pd.DataFrame, group_by: None) -> int: ...

    @overload
    def volume(self, df: pd.DataFrame, group_by: str) -> dict[Any, int]: ...

    def volume(self, df: pd.DataFrame, group_by: str | None = None) -> int | dict[Any, int]:
        """
        Calcula volume de atendimentos (internações).

        Args:
            df: DataFrame com dados de internações
            group_by: Coluna para agrupamento ou 'month' para agrupar por mês

        Returns:
            Volume total (int) ou por grupo (dict com chaves int para mês, str para outros)
        """
        if df.empty:
            return 0

        if group_by is None:
            return len(df)

        if group_by == "month":
            if "DT_INTER" not in df.columns:
                raise KeyError("Coluna 'DT_INTER' necessária para agrupamento por mês")
            # Nota: reportAttributeAccessIssue configurado em pyproject.toml
            month_series = df["DT_INTER"].dt.month
            grouped = df.groupby(month_series).size()
            result: dict[Any, int] = {}
            for k, v in grouped.items():
                result[int(str(k))] = int(v)
            return result

        if group_by not in df.columns:
            raise KeyError(f"Coluna '{group_by}' não encontrada no DataFrame")

        grouped = df.groupby(group_by).size()
        return {str(k): int(v) for k, v in grouped.items()}

    @overload
    def revenue(self, df: pd.DataFrame) -> float: ...

    @overload
    def revenue(self, df: pd.DataFrame, group_by: None) -> float: ...

    @overload
    def revenue(self, df: pd.DataFrame, group_by: str) -> dict[str, float]: ...

    def revenue(self, df: pd.DataFrame, group_by: str | None = None) -> float | dict[str, float]:
        """
        Calcula receita total (valores SUS).

        Args:
            df: DataFrame com coluna 'VAL_TOT'
            group_by: Coluna para agrupamento (opcional)

        Returns:
            Receita total (float) ou por grupo (dict)
        """
        if df.empty or "VAL_TOT" not in df.columns:
            return 0.0

        if group_by is None:
            return float(df["VAL_TOT"].sum())

        if group_by not in df.columns:
            raise KeyError(f"Coluna '{group_by}' não encontrada no DataFrame")

        grouped = df.groupby(group_by)["VAL_TOT"].sum()
        return {str(k): float(v) for k, v in grouped.items()}

    def average_ticket(self, df: pd.DataFrame) -> float:
        """
        Calcula ticket médio (valor médio por internação).

        Args:
            df: DataFrame com coluna 'VAL_TOT'

        Returns:
            Ticket médio em reais
        """
        if df.empty or "VAL_TOT" not in df.columns:
            return 0.0

        return float(df["VAL_TOT"].mean())

    def demographics(self, df: pd.DataFrame) -> dict[str, int]:
        """
        Calcula distribuição por faixa etária.

        Args:
            df: DataFrame com coluna 'age_group'

        Returns:
            Dicionário com contagem por faixa etária

        Raises:
            KeyError: Se coluna 'age_group' não existir
        """
        if "age_group" not in df.columns:
            raise KeyError("Coluna 'age_group' não encontrada no DataFrame")

        if df.empty:
            categories = ["0-17", "18-29", "30-44", "45-59", "60+"]
            return dict.fromkeys(categories, 0)

        counts = df["age_group"].value_counts()
        return {str(k): int(v) for k, v in counts.items()}

    def summary(self, df: pd.DataFrame, beds: int, days: int) -> dict[str, Any]:
        """
        Gera resumo consolidado de todos os KPIs.

        Args:
            df: DataFrame com dados de internações
            beds: Número de leitos disponíveis
            days: Número de dias no período

        Returns:
            Dicionário com todos os KPIs calculados
        """
        return {
            "occupancy_rate": self.occupancy_rate(df, beds, days),
            "average_length_of_stay": self.average_length_of_stay(df),
            "volume": self.volume(df),
            "revenue": self.revenue(df),
            "average_ticket": self.average_ticket(df),
            "demographics": self.demographics(df),
        }
