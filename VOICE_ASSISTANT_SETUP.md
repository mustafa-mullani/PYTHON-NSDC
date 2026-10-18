# Multilingual Voice Assistant — Setup and Usage

This upgrade adds a free browser-based voice assistant to the existing Flask + SQLite Hotel Event Management System. It uses the browser's Web Speech API; no paid AI API key or new Python package is required. Existing Flask routes, booking validation, session-based flow, SQLite database and menu POST handling are retained.

## Files added

- `static/voice-assistant.js` — speech recognition, speech output, booking form filling and menu option matching.
- `static/voice-assistant.css` — floating assistant panel styling.
- `VOICE_ASSISTANT_SETUP.md` — these instructions.

The assistant script and stylesheet are linked in `book.html`, the three hotel menu-choice pages, and all nine individual food menu pages.

## Run the project

1. Extract this ZIP to a normal writable folder.
2. Open a terminal in the `event  management` project folder (the folder containing `app.py`).
3. Activate your existing Python environment if you use one.
4. Install Flask only if it is not already installed:
   ```powershell
   python -m pip install flask
   ```
5. Start the app using the same command you normally use, for example:
   ```powershell
   python app.py
   ```
   If `app.py` does not start the development server at the bottom of the file, use:
   ```powershell
   python -m flask --app app run --debug
   ```
6. Open the local URL shown in the terminal using the latest Google Chrome or Microsoft Edge. Allow microphone access when prompted.
7. Select a hotel and hall as usual, then open the booking form. Use the floating **Voice Assistant** button.

## Supported interactions

### Booking form

Choose English (India), Hindi, or Marathi. Tap the microphone and say one instruction at a time. Examples:

- “Birthday event” / “जन्मदिन” / “वाढदिवस” — selects the event type.
- “25 November 2026” — fills the date (check the year and date afterward).
- “100 guests” / “100 people” — fills capacity.
- “Start time 10 AM” and “End time 2 PM” — fills times. The existing four-hour minimum still applies.
- “Event name is Family Birthday” — attempts to fill the event name.

The browser may transcribe dates, times and regional-language words differently. Always verify the filled fields and complete missing fields manually. The assistant does not submit the form for you.

### Menu pages

On the Veg / Chicken / Mutton menu-choice page, say “Veg menu”, “Chicken menu”, or “Mutton menu” to open that menu. On an individual menu page, say the visible menu item name, for example “Tomato Soup” or “Aloo Corn Tikki”, to select the matching radio option. Menu options are still submitted using the existing form and Flask route.

## Important limitations

- This is browser speech assistance, not a cloud AI model. It uses pattern matching and the visible menu options; it does not have unrestricted conversational understanding.
- Speech recognition availability and Hindi/Marathi accuracy depend on the browser, operating system, microphone and browser speech service. Chrome/Edge support is recommended; some browser configurations require internet access for recognition.
- Speech synthesis voices are provided by the browser/operating system. Hindi or Marathi spoken responses may fall back to another available voice if a matching voice is not installed.
- Voice selection only fills or selects fields. It never bypasses the existing server-side booking checks, database conflict checks, login flow or final form submission.
- For best results, say one field or menu item at a time, check the transcript and verify all values before submitting.

## Quick test checklist

1. Open the booking page and confirm the floating assistant appears.
2. Allow microphone access and test each language using a short phrase.
3. Confirm event type, date, capacity and time are filled correctly.
4. Try an invalid date, capacity or duration and verify the existing Flask validation still blocks it.
5. Open each hotel's menu-choice page and try selecting Veg / Chicken / Mutton by voice.
6. Open a menu item page and say a visible radio option. Confirm it becomes selected.
7. Submit the menu normally and verify the existing login/save-booking flow works as before.
