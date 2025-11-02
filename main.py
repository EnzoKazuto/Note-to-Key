import sounddevice as sd
import numpy as np
import librosa
import keyboard
import time

# ======= CONFIGURAÇÃO =======
SAMPLERATE = 48000
BLOCKSIZE = 1024          # ~21 ms (menor bloco = menor delay, mas mais CPU)
DURATION = BLOCKSIZE / SAMPLERATE
DEBUG = True
VOLUME_THRESHOLD = 0.01
HOLD_TIME = 0.1   # segundos extras para manter 'c' pressionada

note_to_key = {
    "B5": ["l", "x"],
    "C#6": ["o", "x"],
    "A#5": "a",
    "D#5": "s",
    "F#5": ["f"],
    "C5": "n",
    "D5": "m",
    "F5": "z",
    "E5": "x",
    "G#5": "c",
    "G5": ["z", "n"],
    "A5": ["z", "m"],
    "F6": "v",
    "E6": ["o", "f"]
}

repeat_keys = {"o", "l", "x"} #faz as teclas serem pressionadas varias vezes

currently_pressed = set()
last_note = None
last_keys = []
stable_note = None
stable_count = 0
last_gsharp_time = 0   # armazena a última vez que G#5 foi tocada

sustain_c = False  # controla se o sustain do "c" está ligado


# ======= FUNÇÃO DE NOTA =======
def freq_to_note(freq):
    if freq <= 0:
        return None
    A4 = 440.0
    note_num = 12 * np.log2(freq / A4) + 69
    rounded = int(round(note_num))
    if not (0 <= rounded < 128):
        return None
    names = ['C', 'C#', 'D', 'D#', 'E', 'F',
             'F#', 'G', 'G#', 'A', 'A#', 'B']
    note_name = names[rounded % 12]
    octave = (rounded // 12) - 1
    return f"{note_name}{octave}"


# ======= CALLBACK DE ÁUDIO =======
def audio_callback(indata, frames, time_info, status):
    global currently_pressed, last_note, last_keys, stable_note, stable_count, last_gsharp_time, sustain_c

    samples = indata[:, 0]

    # ===== volume mínimo =====
    volume = np.mean(np.abs(samples))
    if volume < VOLUME_THRESHOLD:
        now = time.time()

        # libera teclas
        to_release = set()
        for key in currently_pressed:
            if key == "c" and sustain_c:
                if now - last_gsharp_time > HOLD_TIME:
                    to_release.add(key)
            else:
                to_release.add(key)

        for key in to_release:
            keyboard.release(key)
            currently_pressed.remove(key)
            if DEBUG and to_release:
                print(f"⏳ Soltando: {', '.join(to_release)}")

        last_keys = []
        last_note = None
        stable_note = None
        stable_count = 0
        return

    # ===== pitch detection com Librosa =====
    f0 = librosa.yin(samples, fmin=50, fmax=2000, sr=SAMPLERATE)
    pitch = np.median(f0[np.isfinite(f0)])

    if pitch < 50 or pitch > 2000:
        return

    note = freq_to_note(pitch)

    # ===== estabilização =====
    if note == stable_note:
        stable_count += 1
    else:
        stable_note = note
        stable_count = 1

    if stable_count < 2:
        return

    # ===== mostrar sempre a nota =====
    if DEBUG:
        print(f" Nota detectada: {note} ({pitch:.1f} Hz)")

    # ===== mapeamento tecla =====
    if note and note in note_to_key:
        keys = note_to_key[note]
        if not isinstance(keys, list):
            keys = [keys]

        if note != last_note:
            for old_key in last_keys:
                if old_key in currently_pressed and old_key not in keys:
                    if not (old_key == "c" and sustain_c):
                        keyboard.release(old_key)
                        currently_pressed.remove(old_key)
                        if DEBUG:
                            print(f" Soltando: {old_key}")

        for key in keys:
            if key == "c":
                last_gsharp_time = time.time()
            if key in repeat_keys:
                keyboard.press(key)
                keyboard.release(key)
                if DEBUG:
                    print(f" Repetindo: {key}")
            else:
                if key not in currently_pressed:
                    keyboard.press(key)
                    currently_pressed.add(key)
                    if DEBUG:
                        print(f" Pressionando: {key}")

        last_note = note
        last_keys = keys

    else:
        # nota não mapeada
        if DEBUG:
            print(f" Nota não mapeada: {note} ({pitch:.1f} Hz)")

        if currently_pressed:
            now = time.time()
            to_release = set()
            for key in currently_pressed:
                if key == "c" and sustain_c:
                    if now - last_gsharp_time > HOLD_TIME:
                        to_release.add(key)
                else:
                    to_release.add(key)

            for key in to_release:
                keyboard.release(key)
                currently_pressed.remove(key)
                if DEBUG:
                    print(f" Soltando (não mapeada): {key}")

        last_keys = []
        last_note = None


# ======= LOOP =======
print(" Iniciando detecção em tempo real. Ctrl+C para sair.")
print(" Aperte [ESPAÇO] para ativar/desativar o sustain do 'c'.")

try:
    with sd.InputStream(channels=1, samplerate=SAMPLERATE, blocksize=BLOCKSIZE, callback=audio_callback):
        while True:
            if keyboard.is_pressed("space"):
                sustain_c = not sustain_c
                print(f" Sustain do 'c': {'ATIVADO' if sustain_c else 'DESATIVADO'}") #faz o botao C segurar para pular enquanto corre
                time.sleep(0.3)  # debounce
            time.sleep(0.01)
except KeyboardInterrupt:
    for key in currently_pressed:
        keyboard.release(key)
    print("\n Programa encerrado.")
