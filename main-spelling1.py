import streamlit as st
import re

# ======================
# LOAD KAMUS
# ======================
with open("kbbi_dataset.txt", "r", encoding="utf-8") as f:
    kamus_txt = set([
        line.strip().lower()
        for line in f
        if " " not in line.strip()
    ])

# ======================
# DLD
# ======================
def damerau_levenshtein_distance(s1, s2):
    d = {}
    for i in range(-1, len(s1)+1):
        d[(i, -1)] = i+1
    for j in range(-1, len(s2)+1):
        d[(-1, j)] = j+1

    for i in range(len(s1)):
        for j in range(len(s2)):
            cost = 0 if s1[i] == s2[j] else 1
            d[(i, j)] = min(
                d[(i-1, j)] + 1,
                d[(i, j-1)] + 1,
                d[(i-1, j-1)] + cost
            )
            if i and j and s1[i] == s2[j-1] and s1[i-1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[(i-2, j-2)] + cost)

    return d[len(s1)-1, len(s2)-1]

# ======================
# FILTER KANDIDAT
# ======================
def filtering_kamus(kata):
    return [k for k in kamus_txt if abs(len(k) - len(kata)) <= 2]

# ======================
# MODEL SKENARIO 1 (DLD + HEURISTIC)
# ======================
def model_skenario1(kata):

    kata_asli = kata
    kata = kata.lower().strip(",.!?")

    # jika sudah benar
    if kata in kamus_txt:
        return kata, "BENAR", [], kata_asli

    kandidat = filtering_kamus(kata)

    ranking = []
    for k in kandidat:
        jarak = damerau_levenshtein_distance(kata, k)

        # 🔥 heuristic (sesuai ipynb)
        skor = jarak
        skor += abs(len(kata) - len(k)) * 0.5

        if kata[:2] == k[:2]:
            skor -= 0.5

        if kata in k or k in kata:
            skor -= 0.5

        ranking.append((k, skor))

    ranking.sort(key=lambda x: x[1])

    if ranking:
        top3 = ranking[:3]
        kandidat_terbaik, skor = ranking[0]

        # threshold typo ringan
        if skor <= 2.5:
            return kandidat_terbaik, "DLD", top3, kata_asli

        return kata, "TIDAK DIKOREKSI", top3, kata_asli

    return kata, "TIDAK DIKOREKSI", [], kata_asli

# ======================
# UI STREAMLIT
# ======================
st.title("Spelling Correction - Skenario 1")
st.write("Metode: Damerau Levenshtein Distance + Heuristic")

teks = st.text_area("Masukkan kalimat:")

if st.button("Koreksi"):

    hasil_kalimat = []
    detail = []
    jumlah_koreksi = 0

    for kata in teks.split():

        hasil, metode, top3, kata_asli = model_skenario1(kata)

        # 🔥 PENANDA KOREKSI
        if metode == "DLD" and kata.lower() != hasil:
            hasil_kalimat.append(f"[{kata} → {hasil}]")
            jumlah_koreksi += 1
        else:
            hasil_kalimat.append(hasil)

        if metode != "BENAR":
            detail.append((kata, hasil, metode, top3))

    # ======================
    # OUTPUT HASIL
    # ======================
    st.subheader("Hasil:")
    st.success(" ".join(hasil_kalimat))

    st.info(f"Jumlah kata dikoreksi: {jumlah_koreksi}")

    # ======================
    # DETAIL
    # ======================
    st.subheader("Detail:")

    for kata, hasil, metode, top3 in detail:

        if metode == "TIDAK DIKOREKSI":
            st.warning(f"{kata} → tidak bisa dikoreksi")

        else:
            st.error(f"{kata} → {hasil} ({metode})")

        if top3:
            st.write("Top Kandidat:")
            for i, (k, j) in enumerate(top3, 1):
                st.write(f"{i}. {k} (skor={round(j,2)})")