###############################################################################
#
#   Copyright: (c) 2015 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

from onyx.core import Structure, Curve, Knot, CurveIntersect
from onyx.core import GetObj, GraphNodeVt, ChildrenSet, EvalBlock

from .timeseries_functions import prices_for_risk, get_curve_usd

import numpy as np
import math

__all__ = [
    "WithRiskValueTypes",
    "pca_analysis",
    "risk_metrics",
    "max_loss",
]


# -----------------------------------------------------------------------------
def get_beta(sec_prcs, idx_prcs):
    sec_prcs, idx_prcs = CurveIntersect([sec_prcs, idx_prcs])
    sec_rets = np.diff(np.log(sec_prcs.values))
    idx_rets = np.diff(np.log(idx_prcs.values))
    A = np.vstack([idx_rets, np.ones_like(idx_rets)]).T
    beta, _ = np.linalg.lstsq(A, sec_rets)[0]
    return beta


# -----------------------------------------------------------------------------
def WithRiskValueTypes(cls):
    """
    Description:
        Class decorator. It can be applied to any class implementing MktVal
        and MktValUSD Value Types.
        It adds the following Value Types to the decorated class:
            Deltas
            FxExposures
            GrossExposure
            NetExposure
            BetaAdjNetExposure
            BetaBySecurity
            ForwardVol
            VaR
            AdjVar
            MaxLoss
        These are further auxiliary Value Types used by the ones described
        above:
            RiskMktValues
    """
    # -------------------------------------------------------------------------
    def Deltas(self, graph):
        deltas = Structure()
        for kid in ChildrenSet(self, "MktValUSD", "Spot", "Asset", graph):
            cross = "{0:3s}/USD".format(graph(kid, "Denominated"))
            spot = graph(kid, "Spot")
            fx = graph(cross, "Spot")
            shift = 0.01*spot
            with EvalBlock() as eb:
                eb.set_diddle(kid, "Spot", spot+shift)
                up = graph(self, "MktValUSD")
                eb.set_diddle(kid, "Spot", spot-shift)
                dw = graph(self, "MktValUSD")
            deltas += Structure({kid: (up-dw) / (2.0*shift*fx)})
        deltas.drop_zeros()
        return deltas

    # -------------------------------------------------------------------------
    def FxExposures(self, graph):
        exposures = Structure()
        for kid in ChildrenSet(self, "MktValUSD",
                               "Spot", "CurrencyCross", graph):
            spot = graph(kid, "Spot")
            shift = 0.01*spot
            with EvalBlock() as eb:
                eb.set_diddle(kid, "Spot", spot+shift)
                up = graph(self, "MktValUSD")
                eb.set_diddle(kid, "Spot", spot-shift)
                dw = graph(self, "MktValUSD")
            exposures += Structure({kid: (up-dw) / (2.0*shift)})
        exposures.drop_zeros()
        return exposures

    # -------------------------------------------------------------------------
    def GrossExposure(self, graph):
        gross = 0.0
        for sec, qty in graph(self, "Deltas").items():
            spot_usd = graph(sec, "SpotUSD")
            gross += math.fabs(qty)*spot_usd
        cross = "{0:3s}/USD".format(graph(self, "Denominated"))
        fx = graph(cross, "Spot")
        return gross / fx

    # -------------------------------------------------------------------------
    def NetExposure(self, graph):
        net = 0.0
        for sec, qty in graph(self, "Deltas").items():
            spot_usd = graph(sec, "SpotUSD")
            net += qty*spot_usd
        cross = "{0:3s}/USD".format(graph(self, "Denominated"))
        fx = graph(cross, "Spot")
        return net / fx

    # -------------------------------------------------------------------------
    def BetaAdjNetExposure(self, graph):
        beta_by_sec = graph(self, "BetaBySecurity")
        beta = 0.0
        for sec, qty in graph(self, "Deltas").items():
            beta += beta_by_sec[sec]*qty*graph(sec, "SpotUSD")
        cross = "{0:3s}/USD".format(graph(self, "Denominated"))
        fx = graph(cross, "Spot")
        return beta / fx

    # -------------------------------------------------------------------------
    def BetaBySecurity(self, graph):
        # --- to improve performance:
        #     1) we fetch curves using Risk.StartDate and Risk.EndDate and then
        #        we crop them to Risk.BetaStartDate and Risk.BetaEndDate,
        #     2) we dynamically add BetaLookupTable attribute to each security
        #        and cache there beta by index, start date, end date.
        start = graph("Risk", "StartDate")
        end = graph("Risk", "EndDate")
        beta_start = graph("Risk", "BetaStartDate")
        beta_end = graph("Risk", "BetaEndDate")
        betas = Structure()
        index = graph("Risk", "RefIndex")
        idx_prcs = get_curve_usd(index, beta_start, beta_end)
        for sec in ChildrenSet(self, "MktValUSD", "Spot", "Asset", graph):
            tag = (index, beta_start, beta_end)
            sec = GetObj(sec)
            try:
                beta = sec.BetaLookupTable[tag]
            except AttributeError:
                sec_prcs = graph(sec, "PricesForRisk",
                                 start, end).crop(beta_start, beta_end)
                beta = get_beta(sec_prcs, idx_prcs)
                sec.BetaLookupTable = {tag: beta}
            except KeyError:
                sec_prcs = graph(sec, "PricesForRisk",
                                 start, end).crop(beta_start, beta_end)
                beta = get_beta(sec_prcs, idx_prcs)
                sec.BetaLookupTable[tag] = beta
            betas[sec.Name] = beta
        return betas

    # -------------------------------------------------------------------------
    def RiskMktValues(self, graph):
        start = graph("Risk", "StartDate")
        end = graph("Risk", "EndDate")

        # --- load fx to convert mkt_vls from USD to the Denominated
        #     currency
        cross = "{0:3s}/USD".format(graph(self, "Denominated"))
        fx = graph(cross, "Spot")

        mkt_vls = None
        for sec, qty in graph(self, "Deltas").items():
            prcs = graph(sec, "PricesForRisk", start, end)
            if mkt_vls is None:
                mkt_vls = prcs*qty
            else:
                prcs, mkt_vls = CurveIntersect([prcs, mkt_vls])
                mkt_vls += prcs*qty

        if mkt_vls is None:
            return Curve()
        else:
            return mkt_vls / fx

    # -------------------------------------------------------------------------
    def ForwardVol(self, graph):
        start = graph("Risk", "VaRStartDate")
        end = graph("Risk", "VaREndDate")
        mkt_values_risk = graph(self, "RiskMktValues").crop(start, end)

        return risk_metrics(mkt_values_risk)["Std"]

    # -------------------------------------------------------------------------
    def VaR(self, graph, ndays=1, pctl=95.0):
        start = graph("Risk", "VaRStartDate")
        end = graph("Risk", "VaREndDate")
        mkt_values_risk = graph(self, "RiskMktValues").crop(start, end)

        return risk_metrics(mkt_values_risk, ndays=ndays, pctl=pctl)["VaR"]

    # -------------------------------------------------------------------------
    def AdjVaR(self, graph, ndays=1, pctl=95.0, nbos_adj=60):
        start = graph("Risk", "VaRStartDate")
        end = graph("Risk", "VaREndDate")
        mkt_values_risk = graph(self, "RiskMktValues").crop(start, end)

        metrics = risk_metrics(mkt_values_risk,
                               ndays=ndays, pctl=pctl, nbos_adj=nbos_adj)

        return metrics["AdjFactor"]*["VaR"]

    # -------------------------------------------------------------------------
    def MaxLoss(self, graph, ndays=1):
        return max_loss(graph(self, "RiskMktValues"), ndays=ndays)

    # --- here we whack value types into the decorated class
    cls.Deltas = GraphNodeVt("Property")(Deltas)
    cls.FxExposures = GraphNodeVt("Property")(FxExposures)
    cls.GrossExposure = GraphNodeVt("Property")(GrossExposure)
    cls.NetExposure = GraphNodeVt("Property")(NetExposure)

    cls.BetaBySecurity = GraphNodeVt("Property")(BetaBySecurity)
    cls.BetaAdjNetExposure = GraphNodeVt("Property")(BetaAdjNetExposure)

    cls.RiskMktValues = GraphNodeVt("Property")(RiskMktValues)

    cls.ForwardVol = GraphNodeVt("Calc")(ForwardVol)
    cls.VaR = GraphNodeVt("Calc")(VaR)
    cls.AdjVaR = GraphNodeVt("Calc")(AdjVaR)
    cls.MaxLoss = GraphNodeVt("Calc")(MaxLoss)

    return cls


# -----------------------------------------------------------------------------
def risk_metrics(mkt_values, ndays=1, pctl=95.0, nbos_adj=60):
    """
    Description:
        Return key risk metrics given daily timeseries of market values.
    Inputs:
        mkt_values - a curve with daily market values for the portfolio.
        ndays      - time-horizon for calculation of risk-metrics.
        pctl       - confidence level for calculation of VaR and cVaR.
        nbos_adj   - use the last nbos_adj observations to adjust for
                     higher/lower short term volatility (for AdjVaR).
    Returns:
        A dictionary with:
            Std:       the standard deviation of the distribution of returns.
            VaR:       the Value at Risk at the desired percentile.
            cVaR:      the conditional Value at risk defined as the expected
                       value of the tail of the distribution beyhond the
                       desired percentile.
            AdjFactor: the adjustment factor to account for higher/lower short
                       term volatility.
    """
    if len(mkt_values) == 0:
        std = 0.0
        var = 0.0
        cvar = 0.0
        adj = 1.0
    else:
        # --- we flip the sign so that losses are positive numbers. we reverse
        #     the array so that the eventually unused elements (when the length
        #     of the array is not a whole multiple of ndays) are the oldest
        values = -mkt_values.values[::-1][::ndays][::-1]
        pnl_loss = np.diff(values)
        pnl_loss -= pnl_loss.mean()

        std = pnl_loss.std()
        var = np.percentile(pnl_loss, pctl)
        cvar = pnl_loss[pnl_loss >= var].mean()

        # --- the adjustment is calculated as the ratio between a short-term
        #     estimate of the standard deviation and the estimate calculated
        #     over the full range.
        adj = pnl_loss[-nbos_adj:].std() / std

    return {"Std": std, "VaR": var, "cVaR": cvar, "AdjFactor": adj}


# -----------------------------------------------------------------------------
def max_loss(mkt_values, ndays=1):
    """
    Description:
        Return the largest loss given daily timeseries of market values.
    Inputs:
        mkt_values - a curve with daily market values for the book/ portfolio.
        ndays      - time-horizon for calculation of risk-metrics.
    Returns:
        A knot with the maximum loss (expressed as a positive number) and the
        corresponding date.
    """
    if len(mkt_values) == 0:
        max_loss_val = 0.0
        max_loss_date = None
    else:
        # --- for max loss, consider all (i.e. overlapping) ndays-differences:
        #     flip the sign so that losses are positive numbers
        diffs = -(mkt_values.values[ndays:] - mkt_values.values[:-ndays])
        max_loss_idx = diffs.argmax()
        max_loss_val = diffs[max_loss_idx]

        # --- the date of max loss is meant to be the beginning of the ndays
        #     interval
        max_loss_date = mkt_values.dates[max_loss_idx].strftime("%d-%b-%Y")

    return Knot(max_loss_date, max_loss_val)


# -----------------------------------------------------------------------------
def pca_analysis(names, start, end, pca, agg=None):
    """
    Description:
        Return PCA analisys on the covariance matrix of the log-returns (based
        on adjusted close prices) of a set of securities.
    Inputs:
        names - a list of asset's names
        start - the start date
        end   - the end date
        pca   - the class used to perform PCA analysis (for instance
                matplotlib.mlab.PCA)
        agg   - an optional aggregation function (such as Weekly, etc)
    Returns:
        An instance of pca.
    """
    curves = [prices_for_risk(name, start, end) for name in names]
    curves = [crv for crv in curves if len(crv)]
    if agg is not None:
        curves = [agg(crv) for crv in curves]
    curves = CurveIntersect(curves)
    values = np.vstack([np.diff(np.log(crv.values)) for crv in curves]).T
    return pca(values)
