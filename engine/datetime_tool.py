"""
DateTimeTool — Data e ora per il ReasoningEngine.
"""

from datetime import datetime, timedelta
import calendar


class DateTimeTool:
    """Tool per data e ora."""
    
    def now(self) -> dict:
        """Data e ora attuale."""
        now = datetime.now()
        return {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "day": now.strftime("%A"),
            "day_it": self._day_italian(now.strftime("%A")),
            "month": now.strftime("%B"),
            "month_it": self._month_italian(now.strftime("%B")),
            "year": now.year,
            "timestamp": now.timestamp()
        }
    
    def today(self) -> str:
        """Data di oggi in italiano."""
        now = datetime.now()
        day_name = self._day_italian(now.strftime("%A"))
        month_name = self._month_italian(now.strftime("%B"))
        return f"{day_name} {now.day} {month_name} {now.year}"
    
    def time(self) -> str:
        """Ora attuale."""
        return datetime.now().strftime("%H:%M")
    
    def day_of_week(self, date_str: str = None) -> str:
        """Giorno della settimana."""
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
            except:
                return "Formato data non valido (usa YYYY-MM-DD)"
        else:
            dt = datetime.now()
        
        day_en = dt.strftime("%A")
        return self._day_italian(day_en)
    
    def days_until(self, date_str: str) -> dict:
        """Giorni fino a una data."""
        try:
            target = datetime.strptime(date_str, "%Y-%m-%d")
            now = datetime.now()
            delta = target - now
            
            if delta.days < 0:
                return {"days": abs(delta.days), "message": f"È passato {abs(delta.days)} giorni fa"}
            elif delta.days == 0:
                return {"days": 0, "message": "È oggi!"}
            else:
                return {"days": delta.days, "message": f"Mancano {delta.days} giorni"}
        except:
            return {"error": "Formato data non valido"}
    
    def add_days(self, days: int) -> str:
        """Aggiungi giorni alla data odierna."""
        future = datetime.now() + timedelta(days=days)
        day_name = self._day_italian(future.strftime("%A"))
        month_name = self._month_italian(future.strftime("%B"))
        return f"{day_name} {future.day} {month_name} {future.year}"
    
    def _day_italian(self, day_en: str) -> str:
        days = {
            "Monday": "Lunedì",
            "Tuesday": "Martedì",
            "Wednesday": "Mercoledì",
            "Thursday": "Giovedì",
            "Friday": "Venerdì",
            "Saturday": "Sabato",
            "Sunday": "Domenica"
        }
        return days.get(day_en, day_en)
    
    def _month_italian(self, month_en: str) -> str:
        months = {
            "January": "Gennaio",
            "February": "Febbraio",
            "March": "Marzo",
            "April": "Aprile",
            "May": "Maggio",
            "June": "Giugno",
            "July": "Luglio",
            "August": "Agosto",
            "September": "Settembre",
            "October": "Ottobre",
            "November": "Novembre",
            "December": "Dicembre"
        }
        return months.get(month_en, month_en)
