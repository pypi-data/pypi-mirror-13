###############################################################################
#
#   Agora Portfolio & Risk Management System
#
#   Copyright 2015 Carlo Sbraccia
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

from onyx.core import (Date, RDate, Curve, GCurve, HlocvCurve,
                       Interpolate, ApplyAdjustments, ListField, StringField,
                       Archivable, ReferenceField, GraphNodeVt, EvalBlock)

from agora.corelibs.ufo_functions import (MktIndirectionFactory,
                                          enforce_archivable_entitlements)

import numpy as np
import collections

__all__ = ["CorporateActions"]

# --- these are dividends paid as cash
CASH_ACTIONS = {"Regular Cash", "Special Cash", "Final", "Interim",
                "1st Interim", "2nd Interim", "3rd Interim", "4th Interim",
                "Return of Capital", "Return Prem.", "Interest on Capital",
                "Pro Rata", "Partnership Dist", "Estimated", 
                "Proceeds from sale of Rights"}

# --- these are corporate action for which we mark the multiplicative
#     adjustment factor directly
MUL_ACTIONS = {"Open Offer", "Rights Issue",
               "Entitlement", "Spinoff", "Warrant", "In-specie"}

# --- these are corporate action for which we mark the divisive
#     adjustment factor directly
DIV_ACTIONS = {"Stock Split", "Bonus",
               "Stock Dividend", "Quote Lot Change"}

# --- these are corporate ations that don't affect historical prices
SKIP_ACTIONS = {"Cancelled", "Omitted", "Discontinued"}


###############################################################################
@enforce_archivable_entitlements
class CorporateActions(Archivable):
    """
    Class used to represent corporate actions, archived by their Declared Date.
    """
    Asset = ReferenceField(obj_type="EquityAsset")

    # -------------------------------------------------------------------------
    @MktIndirectionFactory(StringField)
    def DvdCcy(self, graph):
        pass

    # -------------------------------------------------------------------------
    @MktIndirectionFactory(ListField)
    def Info(self, graph):
        pass

    # -------------------------------------------------------------------------
    @GraphNodeVt()
    def LastKnot(self, graph, date=None):
        date = date or graph("Database", "MktDataDate")
        return self.get_dated("Info", date, strict=False)

    # -------------------------------------------------------------------------
    @GraphNodeVt()
    def NextExDateActions(self, graph, start):
        # FIXME: this is extremely inefficient, we should use a specialized
        #        query
        pd = graph("Database", "PositionsDate")
        crv = graph(self, "InfoCurve").crop(start=max(start, pd))
        if len(crv):
            return crv.front.value
        else:
            return [{"Ex-Date": Date.high_date(), "Dividend Type": None}]

    # -------------------------------------------------------------------------
    @GraphNodeVt()
    def InfoCurve(self, graph, by_date="Ex-Date"):
        info_by_date = collections.defaultdict(list)
        for _, info in self.get_history("Info"):
            for item in info:
                # --- sometimes corporate actions are publised before the
                #     ex-date is available
                date = item[by_date]
                if date is not None:
                    info_by_date[date].append(item)

        return GCurve(info_by_date.keys(), info_by_date.values())

    # -------------------------------------------------------------------------
    @GraphNodeVt()
    def DvdCurve(self, graph, start=None, end=None):
        """
        N.B.: we only include cash dividends here.
        """
        info_crv = graph(self, "InfoCurve").crop(start, end)

        dvd_crv = Curve()
        for _, value in info_crv:
            for action in value:
                if action["Dividend Type"] in CASH_ACTIONS:
                    date = action["Ex-Date"]
                    if date in dvd_crv:
                        dvd_crv[date] += action["Dividend Amount"]
                    else:
                        dvd_crv[date] = action["Dividend Amount"]

        return dvd_crv

    # -------------------------------------------------------------------------
    @GraphNodeVt()
    def AdjustCurve(self, graph, crv):
        ccy = GetVal(GetVal(self, "Asset"), "Denominated")
        mul = GetVal(GetVal(self, "Asset"), "Multiplier")

        start = crv.front.date
        end = crv.back.date

        if isinstance(crv, HlocvCurve):
            closes = crv.curve(field="Close")
        else:
            closes = crv

        offset = RDate("-1b")
        adj_crv = Curve()

        for date, actions in graph(self, "InfoCurve", by_date="Ex-Date"):

            if date == start:
                # --- remove this knot from the curve and skip this corporate
                #     action
                start += RDate("+1b")
                continue
            elif date < start or date > end:
                continue

            prev_biz_date = date + offset
            prev_close = Interpolate(closes, prev_biz_date)

            cash, mul, div = [], [], []
            for action in actions:
                dvd_type = action["Dividend Type"]
                amount = action["Dividend Amount"]
                if dvd_type in CASH_ACTIONS:
                    fx_adj = self.fx_ajustment(ccy, mul, date)
                    cash.append(amount*fx_adj)
                elif dvd_type in MUL_ACTIONS:
                    mul.append(amount)
                elif dvd_type in DIV_ACTIONS:
                    div.append(amount)
                elif dvd_type in SKIP_ACTIONS:
                    continue
                else:
                    raise RuntimeError("Unknown Dividend Type {0:s} "
                                       "for {1:s}".format(dvd_type, self.Name))

            adj = 1.0 - sum(cash) / prev_close
            adj *= np.prod(mul)
            adj *= np.prod([1.0 / x for x in div])

            adj_crv[date] = adj

        adj_crv = Curve(adj_crv.dates,
                        np.cumprod(adj_crv.values[::-1])[::-1])

        return ApplyAdjustments(crv, adj_crv).crop(start=start, end=end)

    # -------------------------------------------------------------------------
    def fx_adjustment(self, ccy, mul, mdd):
        with EvalBlock() as eb:
            eb.set_diddle("Database", "MktDataDate", mdd)
            dvd_ccy = GetVal(self, "DvdCcy")

        if ccy == dvd_ccy:
            return 1.0
        else:
            # --- dvd_ccy -> ccy
            to_usd = graph("{0:3s}/USD".format(dvd_ccy), "SpotByDate", mdd)
            to_ccy = 1.0 / graph("{0:3s}/USD".format(ccy), "SpotByDate", mdd)

            return to_usd * to_ccy / mul


# -----------------------------------------------------------------------------
def prepare_for_test():
    import agora.system.ufo_database as ufo_database
    ufo_database.prepare_for_test()
