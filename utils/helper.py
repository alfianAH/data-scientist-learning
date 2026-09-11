import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st

def plot_bar_by_season(
    df: pd.DataFrame,
    params: list[str],
    season_order: list = None,
    ncols: int = 3,
    figsize_per_plot: tuple = (5, 4),
):
    if season_order is None:
        season_order = ["Spring", "Summer", "Autumn", "Winter"]

    df_copy = df.copy()

    n_params = len(params)
    nrows = int(np.ceil(n_params / ncols))

    fig_width = figsize_per_plot[0] * ncols
    fig_height = figsize_per_plot[1] * nrows

    fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(fig_width, fig_height))
    axs = np.array(axs).reshape(nrows, ncols).flatten(order="C")

    for i, col in enumerate(params):
        if col not in df_copy.columns:
            print(f"Peringatan: kolom '{col}' tidak ditemukan, dilewati.")
            axs[i].axis("off")
            continue

        medians = df_copy.groupby('season')[col].median().reindex(season_order)
        highest_season = medians.idxmax()

        colors = ['tomato' if season == highest_season else 'lightgray' for season in season_order]

        sns.barplot(
            data=df_copy, x="season", y=col, order=season_order,
            ax=axs[i], color="lightgreen",
            estimator=np.median,
            palette=colors,
            hue="season", legend=False,
            errorbar=None,
        )
        axs[i].set_title(col)
        axs[i].tick_params(axis="x")

    for j in range(n_params, len(axs)):
        axs[j].axis("off")

    fig.suptitle(f"Distribusi Parameter Polutan per Musim", fontsize=14)
    plt.tight_layout()

    return fig


def plot_trend_line(
    df: pd.DataFrame,
    x_param: str,
    y_param_list: str,
    x_label: str,
    quantile: float = 0.95,
    n_bins: int = 30,
    min_points_per_bin: int = 20,
    show_sample_size: bool = True,
    ncols: int = 3,
    figsize_per_plot: tuple = (5, 4),
):
    """
    Membuat garis tren (median per bin) antara x_param (support parameter,
    misal TEMP, WSPM, PRES, RAIN) dan y_param (polutan, misal PM2.5).

    Parameters:
        df                 : dataframe (idealnya sudah difilter 1 station)
        x_param            : nama kolom untuk sumbu-X (parameter pendukung)
        y_param            : nama kolom untuk sumbu-Y (polutan)
        x_label            : label untuk kolom x (parameter pendukung)
        quantile           : quantile untuk menentukan garis tren
        n_bins             : jumlah bin untuk membagi rentang x_param
        min_points_per_bin : jumlah minimum data dalam 1 bin agar bin tsb
                             tetap ditampilkan (bin dengan data terlalu
                             sedikit akan dilewati, supaya tidak
                             menyesatkan seperti dibahas sebelumnya)
        show_sample_size   : jika True, ketebalan garis/ukuran titik
                             disesuaikan dengan jumlah data per bin,
                             supaya bin dengan sedikit data terlihat
                             "kurang meyakinkan" secara visual
        figsize            : ukuran gambar

    Return: DataFrame ringkasan (bin_center, median, count) untuk
        verifikasi lebih lanjut.
    """

    n_params = len(y_param_list)
    nrows = int(np.ceil(n_params / ncols))

    fig_width = figsize_per_plot[0] * ncols
    fig_height = figsize_per_plot[1] * nrows

    # --- Plot ---
    fig, axs = plt.subplots(nrows, ncols, figsize=(fig_width, fig_height))
    axs = np.array(axs).reshape(nrows, ncols).flatten(order="C")

    for i, y_param in enumerate(y_param_list):
        data = df[[x_param, y_param]]

        # --- Bagi rentang x_param menjadi n_bins ---
        bin_edges = np.linspace(data[x_param].min(), data[x_param].max(), n_bins + 1)
        data = data.copy()
        data["bin"] = pd.cut(data[x_param], bins=bin_edges, include_lowest=True)

        # --- Hitung median & jumlah data per bin ---
        summary = data.groupby("bin", observed=True).agg(
            quantile=(y_param, lambda x: x.quantile(quantile)),
            bin_center=(x_param, "mean"),
            count=(y_param, "count")
        ).reset_index(drop=True)

        # --- Filter bin yang datanya terlalu sedikit (kurang meyakinkan) ---
        summary_reliable = summary[summary["count"] >= min_points_per_bin].copy()
        summary_unreliable = summary[summary["count"] < min_points_per_bin].copy()

        # if len(summary_unreliable) > 0:
        #     print(f"Peringatan: {len(summary_unreliable)} bin dilewati karena "
        #         f"jumlah data < {min_points_per_bin} (kurang meyakinkan).")

        peak_idx = summary_reliable["quantile"].idxmax()
        peak_x = summary_reliable.loc[peak_idx, "bin_center"]
        peak_y = summary_reliable.loc[peak_idx, "quantile"]
        peak_count = summary_reliable.loc[peak_idx, "count"]

        if show_sample_size:
            sizes = (summary_reliable["count"] / summary_reliable["count"].max()) * 200 + 20
            axs[i].plot(
                summary_reliable["bin_center"],
                summary_reliable["quantile"],
                color="#555555",
                linewidth=2,
                zorder=2
            )
            axs[i].scatter(
                summary_reliable["bin_center"],
                summary_reliable["quantile"],
                s=sizes,
                color="#555555",
                alpha=0.2,
                zorder=3,
                label="Titik besar = lebih sering terjadi"
            )
        else:
            axs[i].plot(
                summary_reliable["bin_center"],
                summary_reliable["quantile"],
                color="#555555",
                linewidth=2,
                marker="o",
                markersize=4,
                zorder=2
            )

        # Highlight titik PUNCAK dengan warna mencolok berbeda
        axs[i].scatter(
            [peak_x], [peak_y],
            s=220, color="red",
            zorder=4,
            edgecolor="darkred",
            linewidth=1.5,
            label="Titik puncak (nilai tertinggi)"
        )

        # Anotasi teks + panah menunjuk langsung ke titik puncak ---
        axs[i].annotate(
            f"Puncak {y_param} \u2248 {peak_y:.0f}\n@ {x_param} \u2248 {peak_x:.1f}",
            xy=(peak_x, peak_y),
            xytext=(0.6, 0.5), textcoords="axes fraction",
            fontsize=9, color="darkred", fontweight="bold",
            ha="center",
            arrowprops=dict(arrowstyle="->", color="darkred", linewidth=1.5,
                            connectionstyle="arc3,rad=0.2"),
            bbox=dict(boxstyle="round,pad=0.4", facecolor="mistyrose",
                    edgecolor="darkred", alpha=0.5),
        )

        axs[i].set_xlabel(x_param)
        axs[i].set_ylabel(y_param)
        axs[i].set_title(y_param)

    for j in range(n_params, len(axs)):
        axs[j].axis("off")

    handles, labels = axs[-1].get_legend_handles_labels()
    by_label = dict(zip(labels, handles))

    # 3. Buat legenda global di level figure (di luar grafik)
    fig.legend(by_label.values(), by_label.keys(),
            loc='lower right',
            bbox_to_anchor=(1, 0), # Geser ke kanan luar grafik
            borderaxespad=0)
    fig.suptitle(f"Tren {x_label} berdasarkan polutan", fontsize=14)
    plt.tight_layout()
    fig.subplots_adjust(bottom=0.15)

    return fig


def create_agg_dict(df, columns, agg_values):
    agg_dict = {}

    for col in columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            agg_dict[col] = agg_values

    return agg_dict


def plot_percentage_change(
    df: pd.DataFrame,
    params: list,
    years: list,
):
    agg_dict = create_agg_dict(df, params, ['median'])

    data_df = df.groupby([
        'station',
        'season_year',
    ]).agg(agg_dict).reset_index()
    data_df.columns = data_df.columns.droplevel(1)

    if years is None:
        years = data_df['season_year'].unique()

    # Pisahkan min dan max
    data_min = (
        data_df[data_df['season_year'] == min(years)]
        .set_index('station')[params]
    )

    data_max = (
        data_df[data_df['season_year'] == max(years)]
        .set_index('station')[params]
    )

    # Persentase perubahan
    percentage_change = ((data_max - data_min) / data_min) * 100

    fig = plt.figure(figsize=(10, 7))

    sns.heatmap(
        percentage_change,
        annot=True,
        fmt='.1f',
        center=0,
        cmap='RdYlGn_r',
        vmin=-100, vmax=100, square=True,
    )

    plt.title(
        'Persentase Perubahan Rata-rata Konsentrasi Polutan\n'
        f'{min(years)} vs {max(years)}'
    )

    plt.xlabel('Parameter')
    plt.ylabel('Station')
    plt.tight_layout()

    return fig


def convert_df_year_to_season_year(df):
    df_copy = df.copy()
    df_copy['season_year'] = df_copy['date'].dt.year
    df_copy.loc[
        df_copy['season'].eq('Winter') &
        df_copy['date'].dt.month.isin([1, 2]),
        'season_year'
    ] -= 1

    return df_copy


def plot_percentage_change_per_year(
    df: pd.DataFrame,
    param: str,
    baseline_year: int = 2013,
):
    data_df = df.groupby([
        'station',
        'season_year',
    ])[param].median().reset_index()

    baseline = (
        data_df[data_df['season_year'] == baseline_year]
        .set_index('station')[param]
    )

    # Hitung persentase perubahan
    data_df['change_%'] = (
        (
            data_df[param]
            - data_df['station'].map(baseline)
        )
        / data_df['station'].map(baseline)
        * 100
    )

    change_df = data_df.pivot(
        index='station',
        columns='season_year',
        values='change_%'
    )

    # Urutkan tahun
    change_df = change_df.sort_index(axis=1)

    # Cari MIN dan MAX

    min_idx = data_df['change_%'].idxmin()
    max_idx = data_df['change_%'].idxmax()

    min_row = data_df.loc[min_idx]
    max_row = data_df.loc[max_idx]

    min_value = min_row['change_%']
    min_station = min_row['station']
    min_year = min_row['season_year']

    max_value = max_row['change_%']
    max_station = max_row['station']
    max_year = max_row['season_year']


    # Plot
    fig = plt.figure(figsize=(10, 6))

    ax = sns.heatmap(
        change_df,
        annot=True,
        fmt='.1f',
        center=0,
        cmap='RdYlGn_r',
        linewidths=0.5,
        vmin=-100, vmax=100, square=True,
        cbar_kws={
            'label': f'Perubahan terhadap {baseline_year} (%)'
        }
    )

    # Tentukan posisi MIN/MAX
    columns = list(change_df.columns)
    rows = list(change_df.index)

    min_x = columns.index(min_year)
    min_y = rows.index(min_station)

    max_x = columns.index(max_year)
    max_y = rows.index(max_station)

    ax.add_patch(
        plt.Rectangle(
            (min_x, min_y),
            1,
            1,
            fill=False,
            linewidth=3
        )
    )

    # Tandai MIN
    ax.text(
        min_x + 0.5,
        min_y + 0.22,
        'MIN',
        ha='center',
        va='center',
        fontweight='bold'
    )

    # Tandai MAX
    ax.add_patch(
        plt.Rectangle(
            (max_x, max_y),
            1,
            1,
            fill=False,
            linewidth=3
        )
    )

    ax.text(
        max_x + 0.5,
        max_y + 0.22,
        'MAX',
        ha='center',
        va='center',
        fontweight='bold'
    )

    plt.title(
        f'Perubahan {param} terhadap {baseline_year}\n'
        f'MAX: {max_value:.1f}% ({max_station}, {max_year}) | '
        f'MIN: {min_value:.1f}% ({min_station}, {min_year})'
    )

    plt.title(
        f'Perubahan Median {param}\n'
        f'Baseline {baseline_year}'
    )

    plt.xlabel('Tahun')
    plt.ylabel('Station')
    plt.tight_layout()

    return fig


def plot_annual_heatmap(
    df: pd.DataFrame,
    pollutant: str,
    figsize=(10, 6),
    is_heatmap_square=True,
):
    data_df = df.groupby([
        'station',
        'season_year',
    ])[pollutant].median().reset_index()

    # Pivot untuk heatmap
    heatmap_data = data_df.pivot(
        index='station',
        columns='season_year',
        values=pollutant
    )

    # Cari posisi min dan max
    min_idx = data_df[pollutant].idxmin()
    max_idx = data_df[pollutant].idxmax()

    min_row = data_df.loc[min_idx]
    max_row = data_df.loc[max_idx]

    min_station = min_row['station']
    min_season_year = min_row['season_year'] 
    min_value = min_row[pollutant]

    max_station = max_row['station']
    max_season_year = max_row['season_year']
    max_value = max_row[pollutant]

    # Buat heatmap
    fig = plt.figure(figsize=figsize)

    ax = sns.heatmap(
        heatmap_data,
        annot=True,
        fmt='.1f',
        cmap='RdYlGn_r',
        linewidths=0.5,
        square=is_heatmap_square,
        cbar_kws={
            'label': f'Konsentrasi {pollutant}'
        }
    )

    # Cari posisi cell min dan max
    min_x = list(heatmap_data.columns).index(min_season_year)
    min_y = list(heatmap_data.index).index(min_station)

    max_x = list(heatmap_data.columns).index(max_season_year)
    max_y = list(heatmap_data.index).index(max_station)

    # Tandai MIN
    ax.add_patch(
        plt.Rectangle(
            (min_x, min_y),
            1, 1,
            fill=False,
            edgecolor='blue',
            linewidth=3
        )
    )

    ax.text(
        min_x + 0.5,
        min_y + 0.25,
        'MIN',
        ha='center',
        va='center',
        fontweight='bold'
    )

    # Tandai MAX
    ax.add_patch(
        plt.Rectangle(
            (max_x, max_y),
            1, 1,
            fill=False,
            edgecolor='red',
            linewidth=3
        )
    )

    ax.text(
        max_x + 0.5,
        max_y + 0.25,
        'MAX',
        ha='center',
        va='center',
        fontweight='bold'
    )

    plt.title(
        f'Konsentrasi Tahunan {pollutant}\n'
        f'Min: {min_value:.1f} ({min_station}, {min_season_year}) | '
        f'Max: {max_value:.1f} ({max_station}, {max_season_year})'
    )

    plt.xlabel('Tahun')
    plt.ylabel('Station')
    plt.tight_layout()

    return fig
