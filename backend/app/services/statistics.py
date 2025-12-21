"""
Service de calcul des statistiques de trading
Contient toute la logique métier pour les stats
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from app.models import Trade


class StatisticsService:
    """Service pour calculer les statistiques de trading"""
    
    def __init__(self, trades: List[Trade]):
        self.trades = trades
        self.completed_trades = [t for t in trades if t.result_r is not None]
    
    def calculate_global_stats(self) -> Dict:
        """
        Calcule les statistiques globales.
        """
        if not self.completed_trades:
            return self._empty_global_stats()
        
        total = len(self.completed_trades)
        winners = [t for t in self.completed_trades if t.result_r > 0]
        losers = [t for t in self.completed_trades if t.result_r < 0]
        breakevens = [t for t in self.completed_trades if t.result_r == 0]
        
        # Winrate
        winrate = (len(winners) / total * 100) if total > 0 else 0
        
        # Moyennes
        avg_win_r = sum(t.result_r for t in winners) / len(winners) if winners else 0
        avg_loss_r = sum(t.result_r for t in losers) / len(losers) if losers else 0
        
        # Expectancy = (Winrate × Avg Win) - (Loss Rate × Avg Loss)
        loss_rate = len(losers) / total if total > 0 else 0
        expectancy = (winrate / 100 * avg_win_r) - (loss_rate * abs(avg_loss_r))
        
        # Profit Factor = Gross Profit / Gross Loss
        gross_profit = sum(t.result_r for t in winners)
        gross_loss = abs(sum(t.result_r for t in losers))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Totaux
        total_r = sum(t.result_r for t in self.completed_trades)
        total_pnl = sum(t.pnl_usd or 0 for t in self.completed_trades)
        
        # Drawdown
        max_dd_r, max_dd_pct = self._calculate_drawdown()
        
        # RR moyens
        avg_rr_expected = sum(t.rr_expected for t in self.completed_trades) / total
        avg_rr_actual = total_r / total if total > 0 else 0
        
        # Discipline
        respected_count = sum(1 for t in self.completed_trades if t.respected_plan)
        discipline_rate = (respected_count / total * 100) if total > 0 else 0
        
        # Durée moyenne
        durations = [t.duration_min for t in self.completed_trades if t.duration_min]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total_trades": total,
            "winning_trades": len(winners),
            "losing_trades": len(losers),
            "breakeven_trades": len(breakevens),
            "winrate": round(winrate, 2),
            "avg_win_r": round(avg_win_r, 2),
            "avg_loss_r": round(avg_loss_r, 2),
            "expectancy": round(expectancy, 3),
            "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else 999.99,
            "total_pnl_usd": round(total_pnl, 2),
            "total_r": round(total_r, 2),
            "max_drawdown_r": round(max_dd_r, 2),
            "max_drawdown_pct": round(max_dd_pct, 2),
            "avg_rr_expected": round(avg_rr_expected, 2),
            "avg_rr_actual": round(avg_rr_actual, 2),
            "discipline_rate": round(discipline_rate, 2),
            "avg_duration_min": round(avg_duration, 1)
        }
    
    def _calculate_drawdown(self) -> tuple:
        """
        Calcule le drawdown maximum en R et en %.
        Basé sur la courbe d'equity cumulative.
        """
        if not self.completed_trades:
            return 0, 0
        
        # Trier par date
        sorted_trades = sorted(self.completed_trades, key=lambda t: t.date)
        
        cumulative = 0
        peak = 0
        max_drawdown_r = 0
        
        for trade in sorted_trades:
            cumulative += trade.result_r
            if cumulative > peak:
                peak = cumulative
            
            drawdown = peak - cumulative
            if drawdown > max_drawdown_r:
                max_drawdown_r = drawdown
        
        # Drawdown en % (approximatif basé sur le peak)
        max_dd_pct = (max_drawdown_r / peak * 100) if peak > 0 else 0
        
        return max_drawdown_r, max_dd_pct
    
    def calculate_stats_by_setup(self) -> List[Dict]:
        """Calcule les statistiques par setup"""
        if not self.completed_trades:
            return []
        
        by_setup = defaultdict(list)
        for trade in self.completed_trades:
            by_setup[trade.setup].append(trade)
        
        results = []
        for setup, trades in by_setup.items():
            total = len(trades)
            winners = [t for t in trades if t.result_r > 0]
            losers = [t for t in trades if t.result_r < 0]
            
            winrate = len(winners) / total * 100
            total_r = sum(t.result_r for t in trades)
            avg_rr = total_r / total
            
            # Expectancy
            avg_win = sum(t.result_r for t in winners) / len(winners) if winners else 0
            avg_loss = sum(t.result_r for t in losers) / len(losers) if losers else 0
            loss_rate = len(losers) / total
            expectancy = (winrate / 100 * avg_win) - (loss_rate * abs(avg_loss))
            
            # Profit Factor
            gross_profit = sum(t.result_r for t in winners)
            gross_loss = abs(sum(t.result_r for t in losers))
            pf = gross_profit / gross_loss if gross_loss > 0 else 999.99
            
            results.append({
                "setup": setup,
                "total_trades": total,
                "winrate": round(winrate, 2),
                "expectancy": round(expectancy, 3),
                "total_r": round(total_r, 2),
                "avg_rr": round(avg_rr, 2),
                "profit_factor": round(pf, 2)
            })
        
        # Trier par total_r décroissant
        return sorted(results, key=lambda x: x["total_r"], reverse=True)
    
    def calculate_stats_by_session(self) -> List[Dict]:
        """Calcule les statistiques par session de trading"""
        if not self.completed_trades:
            return []
        
        by_session = defaultdict(list)
        for trade in self.completed_trades:
            by_session[trade.session.value].append(trade)
        
        results = []
        for session, trades in by_session.items():
            total = len(trades)
            winners = [t for t in trades if t.result_r > 0]
            losers = [t for t in trades if t.result_r < 0]
            
            winrate = len(winners) / total * 100
            total_r = sum(t.result_r for t in trades)
            avg_rr = total_r / total
            
            # Expectancy
            avg_win = sum(t.result_r for t in winners) / len(winners) if winners else 0
            avg_loss = sum(t.result_r for t in losers) / len(losers) if losers else 0
            loss_rate = len(losers) / total
            expectancy = (winrate / 100 * avg_win) - (loss_rate * abs(avg_loss))
            
            results.append({
                "session": session,
                "total_trades": total,
                "winrate": round(winrate, 2),
                "expectancy": round(expectancy, 3),
                "total_r": round(total_r, 2),
                "avg_rr": round(avg_rr, 2)
            })
        
        return sorted(results, key=lambda x: x["total_r"], reverse=True)
    
    def calculate_daily_stats(self, days: int = 30) -> List[Dict]:
        """Calcule les statistiques journalières"""
        if not self.completed_trades:
            return []
        
        # Grouper par date
        by_date = defaultdict(list)
        for trade in self.completed_trades:
            date_key = trade.date.strftime("%Y-%m-%d")
            by_date[date_key].append(trade)
        
        results = []
        for date_str, trades in sorted(by_date.items(), reverse=True)[:days]:
            total = len(trades)
            winners = [t for t in trades if t.result_r > 0]
            losers = [t for t in trades if t.result_r < 0]
            
            results.append({
                "date": date_str,
                "total_trades": total,
                "winning_trades": len(winners),
                "losing_trades": len(losers),
                "total_r": round(sum(t.result_r for t in trades), 2),
                "pnl_usd": round(sum(t.pnl_usd or 0 for t in trades), 2),
                "winrate": round(len(winners) / total * 100, 2) if total > 0 else 0
            })
        
        return results
    
    def calculate_weekly_stats(self, weeks: int = 12) -> List[Dict]:
        """Calcule les statistiques hebdomadaires"""
        if not self.completed_trades:
            return []
        
        # Grouper par semaine (ISO week)
        by_week = defaultdict(list)
        for trade in self.completed_trades:
            # Début de la semaine (lundi)
            week_start = trade.date - timedelta(days=trade.date.weekday())
            week_key = week_start.strftime("%Y-%m-%d")
            by_week[week_key].append(trade)
        
        results = []
        for week_start_str, trades in sorted(by_week.items(), reverse=True)[:weeks]:
            week_start = datetime.strptime(week_start_str, "%Y-%m-%d")
            week_end = week_start + timedelta(days=6)
            
            total = len(trades)
            winners = [t for t in trades if t.result_r > 0]
            losers = [t for t in trades if t.result_r < 0]
            
            winrate = len(winners) / total * 100 if total > 0 else 0
            
            # Expectancy
            avg_win = sum(t.result_r for t in winners) / len(winners) if winners else 0
            avg_loss = sum(t.result_r for t in losers) / len(losers) if losers else 0
            loss_rate = len(losers) / total if total > 0 else 0
            expectancy = (winrate / 100 * avg_win) - (loss_rate * abs(avg_loss))
            
            results.append({
                "week_start": week_start_str,
                "week_end": week_end.strftime("%Y-%m-%d"),
                "total_trades": total,
                "winning_trades": len(winners),
                "losing_trades": len(losers),
                "total_r": round(sum(t.result_r for t in trades), 2),
                "pnl_usd": round(sum(t.pnl_usd or 0 for t in trades), 2),
                "winrate": round(winrate, 2),
                "expectancy": round(expectancy, 3)
            })
        
        return results
    
    def calculate_error_stats(self) -> List[Dict]:
        """Analyse les erreurs les plus fréquentes"""
        error_trades = [t for t in self.completed_trades if t.error]
        
        if not error_trades:
            return []
        
        by_error = defaultdict(list)
        for trade in error_trades:
            by_error[trade.error_type.value].append(trade)
        
        total_errors = len(error_trades)
        results = []
        
        for error_type, trades in by_error.items():
            count = len(trades)
            losses = [t.result_r for t in trades if t.result_r < 0]
            avg_loss = sum(losses) / len(losses) if losses else 0
            
            results.append({
                "error_type": error_type,
                "count": count,
                "percentage": round(count / total_errors * 100, 2),
                "avg_loss_r": round(avg_loss, 2)
            })
        
        return sorted(results, key=lambda x: x["count"], reverse=True)
    
    def calculate_mental_state_correlation(self) -> List[Dict]:
        """Analyse la corrélation entre état mental et résultats"""
        trades_with_mental = [t for t in self.completed_trades if t.mental_state]
        
        if not trades_with_mental:
            return []
        
        by_state = defaultdict(list)
        for trade in trades_with_mental:
            by_state[trade.mental_state].append(trade)
        
        results = []
        for state in range(1, 6):
            trades = by_state.get(state, [])
            if not trades:
                continue
            
            total = len(trades)
            winners = [t for t in trades if t.result_r > 0]
            avg_result = sum(t.result_r for t in trades) / total
            
            results.append({
                "mental_state": state,
                "total_trades": total,
                "winrate": round(len(winners) / total * 100, 2),
                "avg_result_r": round(avg_result, 2)
            })
        
        return results
    
    def calculate_equity_curve(self) -> List[Dict]:
        """Génère les points de la courbe d'equity"""
        if not self.completed_trades:
            return []
        
        sorted_trades = sorted(self.completed_trades, key=lambda t: t.date)
        
        cumulative_r = 0
        cumulative_pnl = 0
        results = []
        
        for i, trade in enumerate(sorted_trades, 1):
            cumulative_r += trade.result_r
            cumulative_pnl += trade.pnl_usd or 0
            
            results.append({
                "date": trade.date.strftime("%Y-%m-%d %H:%M"),
                "cumulative_r": round(cumulative_r, 2),
                "cumulative_pnl": round(cumulative_pnl, 2),
                "trade_count": i
            })
        
        return results
    
    def _empty_global_stats(self) -> Dict:
        """Retourne des stats vides"""
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "breakeven_trades": 0,
            "winrate": 0,
            "avg_win_r": 0,
            "avg_loss_r": 0,
            "expectancy": 0,
            "profit_factor": 0,
            "total_pnl_usd": 0,
            "total_r": 0,
            "max_drawdown_r": 0,
            "max_drawdown_pct": 0,
            "avg_rr_expected": 0,
            "avg_rr_actual": 0,
            "discipline_rate": 0,
            "avg_duration_min": 0
        }
