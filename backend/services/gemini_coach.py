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
            prompt = f"""Erstelle einen individuellen Ernährungsplan für:
            - Gewicht: {weight} kg, Größe: {height} cm, Alter: {age} Jahre
            - Geschlecht: {gender}
            - Ziel: {goal}
            - Aktivitätslevel: {activity_level}
            
            Berechne BMR und TDEE, dann:
            1. Tägliche Kalorienempfehlung
            2. Makronährstoff-Verteilung (Protein, KH, Fett in Gramm)
            3. Konkreter Tagesplan mit 3 Hauptmahlzeiten + 2 Snacks
            4. Gib BEISPIELHAFTE Gerichte mit konkreten Zutaten und Mengen an
            5. Variation: Schlage für jede Mahlzeit 2-3 Alternativen vor
            
            WICHTIG: Gib immer verschiedene, abwechslungsreiche Mahlzeiten vor - 
            niemals immer die gleichen. Denke an deutsche Küche, aber auch international.
            Format als Markdown mit Tabellen."""
            
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
            prompt = f"""Erstelle einen Home-Workout-Plan für:
            - Fitnesslevel: {fitness_level}
            - Ziel: {goal}
            - NUR Körpergewichtsübungen - KEIN Equipment, KEINE Geräte
            - Trainingstage pro Woche: {days_per_week}
            
            WICHTIG: Verwende AUSSCHLIESSLICH Übungen mit dem eigenen Körpergewicht:
            - Liegestütz (verschiedene Varianten)
            - Kniebeugen, Ausfallschritte
            - Plank, Mountain Climbers
            - Burpees, Jumping Jacks
            - Dips (am Stuhl), Superman
            KEINE Hanteln, KEINE Bänder, KEINE Geräte!
            
            Für JEDE Übung:
            1. Name der Übung
            2. Klare Beschreibung der Ausführung
            3. Sätze x Wiederholungen
            4. YouTube-Suchlink: https://www.youtube.com/results?search_query=[Übung]+bodyweight+form
            
            Struktur: Aufwärmen → Hauptteil → Cool Down
            Format als Markdown."""
            
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
