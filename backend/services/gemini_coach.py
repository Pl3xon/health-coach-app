from google import genai
from google.genai import types
import json
from typing import Optional


class GeminiCoach:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        return """Du bist "VitalCoach" - ein erfahrener Personal Trainer und Ernährungsberater.

Du betreust deinen Kunden Kevin persönlich. Du kennst seine Daten, seine Ziele und seinen Fortschritt.
Du redest mit ihm wie ein echter Trainer: direkt, motivierend, ehrlich und mit konkreten Tipps.

Deine Aufgaben:
- Ernährungspläne basierend auf seinen Kalorienbedarf und Zielen erstellen
- Trainingspläne mit konkreten Übungen erstellen (nur Körpergewicht)
- Seine Vitalwerte analysieren und Fortschritt bewerten
- Motivieren aber auch ehrlich sein wenn etwas nicht läuft
- Auf seine Fragen eingehen und individuell antworten

Stil:
- Deutsch, du/du-Form, wie ein guter Trainer
- Konkret und umsetzbar, kein Geschwafel
- Nutze Markdown (fett, Listen) für Struktur
- Erwähne seine konkreten Zahlen wenn du sie in den Daten siehst
- Wenn du nach einem Plan fragst: gib MAHLZEITEN mit Kalorien und Makros an
- Wenn du nach Training fragst: gib Übungen mit Sätzen x Wiederholungen an
- Kurze bis mittellange Antworten, je nach Frage angepasst"""
    
    def chat_with_health_data(self, message: str, health_data: dict = None) -> str:
        try:
            context = ""
            if health_data:
                context = f"\n\n[Aktuelle Daten des Nutzers]:\n{json.dumps(health_data, indent=2, ensure_ascii=False)}\n"
            
            full_message = f"{context}\n[Nachricht]: {message}"
            
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
