"""Gerador de gráficos para análise hospitalar."""

from pathlib import Path
from typing import cast

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pandas as pd
from matplotlib.text import Text
from matplotlib.ticker import FuncFormatter

# Configurações globais matplotlib
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.labelsize"] = 10


class ChartGenerator:
    """Gera visualizações estáticas para análise hospitalar."""

    def __init__(self, output_dir: str | Path = "outputs/charts") -> None:
        """Inicializa o gerador de gráficos.

        Args:
            output_dir: Diretório para salvar os gráficos.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _to_array(self, series: pd.Series) -> npt.NDArray[np.float64]:  # type: ignore[type-arg]
        """Converte Series para numpy array tipado.

        Args:
            series: Pandas Series.

        Returns:
            Array numpy.
        """
        return cast(npt.NDArray[np.float64], series.to_numpy())

    def demographics_by_age(self, df: pd.DataFrame) -> Path:
        """Gera gráfico de distribuição por faixa etária.

        Args:
            df: DataFrame com coluna 'age_group'.

        Returns:
            Caminho do arquivo salvo.
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        counts = df["age_group"].value_counts().sort_index()
        values = self._to_array(counts)
        colors = plt.cm.Blues(  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue]
            [0.3 + i * 0.1 for i in range(len(counts))]
        )

        bars = ax.bar(range(len(counts)), values, color=colors)
        ax.set_xticks(range(len(counts)))
        ax.set_xticklabels(counts.index, rotation=45, ha="right")

        ax.set_xlabel("Faixa Etária")
        ax.set_ylabel("Número de Internações")
        ax.set_title("Distribuição de Internações por Faixa Etária\nAC - Janeiro 2024")

        # Adicionar valores nas barras
        for bar, val in zip(bars, values, strict=False):
            ax.annotate(
                f"{int(val):,}",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                ha="center",
                va="bottom",
                fontsize=8,
            )

        plt.tight_layout()
        filepath = self.output_dir / "01_demographics_age.png"
        fig.savefig(filepath)
        plt.close(fig)
        return filepath

    def revenue_by_specialty(self, df: pd.DataFrame) -> Path:
        """Gera gráfico de receita por especialidade.

        Args:
            df: DataFrame com colunas 'ESPEC' e 'VAL_TOT'.

        Returns:
            Caminho do arquivo salvo.
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        revenue = df.groupby("ESPEC")["VAL_TOT"].sum().sort_values(ascending=True)
        values = self._to_array(revenue)
        colors = plt.cm.Greens(  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue]
            [0.3 + i * 0.05 for i in range(len(revenue))]
        )

        ax.barh(range(len(revenue)), values, color=colors)
        ax.set_yticks(range(len(revenue)))
        ax.set_yticklabels([f"Espec. {e}" for e in revenue.index])

        ax.set_xlabel("Receita Total (R$)")
        ax.set_ylabel("Especialidade")
        ax.set_title("Receita Total por Especialidade\nAC - Janeiro 2024")

        # Formatar eixo X para milhares
        def format_currency(x: float, pos: int) -> str:  # noqa: ARG001
            return f"R$ {x / 1000:.0f}k"

        ax.xaxis.set_major_formatter(FuncFormatter(format_currency))

        plt.tight_layout()
        filepath = self.output_dir / "02_revenue_specialty.png"
        fig.savefig(filepath)
        plt.close(fig)
        return filepath

    def avg_stay_by_specialty(self, df: pd.DataFrame) -> Path:
        """Gera gráfico de tempo médio de permanência por especialidade.

        Args:
            df: DataFrame com colunas 'ESPEC' e 'stay_days'.

        Returns:
            Caminho do arquivo salvo.
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        avg_stay = df.groupby("ESPEC")["stay_days"].mean().sort_values(ascending=True)
        values = self._to_array(avg_stay)
        colors = plt.cm.Oranges(  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue]
            [0.3 + i * 0.05 for i in range(len(avg_stay))]
        )

        bars = ax.barh(range(len(avg_stay)), values, color=colors)
        ax.set_yticks(range(len(avg_stay)))
        ax.set_yticklabels([f"Espec. {e}" for e in avg_stay.index])

        ax.set_xlabel("Tempo Médio de Permanência (dias)")
        ax.set_ylabel("Especialidade")
        ax.set_title("Tempo Médio de Permanência por Especialidade\nAC - Janeiro 2024")

        # Adicionar valores nas barras
        for bar, val in zip(bars, values, strict=False):
            ax.annotate(
                f"{val:.1f}",
                xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
                ha="left",
                va="center",
                fontsize=8,
            )

        plt.tight_layout()
        filepath = self.output_dir / "03_avg_stay_specialty.png"
        fig.savefig(filepath)
        plt.close(fig)
        return filepath

    def top_diagnoses(self, df: pd.DataFrame, top_n: int = 10) -> Path:
        """Gera gráfico dos diagnósticos mais frequentes.

        Args:
            df: DataFrame com coluna 'DIAG_PRINC'.
            top_n: Número de diagnósticos a exibir.

        Returns:
            Caminho do arquivo salvo.
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        diag_counts = df["DIAG_PRINC"].value_counts().head(top_n)
        values = self._to_array(diag_counts)
        colors = plt.cm.Reds(  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue]
            [0.3 + i * 0.05 for i in range(len(diag_counts))]
        )

        bars = ax.barh(
            range(len(diag_counts)),
            values[::-1],
            color=colors[::-1],
        )
        ax.set_yticks(range(len(diag_counts)))
        ax.set_yticklabels(list(diag_counts.index)[::-1])

        ax.set_xlabel("Número de Internações")
        ax.set_ylabel("Código CID-10")
        ax.set_title(f"Top {top_n} Diagnósticos Principais (CID-10)\nAC - Janeiro 2024")

        # Adicionar valores nas barras
        for bar, val in zip(bars, values[::-1], strict=False):
            ax.annotate(
                f"{int(val):,}",
                xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
                ha="left",
                va="center",
                fontsize=8,
            )

        plt.tight_layout()
        filepath = self.output_dir / "04_top_diagnoses.png"
        fig.savefig(filepath)
        plt.close(fig)
        return filepath

    def volume_by_day(self, df: pd.DataFrame) -> Path:
        """Gera gráfico de volume de internações por dia.

        Args:
            df: DataFrame com coluna 'DT_INTER'.

        Returns:
            Caminho do arquivo salvo.
        """
        fig, ax = plt.subplots(figsize=(12, 5))

        # Nota: pyright não reconhece .dt.date corretamente
        dt_series = df["DT_INTER"].dt  # pyright: ignore[reportAttributeAccessIssue]
        daily = df.groupby(dt_series.date).size()
        daily_values = cast(npt.NDArray[np.float64], daily.values)

        ax.plot(daily.index, daily_values, marker="o", markersize=3, linewidth=1.5)
        ax.fill_between(daily.index, daily_values, alpha=0.3)

        ax.set_xlabel("Data")
        ax.set_ylabel("Número de Internações")
        ax.set_title("Volume Diário de Internações\nAC - Janeiro 2024")

        # Rotacionar labels do eixo X
        plt.xticks(rotation=45, ha="right")

        # Adicionar linha de média
        mean_val = float(daily.mean())
        ax.axhline(y=mean_val, color="red", linestyle="--", alpha=0.7)
        ax.annotate(
            f"Média: {mean_val:.0f}",
            xy=(daily.index[-1], mean_val),
            ha="right",
            va="bottom",
            color="red",
        )

        plt.tight_layout()
        filepath = self.output_dir / "05_volume_daily.png"
        fig.savefig(filepath)
        plt.close(fig)
        return filepath

    def gender_distribution(self, df: pd.DataFrame) -> Path:
        """Gera gráfico de distribuição por sexo.

        Args:
            df: DataFrame com coluna 'SEXO'.

        Returns:
            Caminho do arquivo salvo.
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        gender_map = {1: "Masculino", 3: "Feminino"}
        gender_counts = df["SEXO"].map(gender_map).value_counts()
        values = self._to_array(gender_counts)

        colors = ["#3498db", "#e74c3c"]
        result = ax.pie(
            values,
            labels=list(gender_counts.index),
            autopct="%1.1f%%",
            colors=colors,
            explode=(0.02, 0.02),
            startangle=90,
        )

        # ax.pie retorna tupla de 3 elementos quando autopct é usado
        # result[0] = wedges, result[1] = texts, result[2] = autotexts
        wedges = result[0]
        autotexts = cast(list[Text], result[2])  # type: ignore[misc]

        # Estilizar autotexts
        for autotext in autotexts:
            autotext.set_fontsize(11)
            autotext.set_fontweight("bold")

        ax.set_title("Distribuição de Internações por Sexo\nAC - Janeiro 2024")

        # Adicionar legenda com valores absolutos
        legend_labels = [
            f"{label}: {int(count):,}"
            for label, count in zip(gender_counts.index, values, strict=False)
        ]
        ax.legend(wedges, legend_labels, loc="lower center", bbox_to_anchor=(0.5, -0.1))

        plt.tight_layout()
        filepath = self.output_dir / "06_gender_distribution.png"
        fig.savefig(filepath)
        plt.close(fig)
        return filepath

    def generate_all(self, df: pd.DataFrame) -> list[Path]:
        """Gera todos os gráficos.

        Args:
            df: DataFrame com dados de internações.

        Returns:
            Lista de caminhos dos arquivos salvos.
        """
        charts = [
            self.demographics_by_age(df),
            self.revenue_by_specialty(df),
            self.avg_stay_by_specialty(df),
            self.top_diagnoses(df),
            self.volume_by_day(df),
            self.gender_distribution(df),
        ]
        return charts
