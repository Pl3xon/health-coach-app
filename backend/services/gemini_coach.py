from google import genai
from google.genai import types
import json
from typing import Optional


class GeminiCoach:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        return """Du bist "VitalCoach" - ein erfahrener, professioneller Gesundheits- und Fitnesscoach.

Deine Aufgaben:
- Beantworte Fragen des Nutzers hilfreich und kompetent
- Nutze die bereitgestellten Vitaldaten um personalisierte Empfehlungen zu geben
- Erstelle Ernährungspläne mit Kalorien und Makros
- Erstelle Workout-Pläne mit konkreten Übungen
- Analysiere den Fortschritt anhand der Daten

Regeln:
- IMMER auf Deutsch antworten
- Freundlich, motivierend und professionell
- Konkrete, umsetzbare Empfehlungen geben
- Bei Fortschrittsfragen: die bereitgestellten Zahlen kommentieren und bewerten
- Bei Ernährungsfragen: Mahlzeiten mit Kalorien und Makros vorschlagen
- Bei Workout-Fragen: Übungen mit Sätzen, Wiederholungen und Ausführung beschreiben
- Markdown nutzen für Struktur (fett, Listen, Überschriften)"""
    
    def chat_with_health_data(self, message: str, health_data: dict = None) -> str:
        try:
            context = ""
            if health_data:
                context = f"\n\n[Aktuelle Vitaldaten des Nutzers]:\n{json.dumps(health_data, indent=2, ensure_ascii=False)}\n"
            
            full_message = f"{context}\n[Nachricht des Nutzers]: {message}"
            
            response = self.client.models.generate_content(
                model="gemini-3.5-flash",
                contents=full_message,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt
                )
            )
            return response.text
        except Exception as e:
            return f"Entschuldigung, es ist ein Fehler aufgetreten: {str(e)}"
    
    def generate_nutrition_plan(self, weight: float, height: float, age: int, 
                                 gender: str, goal: str, activity_level: str) -> str:
        try:
            prompt = f"""Erstelle einen detaillierten Ernährungsplan für folgenden Nutzer:
            - Gewicht: {weight} kg
            - Größe: {height} cm
            - Alter: {age} Jahre
            - Geschlecht: {gender}
            - Ziel: {goal}
            - Aktivitätslevel: {activity_level}
            
            Berechne zuerst den BMR und TDEE, erstelle dann:
            1. Tägliche Kalorienempfehlung
            2. Makronährstoff-Verteilung (Protein, KH, Fett)
            3. Beispiel-Fahrplan für einen Tag (Frühstück, Mittag, Abend, Snacks)
            4. Einkaufsliste für die Woche
            
            Format als Markdown mit Tabellen wo möglich."""
            
            response = self.client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt
                )
            )
            return response.text
        except Exception as e:
            return f"Fehler bei der Planerstellung: {str(e)}"
    
    def generate_workout_plan(self, fitness_level: str, goal: str, 
                               available_equipment: str = "Nur Körpergewicht",
                               days_per_week: int = 4) -> str:
        try:
            prompt = f"""Erstelle einen detaillierten Home-Workout-Plan für:
            - Fitnesslevel: {fitness_level}
            - Ziel: {goal}
            - Equipment: {available_equipment}
            - Trainingstage pro Woche: {days_per_week}
            
            WICHTIG: Für JEDE Übung:
            1. Name der Übung
            2. Detaillierte Beschreibung der Ausführung
            3. Satz- und Wiederholungszahl
            4. YouTube-Link zur Demonstration: https://www.youtube.com/results?search_query=[Übung]+exercise+form
            
            Struktur:
            - Aufwärmen (5 Min)
            - Hauptteil nach Muskelgruppen
            - Cool Down
            
            Format als Markdown mit klaren Überschriften für jeden Trainingstag."""
            
            response = self.client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt
                )
            )
            return response.text
        except Exception as e:
            return f"Fehler bei der Planerstellung: {str(e)}"
    
    def analyze_progress(self, measurements: list, goal: str) -> str:
        try:
            prompt = f"""Analysiere den Fortschritt des Nutzers basierend auf diesen Messdaten:
            {json.dumps(measurements[:10], indent=2, ensure_ascii=False)}
            
            Ziel: {goal}
            
            Gib eine detaillierte Analyse mit:
            1. Trend-Bewertung (Gewicht, Körperfett, Muskelmasse)
            2. Was läuft gut
            3. Was verbessert werden kann
            4. Konkrete Empfehlungen für die nächste Woche
            
            Sei spezifisch und datenbasiert."""
            
            response = self.client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt
                )
            )
            return response.text
        except Exception as e:
            return f"Fehler bei der Analyse: {str(e)}"
