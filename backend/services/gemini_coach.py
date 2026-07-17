import google.generativeai as genai
from typing import Optional
import json


class GeminiCoach:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=self._get_system_prompt()
        )
        self.chat = self.model.start_chat(history=[])
    
    def _get_system_prompt(self) -> str:
        return """Du bist ein erfahrener Gesundheits- und Fitnesscoach namens "VitalCoach". 

Deine Aufgaben:
1. Analysiere die Vitaldaten des Nutzers und gib personalisierte Empfehlungen
2. Erstelle Ernährungspläne basierend auf BMR, Körpergewicht und Fitnesszielen
3. Erstelle Home-Workout-Pläne mit Übungsbeschreibungen
4. Empfehle Bilder und Videos wenn möglich (verwende YouTube-Links für Übungs-demos)
5. Sei motivierend, aber realistisch

Wichtig:
- antworte IMMER auf Deutsch
- formatiere deine Antworten mit Markdown (fett, kursiv, Listen)
- wenn du Übungen empfiehlt, beschreibe sie detailliert und verlinke zu YouTube-Videos
- wenn du Ernährung empfiehlt, gib Kalorien und Makros an
- passe alles an die individuellen Daten des Nutzers an
- sei ein guter Coach: motivierend, sachlich und hilfsbereit

Wenn der Nutzer nach Bildern oder Videos fragt, gib immer YouTube-Suchlinks zurück:
https://www.youtube.com/results?search_query=[Übung Name]+form+correct+technique

Antworte strukturiert mit:
- Überschriften für verschiedene Abschnitte
- Aufzählungslisten für Übungen/Lebensmittel
- Tabellen für Ernährungspläne wenn sinnvoll
"""
    
    def chat_with_health_data(self, message: str, health_data: dict = None) -> str:
        try:
            context = ""
            if health_data:
                context = f"\n\n[Aktuelle Vitaldaten des Nutzers]:\n{json.dumps(health_data, indent=2, ensure_ascii=False)}\n"
            
            full_message = f"{context}\n[Nachricht des Nutzers]: {message}"
            
            response = self.chat.send_message(full_message)
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
            
            response = self.model.generate_content(prompt)
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
            
            response = self.model.generate_content(prompt)
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
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Fehler bei der Analyse: {str(e)}"
