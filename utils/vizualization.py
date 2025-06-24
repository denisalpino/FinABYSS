from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
import plotly.express as px
import pandas as pd

# TODO: Think about removing, cause Optuna has same function but better
def show_feature_importance(df):
    """Function for parallel coordinates vizualization based on Optuna or Ray Tune trials"""
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    X = pd.get_dummies(X)

    # Training random forests
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    result = permutation_importance(model, X, y, n_repeats=10, random_state=42)

    # Creating a DataFrame with importance
    importance_df = pd.DataFrame({
        'feature': X.columns,
        'importance': result.importances_mean
    })

    # Normalization
    total_importance = importance_df['importance'].sum()
    importance_df['normalized_importance'] = importance_df['importance'] / total_importance

    importance_df = importance_df.sort_values('normalized_importance', ascending=True)
    importance_df['importance_rounded'] = importance_df['normalized_importance'].round(2)

    fig = px.bar(
        importance_df,
        x='normalized_importance',
        y='feature',
        orientation='h',
        color='normalized_importance',
        color_continuous_scale='Inferno',
        text='importance_rounded'
    )
    fig.update_layout(
        template="plotly_dark",
        font=dict(size=18),
        paper_bgcolor="black",
        plot_bgcolor="black",
        height=900,
        width=1600,
        title='Feature Importance for Hyperparameters',
        coloraxis_colorbar=dict(title='Importance'),
        xaxis_title='Feature Importance (permutation)',
        yaxis_title='Hyperparameters'
    )
    fig.update_traces(
        marker=dict(line=dict(width=1, color='White')),
        textposition='outside',  # Placing text on the outside of a column
        textfont=dict(
            color='white',
            size=16
        )
    )
    fig.show()
    return fig


def show_hpo(
        study, metric_name,
        title="Оптимизация гиперпараметров",
        top_n=30,
        lib="optuna",
        layout_kw={}
):
    """Function for parallel coordinates vizualization based on Optuna or Ray Tune trials"""
    records = []
    for trial in study.trials:
        if lib == "optuna":
            if trial.state.name != "COMPLETE":
                continue
            score = trial.value
            rec = trial.params
        elif lib == "ray":
            if trial.last_result is None:
                continue
            score = trial.last_result[metric_name]
            if score <= 0:
                continue
            rec = trial.config
        else:
            raise ValueError(f"Unknown optimiztion library {lib}")
        rec = rec.copy()
        rec[metric_name] = score
        records.append(rec)

    df = pd.DataFrame(records)

    fig = px.parallel_coordinates(
        df.sort_values(metric_name, ascending=False)[:top_n],
        color=metric_name,
        color_continuous_scale=px.colors.sequential.Inferno,
        title=title
    )
    fig.update_layout(
        template="plotly_dark",
        font=dict(size=18),
        paper_bgcolor="black",
        plot_bgcolor="black",
        height=900,
        width=1600,
        **layout_kw
    )
    fig.show()
    return df.sort_values(metric_name, ascending=False), fig