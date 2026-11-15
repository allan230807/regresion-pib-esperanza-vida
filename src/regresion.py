"""Funciones de regresión lineal bivariante (Estadística II).

Todas las cuentas se hacen con las fórmulas del curso (sumas de cuadrados,
error estándar, t de Student y F de Fisher) y se contrastan con statsmodels.
El informe en Word y la app de Streamlit usan este mismo módulo, así que
los números coinciden en ambos.
"""
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan, het_white, linear_reset, lilliefors
from statsmodels.stats.stattools import durbin_watson, jarque_bera

RUTA_DATOS = "data/pib_esperanza_vida_2024.csv"
ALFA = 0.05


def cargar_datos(ruta: str = RUTA_DATOS) -> pd.DataFrame:
    df = pd.read_csv(ruta)
    df["ln_pib_pc"] = np.log(df["pib_pc_usd_2024"])
    return df


@dataclass
class Modelo:
    nombre: str
    x: np.ndarray
    y: np.ndarray
    log: bool
    alfa: float = ALFA
    res: dict = field(default_factory=dict)

    # --- estimación -------------------------------------------------------
    def ajustar(self):
        x, y, n = self.x, self.y, len(self.x)
        xm, ym = x.mean(), y.mean()
        sxx = np.sum((x - xm) ** 2)
        syy = np.sum((y - ym) ** 2)
        sxy = np.sum((x - xm) * (y - ym))
        b = sxy / sxx
        a = ym - b * xm
        yhat = a + b * x
        e = y - yhat
        sce = np.sum(e ** 2)              # suma de cuadrados del error (residual)
        scr = np.sum((yhat - ym) ** 2)    # suma de cuadrados de la regresión
        sct = syy
        gl = n - 2
        s2 = sce / gl
        s = np.sqrt(s2)
        se_b = s / np.sqrt(sxx)
        se_a = s * np.sqrt(1 / n + xm ** 2 / sxx)
        tcrit = stats.t.ppf(1 - self.alfa / 2, gl)
        t_b, t_a = b / se_b, a / se_a
        r = sxy / np.sqrt(sxx * syy)
        r2 = r ** 2
        t_r = r * np.sqrt(gl) / np.sqrt(1 - r2)
        z = np.arctanh(r)
        zc = stats.norm.ppf(1 - self.alfa / 2)
        ic_rho = np.tanh([z - zc / np.sqrt(n - 3), z + zc / np.sqrt(n - 3)])
        F = (scr / 1) / s2
        self.res = dict(
            n=n, xm=xm, ym=ym, sxx=sxx, syy=syy, sxy=sxy, a=a, b=b, yhat=yhat, e=e,
            sce=sce, scr=scr, sct=sct, gl=gl, s2=s2, s=s, se_a=se_a, se_b=se_b,
            tcrit=tcrit, t_a=t_a, t_b=t_b,
            p_a=2 * stats.t.sf(abs(t_a), gl), p_b=2 * stats.t.sf(abs(t_b), gl),
            ic_a=(a - tcrit * se_a, a + tcrit * se_a), ic_b=(b - tcrit * se_b, b + tcrit * se_b),
            r=r, r2=r2, r2_aj=1 - (1 - r2) * (n - 1) / gl, t_r=t_r,
            p_r=2 * stats.t.sf(abs(t_r), gl), z_fisher=z, ic_rho=tuple(ic_rho),
            F=F, p_F=stats.f.sf(F, 1, gl), Fcrit=stats.f.ppf(1 - self.alfa, 1, gl),
        )
        # comprobación con statsmodels
        ols = sm.OLS(y, sm.add_constant(x)).fit()
        assert np.allclose([a, b], ols.params) and np.isclose(r2, ols.rsquared)
        self.ols = ols
        self.ols_hc3 = ols.get_robustcov_results(cov_type="HC3")
        return self

    # --- supuestos --------------------------------------------------------
    def supuestos(self):
        e, X = self.res["e"], self.ols.model.exog
        sw = stats.shapiro(e)
        jb = jarque_bera(e)
        ks = lilliefors(e, dist="norm")
        bp = het_breuschpagan(e, X)
        wh = het_white(e, X)
        rs = linear_reset(self.ols, power=2, use_f=True)
        return {
            "Shapiro-Wilk (normalidad)": (sw.statistic, sw.pvalue),
            "Kolmogorov-Smirnov-Lilliefors (normalidad)": (ks[0], ks[1]),
            "Jarque-Bera (normalidad)": (jb[0], jb[1]),
            "Breusch-Pagan (homocedasticidad)": (bp[0], bp[1]),
            "White (homocedasticidad)": (wh[0], wh[1]),
            "RESET de Ramsey (linealidad)": (float(rs.fvalue), float(rs.pvalue)),
            "Durbin-Watson (independencia)": (durbin_watson(e), np.nan),
        }

    # --- intervalos -------------------------------------------------------
    def transformar(self, pib):
        return np.log(pib) if self.log else np.asarray(pib, dtype=float)

    def intervalos(self, pib):
        """IC para la media μ_y|x y para un valor particular Y_a, en X = pib."""
        r = self.res
        x0 = self.transformar(pib)
        y0 = r["a"] + r["b"] * x0
        h = 1 / r["n"] + (x0 - r["xm"]) ** 2 / r["sxx"]
        se_m = r["s"] * np.sqrt(h)
        se_p = r["s"] * np.sqrt(1 + h)
        t = r["tcrit"]
        return dict(x0=x0, y0=y0, se_media=se_m, se_pred=se_p,
                    ic_media=(y0 - t * se_m, y0 + t * se_m),
                    ic_pred=(y0 - t * se_p, y0 + t * se_p))

    def anova(self) -> pd.DataFrame:
        r = self.res
        return pd.DataFrame({
            "Fuente de variación": ["Regresión", "Error (residual)", "Total"],
            "Suma de cuadrados": [r["scr"], r["sce"], r["sct"]],
            "Grados de libertad": [1, r["gl"], r["n"] - 1],
            "Cuadrado medio": [r["scr"], r["s2"], np.nan],
            "F calculado": [r["F"], np.nan, np.nan],
            "Valor p": [r["p_F"], np.nan, np.nan],
        })


def modelos(df: pd.DataFrame):
    y = df["esperanza_vida_2024"].to_numpy()
    lin = Modelo("Modelo 1: Y = a + b·PIB", df["pib_pc_usd_2024"].to_numpy(), y, log=False).ajustar()
    log = Modelo("Modelo 2: Y = a + b·ln(PIB)", df["ln_pib_pc"].to_numpy(), y, log=True).ajustar()
    return lin, log


def descriptivas(s: pd.Series) -> dict:
    s = s.dropna()
    q1, q3 = s.quantile([.25, .75])
    return {
        "n": len(s), "Media": s.mean(), "Mediana": s.median(),
        "Desviación estándar": s.std(ddof=1), "Varianza": s.var(ddof=1),
        "Coef. de variación (%)": 100 * s.std(ddof=1) / s.mean(),
        "Mínimo": s.min(), "Q1": q1, "Q3": q3, "Máximo": s.max(), "Rango": s.max() - s.min(),
        "Rango intercuartílico": q3 - q1,
        "Asimetría": stats.skew(s, bias=False), "Curtosis (exceso)": stats.kurtosis(s, bias=False),
    }
